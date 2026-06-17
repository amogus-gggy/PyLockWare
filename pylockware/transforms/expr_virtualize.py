
import ast
import base64
import random
import marshal
import hashlib
import time
import builtins as _builtins_mod


def generate_opcodes_from_seed(seed_bytes):
    h = hashlib.sha256(seed_bytes).digest()
    opcodes = {}
    used = set([0])
    opcode_names = [
        'CONST', 'GET_VAR', 'SET_VAR', 'GETATTR', 'SETATTR', 'GETITEM', 'SETITEM',
        'DELITEM', 'SLICE', 'CALL', 'ADD', 'SUB', 'MUL', 'TRUEDIV', 'FLOORDIV',
        'MOD', 'POW', 'LSHIFT', 'RSHIFT', 'BITOR', 'BITXOR', 'BITAND', 'MATMUL',
        'UADD', 'USUB', 'INVERT', 'NOT', 'AND', 'OR', 'EQ', 'NE', 'LT', 'LE',
        'GT', 'GE', 'IS', 'IS_NOT', 'CONTAINS', 'NOT_CONTAINS', 'COMPARE',
        'IFEXP', 'LIST', 'TUPLE', 'SET', 'DICT', 'LISTCOMP', 'SETCOMP',
        'DICTCOMP', 'GENEXP', 'FSTRING', 'STARRED', 'NAMEDEXPR', 'LAMBDA',
        'AWAIT', 'YIELD', 'YIELDFROM', 'BUILD_SLICE', 'POP', 'DUP', 'SWAP',
        'JUMP_IF_FALSE', 'JUMP', 'JUMP_IF_TRUE', 'LOAD_FAST', 'STORE_FAST',
    ]
    idx = 0
    for name in opcode_names:
        while True:
            val = h[idx % len(h)]
            if val not in used and val != 0:
                opcodes[name] = val
                used.add(val)
                break
            idx += 1
            if idx > 1000:
                for i in range(1, 256):
                    if i not in used:
                        opcodes[name] = i
                        used.add(i)
                        break
                break
        idx += 1
    opcodes['END'] = 0
    return opcodes


