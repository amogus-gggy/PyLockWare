"""
Call Obfuscation Module for PyLockWare
Obfuscates calls and attribute access via chained lookup tables (_call / _resolve).
"""
import ast
import io
from pathlib import Path
from typing import Any, Dict

from pylockware.core.module_base import ModuleBase
from pylockware.transforms.call_obf_v2 import obfuscate_source

_SKIP_FILENAMES = frozenset({"call_obf_v2.py", "call_obf_module.py"})


class CallObfModule(ModuleBase):
    """Obfuscate function/method calls and dynamic attribute access per file."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.junk_entries = int(self.config.get("junk_entries", 100))
        self.stats = {
            "files_processed": 0,
            "files_modified": 0,
            "total_calls_obfuscated": 0,
            "errors": [],
        }

    def process(self, project_path: Path, output_path: Path) -> bool:
        try:
            print(f"[CallObf] Starting chained-table call obfuscation in: {output_path}")
            py_files = list(output_path.rglob("*.py"))
            print(f"[CallObf] Found {len(py_files)} Python files")

            for py_file in py_files:
                if py_file.name in _SKIP_FILENAMES:
                    continue
                try:
                    with io.open(py_file, "r", encoding="utf-8-sig", newline="") as f:
                        original_code = f.read()

                    if "_resolve(" in original_code and "def _resolve(key):" in original_code:
                        print(f"[CallObf]   Skipping (already obfuscated): {py_file}")
                        self.stats["files_processed"] += 1
                        continue

                    try:
                        ast.parse(original_code)
                    except SyntaxError as e:
                        print(f"[CallObf]   ERROR: Syntax error in {py_file}: {e}")
                        self.stats["errors"].append(f"{py_file}: syntax error - {e}")
                        continue

                    obfuscated_code = self.obfuscate_calls(original_code, str(py_file))

                    '''try:
                        ast.parse(obfuscated_code)
                        print(obfuscated_code)
                    except SyntaxError as e:
                        print(f"[CallObf]   ERROR: Obfuscation broke syntax in {py_file}: {e}")
                        self.stats["errors"].append(f"{py_file}: invalid output - {e}")
                        continue'''

                    if obfuscated_code != original_code:
                        with io.open(py_file, "w", encoding="utf-8", newline="") as f:
                            f.write(obfuscated_code)
                        call_count = obfuscated_code.count("_call(")
                        print(f"[CallObf]   Written: {py_file} ({call_count} _call sites)")
                        self.stats["files_modified"] += 1
                        self.stats["total_calls_obfuscated"] += call_count

                    self.stats["files_processed"] += 1

                except Exception as e:
                    print(f"[CallObf]   ERROR: {py_file}: {type(e).__name__}: {e}")
                    self.stats["errors"].append(f"{py_file}: {type(e).__name__} - {e}")

            print(f"\n[CallObf] SUMMARY:")
            print(f"[CallObf]   Files processed: {self.stats['files_processed']}")
            print(f"[CallObf]   Files modified: {self.stats['files_modified']}")
            print(f"[CallObf]   Total _call sites: {self.stats['total_calls_obfuscated']}")
            print(f"[CallObf]   Errors: {len(self.stats['errors'])}")
            for err in self.stats["errors"][:5]:
                print(f"[CallObf]     - {err}")

            return True
        except Exception as e:
            print(f"[CallObf] FATAL ERROR: {e}")
            return False

    def validate_config(self) -> bool:
        return True

    def obfuscate_calls(self, code: str, filename: str = "unknown") -> str:
        try:
            return obfuscate_source(code, junk_entries=self.junk_entries)
        except Exception as e:
            print(f"[CallObf]   ERROR in obfuscate_calls for {filename}: {e}")
            return code
