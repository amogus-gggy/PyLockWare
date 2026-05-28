"""
Number Obfuscation Module for PyLockWare
Obfuscates numbers by replacing them with arithmetic expressions
"""
import ast
from pathlib import Path
from typing import Dict, Any
from pylockware.core.module_base import ModuleBase
from pylockware.transforms.num_obf import NumberObfuscator


class NumberObfModule(ModuleBase):
    """
    Module that obfuscates numbers by replacing them with arithmetic expressions
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name_gen_settings = self.config.get('name_gen', 'english')
        
    def process(self, project_path: Path, output_path: Path) -> bool:
        """
        Process the project by obfuscating numbers
        
        Args:
            project_path: Path to the original project
            output_path: Path to the output directory
            
        Returns:
            True if processing was successful, False otherwise
        """
        try:
            print("Applying number obfuscation to all Python files...")

            # Create an instance of the number obfuscator with parallel processing enabled
            obfuscator = NumberObfuscator(use_parallel=True)

            # Find all Python files in the output directory
            for py_file in output_path.rglob("*.py"):
                # Skip anti-debug modules and the obfuscator script itself
                if py_file.name not in ["anti_debug_injector.py", "anti_debug_injector_normal.py", "obfuscator.py", "num_obf.py", "antidebug_llvm.py"]:
                    try:
                        with open(py_file, 'r', encoding='utf-8') as f:
                            original_code = f.read()

                        # Parse the code to AST
                        tree = ast.parse(original_code)

                        # Preprocess: collect and obfuscate all numbers in parallel
                        obfuscator.preprocess_numbers(tree)

                        # Apply number obfuscation (using cached results)
                        obfuscated_tree = obfuscator.visit(tree)

                        # Fix missing locations
                        ast.fix_missing_locations(obfuscated_tree)

                        # Convert back to source code
                        obfuscated_code = ast.unparse(obfuscated_tree)

                        # Get required imports and inject them at the top
                        imports_to_add = obfuscator.get_required_imports()
                        if imports_to_add:
                            # Add imports at the beginning of the file
                            obfuscated_code = imports_to_add + '\n' + obfuscated_code

                        # Only write if changes were made
                        if obfuscated_code != original_code:
                            with open(py_file, 'w', encoding='utf-8') as f:
                                f.write(obfuscated_code)

                            # Count obfuscated numbers by counting parentheses (rough estimate)
                            obfuscated_count = obfuscated_code.count('(') - original_code.count('(')
                            print(f"Obfuscated numbers in {py_file} (est. {obfuscated_count} changes)")

                    except Exception as e:
                        print(f"Error applying number obfuscation to {py_file}: {e}")
                        
            return True
        except Exception as e:
            print(f"Error during number obfuscation: {e}")
            return False
    
    def validate_config(self) -> bool:
        """
        Validate the module's configuration
        
        Returns:
            True if configuration is valid, False otherwise
        """
        # Number obfuscation module doesn't have specific validation requirements
        return True