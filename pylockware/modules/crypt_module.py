"""
PyLockWare Crypt Module
Wraps the CryptTransformer for integration with the obfuscator pipeline
"""

import ast
import os
from pathlib import Path
from typing import Dict, Any, List

from pylockware.core.module_base import ModuleBase
from pylockware.transforms.crypter import CryptTransformer, process_file


class CryptModule(ModuleBase):
    """
    Module that encrypts functions marked with @crypt decorator using machine fingerprinting.
    
    This module processes all Python files in the output directory and encrypts
    functions that have the @crypt decorator applied.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config or {})
        self.transformer = None

    def validate_config(self) -> bool:
        """Validate the module's configuration."""
        return True

    def process(self, project_path: Path, output_path: Path) -> bool:
        """
        Process all Python files in the output directory.
        
        Args:
            project_path: Path to the original project
            output_path: Path to the output directory
            
        Returns:
            True if all files processed successfully, False otherwise
        """
        self.transformer = CryptTransformer()
        
        success = True
        total_encrypted = 0

        for py_file in output_path.rglob("*.py"):
            if py_file.name == "obfuscator.py":
                continue
                
            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    source = f.read()

                tree = ast.parse(source)
                tree = self.transformer.visit(tree)
                ast.fix_missing_locations(tree)
                output = ast.unparse(tree)

                # Add header comment
                header = f"""# encrypted
# source: {os.path.basename(py_file)}
# functions: {self.transformer.encrypted_count}

"""
                with open(py_file, "w", encoding="utf-8") as f:
                    f.write(header + output)

                total_encrypted += self.transformer.encrypted_count
                self.transformer.encrypted_count = 0  # Reset for next file
            except Exception as e:
                print(f"Error processing {py_file}: {e}")
                success = False

        if total_encrypted > 0:
            print(f"[+] encrypted {total_encrypted} function(s)")

        return success