class VMExpressionCompiler(ast.NodeVisitor):
    def __init__(self, opcodes):
        self.bytecode = bytearray()
        self.const_pool = []
        self.var_names = []
        self.attr_names = []
        self.opcodes = opcodes
        self.opcode_names = {v: k for k, v in opcodes.items()}

    def _emit(self, opcode_name, *args):
        self.bytecode.append(self.opcodes[opcode_name])
        for arg in args:
            if isinstance(arg, int):
                self.bytecode.extend(arg.to_bytes(2, 'little'))
            elif isinstance(arg, str):
                data = arg.encode('utf-8')
                self.bytecode.extend(len(data).to_bytes(2, 'little'))
                self.bytecode.extend(data)

    def _add_const(self, value):
        try:
            return self.const_pool.index(value)
        except ValueError:
            idx = len(self.const_pool)
            self.const_pool.append(value)
            return idx

    def _add_var(self, name):
        try:
            return self.var_names.index(name)
        except ValueError:
            idx = len(self.var_names)
            self.var_names.append(name)
            return idx

    def _add_attr(self, name):
        try:
            return self.attr_names.index(name)
        except ValueError:
            idx = len(self.attr_names)
            self.attr_names.append(name)
            return idx

    def compile(self, node):
        self.visit(node)
        self._emit('END')
        return bytes(self.bytecode), self.const_pool, self.var_names, self.attr_names

    def visit_Constant(self, node):
        idx = self._add_const(node.value)
        self._emit('CONST', idx)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            idx = self._add_var(node.id)
            self._emit('GET_VAR', idx)
        else:
            raise ValueError("Store/Delete in expression")

    def visit_BinOp(self, node):
        op_map = {
            ast.Add: 'ADD', ast.Sub: 'SUB', ast.Mult: 'MUL',
            ast.Div: 'TRUEDIV', ast.FloorDiv: 'FLOORDIV', ast.Mod: 'MOD',
            ast.Pow: 'POW', ast.LShift: 'LSHIFT', ast.RShift: 'RSHIFT',
            ast.BitOr: 'BITOR', ast.BitXor: 'BITXOR', ast.BitAnd: 'BITAND',
            ast.MatMult: 'MATMUL',
        }
        self.visit(node.left)
        self.visit(node.right)
        self._emit(op_map[type(node.op)])

    def visit_UnaryOp(self, node):
        op_map = {
            ast.UAdd: 'UADD', ast.USub: 'USUB',
            ast.Invert: 'INVERT', ast.Not: 'NOT',
        }
        self.visit(node.operand)
        self._emit(op_map[type(node.op)])

    def visit_BoolOp(self, node):
        op_map = {ast.And: 'AND', ast.Or: 'OR'}
        for value in node.values:
            self.visit(value)
        self._emit(op_map[type(node.op)], len(node.values))

    def visit_Compare(self, node):
        self.visit(node.left)
        for comparator in node.comparators:
            self.visit(comparator)
        op_map = {
            ast.Eq: 'EQ', ast.NotEq: 'NE', ast.Lt: 'LT', ast.LtE: 'LE',
            ast.Gt: 'GT', ast.GtE: 'GE', ast.Is: 'IS', ast.IsNot: 'IS_NOT',
            ast.In: 'CONTAINS', ast.NotIn: 'NOT_CONTAINS',
        }
        ops = [self.opcodes[op_map[type(op)]] for op in node.ops]
        ops_idx = self._add_const(tuple(ops))
        self._emit('COMPARE', ops_idx, len(node.ops))

    def visit_Subscript(self, node):
        self.visit(node.value)
        self.visit(node.slice)
        if isinstance(node.ctx, ast.Load):
            self._emit('GETITEM')
        elif isinstance(node.ctx, ast.Store):
            self._emit('SETITEM')
        else:
            self._emit('DELITEM')

    def visit_Slice(self, node):
        if node.lower:
            self.visit(node.lower)
        else:
            self._emit('CONST', self._add_const(None))
        if node.upper:
            self.visit(node.upper)
        else:
            self._emit('CONST', self._add_const(None))
        if node.step:
            self.visit(node.step)
        else:
            self._emit('CONST', self._add_const(None))
        self._emit('BUILD_SLICE')

    def visit_Attribute(self, node):
        self.visit(node.value)
        idx = self._add_attr(node.attr)
        if isinstance(node.ctx, ast.Load):
            self._emit('GETATTR', idx)
        elif isinstance(node.ctx, ast.Store):
            self._emit('SETATTR', idx)
        else:
            self._emit('DELATTR', idx)

    def visit_Call(self, node):
        self.visit(node.func)
        for arg in node.args:
            self.visit(arg)
        for kw in reversed(node.keywords):
            self.visit(kw.value)
        self._emit('CALL', len(node.args), len(node.keywords))
        for kw in node.keywords:
            data = (kw.arg or '').encode('utf-8')
            self.bytecode.extend(len(data).to_bytes(2, 'little'))
            self.bytecode.extend(data)

    def visit_IfExp(self, node):
        self.visit(node.test)
        self.visit(node.body)
        self.visit(node.orelse)
        self._emit('IFEXP')

    def visit_List(self, node):
        for e in node.elts:
            self.visit(e)
        self._emit('LIST', len(node.elts))

    def visit_Tuple(self, node):
        for e in node.elts:
            self.visit(e)
        self._emit('TUPLE', len(node.elts))

    def visit_Set(self, node):
        for e in node.elts:
            self.visit(e)
        self._emit('SET', len(node.elts))

    def visit_Dict(self, node):
        for k, v in zip(node.keys, node.values):
            if k:
                self.visit(k)
            else:
                self._emit('CONST', self._add_const(None))
            self.visit(v)
        self._emit('DICT', len(node.keys))

    def visit_ListComp(self, node):
        self._emit('LISTCOMP')

    def visit_SetComp(self, node):
        self._emit('SETCOMP')

    def visit_GeneratorExp(self, node):
        self._emit('GENEXP')

    def visit_DictComp(self, node):
        self._emit('DICTCOMP')

    def visit_JoinedStr(self, node):
        self._emit('FSTRING')

    def visit_Starred(self, node):
        self.visit(node.value)
        self._emit('STARRED')

    def visit_NamedExpr(self, node):
        self.visit(node.value)
        idx = self._add_var(node.target.id)
        self._emit('NAMEDEXPR', idx)

    def visit_Lambda(self, node):
        self._emit('LAMBDA')

    def visit_Await(self, node):
        self.visit(node.value)
        self._emit('AWAIT')

    def visit_Yield(self, node):
        if node.value:
            self.visit(node.value)
        self._emit('YIELD')

    def visit_YieldFrom(self, node):
        self.visit(node.value)
        self._emit('YIELDFROM')


