"""
Expression Virtualization Module for PyLockWare
Replaces expressions with VM-interpreted bytecode
"""
import ast
from pathlib import Path
from typing import Dict, Any
from pylockware.core.module_base import ModuleBase
from pylockware.transforms.expr_virtualize import virtualize_code, VM_RUNTIME_CODE


class ExprVirtualizeModule(ModuleBase):
    """
    Module that virtualizes expressions by compiling them to custom bytecode
    and replacing them with calls to a VM interpreter
    """

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)

    def process(self, project_path: Path, output_path: Path) -> bool:
        try:
            print("Applying expression virtualization to all Python files...")

            runtime_file = output_path / "_vmentry_rt.py"
            runtime_file.write_text(VM_RUNTIME_CODE, encoding='utf-8')

            for py_file in output_path.rglob("*.py"):
                if py_file.name in ["anti_debug_injector.py", "anti_debug_injector_normal.py",
                                    "obfuscator.py", "num_obf.py", "antidebug_llvm.py",
                                    "_vmentry_rt.py"]:
                    continue
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        original_code = f.read()

                    if '_vmentry' in original_code:
                        continue

                    virtualized_code = virtualize_code(original_code)

                    if virtualized_code != original_code:
                        final_code = "from _vmentry_rt import _vmentry\n" + virtualized_code
                        with open(py_file, 'w', encoding='utf-8') as f:
                            f.write(final_code)
                        print(f"Virtualized expressions in {py_file}")

                except Exception as e:
                    print(f"Error applying expression virtualization to {py_file}: {e}")

            return True
        except Exception as e:
            print(f"Error during expression virtualization: {e}")
            return False

    def validate_config(self) -> bool:
        return True
