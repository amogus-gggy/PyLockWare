"""
Remapping Module for PyLockWare
Renames functions, variables, classes, etc. to random names
"""
import ast
import random
import string
from pathlib import Path
from typing import Set, Dict, Any
from pylockware.core.module_base import ModuleBase
from pylockware.transforms.remap_transformer import GlobalRenamer
from pylockware.core.name_generator import generate_random_name


class RemapModule(ModuleBase):
    """
    Module that renames identifiers (functions, variables, classes) to random names
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.remap_map = {}
        self.imports_whitelist = set()
        self.entry_function = self.config.get('entry_function', 'main')
        self.name_gen_settings = self.config.get('name_gen', 'english')
        
    def process(self, project_path: Path, output_path: Path) -> bool:
        """
        Process the project by remapping identifiers
        
        Args:
            project_path: Path to the original project
            output_path: Path to the output directory
            
        Returns:
            True if processing was successful, False otherwise
        """
        try:
            # Build global replacements for the entire project
            self.build_global_replacements(output_path)
            
            # Process all Python files in the output directory
            for py_file in output_path.rglob("*.py"):
                self.remap_code_in_file(py_file)
                    
            return True
        except Exception as e:
            return False
    
    def validate_config(self) -> bool:
        """
        Validate the module's configuration
        
        Returns:
            True if configuration is valid, False otherwise
        """
        # Remap module doesn't have specific validation requirements
        return True
    
    def build_global_replacements(self, directory: Path):
        """
        Build a mapping of original names to obfuscated names for the entire project
        """
        py_files = list(directory.rglob("*.py"))

        # First, collect module filenames and directory names
        all_names = set()

        # Also collect module names used in import statements to protect them from remapping
        imported_module_names = set()

        # First pass: collect all module names used in imports
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            # Get the top-level module name
                            module_name = alias.name.split(".")[0]
                            imported_module_names.add(module_name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            # Get the top-level module name for from imports too
                            module_name = node.module.split(".")[0]
                            imported_module_names.add(module_name)
            except Exception:
                continue  # If we can't parse a file, just skip it for import detection

        for py_file in py_files:
            # Include all .py files, including __init__.py files
            if py_file.name != "__main__.py":
                # Extract module name from the file path
                # For __init__.py files, use the parent directory name
                if py_file.name == "__init__.py":
                    module_name = py_file.parent.name
                else:
                    module_name = py_file.stem

                # Skip the entry point module name (e.g., 'main' from 'main.py')
                if module_name == self.entry_function:
                    continue

                if (
                    module_name
                    and not module_name.startswith("_")
                    and not self._is_external_module(module_name)
                    and module_name not in imported_module_names  # Skip if used in imports
                ):
                    all_names.add(module_name)

                # Add directory names from the path (excluding root directory)
                # Get the relative path from the project root
                rel_path = py_file.relative_to(directory)
                # Add each directory component in the path
                for part in rel_path.parts[:-1]:  # Exclude the filename itself
                    if (part
                        and not part.startswith("_")
                        and not self._is_external_module(part)
                        and part not in imported_module_names):  # Skip if used in imports
                        all_names.add(part)

        # Now assign remap names to all collected names
        for name in sorted(all_names):
            if name not in self.remap_map and not name.startswith('_imp_'):
                self.remap_map[name] = self.generate_random_name()

        # Process all Python files to collect functions, classes, and other identifiers
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Skip protected methods (special methods, Qt events, visit_*, etc.)
                        if self._is_protected_method(node.name):
                            continue
                        
                        # Check if function has @external decorator
                        is_external_func = False
                        for decorator in node.decorator_list:
                            if isinstance(decorator, ast.Name) and decorator.id == 'external':
                                is_external_func = True
                                break
                            elif isinstance(decorator, ast.Attribute) and decorator.attr == 'external':
                                is_external_func = True
                                break
                        
                        if not is_external_func and node.name not in self.imports_whitelist and node.name != self.entry_function:
                            if (not node.name.startswith('_imp_')
                                and node.name not in self.remap_map
                                and node.name not in imported_module_names):
                                self.remap_map[node.name] = self.generate_random_name()
                    elif isinstance(node, ast.AsyncFunctionDef):
                        # Skip protected methods (special methods, Qt events, visit_*, etc.)
                        if self._is_protected_method(node.name):
                            continue
                        
                        # Check if function has @external decorator
                        is_external_func = False
                        for decorator in node.decorator_list:
                            if isinstance(decorator, ast.Name) and decorator.id == 'external':
                                is_external_func = True
                                break
                            elif isinstance(decorator, ast.Attribute) and decorator.attr == 'external':
                                is_external_func = True
                                break
                        
                        if not is_external_func and node.name not in self.imports_whitelist and node.name != self.entry_function:
                            if (not node.name.startswith('_imp_')
                                and node.name not in self.remap_map
                                and node.name not in imported_module_names):
                                self.remap_map[node.name] = self.generate_random_name()
                    elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
                        # Check if class has @external decorator
                        is_external_class = False
                        for decorator in node.decorator_list:
                            if isinstance(decorator, ast.Name) and decorator.id == 'external':
                                is_external_class = True
                                break
                            elif isinstance(decorator, ast.Attribute) and decorator.attr == 'external':
                                is_external_class = True
                                break
                        
                        if not is_external_class and node.name not in self.imports_whitelist:
                            if (not node.name.startswith('_imp_')
                                and node.name not in self.remap_map
                                and node.name not in imported_module_names):
                                self.remap_map[node.name] = self.generate_random_name()
                    elif isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and not target.id.startswith("_"):
                                if (target.id not in self.imports_whitelist
                                    and not target.id.startswith('_imp_')
                                    and target.id not in imported_module_names):
                                    if target.id not in self.remap_map:
                                        self.remap_map[target.id] = self.generate_random_name()
                    elif isinstance(node, ast.AnnAssign):
                        if isinstance(node.target, ast.Name) and not node.target.id.startswith("_"):
                            if (node.target.id not in self.imports_whitelist
                                and not node.target.id.startswith('_imp_')
                                and node.target.id not in imported_module_names):
                                if node.target.id not in self.remap_map:
                                    self.remap_map[node.target.id] = self.generate_random_name()
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.asname and not alias.asname.startswith("_"):
                                if (alias.asname not in self.imports_whitelist
                                    and not alias.asname.startswith('_imp_')
                                    and alias.asname not in imported_module_names):
                                    if alias.asname not in self.remap_map:
                                        self.remap_map[alias.asname] = self.generate_random_name()
                            else:
                                module_name = alias.name.split(".")[0]
                                if module_name not in self.remap_map:
                                    self.remap_map[module_name] = module_name
                    elif isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            if alias.asname and not alias.asname.startswith("_"):
                                if (alias.asname not in self.imports_whitelist
                                    and not alias.asname.startswith('_imp_')
                                    and alias.asname not in imported_module_names):
                                    if alias.asname not in self.remap_map:
                                        self.remap_map[alias.asname] = self.generate_random_name()

            except Exception as e:
                pass

    def _is_protected_method(self, method_name: str) -> bool:
        """
        Check if a method name is protected and should not be renamed.
        This includes special methods, Qt events, and AST visitor methods.
        """
        # Special Python methods (dunder methods)
        if method_name.startswith('__') and method_name.endswith('__'):
            return True
        
        # AST NodeTransformer visit_* methods
        if method_name.startswith('visit_'):
            return True
        
        # Qt/QSyntaxHighlighter
        qt_methods = {
            'highlightBlock',
            # Qt/QWidget events
            'paintEvent', 'resizeEvent', 'mousePressEvent', 'mouseReleaseEvent',
            'mouseMoveEvent', 'keyPressEvent', 'keyReleaseEvent', 'focusInEvent',
            'focusOutEvent', 'enterEvent', 'leaveEvent', 'showEvent', 'hideEvent',
            'closeEvent', 'moveEvent', 'changeEvent', 'contextMenuEvent',
            'dragEnterEvent', 'dragMoveEvent', 'dragLeaveEvent', 'dropEvent',
            'wheelEvent', 'inputMethodEvent', 'tabletEvent', 'actionEvent',
            'fontChange', 'languageChange', 'styleChange', 'enabledChange',
            'focusNextPrevChild', 'event', 'eventFilter',
            # Qt/QAbstractItemModel
            'rowCount', 'columnCount', 'data', 'flags', 'setData', 'headerData',
            'index', 'parent', 'hasIndex', 'insertRows', 'removeRows',
            # Common Python framework methods
            'setUp', 'tearDown', 'setup', 'teardown',
            'get_context_data', 'form_valid', 'form_invalid',
            'dispatch', 'get', 'post', 'put', 'delete', 'patch',
            'create', 'retrieve', 'update', 'partial_update', 'destroy',
            'list', 'create', 'read', 'write', 'open', 'close',
            'read', 'write', 'flush', 'seek', 'tell',
            'copy', 'deepcopy', '__copy__', '__deepcopy__',
        }
        
        return method_name in qt_methods

    def _is_external_module(self, module_name: str) -> bool:
        """Check if a module is external (stdlib or pip package)."""
        # Hardcoded list of common standard library modules
        stdlib_modules = {
            "sys", "os", "json", "datetime", "pathlib", "time", "random", "math",
            "collections", "typing", "base64", "zlib", "numpy", "requests", "urllib",
            "http", "email", "html", "xml", "sqlite3", "logging", "unittest", "argparse",
            "configparser", "tempfile", "shutil", "glob", "fnmatch", "re", "string",
            "textwrap", "struct", "codecs", "pickle", "csv", "hashlib", "hmac", "secrets",
            "uuid", "socket", "ssl", "ftplib", "poplib", "imaplib", "smtplib", "telnetlib",
            "urllib", "http", "email", "mimetypes", "zipfile", "tarfile", "linecache",
            "shlex", "platform", "errno", "stat", "filecmp", "fileinput", "calendar",
            "zoneinfo", "getopt", "getpass", "curses", "ctypes", "threading", "multiprocessing",
            "concurrent", "subprocess", "sched", "queue", "contextlib", "asyncio", "select",
            "selectors", "asyncore", "asynchat", "signal", "mmap", "pipes", "resource",
            "posix", "pwd", "spwd", "grp", "crypt", "termios", "tty", "pty", "fcntl",
            "io", "sysconfig", "warnings", "traceback", "faulthandler", "gc", "inspect",
            "site", "importlib", "pkgutil", "modulefinder", "runpy", "parser", "ast", "dis",
            "pickletools", "compileall", "py_compile", "tabnanny", "pyclbr", "pydoc", "doctest",
            "bdb", "pdb", "profile", "pstats", "timeit", "trace", "tracemalloc", "encodings",
            "code", "codeop", "zipimport", "symbol", "token", "keyword", "tokenize", "symbol",
            "token", "keyword", "distutils", "ensurepip", "venv", "pip", "setuptools", "wheel"
        }
        return module_name in stdlib_modules

    def generate_random_name(self) -> str:
        """
        Generate a random name for remapping
        Names will always start with an underscore to ensure valid Python identifiers
        """
        # Generate a random name with underscore prefix to ensure valid identifier
        from pylockware.core.name_generator import generate_random_name
        return generate_random_name("_", self.name_gen_settings)

    def remap_code_in_file(self, file_path: Path):
        """
        Remap identifiers in a single file using AST transformation
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        try:
            tree = ast.parse(content)
            transformer = GlobalRenamer(self.remap_map)
            # First pass: collect Pydantic classes to protect their fields
            transformer._collect_pydantic_classes(tree)
            transformed_tree = transformer.visit(tree)
            ast.fix_missing_locations(transformed_tree)

            # Convert back to source code
            new_content = ast.unparse(transformed_tree)

            # Write the remapped content back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

        except Exception as e:
            pass