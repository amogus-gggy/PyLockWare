"""
Decorator Obfuscation Transformer for PyLockWare
Converts @decorator syntax to explicit assignment: func = decorator(func)
"""
import ast
from pylockware.core.name_generator import generate_random_name


class DecoratorObfuscator(ast.NodeTransformer):
    """
    Converts @decorator syntax to explicit assignments to make code harder to analyze.
    Example:
        @dec1
        @dec2(arg)
        def func(): pass
    becomes:
        def func(): pass
        func = dec1(dec2(arg)(func))
    """

    def __init__(self, name_gen_settings='english'):
        self.name_gen_settings = name_gen_settings

    def _build_decorated_assignment(self, target_name, decorator_list, is_async=False):
        """
        Build assignment: func = dec1(dec2(arg)(func))
        Decorators are applied bottom-up (last decorator is outermost).
        """
        # Start with the function reference
        expr = ast.Name(id=target_name, ctx=ast.Load())

        # Apply decorators from bottom to top (reverse order)
        for dec in reversed(decorator_list):
            if isinstance(dec, ast.Call):
                # @decorator(args) -> decorator(args)(func)
                expr = ast.Call(
                    func=ast.Call(
                        func=dec.func,
                        args=dec.args,
                        keywords=dec.keywords,
                    ),
                    args=[expr],
                    keywords=[],
                )
            else:
                # @decorator -> decorator(func)
                expr = ast.Call(
                    func=dec,
                    args=[expr],
                    keywords=[],
                )

        # func = decorated_expr
        assignment = ast.Assign(
            targets=[ast.Name(id=target_name, ctx=ast.Store())],
            value=expr,
        )
        return assignment

    def visit_FunctionDef(self, node):
        """Convert decorators to assignment after function definition."""
        # First process nested nodes
        self.generic_visit(node)
        
        if node.decorator_list:
            # Build the assignment
            assignment = self._build_decorated_assignment(node.name, node.decorator_list)
            ast.fix_missing_locations(assignment)
            # Store assignment to be added after the node by parent
            # We'll add it as a sibling by appending to a wrapper
            node._decorator_assignment = assignment
            # Remove decorators from the function
            node.decorator_list = []

        return node

    def visit_AsyncFunctionDef(self, node):
        """Convert decorators to assignment after async function definition."""
        self.generic_visit(node)
        
        if node.decorator_list:
            assignment = self._build_decorated_assignment(node.name, node.decorator_list, is_async=True)
            ast.fix_missing_locations(assignment)
            node._decorator_assignment = assignment
            node.decorator_list = []

        return node

    def visit_ClassDef(self, node):
        """Convert decorators to assignment after class definition."""
        self.generic_visit(node)
        
        if node.decorator_list:
            assignment = self._build_decorated_assignment(node.name, node.decorator_list)
            ast.fix_missing_locations(assignment)
            node._decorator_assignment = assignment
            node.decorator_list = []

        return node

    def generic_visit(self, node):
        """Override to inject decorator assignments after functions/classes."""
        if not isinstance(node, ast.AST):
            return node
            
        for field, old_value in list(ast.iter_fields(node)):
            if isinstance(old_value, list):
                new_value = []
                for item in old_value:
                    if isinstance(item, ast.AST):
                        self.visit(item)
                        new_value.append(item)
                        # If item has decorator_assignment, add it after
                        if hasattr(item, '_decorator_assignment'):
                            new_value.append(item._decorator_assignment)
                            delattr(item, '_decorator_assignment')
                    else:
                        new_value.append(item)
                setattr(node, field, new_value)
        return node

    def apply_transformation(self, code):
        """
        Apply decorator obfuscation to Python code.
        """
        try:
            print(f"[DECORATOR_OBF] Starting transformation...")
            tree = ast.parse(code)
            transformed_tree = self.visit(tree)
            ast.fix_missing_locations(transformed_tree)
            result = ast.unparse(transformed_tree)

            print(f"[DECORATOR_OBF] Transformation complete. Code changed: {result != code}")
            return result
        except Exception as e:
            print(f"Decorator obfuscation failed: {e}")
            import traceback
            traceback.print_exc()
            return code
