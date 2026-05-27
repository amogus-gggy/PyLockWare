import ast
import shutil
from pathlib import Path
from typing import Dict, Any

from pylockware.core.module_base import ModuleBase

_GUARD_MARKER = "# __pylockware_anti_tamper_builtins__"
_MODULE_NAME = "anti_tamper_builtins"
_SKIP_FILES = {
    f"{_MODULE_NAME}.py",
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
        Find a good insertion point after shebang/encoding and initial imports.
        Mirrors the behavior of AntiDebugModule for consistency.
        """
        last_import_line = 0

        for node in ast.iter_child_nodes(tree):
            if not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            end = getattr(node, "end_lineno", node.lineno)
            if end > last_import_line:
                last_import_line = end

        # AST line numbers are 1-based, our splitlines index is 0-based
        return last_import_line

    def _find_insert_line_text_fallback(self, lines) -> int:
        """
        Fallback insertion point preserving shebang/encoding/__future__ imports.
        """
        idx = 0
        total = len(lines)

        if idx < total and lines[idx].startswith("#!"):
            idx += 1

        if idx < total and "coding" in lines[idx]:
            idx += 1

        # Skip leading comments/blank lines
        while idx < total and (not lines[idx].strip() or lines[idx].lstrip().startswith("#")):
            idx += 1

        # Skip module docstring if present
        if idx < total and lines[idx].lstrip().startswith(('"""', "'''")):
            quote = '"""' if '"""' in lines[idx] else "'''"
            if lines[idx].count(quote) >= 2:
                idx += 1
            else:
                idx += 1
                while idx < total and quote not in lines[idx]:
                    idx += 1
                if idx < total:
                    idx += 1

        # Keep all __future__ imports first
        while idx < total:
            stripped = lines[idx].strip()
            if stripped.startswith("from __future__ import"):
                idx += 1
                continue
            break

        return idx

