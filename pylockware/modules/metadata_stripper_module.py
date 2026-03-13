"""
Metadata Stripping Module for PyLockWare
Removes __doc__, __annotations__, type hints
"""
from pathlib import Path
from typing import Dict, Any
from pylockware.core.module_base import ModuleBase
from pylockware.transforms.metadata_stripper import MetadataStripper


class MetadataStripperModule(ModuleBase):
    """
    Module that strips metadata from Python code:
    - Docstrings (__doc__)
    - Type annotations
    - __annotations__ assignments
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)

    def process(self, project_path: Path, output_path: Path) -> bool:
        """
        Process the project by stripping metadata

        Args:
            project_path: Path to the original project
            output_path: Path to the output directory

        Returns:
            True if processing was successful, False otherwise
        """
        try:
            print("Stripping metadata from all Python files...")

            stripper = MetadataStripper()

            for py_file in output_path.rglob("*.py"):
                # Skip anti-debug modules and core files
                if py_file.name not in ["anti_debug_injector.py", "anti_debug_injector_normal.py", 
                                        "obfuscator.py", "metadata_stripper.py"]:
                    try:
                        stripper.reset()
                        with open(py_file, 'r', encoding='utf-8') as f:
                            original_code = f.read()

                        stripped_code = stripper.apply_stripping(original_code)

                        if stripped_code != original_code:
                            with open(py_file, 'w', encoding='utf-8') as f:
                                f.write(stripped_code)
                            print(f"Stripped {stripper.stripped_count} metadata items from {py_file}")

                    except Exception as e:
                        print(f"Error stripping metadata from {py_file}: {e}")

            return True
        except Exception as e:
            print(f"Error during metadata stripping: {e}")
            return False

    def validate_config(self) -> bool:
        """Validate configuration."""
        return True