def compile_expr_to_b64(source_expr):
    tree = ast.parse(source_expr, mode='eval')
    seed = bytes(random.randint(0, 255) for _ in range(32))
    opcodes = generate_opcodes_from_seed(seed)
    compiler = VMExpressionCompiler(opcodes)
    bytecode, const_pool, var_names, attr_names = compiler.compile(tree.body)
    package = {
        'bytecode': bytecode,
        'const_pool': const_pool,
        'var_names': var_names,
        'attr_names': attr_names,
    }
    data = seed + marshal.dumps(package)
    return base64.b64encode(data).decode('ascii'), var_names


class VMVirtualizer(ast.NodeTransformer):
    def __init__(self):
        self._target_depth = 0

    _UNSUPPORTED = (ast.Lambda, ast.ListComp, ast.SetComp, ast.GeneratorExp,
                    ast.DictComp, ast.JoinedStr, ast.Await, ast.Yield, ast.YieldFrom)

    _CALLOBF_NAMES = frozenset({
        '_call', '_method_call', '_get_attr', '_set_attr',
        '_get_item', '_set_item', '_resolve', '_decode',
        '_resolve2', '_resolve3', '_call2', '_get_attr2', '_method_call2',
    })

    def visit_FunctionDef(self, node):
        if node.name in self._CALLOBF_NAMES:
            return node
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node):
        if node.name in self._CALLOBF_NAMES:
            return node
        self.generic_visit(node)
        return node

    def _has_callobf_name(self, node):
        for child in ast.walk(node):
            if isinstance(child, ast.Name) and child.id in self._CALLOBF_NAMES:
                return True
        return False

    def _try_compile(self, node):
        if self._target_depth > 0:
            return None
        if self._has_super_call(node):
            return None
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg is None:
                    return None
        for child in ast.walk(node):
            if isinstance(child, self._UNSUPPORTED):
                return None
            if isinstance(child, ast.Name) and child.id in self._CALLOBF_NAMES:
                return None
        try:
            source = ast.unparse(node)
            b64_str, var_names = compile_expr_to_b64(source)
            return b64_str, list(var_names)
        except Exception:
            return None

    def _make_vmentry_call(self, b64_str, ns_vars=None):
        args = [ast.Constant(value=b64_str)]
        if ns_vars:
            dict_keys = [ast.Constant(value=name) for name in ns_vars]
            dict_values = [ast.Name(id=name, ctx=ast.Load()) for name in ns_vars]
            args.append(ast.Dict(keys=dict_keys, values=dict_values))
        return ast.Call(
            func=ast.Name(id='_vmentry', ctx=ast.Load()),
            args=args,
            keywords=[]
        )

    def visit_For(self, node):
        node.target = self._visit_target(node.target)
        node.iter = self.visit(node.iter)
        node.body = [self.visit(n) for n in node.body]
        node.orelse = [self.visit(n) for n in node.orelse]
        return node

    def visit_With(self, node):
        for item in node.items:
            if item.optional_vars:
                item.optional_vars = self._visit_target(item.optional_vars)
            item.context_expr = self.visit(item.context_expr)
        node.body = [self.visit(n) for n in node.body]
        return node

    def visit_Assign(self, node):
        node.targets = [self._visit_target(t) for t in node.targets]
        node.value = self.visit(node.value)
        return node

    def visit_AugAssign(self, node):
        node.target = self._visit_target(node.target)
        node.value = self.visit(node.value)
        return node

    def visit_AnnAssign(self, node):
        node.target = self._visit_target(node.target)
        if node.value:
            node.value = self.visit(node.value)
        return node

    def visit_Delete(self, node):
        node.targets = [self._visit_target(t) for t in node.targets]
        return node

    def visit_NamedExpr(self, node):
        node.target = self._visit_target(node.target)
        node.value = self.visit(node.value)
        return node

    def _visit_target(self, node):
        self._target_depth += 1
        result = self.visit(node)
        self._target_depth -= 1
        return result

    def visit_BinOp(self, node):
        if self._has_callobf_name(node):
            return node
        info = self._try_compile(node)
        self.generic_visit(node)
        if info:
            return self._make_vmentry_call(*info)
        return node

    def visit_UnaryOp(self, node):
        if self._has_callobf_name(node):
            return node
        info = self._try_compile(node)
        self.generic_visit(node)
        if info:
            return self._make_vmentry_call(*info)
        return node

    def visit_BoolOp(self, node):
        if self._has_callobf_name(node):
            return node
        info = self._try_compile(node)
        self.generic_visit(node)
        if info:
            return self._make_vmentry_call(*info)
        return node

    def visit_Compare(self, node):
        if self._has_callobf_name(node):
            return node
        info = self._try_compile(node)
        self.generic_visit(node)
        if info:
            return self._make_vmentry_call(*info)
        return node

    def visit_Call(self, node):
        if self._has_callobf_name(node):
            return node
        info = self._try_compile(node)
        self.generic_visit(node)
        if info:
            return self._make_vmentry_call(*info)
        return node

    def visit_Attribute(self, node):
        if self._has_callobf_name(node):
            return node
        self.generic_visit(node)
        if isinstance(node.ctx, ast.Load):
            info = self._try_compile(node)
            if info:
                return self._make_vmentry_call(*info)
        return node

    def visit_Subscript(self, node):
        if self._has_callobf_name(node):
            return node
        self.generic_visit(node)
        if isinstance(node.ctx, ast.Load):
            info = self._try_compile(node)
            if info:
                return self._make_vmentry_call(*info)
        return node

    def visit_IfExp(self, node):
        if self._has_callobf_name(node):
            return node
        info = self._try_compile(node)
        self.generic_visit(node)
        if info:
            return self._make_vmentry_call(*info)
        return node

    def visit_List(self, node):
        if self._has_callobf_name(node):
            return node
        info = self._try_compile(node)
        self.generic_visit(node)
        if info:
            return self._make_vmentry_call(*info)
        return node

    def visit_Tuple(self, node):
        if self._has_callobf_name(node):
            return node
        info = self._try_compile(node)
        self.generic_visit(node)
        if info:
            return self._make_vmentry_call(*info)
        return node

    def visit_Set(self, node):
        if self._has_callobf_name(node):
            return node
        info = self._try_compile(node)
        self.generic_visit(node)
        if info:
            return self._make_vmentry_call(*info)
        return node

    def visit_Dict(self, node):
        if self._has_callobf_name(node):
            return node
        info = self._try_compile(node)
        self.generic_visit(node)
        if info:
            return self._make_vmentry_call(*info)
        return node

    def visit_ListComp(self, node):
        return node

    def visit_SetComp(self, node):
        return node

    def visit_GeneratorExp(self, node):
        return node

    def visit_DictComp(self, node):
        return node

    def visit_JoinedStr(self, node):
        return node

    def visit_Lambda(self, node):
        return node

    def visit_Await(self, node):
        return node

    def visit_Yield(self, node):
        return node

    def visit_YieldFrom(self, node):
        return node

    def _has_super_call(self, node):
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func = child.func
                if isinstance(func, ast.Name) and func.id == 'super' and not child.args:
                    return True
                if isinstance(func, ast.Attribute) and func.attr == 'super':
                    return True
        return False


