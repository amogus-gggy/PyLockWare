"""
Disable Traceback Module for PyLockWare
Adds sys.tracebacklimit = 0 to disable traceback output
"""
from pathlib import Path
from typing import Dict, Any
from pylockware.core.module_base import ModuleBase


class DisableTracebackModule(ModuleBase):
    """
    Module that adds sys.tracebacklimit = 0 to the beginning of Python files
    to disable traceback output
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)

    def process(self, project_path: Path, output_path: Path) -> bool:
        """
        Process the project by adding sys.tracebacklimit = 0 to all Python files

        Args:
            project_path: Path to the original project
            output_path: Path to the output directory

        Returns:
            True if processing was successful, False otherwise
        """
        try:
            print("Adding traceback disable to all Python files...")

            # Find all Python files in the output directory
            for py_file in output_path.rglob("*.py"):
                # Skip the obfuscator script itself and the antidebug engine
                if py_file.name not in ("obfuscator.py", "antidebug_llvm.py"):
                    try:
                        self._add_disable_traceback(py_file)
                    except Exception as e:
                        print(f"Error adding traceback disable to {py_file}: {e}")

            return True
        except Exception as e:
            print(f"Error during traceback disable: {e}")
            return False

    def _add_disable_traceback(self, module_path: Path):
        """
        Add sys.tracebacklimit = 0 at the start of a module
        """
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if tracebacklimit already exists
        if 'sys.tracebacklimit' in content[:500]:  # Check first 500 chars for efficiency
            return

        # Add import sys and tracebacklimit at the beginning, preserving any existing shebang or encoding declaration
        lines = content.split('\n')
        insert_position = 0

        # Skip shebang and encoding declarations
        for i, line in enumerate(lines):
            if line.startswith('#!') or line.startswith('# -*- coding:'):
                insert_position = i + 1
            else:
                break

        # Check if 'import sys' already exists at the beginning
        has_sys_import = any('import sys' in line for line in lines[:20])

        if has_sys_import:
            # Just add tracebacklimit after the sys import
            for i, line in enumerate(lines):
                if 'import sys' in line:
                    lines.insert(i + 1, 'sys.tracebacklimit = 0')
                    break
            new_content = '\n'.join(lines)
        else:
            # Add import sys and tracebacklimit
            prefix = 'import sys\nsys.tracebacklimit = 0\n\n'
            new_content = '\n'.join(lines[:insert_position]) + prefix + '\n'.join(lines[insert_position:])

        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        print(f"Added traceback disable to: {module_path}")

    def validate_config(self) -> bool:
        """
        Validate the module's configuration

        Returns:
            True if configuration is valid, False otherwise
        """
        # Disable traceback module doesn't have specific validation requirements
        return True
