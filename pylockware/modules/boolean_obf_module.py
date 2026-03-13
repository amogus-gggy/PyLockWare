"""
Boolean Expression Obfuscation Module for PyLockWare
Obfuscates True/False/bool operations with complex equivalent expressions
"""
from pathlib import Path
from typing import Dict, Any
from pylockware.core.module_base import ModuleBase
from pylockware.transforms.bool_obf import BooleanObfuscator


class BooleanObfModule(ModuleBase):
    """
    Module that obfuscates boolean expressions:
    - True/False literals → complex equivalent expressions
    - bool() calls → obfuscated versions
    - Logical operators (and, or, not) → equivalent complex forms
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name_gen_settings = self.config.get('name_gen', 'english')

    def process(self, project_path: Path, output_path: Path) -> bool:
        """
        Process the project by obfuscating boolean expressions

        Args:
            project_path: Path to the original project
            output_path: Path to the output directory

        Returns:
            True if processing was successful, False otherwise
        """
        try:
            print("Applying boolean obfuscation to all Python files...")

            obfuscator = BooleanObfuscator(name_gen_settings=self.name_gen_settings)

            for py_file in output_path.rglob("*.py"):
                # Skip anti-debug modules and core files
                if py_file.name not in ["anti_debug_injector.py", "anti_debug_injector_normal.py",
                                        "obfuscator.py", "bool_obf.py"]:
                    try:
                        obfuscator.reset()
                        with open(py_file, 'r', encoding='utf-8') as f:
                            original_code = f.read()

                        obfuscated_code = obfuscator.apply_obfuscation(original_code)

                        if obfuscated_code != original_code:
                            with open(py_file, 'w', encoding='utf-8') as f:
                                f.write(obfuscated_code)
                            print(f"Obfuscated {obfuscator.obf_count} boolean expressions in {py_file}")

                    except Exception as e:
                        print(f"Error applying boolean obfuscation to {py_file}: {e}")

            return True
        except Exception as e:
            print(f"Error during boolean obfuscation: {e}")
            return False

    def validate_config(self) -> bool:
        """Validate configuration."""
        return True
