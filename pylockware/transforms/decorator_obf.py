"""
Decorator Obfuscation Transformer for PyLockWare
Obfuscates decorator usage to make code harder to analyze
"""
import ast
import random
from pylockware.core.name_generator import generate_random_name


class DecoratorObfuscator(ast.NodeTransformer):
    """
    Obfuscates decorators by wrapping them in lambda functions and using indirect calls.
    This makes it harder to identify which decorators are being applied.
    """

    def __init__(self, name_gen_settings='english'):
        self.name_gen_settings = name_gen_settings
        self.helper_vars = {}

    def _create_decorator_wrapper(self, decorator_node):
        """
        Create an obfuscated decorator wrapper.
        Instead of @decorator, uses a helper variable pattern.
        """
        # For now, just return the decorator as-is to avoid issues
        # The indirect strategy is safer here
        return self._create_indirect_decorator(decorator_node)

    def _create_indirect_decorator(self, decorator_node):
        """
        Create indirect decorator reference using helper variable.
        Only works for simple Name/Attribute decorators, not Call decorators.
        """
        # Only obfuscate simple decorator references (Name, Attribute)
        # Skip Call decorators like @wraps(func), @lru_cache() etc.
        # because their arguments may reference local-scope variables
        if isinstance(decorator_node, (ast.Name, ast.Attribute)):
            helper_name = generate_random_name("_d", self.name_gen_settings)
            self.helper_vars[helper_name] = decorator_node
            return ast.Name(id=helper_name, ctx=ast.Load())
        
        # Return original for complex decorators (Call, etc.)
        return decorator_node

    def visit_FunctionDef(self, node):
        """Obfuscate decorators on function definitions."""
        if node.decorator_list:
            new_decorators = []
            for decorator in node.decorator_list:
                # Always use indirect strategy to avoid forward reference issues
                new_decorators.append(self._create_indirect_decorator(decorator))

            node.decorator_list = new_decorators

        # Visit function body
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node):
        """Obfuscate decorators on async function definitions."""
        if node.decorator_list:
            new_decorators = []
            for decorator in node.decorator_list:
                # Always use indirect strategy to avoid forward reference issues
                new_decorators.append(self._create_indirect_decorator(decorator))

            node.decorator_list = new_decorators

        # Visit function body
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node):
        """Obfuscate decorators on class definitions."""
        if node.decorator_list:
            new_decorators = []
            for decorator in node.decorator_list:
                # Always use indirect strategy to avoid forward reference issues
                new_decorators.append(self._create_indirect_decorator(decorator))

            node.decorator_list = new_decorators

        # Visit class body
        self.generic_visit(node)
        return node

    def get_helper_definitions(self):
        """
        Generate helper variable definitions for indirect decorators.
        Returns Python code string with helper assignments.
        """
        if not self.helper_vars:
            return ""

        lines = []
        for var_name, decorator_node in self.helper_vars.items():
            # Convert decorator AST node to string
            try:
                decorator_str = ast.unparse(decorator_node)
                lines.append(f"{var_name} = {decorator_str}")
            except:
                # If unparse fails, skip this one
                pass

        return "\n".join(lines)

    def apply_transformation(self, code):
        """
        Apply decorator obfuscation to Python code.

        Args:
            code: Python source code as string

        Returns:
            Transformed code with obfuscated decorators
        """
        try:
            print(f"[DECORATOR_OBF] Starting transformation...")
            tree = ast.parse(code)
            transformed_tree = self.visit(tree)
            ast.fix_missing_locations(transformed_tree)
            result = ast.unparse(transformed_tree)

            # Add helper definitions after imports to avoid issues
            helpers = self.get_helper_definitions()
            if helpers:
                # Find position after imports
                lines = result.split('\n')
                insert_pos = 0
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        insert_pos = i + 1
                    elif insert_pos > 0 and line.strip() == '':
                        continue
                    elif insert_pos > 0:
                        break

                # Insert helpers after imports
                result = '\n'.join(lines[:insert_pos]) + '\n\n' + helpers + '\n' + '\n'.join(lines[insert_pos:])

            print(f"[DECORATOR_OBF] Transformation complete. Code changed: {result != code}")
            return result
        except Exception as e:
            print(f"Decorator obfuscation failed: {e}")
            import traceback
            traceback.print_exc()
            return code
