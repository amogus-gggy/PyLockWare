"""Debug MOD operation."""
import io
import os
import sys
import tempfile

sys.path.insert(0, r'C:\Users\fedor\Desktop\CustomVM')

from customvm import VMBuilder, BytecodeLoader, VirtualMachine
from customvm.compiler import PythonCompiler

# Test: 17 % 5 should be 2
source = """
x = 17
x %= 5
print(x)
"""

builder = VMBuilder()
compiler = PythonCompiler(builder)
compiler.compile(source)

with tempfile.NamedTemporaryFile(suffix='.cvm', delete=False) as tmp:
    tmp_path = tmp.name

try:
    builder.build(tmp_path)
    loader = BytecodeLoader()
    code, opcode_set, crypto, const_pool, integrity_hash, func_pool, string_pool = loader.load(tmp_path)
    
    print(f"Code size: {len(code)} bytes")
    print(f"Code hex: {code.hex()[:100]}...")
    print(f"Const pool: {const_pool}")
    print(f"Func pool count: {len(func_pool)}")
    
    vm = VirtualMachine()
    vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash, func_pool)
    
    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        result = vm.execute()
        print(f"VM returned: {result}")
    finally:
        sys.stdout = old_stdout
    
    print(f"Captured output: {captured.getvalue()!r}")
finally:
    os.unlink(tmp_path)
