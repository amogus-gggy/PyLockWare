"""
Type Annotation Obfuscation Module for PyLockWare
Obfuscates type annotations to make code harder to understand
"""
from pathlib import Path
from typing import Dict, Any
from pylockware.core.module_base import ModuleBase
from pylockware.transforms.type_annotation_obf import TypeAnnotationObfuscator


class TypeAnnotationObfModule(ModuleBase):
    """
    Module that obfuscates type annotations to make code harder to understand
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name_gen_settings = self.config.get('name_gen', 'english')

    def process(self, project_path: Path, output_path: Path) -> bool:
        """
        Process the project by obfuscating type annotations in all Python files

        Args:
            project_path: Path to the original project
            output_path: Path to the output directory

        Returns:
            True if processing was successful, False otherwise
        """
        try:
            print("Applying type annotation obfuscation to all Python files...")

            # Create an instance of the type annotation obfuscator
            transformer = TypeAnnotationObfuscator(
                name_gen_settings=self.name_gen_settings
            )

            # Find all Python files in the output directory
            for py_file in output_path.rglob("*.py"):
                # Skip special files
                if py_file.name not in ["obfuscator.py", "type_annotation_obf.py"]:
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            original_code = f.read()

                        # Apply type annotation obfuscation
                        transformed_code = transformer.apply_transformation(original_code)

                        # Only write if changes were made
                        if transformed_code != original_code:
                            with open(py_file, 'w', encoding='utf-8') as f:
                                f.write(transformed_code)
                            print(f"Applied type annotation obfuscation to {py_file}")

                    except Exception as e:
                        print(f"Error applying type annotation obfuscation to {py_file}: {e}")

            return True
        except Exception as e:
            print(f"Error during type annotation obfuscation: {e}")
            return False

    def validate_config(self) -> bool:
        """
        Validate the module's configuration

        Returns:
            True if configuration is valid, False otherwise
        """
        return True
