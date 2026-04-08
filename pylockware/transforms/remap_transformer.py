"""
AST Transformer for remapping identifiers in Python code
"""
import ast
import builtins
from pylockware.core.name_generator import NameGenerator


class GlobalRenamer(ast.NodeTransformer):
    """Renames global identifiers in AST nodes, excluding builtins."""

    def __init__(self, global_replacements=None):
        # Get all built-in names to protect them from renaming
        self.builtin_names = set(dir(builtins)) | {
            "self",
            "cls",  # Common method/class parameters
            "args",
            "kwargs",  # Common function parameters
            "_"
        }

        # Track classes that inherit from BaseModel (Pydantic)
        self.pydantic_classes = set()

        # Add common built-in methods and attributes that shouldn't be renamed
        self.protected_names = self.builtin_names | {
            # Dictionary methods
            'keys', 'values', 'items', 'get', 'pop', 'popitem', 'update', 
            'setdefault', 'clear', 'copy', 'fromkeys',
            # List methods
            'append', 'extend', 'insert', 'remove', 'pop', 'index', 'count', 
            'sort', 'reverse',
            # String methods
            'capitalize', 'casefold', 'center', 'count', 'encode', 'endswith', 
            'expandtabs', 'find', 'format', 'format_map', 'index', 'isalnum', 
            'isalpha', 'isdecimal', 'isdigit', 'isidentifier', 'islower', 
            'isnumeric', 'isprintable', 'isspace', 'istitle', 'isupper', 
            'join', 'ljust', 'lower', 'lstrip', 'maketrans', 'partition', 
            'replace', 'rfind', 'rindex', 'rjust', 'rpartition', 'rsplit', 
            'rstrip', 'split', 'splitlines', 'startswith', 'strip', 'swapcase', 
            'title', 'translate', 'upper', 'zfill',
            # General object methods
            'append', 'extend', 'insert', 'remove', 'index', 'count', 'sort', 
            'reverse', 'pop', 'clear', 'copy', 'keys', 'values', 'items', 
            'get', 'setdefault', 'update', 'pop', 'popitem', 'clear', 'copy', 
            'fromkeys', '__class__', '__delattr__', '__dir__', '__eq__', 
            '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', 
            '__init__', '__init_subclass__', '__le__', '__lt__', '__ne__', 
            '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', 
            '__sizeof__', '__str__', '__subclasshook__',
            # File methods
            'close', 'flush', 'read', 'readline', 'readlines', 'seek', 'tell', 
            'truncate', 'write', 'writelines',
            # Set methods
            'add', 'discard', 'intersection', 'intersection_update', 'isdisjoint', 
            'issubset', 'issuperset', 'pop', 'remove', 'symmetric_difference', 
            'symmetric_difference_update', 'union', 'update',
            # Tuple methods (though tuples don't have many)
            '__add__', '__contains__', '__getitem__', '__iter__', '__len__', 
            '__mul__', '__rmul__',
            # Type methods
            'mro', '__bases__', '__name__', '__qualname__', '__doc__', 
            '__module__', '__dict__', '__weakref__', '__annotations__', 
            '__init__', '__new__', '__del__', '__repr__', '__str__', 
            '__format__', '__hash__', '__getattribute__', '__setattr__', 
            '__delete__', '__lt__', '__le__', '__eq__', '__ne__', '__gt__', 
            '__ge__', '__get__', '__set__', '__delete__', '__set_name__', 
            '__init_subclass__', '__prepare__', '__instancecheck__', 
            '__subclasscheck__', '__class_getitem__',
        }
        
        # Only include non-protected names in replacements
        self.global_replacements = {
            k: v
            for k, v in (global_replacements or {}).items()
            if k not in self.protected_names
        }

    def visit_Import(self, node):
        for alias in node.names:
            # Don't rename imports of builtin modules
            if alias.name.split(".")[0] in self.builtin_names:
                continue
            if alias.asname and alias.asname in self.global_replacements:
                alias.asname = self.global_replacements[alias.asname]
        return node

    def visit_ImportFrom(self, node):
        # Don't rename imports from builtin modules
        if node.module and any(
            node.module == name or node.module.startswith(f"{name}.")
            for name in self.builtin_names
        ):
            return node

        for alias in node.names:
            old = alias.name
            if old in self.global_replacements:
                alias.name = self.global_replacements[old]
            if alias.asname and alias.asname in self.global_replacements:
                alias.asname = self.global_replacements[alias.asname]
        return node

    def visit_Attribute(self, node):
        # Rename attribute names if they're in the remap map
        # Only rename the attribute part (not the value part)
        # But don't rename protected/built-in attributes
        if node.attr in self.global_replacements and node.attr not in self.protected_names:
            node.attr = self.global_replacements[node.attr]
        # Visit the value part (the object whose attribute we're accessing)
        self.generic_visit(node)
        return node

    def visit_Global(self, node):
        # Rename global declarations
        for i, name in enumerate(node.names):
            if name in self.global_replacements:
                node.names[i] = self.global_replacements[name]
        return node

    def visit_Name(self, node):
        # Don't rename builtin names
        if node.id in self.builtin_names:
            return node

        if isinstance(node.ctx, ast.Load) and node.id in self.global_replacements:
            node.id = self.global_replacements[node.id]
        elif isinstance(node.ctx, ast.Store) and node.id in self.global_replacements:
            node.id = self.global_replacements[node.id]
        elif isinstance(node.ctx, ast.Del) and node.id in self.global_replacements:
            node.id = self.global_replacements[node.id]
        return node

    def visit_FunctionDef(self, node):
        # Rename function name if it's in the remap map
        if node.name in self.global_replacements:
            node.name = self.global_replacements[node.name]
        # Visit the body of the function
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node):
        # Rename async function name if it's in the remap map
        if node.name in self.global_replacements:
            node.name = self.global_replacements[node.name]
        # Visit the body of the function
        self.generic_visit(node)
        return node

    def _collect_pydantic_classes(self, node):
        """First pass: find all classes that inherit from BaseModel"""
        for child in ast.walk(node):
            if isinstance(child, ast.ClassDef):
                for base in child.bases:
                    if isinstance(base, ast.Name) and base.id == 'BaseModel':
                        self.pydantic_classes.add(child.name)
                    elif isinstance(base, ast.Attribute) and base.attr == 'BaseModel':
                        self.pydantic_classes.add(child.name)

    def visit_ClassDef(self, node):
        # Rename class name if it's in the remap map
        if node.name in self.global_replacements:
            node.name = self.global_replacements[node.name]
        
        # If this is a Pydantic model, protect its field names from renaming
        if node.name in self.pydantic_classes or any(
            (isinstance(base, ast.Name) and base.id == 'BaseModel') or 
            (isinstance(base, ast.Attribute) and base.attr == 'BaseModel')
            for base in node.bases
        ):
            # Protect field names in this class
            for item in node.body:
                if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                    field_name = item.target.id
                    if field_name in self.global_replacements:
                        del self.global_replacements[field_name]
        
        # Visit the body of the class
        self.generic_visit(node)
        return node

    def visit_arg(self, node):
        # Rename function argument names if they're in the remap map
        if node.arg in self.global_replacements:
            node.arg = self.global_replacements[node.arg]
        # Visit annotation if present
        self.generic_visit(node)
        return node