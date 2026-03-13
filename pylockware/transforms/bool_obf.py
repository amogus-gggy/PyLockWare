"""
Boolean Expression Obfuscation Module for PyLockWare
Obfuscates True/False/bool operations with complex equivalent expressions
"""
import ast
import random
from pylockware.core.name_generator import generate_random_name


class BooleanObfuscator(ast.NodeTransformer):
    """
    AST transformer that obfuscates boolean expressions:
    - True/False literals → complex equivalent expressions
    - bool() calls → obfuscated versions
    - Logical operators (and, or, not) → equivalent complex forms
    - Comparison results → wrapped in obfuscated expressions
    """

    def __init__(self, name_gen_settings='english'):
        self.name_gen_settings = name_gen_settings
        self.obf_count = 0
        self.helper_func_name = generate_random_name("_", name_gen_settings)
        self.call_depth = 0  # Track call nesting depth

    def _generate_true_expr(self):
        """Generate expression that always evaluates to True."""
        exprs = [
            # Mathematical identities
            ast.Compare(
                left=ast.Constant(1),
                ops=[ast.Eq()],
                comparators=[ast.Constant(1)]
            ),
            # x == x
            ast.Compare(
                left=ast.Name(id='len', ctx=ast.Load()),
                ops=[ast.Is()],
                comparators=[ast.Name(id='len', ctx=ast.Load())]
            ),
            # x - x == 0
            ast.Compare(
                left=ast.BinOp(
                    left=ast.Constant(42),
                    op=ast.Sub(),
                    right=ast.Constant(42)
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(0)]
            ),
            # x | 0 == x
            ast.Compare(
                left=ast.BinOp(
                    left=ast.Constant(1337),
                    op=ast.BitOr(),
                    right=ast.Constant(0)
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(1337)]
            ),
            # len("") == 0
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='len', ctx=ast.Load()),
                    args=[ast.Constant("")],
                    keywords=[]
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(0)]
            ),
            # bool(1) is True
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='bool', ctx=ast.Load()),
                    args=[ast.Constant(1)],
                    keywords=[]
                ),
                ops=[ast.Is()],
                comparators=[ast.Constant(True)]
            ),
            # pow(x, 0) == 1
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='pow', ctx=ast.Load()),
                    args=[ast.Constant(7), ast.Constant(0)],
                    keywords=[]
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(1)]
            ),
            # (x ^ y) ^ y == x
            ast.Compare(
                left=ast.BinOp(
                    left=ast.BinOp(
                        left=ast.Constant(0x12345678),
                        op=ast.BitXor(),
                        right=ast.Constant(0xABCDEF00)
                    ),
                    op=ast.BitXor(),
                    right=ast.Constant(0xABCDEF00)
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(0x12345678)]
            ),
            # chr(ord('A')) == 'A'
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='chr', ctx=ast.Load()),
                    args=[ast.Call(
                        func=ast.Name(id='ord', ctx=ast.Load()),
                        args=[ast.Constant("A")],
                        keywords=[]
                    )],
                    keywords=[]
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant("A")]
            ),
            # sum([1,2,3]) == 6
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='sum', ctx=ast.Load()),
                    args=[ast.List(
                        elts=[ast.Constant(1), ast.Constant(2), ast.Constant(3)],
                        ctx=ast.Load()
                    )],
                    keywords=[]
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(6)]
            ),
            # all([True, True, True]) == True
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='all', ctx=ast.Load()),
                    args=[ast.List(
                        elts=[ast.Constant(True), ast.Constant(True), ast.Constant(True)],
                        ctx=ast.Load()
                    )],
                    keywords=[]
                ),
                ops=[ast.Is()],
                comparators=[ast.Constant(True)]
            ),
            # not False
            ast.UnaryOp(
                op=ast.Not(),
                operand=ast.Constant(False)
            ),
        ]
        return random.choice(exprs)

    def _generate_false_expr(self):
        """Generate expression that always evaluates to False."""
        exprs = [
            # x != x
            ast.Compare(
                left=ast.Name(id='len', ctx=ast.Load()),
                ops=[ast.IsNot()],
                comparators=[ast.Name(id='len', ctx=ast.Load())]
            ),
            # 1 == 0
            ast.Compare(
                left=ast.Constant(1),
                ops=[ast.Eq()],
                comparators=[ast.Constant(0)]
            ),
            # x - x != 0
            ast.Compare(
                left=ast.BinOp(
                    left=ast.Constant(42),
                    op=ast.Sub(),
                    right=ast.Constant(42)
                ),
                ops=[ast.NotEq()],
                comparators=[ast.Constant(0)]
            ),
            # len("") != 0
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='len', ctx=ast.Load()),
                    args=[ast.Constant("")],
                    keywords=[]
                ),
                ops=[ast.NotEq()],
                comparators=[ast.Constant(0)]
            ),
            # bool(0) is True (false statement)
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='bool', ctx=ast.Load()),
                    args=[ast.Constant(0)],
                    keywords=[]
                ),
                ops=[ast.Is()],
                comparators=[ast.Constant(True)]
            ),
            # pow(x, 1) != x
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='pow', ctx=ast.Load()),
                    args=[ast.Constant(42), ast.Constant(1)],
                    keywords=[]
                ),
                ops=[ast.NotEq()],
                comparators=[ast.Constant(42)]
            ),
            # "abc" in "def"
            ast.Compare(
                left=ast.Constant("abc"),
                ops=[ast.In()],
                comparators=[ast.Constant("def")]
            ),
            # sum([1,2,3]) != 6
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='sum', ctx=ast.Load()),
                    args=[ast.List(
                        elts=[ast.Constant(1), ast.Constant(2), ast.Constant(3)],
                        ctx=ast.Load()
                    )],
                    keywords=[]
                ),
                ops=[ast.NotEq()],
                comparators=[ast.Constant(6)]
            ),
            # all([True, False, True]) == True
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='all', ctx=ast.Load()),
                    args=[ast.List(
                        elts=[ast.Constant(True), ast.Constant(False), ast.Constant(True)],
                        ctx=ast.Load()
                    )],
                    keywords=[]
                ),
                ops=[ast.Is()],
                comparators=[ast.Constant(True)]
            ),
            # not True
            ast.UnaryOp(
                op=ast.Not(),
                operand=ast.Constant(True)
            ),
        ]
        return random.choice(exprs)

    def visit_Constant(self, node):
        """Obfuscate True/False literals, but not inside call arguments."""
        # Don't obfuscate constants inside function call arguments
        # This prevents breaking encoded string decoder calls
        if self.call_depth > 0:
            return node
            
        if node.value is True:
            self.obf_count += 1
            return self._generate_true_expr()
        elif node.value is False:
            self.obf_count += 1
            return self._generate_false_expr()
        return node

    def visit_NameConstant(self, node):
        """Handle True/False for older Python versions."""
        if node.value is True:
            self.obf_count += 1
            return self._generate_true_expr()
        elif node.value is False:
            self.obf_count += 1
            return self._generate_false_expr()
        return node

    def visit_UnaryOp(self, node):
        """Obfuscate 'not' operator."""
        if isinstance(node.op, ast.Not):
            # Wrap in double negation or transform
            self.obf_count += 1
            # not x → (x is False) or (not x) with obfuscated operand
            return ast.UnaryOp(
                op=ast.Not(),
                operand=self.generic_visit(node.operand)
            )
        return self.generic_visit(node)

    def visit_BoolOp(self, node):
        """Obfuscate 'and'/'or' operations."""
        # Visit children first
        node = self.generic_visit(node)
        
        # Sometimes wrap in additional boolean logic
        if random.random() < 0.3:
            self.obf_count += 1
            if isinstance(node.op, ast.And):
                # (a and b) → (a and b) and (True)
                node.values.append(self._generate_true_expr())
            elif isinstance(node.op, ast.Or):
                # (a or b) → (a or b) or (False)
                node.values.append(self._generate_false_expr())
        
        return node

    def visit_Compare(self, node):
        """Obfuscate comparison results."""
        # Visit children first
        node = self.generic_visit(node)
        
        # Sometimes wrap comparison in boolean identity
        if random.random() < 0.3:
            self.obf_count += 1
            # x == y → (x == y) == True
            return ast.Compare(
                left=node,
                ops=[ast.Is()],
                comparators=[ast.Constant(True)]
            )
        
        return node

    def visit_Call(self, node):
        """Don't obfuscate inside call nodes to avoid breaking function calls."""
        # Increase call depth to prevent obfuscation of constants in arguments
        self.call_depth += 1
        
        # Visit the function itself (may contain names to obfuscate)
        node.func = self.visit(node.func)
        
        # Don't visit arguments or keywords - they may contain constants/lists that shouldn't be obfuscated
        self.call_depth -= 1
        return node

    def visit_List(self, node):
        """Don't obfuscate inside list literals."""
        # Lists may contain keys for string decoder
        return node

    def visit_Tuple(self, node):
        """Don't obfuscate inside tuple literals."""
        return node

    def visit_Dict(self, node):
        """Don't obfuscate inside dict literals."""
        return node

    def visit_If(self, node):
        """Obfuscate if condition."""
        # Don't obfuscate inside call depth (e.g., inside decoder function)
        if self.call_depth > 0:
            return self.generic_visit(node)
            
        # Visit children first
        node.test = self.visit(node.test)

        # Sometimes wrap condition
        if random.random() < 0.2:
            self.obf_count += 1
            # if x → if x and True
            node.test = ast.BoolOp(
                op=ast.And(),
                values=[node.test, self._generate_true_expr()]
            )
        
        # Visit body and orelse
        node.body = [self.visit(stmt) for stmt in node.body]
        node.orelse = [self.visit(stmt) for stmt in node.orelse]
        
        return node

    def visit_While(self, node):
        """Obfuscate while condition."""
        node.test = self.visit(node.test)
        
        if random.random() < 0.2:
            self.obf_count += 1
            node.test = ast.BoolOp(
                op=ast.And(),
                values=[node.test, self._generate_true_expr()]
            )
        
        node.body = [self.visit(stmt) for stmt in node.body]
        node.orelse = [self.visit(stmt) for stmt in node.orelse]
        
        return node

    def apply_obfuscation(self, code: str) -> str:
        """
        Apply boolean obfuscation to Python code.
        
        Args:
            code: Python source code
            
        Returns:
            Obfuscated code
        """
        try:
            tree = ast.parse(code)
            obfuscated_tree = self.visit(tree)
            ast.fix_missing_locations(obfuscated_tree)
            return ast.unparse(obfuscated_tree)
        except Exception as e:
            print(f"Boolean obfuscation failed: {e}")
            return code

    def reset(self):
        """Reset counter for new file."""
        self.obf_count = 0
        self.call_depth = 0


def obfuscate_booleans(code: str, name_gen_settings: str = 'english') -> str:
    """
    Obfuscate boolean expressions in Python code.
    
    Args:
        code: Python source code
        name_gen_settings: Character set for name generation
        
    Returns:
        Obfuscated code
    """
    obfuscator = BooleanObfuscator(name_gen_settings)
    return obfuscator.apply_obfuscation(code)
