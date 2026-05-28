"""
Builtin Dispatcher Module for PyLockWare
Replaces all built-in function calls with calls via a dispatcher
"""
import ast
import shutil
from pathlib import Path
from typing import Dict, Any, Set
from pylockware.core.module_base import ModuleBase
from pylockware.transforms.builtin_dispatcher import BuiltinDispatcherTransformer, BUILTIN_FUNCTIONS


# Имя файла для центрального dispatcher
DISPATCHER_FILENAME = "_builtin_dispatcher.py"


class BuiltinDispatcherModule(ModuleBase):
    """
    Module that replaces built-in function calls with dispatcher calls
    e.g., print() -> _dispatcher.ghjfkd()
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name_gen_settings = self.config.get('name_gen', 'english')
        self.dispatcher_var_name = None  # Имя переменной dispatcher (например, _d8xk2)

    def process(self, project_path: Path, output_path: Path) -> bool:
        """
        Process the project by replacing built-in calls with dispatcher calls

        Args:
            project_path: Path to the original project
            output_path: Path to the output directory

        Returns:
            True if processing was successful, False otherwise
        """
        try:
            print("Applying builtin dispatcher obfuscation...")

            # Find all Python files in the output directory
            py_files = list(output_path.rglob("*.py"))

            # First pass: collect all built-in functions used across all files
            all_builtins_used = set()
            
            # Files that should NOT be transformed (they contain critical runtime checks)
            protected_files = {
                DISPATCHER_FILENAME,
                "antidebug_llvm.py",
                "antidebug_crossplatform.py",
                "anti_tamper_builtins.py",
            }
            
            for py_file in py_files:
                if py_file.name in protected_files:
                    continue
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    tree = ast.parse(content)

                    for node in ast.walk(tree):
                        if isinstance(node, ast.Call):
                            if isinstance(node.func, ast.Name) and node.func.id in BUILTIN_FUNCTIONS:
                                all_builtins_used.add(node.func.id)
                            elif isinstance(node.func, ast.Attribute):
                                if isinstance(node.func.value, ast.Name):
                                    if node.func.value.id in {'builtins', '__builtins__'}:
                                        all_builtins_used.add(node.func.attr)
                        elif isinstance(node, ast.Name) and node.id in BUILTIN_FUNCTIONS:
                            # Handle references to builtins without calling
                            all_builtins_used.add(node.id)
                except Exception:
                    continue

            if not all_builtins_used:
                print("No built-in functions found, skipping builtin dispatcher obfuscation.")
                return True

            # Create transformer with only the builtins that are actually used
            from pylockware.core.name_generator import generate_random_name
            self.dispatcher_var_name = generate_random_name('_', self.name_gen_settings)

            final_transformer = BuiltinDispatcherTransformer(name_gen_settings=self.name_gen_settings)
            # Override dispatcher name with our generated one
            final_transformer.dispatcher_name = self.dispatcher_var_name

            # Generate mapping only for used builtins
            for builtin_name in sorted(all_builtins_used):
                final_transformer.builtins_map[builtin_name] = generate_random_name('_', self.name_gen_settings)

            # Create the central dispatcher file
            dispatcher_file = output_path / DISPATCHER_FILENAME
            dispatcher_code = self._generate_dispatcher_code(final_transformer)

            with open(dispatcher_file, 'w', encoding='utf-8') as f:
                f.write(dispatcher_code)
            print(f"  Created central dispatcher: {dispatcher_file}")

            # Find all package directories (directories containing __init__.py)
            package_dirs = set()
            for init_file in output_path.rglob("__init__.py"):
                package_dirs.add(init_file.parent)

            # Copy dispatcher to each package directory
            for pkg_dir in package_dirs:
                pkg_dispatcher = pkg_dir / DISPATCHER_FILENAME
                if pkg_dispatcher != dispatcher_file:  # Don't copy to root if already there
                    shutil.copy2(dispatcher_file, pkg_dispatcher)
                    print(f"  Copied dispatcher to {pkg_dir}")

            # Find all Python files in the output directory
            py_files = list(output_path.rglob("*.py"))

            # Process all Python files (except the dispatcher files themselves)
            files_modified = 0
            
            for py_file in py_files:
                if py_file.name in protected_files:
                    continue
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        original_code = f.read()

                    # Skip files that don't use any builtins
                    tree = ast.parse(original_code)
                    transformed_tree = final_transformer.visit(tree)
                    ast.fix_missing_locations(transformed_tree)

                    # Convert back to source code
                    new_content = ast.unparse(transformed_tree)

                    # Only add import and write if changes were made
                    if new_content != original_code:
                        # Add import statement for dispatcher
                        new_content = self._add_dispatcher_import(new_content)
                        
                        with open(py_file, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        files_modified += 1
                        print(f"  Obfuscated builtins in {py_file}")

                except Exception as e:
                    print(f"Error processing {py_file}: {e}")
                    continue

            print(f"Builtin dispatcher obfuscation complete. Modified {files_modified} files.")
            return True

        except Exception as e:
            print(f"Error during builtin dispatcher obfuscation: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _generate_dispatcher_code(self, transformer: BuiltinDispatcherTransformer) -> str:
        """
        Generate the central dispatcher module code
        """
        mappings = []
        for original, obfuscated in sorted(transformer.builtins_map.items()):
            mappings.append(f"    '{obfuscated}': {original},")

        mappings_code = '\n'.join(mappings)

        dispatcher_code = f'''"""
Builtin Dispatcher Module
Generated by PyLockWare Obfuscator
"""


class {transformer.dispatcher_name}:
    """Central dispatcher for built-in functions"""
    _builtins = {{
{mappings_code}
    }}

    def __getattr__(self, name):
        if name in self._builtins:
            return self._builtins[name]
        raise AttributeError(f"Unknown builtin: {{name}}")


# Global dispatcher instance
{transformer.dispatcher_name.lower()} = {transformer.dispatcher_name}()
'''
        return dispatcher_code

    def _add_dispatcher_import(self, code: str) -> str:
        """
        Add import statement for the dispatcher module at the beginning of the code

        Args:
            code: Source code to modify
        """
        lines = code.split('\n')
        insert_position = 0

        # Skip shebang and encoding declarations
        for i, line in enumerate(lines):
            if line.startswith('#!') or line.startswith('# -*- coding:'):
                insert_position = i + 1
            else:
                break

        # Add simple import without dots - dispatcher is in the same package
        import_line = f"from {DISPATCHER_FILENAME[:-3]} import {self.dispatcher_var_name.lower()} as {self.dispatcher_var_name}"

        lines.insert(insert_position, import_line)

        return '\n'.join(lines)

    def validate_config(self) -> bool:
        """
        Validate the module's configuration

        Returns:
            True if configuration is valid, False otherwise
        """
        return True
