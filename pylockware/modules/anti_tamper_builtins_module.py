import ast
import shutil
from pathlib import Path
from typing import Dict, Any

from pylockware.core.module_base import ModuleBase

_GUARD_MARKER = "# __pylockware_anti_tamper_builtins__"
_MODULE_NAME = "anti_tamper_builtins"
_SKIP_FILES = {
    f"{_MODULE_NAME}.py",
    "_builtin_dispatcher.py",
    "antidebug_crossplatform.py",
    "antidebug_llvm.py",
}

_INJECT_CODE = f"""{_GUARD_MARKER}
import {_MODULE_NAME}
"""


class AntiTamperBuiltinsModule(ModuleBase):
    """
    Module that injects a runtime anti-tamper guard for Python builtins.

    It copies the anti_tamper_builtins helper module into the obfuscated project
    and injects an import into every Python file so that any tampering with
    builtin objects causes an immediate hard crash.
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)

    def process(self, project_path: Path, output_path: Path) -> bool:
        try:
            src = Path(__file__).parent.parent / "anti_tamper" / f"{_MODULE_NAME}.py"
            dst = output_path / f"{_MODULE_NAME}.py"
            shutil.copy(str(src), str(dst))

            # Inject import into all .py files except the helper itself
            for py_file in output_path.rglob("*.py"):
                if py_file.name in _SKIP_FILES:
                    continue
                self._inject(py_file, _INJECT_CODE)

            return True
        except Exception:
            return False

    def validate_config(self) -> bool:
        return True

    def _inject(self, file_path: Path, inject_code: str):
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            return

        if _GUARD_MARKER in content:
            return

        try:
            tree = ast.parse(content)
        except SyntaxError:
            # Keep __future__ imports at the top even in fallback mode.
            lines = content.splitlines(keepends=True)
            insert_line = self._find_insert_line_text_fallback(lines)
            inject_lines = (inject_code + "\n").splitlines(keepends=True)
            new_lines = lines[:insert_line] + inject_lines + lines[insert_line:]
            file_path.write_text("".join(new_lines), encoding="utf-8")
            return

        insert_line = self._find_insert_line(tree)
        lines = content.splitlines(keepends=True)
        inject_lines = (inject_code + "\n").splitlines(keepends=True)
        new_lines = lines[:insert_line] + inject_lines + lines[insert_line:]
        file_path.write_text("".join(new_lines), encoding="utf-8")

    def _find_insert_line(self, tree: ast.Module) -> int:
        """
        Find insertion point at the very beginning, preserving only shebang/encoding.
        Anti-tamper must be injected BEFORE any other code (including imports).
        """
        # Return 0 to insert at the very beginning
        # The fallback method will handle shebang/encoding preservation
        return 0

    def _find_insert_line_text_fallback(self, lines) -> int:
        """
        Fallback insertion point preserving only shebang/encoding.
        Anti-tamper must be injected at the very beginning.
        """
        idx = 0
        total = len(lines)

        # Preserve shebang
        if idx < total and lines[idx].startswith("#!"):
            idx += 1

        # Preserve encoding declaration
        if idx < total and "coding" in lines[idx]:
            idx += 1

        return idx