def virtualize_code(source):
    tree = ast.parse(source)
    transformer = VMVirtualizer()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    return ast.unparse(new_tree)


VM_RUNTIME_CODE = """import base64, marshal, hashlib

def _vmentry(b64_str, ns=None):
    data = base64.b64decode(b64_str)
    seed = data[:32]
    package = marshal.loads(data[32:])

    bytecode = package['bytecode']
    const_pool = package['const_pool']
    var_names = package['var_names']
    attr_names = package['attr_names']

    h = hashlib.sha256(seed).digest()
    opcodes = {}
    used = set([0])
    opcode_names = [
        'CONST', 'GET_VAR', 'SET_VAR', 'GETATTR', 'SETATTR', 'GETITEM', 'SETITEM',
        'DELITEM', 'SLICE', 'CALL', 'ADD', 'SUB', 'MUL', 'TRUEDIV', 'FLOORDIV',
        'MOD', 'POW', 'LSHIFT', 'RSHIFT', 'BITOR', 'BITXOR', 'BITAND', 'MATMUL',
        'UADD', 'USUB', 'INVERT', 'NOT', 'AND', 'OR', 'EQ', 'NE', 'LT', 'LE',
        'GT', 'GE', 'IS', 'IS_NOT', 'CONTAINS', 'NOT_CONTAINS', 'COMPARE',
        'IFEXP', 'LIST', 'TUPLE', 'SET', 'DICT', 'LISTCOMP', 'SETCOMP',
        'DICTCOMP', 'GENEXP', 'FSTRING', 'STARRED', 'NAMEDEXPR', 'LAMBDA',
        'AWAIT', 'YIELD', 'YIELDFROM', 'BUILD_SLICE', 'POP', 'DUP', 'SWAP',
        'JUMP_IF_FALSE', 'JUMP', 'JUMP_IF_TRUE', 'LOAD_FAST', 'STORE_FAST',
    ]
    idx = 0
    for name in opcode_names:
        while True:
            val = h[idx % len(h)]
            if val not in used and val != 0:
                opcodes[name] = val
                used.add(val)
                break
            idx += 1
            if idx > 1000:
                for i in range(1, 256):
                    if i not in used:
                        opcodes[name] = i
                        used.add(i)
                        break
                break
        idx += 1
    opcodes['END'] = 0

    stack = []
    pc = 0

    def get_op(name):
        return opcodes.get(name, -1)

    while pc < len(bytecode):
        op = bytecode[pc]
        pc += 1

        if op == 0:
            return stack.pop() if stack else None

        elif op == get_op('CONST'):
            idx = int.from_bytes(bytecode[pc:pc+2], 'little')
            pc += 2
            stack.append(const_pool[idx])

        elif op == get_op('GET_VAR'):
            idx = int.from_bytes(bytecode[pc:pc+2], 'little')
            pc += 2
            name = var_names[idx]
            if ns is not None and name in ns:
                stack.append(ns[name])
            elif name in globals():
                stack.append(globals()[name])
            else:
                b = __builtins__ if isinstance(__builtins__, dict) else vars(__builtins__)
                val = b.get(name) if isinstance(b, dict) else getattr(b, name, None)
                stack.append(val)

        elif op == get_op('GETATTR'):
            idx = int.from_bytes(bytecode[pc:pc+2], 'little')
            pc += 2
            obj = stack.pop()
            name = attr_names[idx]
            stack.append(getattr(obj, name))

        elif op == get_op('GETITEM'):
            key = stack.pop()
            obj = stack.pop()
            stack.append(obj[key])

        elif op == get_op('BUILD_SLICE'):
            step = stack.pop()
            stop = stack.pop()
            start = stack.pop()
            stack.append(slice(start, stop, step))

        elif op == get_op('CALL'):
            argc = int.from_bytes(bytecode[pc:pc+2], 'little')
            pc += 2
            kwargc = int.from_bytes(bytecode[pc:pc+2], 'little')
            pc += 2
            kwargs = {}
            for _ in range(kwargc):
                kn_len = int.from_bytes(bytecode[pc:pc+2], 'little')
                pc += 2
                kn = bytecode[pc:pc+kn_len].decode('utf-8')
                pc += kn_len
                kwargs[kn] = stack.pop()
            args = [stack.pop() for _ in range(argc)]
            args.reverse()
            func = stack.pop()
            stack.append(func(*args, **kwargs))

        elif op == get_op('ADD'):
            b = stack.pop(); a = stack.pop(); stack.append(a + b)
        elif op == get_op('SUB'):
            b = stack.pop(); a = stack.pop(); stack.append(a - b)
        elif op == get_op('MUL'):
            b = stack.pop(); a = stack.pop(); stack.append(a * b)
        elif op == get_op('TRUEDIV'):
            b = stack.pop(); a = stack.pop(); stack.append(a / b)
        elif op == get_op('FLOORDIV'):
            b = stack.pop(); a = stack.pop(); stack.append(a // b)
        elif op == get_op('MOD'):
            b = stack.pop(); a = stack.pop(); stack.append(a % b)
        elif op == get_op('POW'):
            b = stack.pop(); a = stack.pop(); stack.append(a ** b)
        elif op == get_op('LSHIFT'):
            b = stack.pop(); a = stack.pop(); stack.append(a << b)
        elif op == get_op('RSHIFT'):
            b = stack.pop(); a = stack.pop(); stack.append(a >> b)
        elif op == get_op('BITOR'):
            b = stack.pop(); a = stack.pop(); stack.append(a | b)
        elif op == get_op('BITXOR'):
            b = stack.pop(); a = stack.pop(); stack.append(a ^ b)
        elif op == get_op('BITAND'):
            b = stack.pop(); a = stack.pop(); stack.append(a & b)
        elif op == get_op('MATMUL'):
            b = stack.pop(); a = stack.pop(); stack.append(a @ b)
        elif op == get_op('UADD'):
            a = stack.pop(); stack.append(+a)
        elif op == get_op('USUB'):
            a = stack.pop(); stack.append(-a)
        elif op == get_op('INVERT'):
            a = stack.pop(); stack.append(~a)
        elif op == get_op('NOT'):
            a = stack.pop(); stack.append(not a)

        elif op == get_op('AND'):
            count = int.from_bytes(bytecode[pc:pc+2], 'little')
            pc += 2
            values = [stack.pop() for _ in range(count)]
            values.reverse()
            result = True
            for v in values:
                result = result and v
                if not result: break
            stack.append(result)

        elif op == get_op('OR'):
            count = int.from_bytes(bytecode[pc:pc+2], 'little')
            pc += 2
            values = [stack.pop() for _ in range(count)]
            values.reverse()
            result = False
            for v in values:
                result = result or v
                if result: break
            stack.append(result)

        elif op == get_op('COMPARE'):
            ops_idx = int.from_bytes(bytecode[pc:pc+2], 'little')
            pc += 2
            count = int.from_bytes(bytecode[pc:pc+2], 'little')
            pc += 2
            ops = const_pool[ops_idx]
            comparators = [stack.pop() for _ in range(count)]
            comparators.reverse()
            left = stack.pop()
            rev = {v: k for k, v in opcodes.items()}
            result = True
            current = left
            for op_code, right in zip(ops, comparators):
                op_name = rev.get(op_code, '')
                if 'EQ' in op_name and 'NE' not in op_name: ok = current == right
                elif 'NE' in op_name: ok = current != right
                elif 'LT' in op_name and 'LE' not in op_name: ok = current < right
                elif 'LE' in op_name: ok = current <= right
                elif 'GT' in op_name and 'GE' not in op_name: ok = current > right
                elif 'GE' in op_name: ok = current >= right
                elif 'IS_NOT' in op_name: ok = current is not right
                elif 'IS' in op_name and 'NOT' not in op_name: ok = current is right
                elif 'NOT_CONTAINS' in op_name: ok = current not in right
                elif 'CONTAINS' in op_name and 'NOT' not in op_name: ok = current in right
                else: ok = False
                if not ok:
                    result = False
                    break
                current = right
            stack.append(result)

        elif op == get_op('IFEXP'):
            orelse = stack.pop()
            body = stack.pop()
            test = stack.pop()
            stack.append(body if test else orelse)

        elif op == get_op('LIST'):
            count = int.from_bytes(bytecode[pc:pc+2], 'little')
            pc += 2
            items = [stack.pop() for _ in range(count)]
            items.reverse()
            stack.append(items)

        elif op == get_op('TUPLE'):
            count = int.from_bytes(bytecode[pc:pc+2], 'little')
            pc += 2
            items = [stack.pop() for _ in range(count)]
            items.reverse()
            stack.append(tuple(items))

        elif op == get_op('SET'):
            count = int.from_bytes(bytecode[pc:pc+2], 'little')
            pc += 2
            items = [stack.pop() for _ in range(count)]
            items.reverse()
            stack.append(set(items))

        elif op == get_op('DICT'):
            count = int.from_bytes(bytecode[pc:pc+2], 'little')
            pc += 2
            items = {}
            for _ in range(count):
                v = stack.pop()
                k = stack.pop()
                items[k] = v
            stack.append(items)

        elif op == get_op('STARRED'):
            pass

        elif op == get_op('NAMEDEXPR'):
            idx = int.from_bytes(bytecode[pc:pc+2], 'little')
            pc += 2
            value = stack[-1]
            name = var_names[idx]
            locals()[name] = value

        else:
            pass

    return stack.pop() if stack else None
"""


