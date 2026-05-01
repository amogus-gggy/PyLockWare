import ast
import shutil
from pathlib import Path
from typing import Dict, Any
from pylockware.core.module_base import ModuleBase

# Protection module names for different modes
_PROTECTION_MODULE_LLVM = "antidebug_llvm"
_PROTECTION_MODULE_CROSSPLATFORM = "antidebug_crossplatform"
_GUARD_MARKER = "# __pylockware_antidebug__"

# Default: native mode (Windows AMD64 only)
_INJECT_CODE_NATIVE = f"""{_GUARD_MARKER}
try:
    import {_PROTECTION_MODULE_LLVM} as _ad
    _ad.guard()
    _ad.monitor(interval_ms=500)
except Exception:
    import os; os._exit(1)
"""

# Cross-platform mode
_INJECT_CODE_CROSSPLATFORM = f"""{_GUARD_MARKER}
try:
    import {_PROTECTION_MODULE_CROSSPLATFORM} as _ad
    _ad.guard()
    _ad.monitor(interval_ms=500)
except Exception:
    import os; os._exit(1)
"""


class AntiDebugModule(ModuleBase):

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        # Get the anti_debug mode from config: 'native', 'crossplatform', or None
        self.mode = config.get('mode', 'native') if config else 'native'

    def process(self, project_path: Path, output_path: Path) -> bool:
        import platform, sys
        try:
            # Determine which mode to use
            is_windows_amd64 = sys.platform == 'win32' and platform.machine().lower() in ['amd64', 'x86_64']
            
            if self.mode == 'crossplatform' or not is_windows_amd64:
                # Use cross-platform mode
                src = Path(__file__).parent.parent / 'anti_debug' / 'antidebug_crossplatform.py'
                dst_name = f'{_PROTECTION_MODULE_CROSSPLATFORM}.py'
                inject_code = _INJECT_CODE_CROSSPLATFORM
                print(f"Anti-debug: using cross-platform mode")
            else:
                # Use native LLVM mode (Windows AMD64 only)
                src = Path(__file__).parent.parent / 'anti_debug' / 'antidebug_llvm.py'
                dst_name = f'{_PROTECTION_MODULE_LLVM}.py'
                inject_code = _INJECT_CODE_NATIVE
                print(f"Anti-debug: using native LLVM mode")

            # Copy the appropriate anti-debug module
            shutil.copy(str(src), str(output_path / dst_name))

            entry_point = self.config.get('entry_point')
            if entry_point:
                ep = output_path / entry_point
                if ep.exists():
                    self._inject(ep, inject_code, is_entry=True)

            for py_file in output_path.rglob("*.py"):
                if py_file.name == dst_name:
                    continue
                if entry_point and py_file == output_path / entry_point:
                    continue
                self._inject(py_file, inject_code, is_entry=False)

            return True
        except Exception as e:
            print(f"Anti-debug error: {e}")
            return False

    def validate_config(self) -> bool:
        return True

    def _inject(self, file_path: Path, inject_code: str, is_entry: bool):
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return

        if _GUARD_MARKER in content:
            return

        try:
            tree = ast.parse(content)
        except SyntaxError:
            file_path.write_text(inject_code + "\n" + content, encoding='utf-8')
            return

        insert_line = self._find_insert_line(tree, content)
        lines = content.splitlines(keepends=True)
        inject_lines = (inject_code + "\n").splitlines(keepends=True)
        new_lines = lines[:insert_line] + inject_lines + lines[insert_line:]
        file_path.write_text("".join(new_lines), encoding='utf-8')

    def _find_insert_line(self, tree: ast.Module, content: str) -> int:
        last_import_line = 0
        last_pyside_line = 0

        for node in ast.iter_child_nodes(tree):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            end = getattr(node, 'end_lineno', node.lineno)
            if end > last_import_line:
                last_import_line = end

            is_pyside = False
            if isinstance(node, ast.Import):
                is_pyside = any(a.name.startswith(('PySide', 'PyQt')) for a in node.names)
            elif isinstance(node, ast.ImportFrom):
                is_pyside = bool(node.module and node.module.startswith(('PySide', 'PyQt')))
            if is_pyside and end > last_pyside_line:
                last_pyside_line = end

        return (last_pyside_line or last_import_line)
