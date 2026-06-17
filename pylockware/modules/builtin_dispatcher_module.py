"""
Builtin Dispatcher Module for PyLockWare
Replaces all built-in function calls with calls via a dispatcher
Встраивает dispatcher прямо в каждый модуль — без внешних файлов
"""
import ast
from pathlib import Path
from typing import Dict, Any
from pylockware.core.module_base import ModuleBase
from pylockware.transforms.builtin_dispatcher import BuiltinDispatcherTransformer, BUILTIN_FUNCTIONS


class BuiltinDispatcherModule(ModuleBase):
    """
    Module that replaces built-in function calls with dispatcher calls
    e.g., print() -> _dispatcher.ghjfkd()
    Dispatcher code is embedded directly into each module - no external files needed
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name_gen_settings = self.config.get('name_gen', 'english')

    def process(self, project_path: Path, output_path: Path) -> bool:
        """
        Process the project by replacing built-in calls with dispatcher calls
        Dispatcher code is embedded directly into each module

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

            # Files that should NOT be transformed (they contain critical runtime checks)
            protected_files = {
                "antidebug_llvm.py",
                "antidebug_crossplatform.py",
                "anti_tamper_builtins.py",
            }

            files_modified = 0

            for py_file in py_files:
                if py_file.name in protected_files:
                    continue
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        original_code = f.read()

                    tree = ast.parse(original_code)

                    # Create a fresh transformer for each file (unique obfuscated names)
                    transformer = BuiltinDispatcherTransformer(name_gen_settings=self.name_gen_settings)

                    # Use transform_module which embeds dispatcher directly
                    transformed_tree = transformer.transform_module(tree)

                    # Only write if changes were made
                    if transformer.builtins_map:
                        new_content = ast.unparse(transformed_tree)

                        with open(py_file, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        files_modified += 1
                        print(f"  Obfuscated builtins in {py_file}")

                except Exception as e:
                    print(f"Error processing {py_file}: {e}")
                    continue

            if files_modified == 0:
                print("No built-in functions found, skipping builtin dispatcher obfuscation.")
            else:
                print(f"Builtin dispatcher obfuscation complete. Modified {files_modified} files.")
            return True

        except Exception as e:
            print(f"Error during builtin dispatcher obfuscation: {e}")
            import traceback
            traceback.print_exc()
            return False

    def validate_config(self) -> bool:
        """
        Validate the module's configuration

        Returns:
            True if configuration is valid, False otherwise
        """
        return True
