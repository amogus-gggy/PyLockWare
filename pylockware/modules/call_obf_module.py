"""
Call Obfuscation Module for PyLockWare
Obfuscates function calls using globals()["func_name"]() pattern
"""
import ast
import sys
import io
from pathlib import Path
from typing import Dict, Any, List, Set
from pylockware.core.module_base import ModuleBase


class CallObfModule(ModuleBase):
    """
    Module that obfuscates direct function calls by wrapping them with globals()["func_name"]()
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.call_map = {}
        self.stats = {
            'files_processed': 0,
            'files_modified': 0,
            'total_calls_obfuscated': 0,
            'errors': []
        }

    def process(self, project_path: Path, output_path: Path) -> bool:
        """
        Process the Project by obfuscating function calls
        """
        try:
            print(f"[CallObf] Starting call obfuscation in: {output_path}")
            print(f"[CallObf] Current working directory: {Path.cwd()}")

            py_files = list(output_path.rglob("*.py"))
            print(f"[CallObf] Found {len(py_files)} Python files")

            for py_file in py_files:
                try:
                    print(f"\n[CallObf] Processing: {py_file}")

                    with io.open(py_file, 'r', encoding='utf-8-sig', newline='') as f:
                        original_code = f.read()

                    print(f"[CallObf]   File size: {len(original_code)} chars, {len(original_code.encode('utf-8'))} bytes")

                    # Check for existing corruption
                    corruption_chars = ['¯', '┬', '┴', '├', '┤', '│', '─', '▀', '▄', '█']
                    found_corruption = [c for c in corruption_chars if c in original_code]
                    if found_corruption:
                        print(f"[CallObf]   WARNING: File already contains corrupted chars: {found_corruption}")
                        self.stats['errors'].append(f"{py_file}: existing corruption")
                        continue

                    # Parse to check validity
                    try:
                        tree = ast.parse(original_code)
                        print(f"[CallObf]   AST parsed successfully, {len(list(ast.walk(tree)))} nodes")
                    except SyntaxError as e:
                        print(f"[CallObf]   ERROR: Syntax error in original file: {e}")
                        self.stats['errors'].append(f"{py_file}: syntax error - {e}")
                        continue

                    obfuscated_code = self.obfuscate_calls(original_code, str(py_file))

                    # Check for new corruption
                    found_new_corruption = [c for c in corruption_chars if c in obfuscated_code]
                    if found_new_corruption:
                        print(f"[CallObf]   ERROR: Obfuscation introduced corruption: {found_new_corruption}")
                        self.stats['errors'].append(f"{py_file}: obfuscation corruption")
                        continue

                    # Verify result is valid Python
                    try:
                        ast.parse(obfuscated_code)
                        print(f"[CallObf]   Obfuscated AST valid")
                    except SyntaxError as e:
                        print(f"[CallObf]   ERROR: Obfuscation broke syntax: {e}")
                        print(f"[CallObf]   Problem area: {obfuscated_code[max(0, e.offset-30):e.offset+30] if hasattr(e, 'offset') else 'N/A'}")
                        self.stats['errors'].append(f"{py_file}: invalid output - {e}")
                        continue

                    if obfuscated_code != original_code:
                        with io.open(py_file, 'w', encoding='utf-8', newline='') as f:
                            f.write(obfuscated_code)

                        obfuscated_count = obfuscated_code.count('globals()[')
                        print(f"[CallObf]   WRITTEN: {obfuscated_count} calls obfuscated")
                        self.stats['files_modified'] += 1
                        self.stats['total_calls_obfuscated'] += obfuscated_count
                    else:
                        print(f"[CallObf]   No changes needed")

                    self.stats['files_processed'] += 1

                except UnicodeDecodeError as e:
                    print(f"[CallObf]   ERROR: Encoding issue: {e}")
                    self.stats['errors'].append(f"{py_file}: encoding error - {e}")
                except Exception as e:
                    print(f"[CallObf]   ERROR: {type(e).__name__}: {e}")
                    import traceback
                    traceback.print_exc()
                    self.stats['errors'].append(f"{py_file}: {type(e).__name__} - {e}")

            # Print summary
            print(f"\n[CallObf] SUMMARY:")
            print(f"[CallObf]   Files processed: {self.stats['files_processed']}")
            print(f"[CallObf]   Files modified: {self.stats['files_modified']}")
            print(f"[CallObf]   Total calls obfuscated: {self.stats['total_calls_obfuscated']}")
            print(f"[CallObf]   Errors: {len(self.stats['errors'])}")
            for err in self.stats['errors'][:5]:  # Show first 5 errors
                print(f"[CallObf]     - {err}")

            return True
        except Exception as e:
            print(f"[CallObf] FATAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

    def validate_config(self) -> bool:
        return True

    def obfuscate_calls(self, code: str, filename: str = "unknown") -> str:
        """
        Obfuscate function calls in the given code
        """
        try:
            tree = ast.parse(code)

            transformer = CallObfuscatorTransformer(filename)
            transformed_tree = transformer.visit(tree)
            ast.fix_missing_locations(transformed_tree)

            result = ast.unparse(transformed_tree)

            # DEBUG: Show generated code for globals() calls
            import re
            globals_calls = re.findall(r'globals\(\)\[[^\]]+\]', result)
            if globals_calls:
                print(f"[CallObf]   DEBUG globals() calls in {filename}: {globals_calls[:3]}")

            corruption_chars = ['¯', '┬', '┴', '├', '┤', '│', '─', '▀', '▄', '█']
            for char in corruption_chars:
                if char in result:
                    print(f"[CallObf]   WARNING in {filename}: Corruption char U+{ord(char):04X} detected")

            if transformer.obfuscated_calls:
                print(f"[CallObf]   In {filename} obfuscated: {transformer.obfuscated_calls}")

            return result

        except Exception as e:
            print(f"[CallObf]   ERROR in obfuscate_calls for {filename}: {e}")
            import traceback
            traceback.print_exc()
            return code


class CallObfuscatorTransformer(ast.NodeTransformer):
    """
    AST transformer that replaces direct function calls with globals()["func_name"]()
    """

    def __init__(self, filename: str = "unknown"):
        self.filename = filename
        self.obfuscated_calls: List[str] = []
        self.skipped_calls: List[str] = []
        self.excluded_names: Set[str] = {
            'print', 'len', 'range', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple',
            'max', 'min', 'sum', 'abs', 'all', 'any', 'chr', 'ord', 'hex', 'bin', 'oct',
            'open', 'input', 'type', 'isinstance', 'issubclass', 'hasattr', 'getattr', 'setattr',
            'delattr', 'zip', 'enumerate', 'iter', 'next', 'map', 'filter', 'reduce', 'sorted',
            'reversed', 'format', 'eval', 'exec', 'compile', 'vars', 'dir', 'locals', 'globals',
            'breakpoint', 'help', 'exit', 'quit', 'copyright', 'credits', 'license',
            '__init__', '__main__', '__name__', '__file__', '__doc__', '__package__',
            '__spec__', '__annotations__', '__builtins__', '__cached__', '__loader__',
            'main', 'run', 'start', 'init', 'setup', 'configure', 'initialize',
            'globals',
        }
        self.defined_names: Set[str] = set()
        self.imported_modules: Set[str] = set()

    def visit_Import(self, node: ast.Import) -> ast.Import:
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            base_name = name.split('.')[0]
            self.imported_modules.add(base_name)
            print(f"[CallObf]     [AST] Import detected: {base_name}")
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        module = node.module or "unknown"
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.defined_names.add(name)
            print(f"[CallObf]     [AST] From {module} import: {name} (added to defined_names)")
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        self.defined_names.add(node.name)
        print(f"[CallObf]     [AST] Function defined: {node.name}")
        self.generic_visit(node)
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        self.defined_names.add(node.name)
        print(f"[CallObf]     [AST] Async function defined: {node.name}")
        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        self.defined_names.add(node.name)
        print(f"[CallObf]     [AST] Class defined: {node.name}")
        self.generic_visit(node)
        return node

    def visit_Assign(self, node: ast.Assign) -> ast.AST:
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.defined_names.add(target.id)
                print(f"[CallObf]     [AST] Variable assigned: {target.id}")
        return self.generic_visit(node)

    def _create_dict_access_call(self, func_name: str, args: List[ast.expr], keywords: List[ast.keyword]) -> ast.Call:
        """
        Create globals()["func_name"](*args, **kwargs)
        """
        # DEBUG: Print what we're creating
        print(f"[CallObf]       [CREATE] Creating globals()[\"{func_name}\"]")

        globals_call = ast.Call(
            func=ast.Name(id='globals', ctx=ast.Load()),
            args=[],
            keywords=[]
        )

        # CRITICAL: Use ast.Constant with string value explicitly
        func_name_constant = ast.Constant(value=func_name, kind=None)

        subscript = ast.Subscript(
            value=globals_call,
            slice=func_name_constant,
            ctx=ast.Load()
        )

        return ast.Call(func=subscript, args=args, keywords=keywords)

    def visit_Call(self, node: ast.Call) -> ast.AST:
        node = self.generic_visit(node)

        # Handle direct function calls: func_name()
        if isinstance(node.func, ast.Name):
            func_name = node.func.id

            print(f"[CallObf]     [AST] Direct call detected: {func_name}")

            if func_name in self.excluded_names:
                print(f"[CallObf]       -> SKIPPED (excluded: {func_name})")
                self.skipped_calls.append(func_name)
                return node

            if func_name not in self.defined_names:
                print(f"[CallObf]       -> SKIPPED (not defined in this module: {func_name})")
                self.skipped_calls.append(func_name)
                return node

            print(f"[CallObf]       -> OBFUSCATING: {func_name}")
            new_call = self._create_dict_access_call(func_name, node.args, node.keywords)
            self.obfuscated_calls.append(func_name)
            return new_call

        # Handle module attribute calls: utils.calculate_sum()
        if isinstance(node.func, ast.Attribute):
            attr_name = node.func.attr
            obj = node.func.value

            print(f"[CallObf]     [AST] Attribute call detected: {attr_name} on {type(obj).__name__}")

            if attr_name in self.excluded_names:
                print(f"[CallObf]       -> SKIPPED (excluded: {attr_name})")
                self.skipped_calls.append(attr_name)
                return node

            # Check if it's a module call: utils.calculate_sum()
            if isinstance(obj, ast.Name) and obj.id in self.imported_modules:
                print(f"[CallObf]       -> SKIPPED (module attribute access: {obj.id}.{attr_name})")
                self.skipped_calls.append(f"{obj.id}.{attr_name}")
                return node

            # It's a method call on an object
            print(f"[CallObf]       -> OBFUSCATING method: {attr_name}")
            new_call = self._create_dict_access_call(attr_name, node.args, node.keywords)
            self.obfuscated_calls.append(attr_name)
            return new_call

        return node