"""
String Protection Module for PyLockWare
Protects strings by encoding them with base64 and zlib
"""
from pathlib import Path
from typing import Dict, Any
from pylockware.core.module_base import ModuleBase
from pylockware.transforms.str_prot import StringProtectionTransformer


class StringProtectModule(ModuleBase):
    """
    Module that protects strings by encoding them with base64 and zlib
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name_gen_settings = self.config.get('name_gen', 'english')
        
    def process(self, project_path: Path, output_path: Path) -> bool:
        """
        Process the project by protecting strings
        
        Args:
            project_path: Path to the original project
            output_path: Path to the output directory
            
        Returns:
            True if processing was successful, False otherwise
        """
        try:
            print("Applying string protection to all Python files...")

            # Create an instance of the string protection transformer with name generator settings
            protector = StringProtectionTransformer(name_gen_settings=self.name_gen_settings)

            # Find all Python files in the output directory
            for py_file in output_path.rglob("*.py"):
                # Skip anti-debug modules and the obfuscator script itself
                if py_file.name not in ["anti_debug_injector.py", "anti_debug_injector_normal.py", "obfuscator.py", "str_prot.py"]:
                    try:
                        protector.reset()
                        with open(py_file, 'r', encoding='utf-8') as f:
                            original_code = f.read()

                        # Apply string protection
                        protected_code = protector.apply_protection(original_code)

                        # Only write if changes were made
                        if protected_code != original_code:
                            with open(py_file, 'w', encoding='utf-8') as f:
                                f.write(protected_code)

                        # Count protected strings by counting _protected_str_ occurrences
                        protected_count = protector.string_counter
                        print(f"Protected {protected_count} strings in {py_file}")

                    except Exception as e:
                        print(f"Error applying string protection to {py_file}: {e}")
                        
            return True
        except Exception as e:
            print(f"Error during string protection: {e}")
            return False
    
    def validate_config(self) -> bool:
        """
        Validate the module's configuration
        
        Returns:
            True if configuration is valid, False otherwise
        """
        # String protection module doesn't have specific validation requirements
        return True