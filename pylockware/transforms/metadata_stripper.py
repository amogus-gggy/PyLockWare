"""
Metadata Stripping Module for PyLockWare
Removes __doc__, __annotations__, type hints at AST level
"""
import ast
from pylockware.core.name_generator import generate_random_name


class MetadataStripper(ast.NodeTransformer):
    """
    AST transformer that strips metadata from Python code:
    - Docstrings (__doc__)
    - Type annotations (function parameters, return types, variables)
    - __annotations__ assignments
    """

    def __init__(self):
        self.stripped_count = 0

    def visit_Module(self, node):
        """Remove module-level docstring."""
        node = self.generic_visit(node)
        
        # Remove module docstring (first statement if it's a string)
        if node.body and isinstance(node.body[0], ast.Expr):
            if isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body = node.body[1:]
                self.stripped_count += 1
        
        return node

    def visit_ClassDef(self, node):
        """Remove class docstring and annotations."""
        # Remove class docstring
        if node.body and isinstance(node.body[0], ast.Expr):
            if isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body = node.body[1:]
                self.stripped_count += 1
        
        # Remove type annotations from class body (__annotations__ = {...})
        new_body = []
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                # Remove __annotations__ assignment
                is_annotations = False
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id == '__annotations__':
                        is_annotations = True
                        self.stripped_count += 1
                        break
                if not is_annotations:
                    new_body.append(stmt)
            else:
                new_body.append(stmt)
        
        node.body = new_body
        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Remove function docstring and type annotations."""
        # Remove function docstring
        if node.body and isinstance(node.body[0], ast.Expr):
            if isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str):
                node.body = node.body[1:]
                self.stripped_count += 1
        
        # Remove type annotations from arguments
        for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
            if arg.annotation is not None:
                arg.annotation = None
                self.stripped_count += 1
        
        # Remove return type annotation
        if node.returns is not None:
            node.returns = None
            self.stripped_count += 1
        
        # Remove __annotations__ from function body
        new_body = []
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                is_annotations = False
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id == '__annotations__':
                        is_annotations = True
                        self.stripped_count += 1
                        break
                if not is_annotations:
                    new_body.append(stmt)
            else:
                new_body.append(stmt)
        
        node.body = new_body
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Remove async function docstring and type annotations."""
        return self.visit_FunctionDef(node)

    def visit_AnnAssign(self, node):
        """Remove annotated assignments (var: type = value -> var = value)."""
        if node.annotation is not None:
            node.annotation = None
            self.stripped_count += 1
        return self.generic_visit(node)

    def apply_stripping(self, code: str) -> str:
        """
        Apply metadata stripping to Python code.
        
        Args:
            code: Python source code
            
        Returns:
            Code with metadata stripped
        """
        try:
            tree = ast.parse(code)
            stripped_tree = self.visit(tree)
            ast.fix_missing_locations(stripped_tree)
            return ast.unparse(stripped_tree)
        except Exception as e:
            print(f"Metadata stripping failed: {e}")
            return code

    def reset(self):
        """Reset counter for new file."""
        self.stripped_count = 0


def strip_metadata(code: str) -> str:
    """
    Strip metadata from Python code.
    
    Args:
        code: Python source code
        
    Returns:
        Code with metadata stripped
    """
    stripper = MetadataStripper()
    return stripper.apply_stripping(code)
