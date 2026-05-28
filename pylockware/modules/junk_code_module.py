"""
Junk Code Module for PyLockWare
Adds fake if/elif branches with true/false conditions to obfuscate code
"""
from pathlib import Path
from typing import Dict, Any
from pylockware.core.module_base import ModuleBase
from pylockware.transforms.junk_code_transformer import JunkCodeTransformer


class JunkCodeModule(ModuleBase):
    """
    Module that adds fake if/elif branches with true/false conditions
    to obfuscate code and complicate analysis
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name_gen_settings = self.config.get('name_gen', 'english')
        self.junk_density = self.config.get('junk_density', 0.5)
        self.opaque_complexity = self.config.get('opaque_complexity', 'high')

    def process(self, project_path: Path, output_path: Path) -> bool:
        """
        Process the project by adding junk code to all Python files

        Args:
            project_path: Path to the original project
            output_path: Path to the output directory

        Returns:
            True if processing was successful, False otherwise
        """
        try:
            print("Applying junk code transformation to all Python files...")

            # Create an instance of the junk code transformer
            transformer = JunkCodeTransformer(
                name_gen_settings=self.name_gen_settings,
                junk_density=self.junk_density,
                opaque_complexity=self.opaque_complexity
            )

            # Find all Python files in the output directory
            for py_file in output_path.rglob("*.py"):
                # Skip special files
                if py_file.name not in ["obfuscator.py", "junk_code_transformer.py", "antidebug_llvm.py"]:
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            original_code = f.read()

                        # Apply junk code transformation
                        transformed_code = transformer.apply_transformation(original_code)

                        # Only write if changes were made
                        if transformed_code != original_code:
                            with open(py_file, 'w', encoding='utf-8') as f:
                                f.write(transformed_code)
                            print(f"Applied junk code transformation to {py_file}")

                    except Exception as e:
                        print(f"Error applying junk code transformation to {py_file}: {e}")

            return True
        except Exception as e:
            print(f"Error during junk code transformation: {e}")
            return False

    def validate_config(self) -> bool:
        """
        Validate the module's configuration

        Returns:
            True if configuration is valid, False otherwise
        """
        # Validate junk_density is between 0 and 1
        if 'junk_density' in self.config:
            density = self.config['junk_density']
            if not isinstance(density, (int, float)) or density < 0 or density > 1:
                print(f"Invalid junk_density: {density}. Must be between 0 and 1")
                return False
        return True
