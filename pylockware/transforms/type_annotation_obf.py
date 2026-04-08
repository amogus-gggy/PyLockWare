"""
Type Annotation Obfuscation Transformer for PyLockWare
Obfuscates type annotations to make code harder to understand
"""
import ast
import random
from pylockware.core.name_generator import generate_random_name


class TypeAnnotationObfuscator(ast.NodeTransformer):
    """
    Obfuscates type annotations by:
    1. Replacing specific types with generic aliases
    2. Adding unnecessary Union/Optional wrappers
    3. Obscuring complex type hints with Any
    4. Preserving runtime type checking compatibility
    """

    def __init__(self, name_gen_settings='english'):
        self.name_gen_settings = name_gen_settings
        self.type_aliases = {}
        # Built-in types that should not be obfuscated
        self.protected_types = {
            'int', 'float', 'str', 'bool', 'bytes', 'list', 'dict', 'tuple',
            'set', 'frozenset', 'None', 'NoneType', 'object', 'type',
            'Any', 'Union', 'Optional', 'Callable', 'Generic', 'TypeVar',
            'List', 'Dict', 'Tuple', 'Set', 'FrozenSet', 'Optional',
            'Iterable', 'Iterator', 'Generator', 'AsyncIterable', 'AsyncIterator',
            'AsyncGenerator', 'Sequence', 'Mapping', 'MutableSequence',
            'MutableMapping', 'MappingView', 'ItemsView', 'KeysView', 'ValuesView',
            'Coroutine', 'Awaitable', 'Collection', 'Container', 'Sized',
        }

    def _obfuscate_type_annotation(self, node):
        """Obfuscate a type annotation node."""
        if node is None:
            return None

        # Strategy 1: Wrap in Union with Any (30% chance)
        if random.random() < 0.3 and isinstance(node, ast.Name):
            if node.id not in self.protected_types:
                # Create Union[original_type, Any]
                union_annotation = ast.Subscript(
                    value=ast.Name(id='Union', ctx=ast.Load()),
                    slice=ast.Tuple(
                        elts=[
                            node,
                            ast.Name(id='Any', ctx=ast.Load())
                        ],
                        ctx=ast.Load()
                    ),
                    ctx=ast.Load()
                )
                return union_annotation

        # Strategy 2: Replace complex annotations with Any (20% chance)
        if random.random() < 0.2 and isinstance(node, (ast.Subscript, ast.Attribute)):
            return ast.Name(id='Any', ctx=ast.Load())

        # Strategy 3: Add Optional wrapper (25% chance)
        if random.random() < 0.25 and isinstance(node, ast.Name):
            if node.id not in self.protected_types:
                # Create Optional[original_type]
                optional_annotation = ast.Subscript(
                    value=ast.Name(id='Optional', ctx=ast.Load()),
                    slice=node,
                    ctx=ast.Load()
                )
                return optional_annotation

        # Strategy 4: Transform List/Dict/etc to lowercase versions
        if isinstance(node, ast.Name):
            type_mapping = {
                'List': 'list',
                'Dict': 'dict',
                'Tuple': 'tuple',
                'Set': 'set',
                'FrozenSet': 'frozenset',
            }
            if node.id in type_mapping and random.random() < 0.5:
                return ast.Name(id=type_mapping[node.id], ctx=ast.Load())

        return node

    def visit_arg(self, node):
        """Obfuscate type annotations in function arguments."""
        if node.annotation:
            node.annotation = self._obfuscate_type_annotation(node.annotation)
        return node

    def visit_FunctionDef(self, node):
        """Obfuscate type annotations in function definitions."""
        # Obfuscate return type
        if node.returns:
            node.returns = self._obfuscate_type_annotation(node.returns)

        # Visit arguments (handled by visit_arg)
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node):
        """Obfuscate type annotations in async function definitions."""
        # Obfuscate return type
        if node.returns:
            node.returns = self._obfuscate_type_annotation(node.returns)

        # Visit arguments (handled by visit_arg)
        self.generic_visit(node)
        return node

    def visit_AnnAssign(self, node):
        """Obfuscate type annotations in variable assignments."""
        if node.annotation:
            node.annotation = self._obfuscate_type_annotation(node.annotation)
        return node

    def visit_ClassDef(self, node):
        """Process class definitions - obfuscate type annotations in methods."""
        # Visit class body
        self.generic_visit(node)
        return node

    def _add_typing_imports(self, code):
        """Add necessary typing imports if they're not already present."""
        imports_needed = set()

        # Check if code uses Union, Optional, Any
        if 'Union' in code or 'Optional' in code or 'Any' in code:
            # We need to ensure these are imported from typing
            # This is a simple check - in practice, you'd want to parse the AST
            imports_needed.update(['Union', 'Optional', 'Any'])

        if not imports_needed:
            return code

        # Check if typing import already exists
        if 'from typing import' in code:
            # Add missing imports to existing import
            import_line = f"from typing import {', '.join(sorted(imports_needed))}"
            # Simple approach: add at the beginning after other imports
            lines = code.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('from typing import'):
                    # Extend existing import
                    existing = line.replace('from typing import', '').strip()
                    existing_types = [t.strip() for t in existing.split(',')]
                    all_types = sorted(set(existing_types + list(imports_needed)))
                    lines[i] = f"from typing import {', '.join(all_types)}"
                    return '\n'.join(lines)

        # Add import at the beginning
        import_code = f"from typing import {', '.join(sorted(imports_needed))}"
        return import_code + '\n\n' + code

    def apply_transformation(self, code):
        """
        Apply type annotation obfuscation to Python code.

        Args:
            code: Python source code as string

        Returns:
            Transformed code with obfuscated type annotations
        """
        try:
            print(f"[TYPE_OBF] Starting transformation...")
            tree = ast.parse(code)
            transformed_tree = self.visit(tree)
            ast.fix_missing_locations(transformed_tree)
            result = ast.unparse(transformed_tree)

            # Add typing imports if needed
            result = self._add_typing_imports(result)

            print(f"[TYPE_OBF] Transformation complete. Code changed: {result != code}")
            return result
        except Exception as e:
            print(f"Type annotation obfuscation failed: {e}")
            import traceback
            traceback.print_exc()
            return code
