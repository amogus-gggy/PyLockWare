import ast
import builtins


class PythonCompiler:
    """Compiles Python source code AST into CustomVM bytecode.

    Supports:
      - Expressions: arithmetic (+,-,*,/,%), comparison (==,!=,<,>,<=,>=),
        boolean (and, or, not), bitwise (&,|,^,<<,>>,~), unary (-,+)
      - Statements: assignments, augmented assignments (+=,-=,*=,/=,%=,&=,|=,^=,<<=,>>=)
      - Conditionals: if / elif / else
      - Loops: while, for var in range(...)
      - Loop control: break, continue
      - Function calls: via syscall 10 bridge (builtins + user-defined)
    """

    # Register 15 is reserved for temp/discard operations
    _TEMP_REG = 15
    _MAX_REGS = 256  # registers 0-255 for user variables (removed limit)

    def __init__(self, builder):
        self.builder = builder
        self.variables = {}           # var_name -> register_index
        self.next_reg = 0
        self.user_funcs = {}          # func_name -> ast.FunctionDef
        self.func_to_idx = {}         # func_name -> index in builder.func_pool
        self._label_counter = 0
        self._loop_stack = []         # [(start_label, end_label), ...]
        self._string_vars = set()     # variable names known to hold strings

    # ---- Helpers ----

    def _new_label(self, prefix='lbl'):
        self._label_counter += 1
        return f'{prefix}_{self._label_counter}'

    def _discard(self):
        """Pop and discard the top of stack using the temp register."""
        self.builder.pop_reg(self._TEMP_REG)

    # ---- Public API ----

    def compile(self, source):
        tree = ast.parse(source)

        # First pass: collect user-defined function names
        for stmt in tree.body:
            if isinstance(stmt, ast.FunctionDef):
                self.user_funcs[stmt.name] = stmt

        # Second pass: compile body
        self._visit(tree)

    # ---- Dispatch ----

    def _visit(self, node):
        method = f'_visit_{type(node).__name__}'
        visitor = getattr(self, method, None)
        if visitor is None:
            raise NotImplementedError(
                f"Python construct not supported yet: {type(node).__name__}"
            )
        return visitor(node)

    def _visit_body(self, stmts):
        for stmt in stmts:
            self._visit(stmt)

    # ==================== Statements ====================

    def _visit_Module(self, node):
        func_defs = []
        body_stmts = []
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef):
                func_defs.append(stmt)
            else:
                body_stmts.append(stmt)

        # Register user-defined functions
        for func in func_defs:
            self._register_user_function(func)

        # Compile main body
        self._visit_body(body_stmts)

        self.builder.halt()

    def _visit_Assign(self, node):
        if len(node.targets) != 1:
            raise NotImplementedError("Multi-target assignment not supported")
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            raise NotImplementedError(
                f"Assignment target type not supported: {type(target).__name__}"
            )
        self._visit(node.value)

        # Track string variables for + → str_concat detection
        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            self._string_vars.add(target.id)
        elif isinstance(node.value, ast.Name) and node.value.id in self._string_vars:
            self._string_vars.add(target.id)

        reg = self._get_or_create_var(target.id)
        self.builder.pop_reg(reg)

    def _visit_AugAssign(self, node):
        """x += expr, x -= expr, x *= expr, x /= expr, x %= expr,
        x &= expr, x |= expr, x ^= expr, x <<= expr, x >>= expr"""
        if not isinstance(node.target, ast.Name):
            raise NotImplementedError(
                "Augmented assignment target must be a variable, "
                f"got {type(node.target).__name__}"
            )
        var_name = node.target.id
        reg = self._get_or_create_var(var_name)

        self.builder.push_reg(reg)
        self._visit(node.value)

        # String += handling
        if isinstance(node.op, ast.Add) and var_name in self._string_vars:
            self.builder.str_concat()
            self.builder.pop_reg(reg)
            return

        aug_ops = {
            ast.Add:    self.builder.add,
            ast.Sub:    self.builder.sub,
            ast.Mult:   self.builder.mul,
            ast.Div:    self.builder.div,
            ast.FloorDiv: self.builder.div,
            ast.Mod:    self.builder.mod,
            ast.BitAnd: self.builder.and_op,
            ast.BitOr:  self.builder.or_op,
            ast.BitXor: self.builder.xor_op,
            ast.LShift: self.builder.shl,
            ast.RShift: self.builder.shr,
        }
        handler = aug_ops.get(type(node.op))
        if handler is None:
            raise NotImplementedError(
                f"Augmented assignment operator not supported: "
                f"{type(node.op).__name__}"
            )
        handler()
        self.builder.pop_reg(reg)

    def _visit_Expr(self, node):
        self._visit(node.value)

    def _visit_FunctionDef(self, node):
        pass  # handled in _visit_Module

    def _visit_If(self, node):
        """if / elif / else statement."""
        else_label = self._new_label('if_else')
        end_label = self._new_label('if_end')

        # Condition
        self._visit(node.test)
        self.builder.push_imm(0)
        self.builder.cmp()
        self.builder.jz(else_label)

        # If body
        self._visit_body(node.body)
        self.builder.jmp(end_label)

        # Else / elif
        self.builder.add_label(else_label)
        if node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                self._visit_elif(node.orelse[0], end_label)
            else:
                self._visit_body(node.orelse)

        self.builder.add_label(end_label)

    def _visit_elif(self, node, end_label):
        """Recursively handle elif chain; all branches target end_label."""
        else_label = self._new_label('elif_else')

        self._visit(node.test)
        self.builder.push_imm(0)
        self.builder.cmp()
        self.builder.jz(else_label)

        self._visit_body(node.body)
        self.builder.jmp(end_label)

        self.builder.add_label(else_label)
        if node.orelse:
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                self._visit_elif(node.orelse[0], end_label)
            else:
                self._visit_body(node.orelse)

    def _visit_While(self, node):
        """while condition: body"""
        start_label = self._new_label('while_start')
        end_label = self._new_label('while_end')

        self._loop_stack.append((start_label, end_label))

        self.builder.add_label(start_label)
        self._visit(node.test)
        self.builder.push_imm(0)
        self.builder.cmp()
        self.builder.jz(end_label)

        self._visit_body(node.body)
        self.builder.jmp(start_label)

        self.builder.add_label(end_label)
        self._loop_stack.pop()

    def _visit_For(self, node):
        """for var in range(start, stop, step): body"""
        range_info = self._parse_range_call(node.iter)
        if range_info is None:
            raise NotImplementedError(
                "Only 'for var in range(...)' is supported"
            )

        start, stop, step = range_info

        if not isinstance(node.target, ast.Name):
            raise NotImplementedError(
                "For loop target must be a variable, "
                f"got {type(node.target).__name__}"
            )

        var_name = node.target.id
        reg = self._get_or_create_var(var_name)

        continue_label = self._new_label('for_continue')
        check_label = self._new_label('for_check')
        end_label = self._new_label('for_end')

        # _loop_stack stores (continue_target, end_label):
        #   - continue jumps to continue_label (increment first)
        #   - break jumps to end_label
        self._loop_stack.append((continue_label, end_label))

        # Initialize counter
        self.builder.push_imm(start)
        self.builder.pop_reg(reg)

        # Jump to check first (skip increment before first iteration)
        self.builder.jmp(check_label)

        # Continue point: increment counter, then re-check condition
        self.builder.add_label(continue_label)
        self.builder.push_reg(reg)
        self.builder.push_imm(step)
        self.builder.add()
        self.builder.pop_reg(reg)

        # Loop condition check
        self.builder.add_label(check_label)

        if step > 0:
            self.builder.push_reg(reg)
            self.builder.push_imm(stop)
            self.builder.cmp()
            self.builder.jge(end_label)
        elif step < 0:
            self.builder.push_reg(reg)
            self.builder.push_imm(stop)
            self.builder.cmp()
            self.builder.jle(end_label)
        else:
            raise ValueError("range() step must not be zero")

        # Body
        self._visit_body(node.body)

        # Back to continue (increment + re-check)
        self.builder.jmp(continue_label)

        self.builder.add_label(end_label)
        self._loop_stack.pop()

    def _parse_range_call(self, node):
        """Extract (start, stop, step) from a range() call with constant args.
        Returns None if not a range() call."""
        if not isinstance(node, ast.Call):
            return None
        if not (isinstance(node.func, ast.Name) and node.func.id == 'range'):
            return None

        args = []
        for arg in node.args:
            val = self._eval_constant_expr(arg)
            if val is None:
                return None
            args.append(val)

        if len(args) == 1:
            return (0, args[0], 1)
        elif len(args) == 2:
            return (args[0], args[1], 1)
        elif len(args) == 3:
            if args[2] == 0:
                raise ValueError("range() step must not be zero")
            return (args[0], args[1], args[2])
        return None

    def _eval_constant_expr(self, node):
        """Evaluate a compile-time constant expression to an int, or None."""
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            inner = self._eval_constant_expr(node.operand)
            if inner is not None:
                return -inner
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.UAdd):
            return self._eval_constant_expr(node.operand)
        return None

    def _visit_Break(self, node):
        if not self._loop_stack:
            raise RuntimeError("break outside loop")
        _, end_label = self._loop_stack[-1]
        self.builder.jmp(end_label)

    def _visit_Continue(self, node):
        if not self._loop_stack:
            raise RuntimeError("continue outside loop")
        start_label, _ = self._loop_stack[-1]
        self.builder.jmp(start_label)
    
    def _visit_Return(self, node):
        """Handle return statement.
        
        For module-level code (not inside a function), we treat return as:
        - Evaluate the return value expression
        - Leave it on the stack (VM will return top of stack)
        - Jump to end (halt)
        """
        if node.value is not None:
            # Evaluate return value and leave on stack
            self._visit(node.value)
        else:
            # Return None (represented as 0)
            self.builder.push_imm(0)
        
        # For module-level code, we just leave the value on stack
        # The VM will return the top of stack when it halts
        # No need to jump anywhere - execution will continue to HALT

    # ==================== Expressions ====================

    def _visit_Call(self, node):
        # Check if this is a method call (e.g., message.upper())
        if isinstance(node.func, ast.Attribute):
            return self._visit_method_call(node)
        
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        else:
            raise NotImplementedError(
                f"Call type not supported: {type(node.func).__name__}"
            )

        # Register the function in func_pool if not already registered
        if func_name not in self.func_to_idx:
            self._register_external_function(func_name)

        func_idx = self.func_to_idx[func_name]

        # Compile arguments (push onto stack left to right)
        for arg in node.args:
            self._visit(arg)

        # Emit syscall 10 calling convention:
        #   stack: [argN, ..., arg1, num_args, func_idx, 10]
        self.builder.push_imm(len(node.args))
        self.builder.push_imm(func_idx)
        self.builder.push_imm(10)
        self.builder.syscall()
    
    def _visit_method_call(self, node):
        """Handle method calls like s.upper(), s.lower(), s.strip(), etc."""
        method_name = node.func.attr
        obj = node.func.value
        
        # Supported string methods
        string_methods = {
            'upper': lambda: self._compile_string_method_upper(obj),
            'lower': lambda: self._compile_string_method_lower(obj),
            'strip': lambda: self._compile_string_method_strip(obj),
            'lstrip': lambda: self._compile_string_method_lstrip(obj),
            'rstrip': lambda: self._compile_string_method_rstrip(obj),
            'capitalize': lambda: self._compile_string_method_capitalize(obj),
            'title': lambda: self._compile_string_method_title(obj),
            'swapcase': lambda: self._compile_string_method_swapcase(obj),
            'replace': lambda: self._compile_string_method_replace(obj, node.args),
            'split': lambda: self._compile_string_method_split(obj, node.args),
            'join': lambda: self._compile_string_method_join(obj, node.args),
            'startswith': lambda: self._compile_string_method_startswith(obj, node.args),
            'endswith': lambda: self._compile_string_method_endswith(obj, node.args),
            'find': lambda: self._compile_string_method_find(obj, node.args),
            'count': lambda: self._compile_string_method_count(obj, node.args),
        }
        
        if method_name in string_methods:
            return string_methods[method_name]()
        
        # Fallback: try to call as a builtin function with object as first arg
        # This allows calling str.upper(s) style
        func_name = f"str.{method_name}"
        if func_name not in self.func_to_idx:
            # Register a lambda that calls the method
            idx = len(self.builder.func_pool)
            # Create a wrapper function
            wrapper_name = f"_method_{method_name}"
            self.builder.func_pool.append((wrapper_name, 'builtin', None))
            self.func_to_idx[func_name] = idx
        
        # Push object
        self._visit(obj)
        
        # Push arguments
        for arg in node.args:
            self._visit(arg)
        
        # Call via syscall 10
        func_idx = self.func_to_idx[func_name]
        self.builder.push_imm(len(node.args) + 1)  # +1 for self
        self.builder.push_imm(func_idx)
        self.builder.push_imm(10)
        self.builder.syscall()
    
    def _compile_string_method_upper(self, obj):
        """Compile s.upper() by calling str.upper as a function"""
        # Register str.upper as a callable
        if 'str.upper' not in self.func_to_idx:
            idx = len(self.builder.func_pool)
            self.builder.func_pool.append(('upper', 'builtin', None))
            self.func_to_idx['str.upper'] = idx
        
        # Push the string object
        self._visit(obj)
        
        # Call str.upper(s)
        func_idx = self.func_to_idx['str.upper']
        self.builder.push_imm(1)  # 1 argument
        self.builder.push_imm(func_idx)
        self.builder.push_imm(10)
        self.builder.syscall()
    
    def _compile_string_method_lower(self, obj):
        """Compile s.lower()"""
        if 'str.lower' not in self.func_to_idx:
            idx = len(self.builder.func_pool)
            self.builder.func_pool.append(('lower', 'builtin', None))
            self.func_to_idx['str.lower'] = idx
        
        self._visit(obj)
        func_idx = self.func_to_idx['str.lower']
        self.builder.push_imm(1)
        self.builder.push_imm(func_idx)
        self.builder.push_imm(10)
        self.builder.syscall()
    
    def _compile_string_method_strip(self, obj):
        """Compile s.strip()"""
        if 'str.strip' not in self.func_to_idx:
            idx = len(self.builder.func_pool)
            self.builder.func_pool.append(('strip', 'builtin', None))
            self.func_to_idx['str.strip'] = idx
        
        self._visit(obj)
        func_idx = self.func_to_idx['str.strip']
        self.builder.push_imm(1)
        self.builder.push_imm(func_idx)
        self.builder.push_imm(10)
        self.builder.syscall()
    
    def _compile_string_method_lstrip(self, obj):
        """Compile s.lstrip()"""
        if 'str.lstrip' not in self.func_to_idx:
            idx = len(self.builder.func_pool)
            self.builder.func_pool.append(('lstrip', 'builtin', None))
            self.func_to_idx['str.lstrip'] = idx
        
        self._visit(obj)
        func_idx = self.func_to_idx['str.lstrip']
        self.builder.push_imm(1)
        self.builder.push_imm(func_idx)
        self.builder.push_imm(10)
        self.builder.syscall()
    
    def _compile_string_method_rstrip(self, obj):
        """Compile s.rstrip()"""
        if 'str.rstrip' not in self.func_to_idx:
            idx = len(self.builder.func_pool)
            self.builder.func_pool.append(('rstrip', 'builtin', None))
            self.func_to_idx['str.rstrip'] = idx
        
        self._visit(obj)
        func_idx = self.func_to_idx['str.rstrip']
        self.builder.push_imm(1)
        self.builder.push_imm(func_idx)
        self.builder.push_imm(10)
        self.builder.syscall()
    
    def _compile_string_method_capitalize(self, obj):
        """Compile s.capitalize()"""
        if 'str.capitalize' not in self.func_to_idx:
            idx = len(self.builder.func_pool)
            self.builder.func_pool.append(('capitalize', 'builtin', None))
            self.func_to_idx['str.capitalize'] = idx
        
        self._visit(obj)
        func_idx = self.func_to_idx['str.capitalize']
        self.builder.push_imm(1)
        self.builder.push_imm(func_idx)
        self.builder.push_imm(10)
        self.builder.syscall()
    
    def _compile_string_method_title(self, obj):
        """Compile s.title()"""
        if 'str.title' not in self.func_to_idx:
            idx = len(self.builder.func_pool)
            self.builder.func_pool.append(('title', 'builtin', None))
            self.func_to_idx['str.title'] = idx
        
        self._visit(obj)
        func_idx = self.func_to_idx['str.title']
        self.builder.push_imm(1)
        self.builder.push_imm(func_idx)
        self.builder.push_imm(10)
        self.builder.syscall()
    
    def _compile_string_method_swapcase(self, obj):
        """Compile s.swapcase()"""
        if 'str.swapcase' not in self.func_to_idx:
            idx = len(self.builder.func_pool)
            self.builder.func_pool.append(('swapcase', 'builtin', None))
            self.func_to_idx['str.swapcase'] = idx
        
        self._visit(obj)
        func_idx = self.func_to_idx['str.swapcase']
        self.builder.push_imm(1)
        self.builder.push_imm(func_idx)
        self.builder.push_imm(10)
        self.builder.syscall()
    
    def _compile_string_method_replace(self, obj, args):
        """Compile s.replace(old, new)"""
        if len(args) < 2:
            raise ValueError("replace() requires 2 arguments")
        
        if 'str.replace' not in self.func_to_idx:
            idx = len(self.builder.func_pool)
            self.builder.func_pool.append(('replace', 'builtin', None))
            self.func_to_idx['str.replace'] = idx
        
        self._visit(obj)
        self._visit(args[0])
        self._visit(args[1])
        
        func_idx = self.func_to_idx['str.replace']
        self.builder.push_imm(3)
        self.builder.push_imm(func_idx)
        self.builder.push_imm(10)
        self.builder.syscall()
    
    def _compile_string_method_split(self, obj, args):
        """Compile s.split()"""
        if 'str.split' not in self.func_to_idx:
            idx = len(self.builder.func_pool)
            self.builder.func_pool.append(('split', 'builtin', None))
            self.func_to_idx['str.split'] = idx
        
        self._visit(obj)
        for arg in args:
            self._visit(arg)
        
        func_idx = self.func_to_idx['str.split']
        self.builder.push_imm(len(args) + 1)
        self.builder.push_imm(func_idx)
        self.builder.push_imm(10)
        self.builder.syscall()
    
    def _compile_string_method_join(self, obj, args):
        """Compile sep.join(iterable)"""
        if len(args) < 1:
            raise ValueError("join() requires 1 argument")
        
        if 'str.join' not in self.func_to_idx:
            idx = len(self.builder.func_pool)
            self.builder.func_pool.append(('join', 'builtin', None))
            self.func_to_idx['str.join'] = idx
        
        self._visit(obj)
        self._visit(args[0])
        
        func_idx = self.func_to_idx['str.join']
        self.builder.push_imm(2)
        self.builder.push_imm(func_idx)
        self.builder.push_imm(10)
        self.builder.syscall()
    
    def _compile_string_method_startswith(self, obj, args):
        """Compile s.startswith(prefix)"""
        if len(args) < 1:
            raise ValueError("startswith() requires 1 argument")
        
        if 'str.startswith' not in self.func_to_idx:
            idx = len(self.builder.func_pool)
            self.builder.func_pool.append(('startswith', 'builtin', None))
            self.func_to_idx['str.startswith'] = idx
        
        self._visit(obj)
        self._visit(args[0])
        
        func_idx = self.func_to_idx['str.startswith']
        self.builder.push_imm(2)
        self.builder.push_imm(func_idx)
        self.builder.push_imm(10)
        self.builder.syscall()
    
    def _compile_string_method_endswith(self, obj, args):
        """Compile s.endswith(suffix)"""
        if len(args) < 1:
            raise ValueError("endswith() requires 1 argument")
        
        if 'str.endswith' not in self.func_to_idx:
            idx = len(self.builder.func_pool)
            self.builder.func_pool.append(('endswith', 'builtin', None))
            self.func_to_idx['str.endswith'] = idx
        
        self._visit(obj)
        self._visit(args[0])
        
        func_idx = self.func_to_idx['str.endswith']
        self.builder.push_imm(2)
        self.builder.push_imm(func_idx)
        self.builder.push_imm(10)
        self.builder.syscall()
    
    def _compile_string_method_find(self, obj, args):
        """Compile s.find(sub)"""
        if len(args) < 1:
            raise ValueError("find() requires 1 argument")
        
        if 'str.find' not in self.func_to_idx:
            idx = len(self.builder.func_pool)
            self.builder.func_pool.append(('find', 'builtin', None))
            self.func_to_idx['str.find'] = idx
        
        self._visit(obj)
        self._visit(args[0])
        
        func_idx = self.func_to_idx['str.find']
        self.builder.push_imm(2)
        self.builder.push_imm(func_idx)
        self.builder.push_imm(10)
        self.builder.syscall()
    
    def _compile_string_method_count(self, obj, args):
        """Compile s.count(sub)"""
        if len(args) < 1:
            raise ValueError("count() requires 1 argument")
        
        if 'str.count' not in self.func_to_idx:
            idx = len(self.builder.func_pool)
            self.builder.func_pool.append(('count', 'builtin', None))
            self.func_to_idx['str.count'] = idx
        
        self._visit(obj)
        self._visit(args[0])
        
        func_idx = self.func_to_idx['str.count']
        self.builder.push_imm(2)
        self.builder.push_imm(func_idx)
        self.builder.push_imm(10)
        self.builder.syscall()

    def _visit_Subscript(self, node):
        """String indexing: s[i] or slicing: s[start:end]"""
        # Only support simple variable[index] for strings
        if not isinstance(node.value, ast.Name):
            raise NotImplementedError("Subscript only supported for variables")
        
        # Get the variable
        var_name = node.value.id
        reg = self._get_or_create_var(var_name)
        self.builder.push_reg(reg)
        
        # Check if it's a slice or index
        if isinstance(node.slice, ast.Slice):
            # Handle slice s[start:end]
            # Use 0x7FFFFFFF (max int32) to represent None
            SLICE_NONE = 0x7FFFFFFF
            
            # Push start (or SLICE_NONE for None)
            if node.slice.lower is None:
                self.builder.push_imm(SLICE_NONE)
            else:
                self._visit(node.slice.lower)
            
            # Push end (or SLICE_NONE for None)
            if node.slice.upper is None:
                self.builder.push_imm(SLICE_NONE)
            else:
                self._visit(node.slice.upper)
            
            # String slice
            self.builder.str_slice()
        else:
            # Push index (can be constant or expression)
            self._visit(node.slice)
            
            # String index access
            self.builder.str_get()

    def _visit_BinOp(self, node):
        self._visit(node.left)
        self._visit(node.right)
        
        # String concatenation: + with string variables
        if isinstance(node.op, ast.Add):
            left_str = isinstance(node.left, ast.Name) and node.left.id in self._string_vars
            right_str = isinstance(node.right, ast.Name) and node.right.id in self._string_vars
            if left_str or right_str:
                self.builder.str_concat()
                return
        
        op_map = {
            ast.Add:    self.builder.add,
            ast.Sub:    self.builder.sub,
            ast.Mult:   self.builder.mul,
            ast.Div:    self.builder.div,
            ast.FloorDiv: self.builder.div,
            ast.Mod:    self.builder.mod,
            ast.BitAnd: self.builder.and_op,
            ast.BitOr:  self.builder.or_op,
            ast.BitXor: self.builder.xor_op,
            ast.LShift: self.builder.shl,
            ast.RShift: self.builder.shr,
        }
        handler = op_map.get(type(node.op))
        if handler is None:
            raise NotImplementedError(
                f"Binary operator not supported: {type(node.op).__name__}"
            )
        handler()

    def _visit_Compare(self, node):
        """Comparison: ==, !=, <, >, <=, >=

        Pushes 0 (false) or 1 (true) onto the stack.
        """
        if len(node.ops) != 1:
            raise NotImplementedError("Chained comparisons not supported")

        self._visit(node.left)
        self._visit(node.comparators[0])
        
        # Check if we're comparing strings
        left_is_str = (isinstance(node.left, ast.Name) and node.left.id in self._string_vars) or \
                      (isinstance(node.left, ast.Constant) and isinstance(node.left.value, str))
        right_is_str = (isinstance(node.comparators[0], ast.Name) and node.comparators[0].id in self._string_vars) or \
                       (isinstance(node.comparators[0], ast.Constant) and isinstance(node.comparators[0].value, str))
        
        # Use STR_CMP for string comparisons, CMP for numeric
        if left_is_str or right_is_str:
            self.builder.str_cmp()
        else:
            self.builder.cmp()

        true_label = self._new_label('cmp_true')
        end_label = self._new_label('cmp_end')

        op = node.ops[0]
        if isinstance(op, ast.Eq):
            self.builder.jz(true_label)
        elif isinstance(op, ast.NotEq):
            self.builder.jnz(true_label)
        elif isinstance(op, ast.Lt):
            self.builder.jl(true_label)
        elif isinstance(op, ast.Gt):
            self.builder.jg(true_label)
        elif isinstance(op, ast.LtE):
            self.builder.jle(true_label)
        elif isinstance(op, ast.GtE):
            self.builder.jge(true_label)
        else:
            raise NotImplementedError(
                f"Comparison operator not supported: {type(op).__name__}"
            )

        # False branch
        self.builder.push_imm(0)
        self.builder.jmp(end_label)

        # True branch
        self.builder.add_label(true_label)
        self.builder.push_imm(1)

        self.builder.add_label(end_label)

    def _visit_BoolOp(self, node):
        """and / or with short-circuit evaluation."""
        if isinstance(node.op, ast.And):
            self._visit_and_values(node.values)
        elif isinstance(node.op, ast.Or):
            self._visit_or_values(node.values)
        else:
            raise NotImplementedError(
                f"Boolean operator not supported: {type(node.op).__name__}"
            )

    def _visit_and_values(self, values):
        """Short-circuit AND chain.

        For (a and b and c):
          eval a; push 0; cmp; jz false_label
          eval b; push 0; cmp; jz false_label
          eval c; jmp end_label
          false_label: push 0
          end_label:
        """
        if not values:
            self.builder.push_imm(0)
            return
        if len(values) == 1:
            self._visit(values[0])
            return

        false_label = self._new_label('bool_and_false')
        end_label = self._new_label('bool_and_end')

        for val in values[:-1]:
            self._visit(val)
            self.builder.push_imm(0)
            self.builder.cmp()
            self.builder.jz(false_label)

        # Last value — if we get here, all previous were truthy
        self._visit(values[-1])
        self.builder.jmp(end_label)

        self.builder.add_label(false_label)
        self.builder.push_imm(0)
        self.builder.add_label(end_label)

    def _visit_or_values(self, values):
        """Short-circuit OR chain.

        For (a or b or c):
          eval a; dup; push 0; cmp; jnz end_label
          discard; eval b; dup; push 0; cmp; jnz end_label
          discard; eval c
          end_label:
        """
        if not values:
            self.builder.push_imm(0)
            return
        if len(values) == 1:
            self._visit(values[0])
            return

        end_label = self._new_label('bool_or_end')

        for val in values[:-1]:
            self._visit(val)
            self.builder.dup()
            self.builder.push_imm(0)
            self.builder.cmp()
            self.builder.jnz(end_label)
            self._discard()

        # Last value — always evaluated if all previous were falsy
        self._visit(values[-1])

        self.builder.add_label(end_label)

    def _visit_UnaryOp(self, node):
        if isinstance(node.op, ast.USub):
            self._visit(node.operand)
            self.builder.push_imm(0)
            self.builder.swap()
            self.builder.sub()
        elif isinstance(node.op, ast.UAdd):
            self._visit(node.operand)
        elif isinstance(node.op, ast.Not):
            # not x  →  (x == 0) ? 1 : 0
            self._visit(node.operand)
            self.builder.push_imm(0)
            self.builder.cmp()
            true_label = self._new_label('not_true')
            end_label = self._new_label('not_end')
            self.builder.jz(true_label)      # if x == 0, push 1
            self.builder.push_imm(0)
            self.builder.jmp(end_label)
            self.builder.add_label(true_label)
            self.builder.push_imm(1)
            self.builder.add_label(end_label)
        elif isinstance(node.op, ast.Invert):
            # ~x  →  bitwise NOT
            self._visit(node.operand)
            self.builder.not_op()
        else:
            raise NotImplementedError(
                f"Unary operator not supported: {type(node.op).__name__}"
            )

    def _visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            reg = self._get_var(node.id)
            self.builder.push_reg(reg)

    def _visit_Constant(self, node):
        if isinstance(node.value, (int, bool)):
            self.builder.push_imm(int(node.value))
        elif isinstance(node.value, str):
            idx = self.builder.add_string(node.value)
            self.builder.str_load(idx)
        elif node.value is None:
            self.builder.push_imm(0)
        else:
            raise NotImplementedError(
                f"Constant type not supported: {type(node.value).__name__}"
            )

    # ---- Variable / Function Helpers ----

    def _register_user_function(self, func_node):
        name = func_node.name
        if name in self.func_to_idx:
            return
        source = ast.unparse(func_node)
        idx = len(self.builder.func_pool)
        self.builder.func_pool.append((name, 'user', source))
        self.func_to_idx[name] = idx

    def _register_external_function(self, name):
        if name in self.func_to_idx:
            return
        if name in self.user_funcs:
            return
        func = getattr(builtins, name, None)
        if func is None or not callable(func):
            raise NameError(f"Function '{name}' is not defined and is not a builtin")
        idx = len(self.builder.func_pool)
        self.builder.func_pool.append((name, 'builtin', None))
        self.func_to_idx[name] = idx

    def _get_var(self, name):
        if name in self.variables:
            return self.variables[name]
        raise NameError(f"Undefined variable: '{name}'")

    def _get_or_create_var(self, name):
        if name not in self.variables:
            if self.next_reg >= self._MAX_REGS:
                raise RuntimeError(
                    f"Too many variables (max {self._MAX_REGS} registers)"
                )
            self.variables[name] = self.next_reg
            self.next_reg += 1
        return self.variables[name]