def build_virtualized_module(source_code):
    virtualized = virtualize_code(source_code)
    return VM_RUNTIME_CODE + "\n" + virtualized


def compare_execution(source_code, iterations=1000):
    print("=" * 60)
    print("COMPARISON: ORIGINAL vs VIRTUALIZED")
    print("=" * 60)

    print("\n--- ORIGINAL CODE ---")
    print(source_code)

    virtualized = virtualize_code(source_code)
    full_code = VM_RUNTIME_CODE + "\n" + virtualized

    print("\n--- VIRTUALIZED CODE ---")
    print(virtualized)

    print("\n--- RESULTS ---")
    orig_ns = {}
    exec(source_code, orig_ns)

    virt_ns = {}
    exec(full_code, virt_ns)

    keys = [k for k in orig_ns if not k.startswith('__')]
    all_ok = True
    for k in keys:
        o = orig_ns.get(k)
        v = virt_ns.get(k)
        match = o == v or (type(o) == type(v) and type(o) in (list, tuple, set, dict) and list(o) == list(v))
        if not match:
            all_ok = False
        status = "OK" if match else "FAIL"
        print(f"  {k}: orig={o}, virt={v}, {status}")

    print(f"\n{'ALL MATCH' if all_ok else 'SOME MISMATCHES'}")

    print("\n--- PERFORMANCE ---")
    t1 = time.perf_counter()
    for _ in range(iterations):
        ns = {}
        exec(source_code, ns)
    t2 = time.perf_counter()
    orig_time = t2 - t1

    t1 = time.perf_counter()
    for _ in range(iterations):
        ns = {}
        exec(full_code, ns)
    t2 = time.perf_counter()
    virt_time = t2 - t1

    print(f"  Original:    {orig_time:.4f}s ({iterations} runs)")
    print(f"  Virtualized: {virt_time:.4f}s ({iterations} runs)")
    print(f"  Overhead:    {virt_time/orig_time:.1f}x")

    return all_ok


if __name__ == "__main__":
    demo_code = """
a = 10
b = 20
c = a + b * 2
d = [1, 2, 3, 4, 5]
e = d[0] + d[1:3][0]
f = c > 30 and b < 50
g = (a, b, c)
h = {1: 'one', 2: 'two'}
result = (a + b) * 2 > 50 and d[0] + d[1] == 3
"""
    compare_execution(demo_code, iterations=100)