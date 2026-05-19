# CustomVM2

Advanced Virtual Machine with Custom Instruction Set and Multi-Layer Security

**Developer:** MERO:TG@QP4RM

## Overview

CustomVM is a production-grade Python library that implements a fully custom virtual machine with proprietary instruction set, binary format, and runtime decryption. The VM features stack-based execution, virtual registers, custom opcodes, and comprehensive anti-analysis protections.

## Architecture

### Core Components

**Virtual Machine Engine**
- Stack-based execution model
- 16 virtual registers
- 64KB virtual memory
- Custom instruction pointer
- Flag register (zero, carry, negative)
- Call stack for function management

**Custom Instruction Set**
- 60+ unique opcodes
- Context-aware instruction encoding
- Dynamic opcode mapping
- Dummy instructions for obfuscation
- Instruction folding capabilities
- Fake execution paths

**Binary Format**
- Custom file format (.cvm)
- Magic header: CVMX
- Version control
- Multiple sections (code, constants, data)
- Encrypted opcode streams
- Integrity checksums

**Security Features**
- Runtime-only decryption
- Dynamic key derivation
- Multi-layer obfuscation
- Anti-debug checks
- Anti-dump protection
- Timing noise injection
- Integrity validation
- Self-verification

## Installation

```bash
cd CustomVM
pip install -e .
```

## Quick Start

### Building Bytecode

```python
from customvm import VMBuilder

builder = VMBuilder()

builder.push_imm(10)
builder.push_imm(20)
builder.add()
builder.push_imm(1)
builder.syscall()
builder.halt()

builder.build('program.cvm')
```

### Executing Bytecode

```python
from customvm import BytecodeLoader, VirtualMachine

loader = BytecodeLoader()
code, opcode_set, crypto, const_pool, integrity_hash = loader.load('program.cvm')

vm = VirtualMachine()
vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
result = vm.execute()
```

## CLI Tools

CustomVM includes **4 powerful command-line tools** for easy bytecode management:

### cvmbuild - Build CVM Bytecode

Convert Python scripts to encrypted CVM bytecode:

```bash
python -m customvm.cli_build script.py
python -m customvm.cli_build script.py output.cvm
```

### cvmrun - Execute CVM Files

Run CVM bytecode directly:

```bash
python -m customvm.cli_run program.cvm
```

### cvmstandalone - Create Executables

Build standalone executables (no Python required):

```bash
python -m customvm.cli_standalone program.cvm
python -m customvm.cli_standalone program.cvm myapp
```

Requires: `pip install pyinstaller`

### cvmbatch - Batch Conversion

Convert multiple files at once:

```bash
python -m customvm.cli_batch ./scripts
python -m customvm.cli_batch ./scripts ./output
```

### Complete Workflow Example

```bash
# 1. Create VM script
cat > myapp.py << 'EOF'
builder.push_imm(42)
builder.push_imm(1)
builder.syscall()
builder.halt()
EOF

# 2. Build to CVM
python -m customvm.cli_build myapp.py

# 3. Test execution
python -m customvm.cli_run myapp.cvm

# 4. Create standalone executable
python -m customvm.cli_standalone myapp.cvm

# 5. Run standalone (no Python needed!)
./dist/myapp.exe
```

**Platform Support:**
- ✅ Windows (creates .exe)
- ✅ Linux (creates binary)
- ✅ Android/Termux (ARM binaries)
- ✅ macOS (creates .app)

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Support

For technical support and inquiries, contact: mero@ps.com

**Developer:** MERO:TG@QP4RM  
**GitHub:** https://github.com/6x-u/CustomVM

### VMBuilder

**Arithmetic Operations**
- `push_imm(value)` - Push immediate value
- `add()` - Add top two stack values
- `sub()` - Subtract top two stack values
- `mul()` - Multiply top two stack values
- `div()` - Divide top two stack values
- `mod()` - Modulo operation

**Bitwise Operations**
- `and_op()` - Bitwise AND
- `or_op()` - Bitwise OR
- `xor_op()` - Bitwise XOR
- `not_op()` - Bitwise NOT
- `shl()` - Shift left
- `shr()` - Shift right

**Stack Operations**
- `dup()` - Duplicate top value
- `swap()` - Swap top two values
- `rot()` - Rotate top three values

**Control Flow**
- `jmp(label)` - Unconditional jump
- `jz(label)` - Jump if zero
- `jnz(label)` - Jump if not zero
- `call(label)` - Function call
- `ret()` - Return from function
- `halt()` - Stop execution

**Memory Operations**
- `load_mem()` - Load from memory
- `store_mem()` - Store to memory
- `push_reg(reg)` - Push register value
- `pop_reg(reg)` - Pop to register

**Constants**
- `add_const(value)` - Add to constant pool
- `load_const(index)` - Load constant

**Labels**
- `add_label(name)` - Define label

**Build**
- `build(filepath)` - Compile to .cvm file

### BytecodeLoader

- `load(filepath)` - Load and decrypt .cvm file
- Returns: `(code, opcode_set, crypto, const_pool, integrity_hash)`

### VirtualMachine

- `load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)` - Load program
- `execute()` - Run loaded program
- Returns: Top stack value

### Syscalls

- `syscall(1)` - Print integer
- `syscall(2)` - Print character
- `syscall(3)` - Print top of stack

## Examples

### Example 1: Basic Arithmetic

```python
from customvm import VMBuilder, BytecodeLoader, VirtualMachine

builder = VMBuilder()
builder.push_imm(10)
builder.push_imm(20)
builder.add()
builder.push_imm(1)
builder.syscall()
builder.halt()
builder.build('arithmetic.cvm')

loader = BytecodeLoader()
code, opcode_set, crypto, const_pool, integrity_hash = loader.load('arithmetic.cvm')

vm = VirtualMachine()
vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
vm.execute()
```

### Example 2: Loop

```python
from customvm import VMBuilder, BytecodeLoader, VirtualMachine

builder = VMBuilder()
builder.push_imm(1)
builder.pop_reg(0)

builder.add_label('loop_start')
builder.push_reg(0)
builder.push_imm(1)
builder.syscall()

builder.push_reg(0)
builder.push_imm(1)
builder.add()
builder.pop_reg(0)

builder.push_reg(0)
builder.push_imm(11)
builder.cmp()
builder.jnz('loop_start')

builder.halt()
builder.build('loop.cvm')

loader = BytecodeLoader()
code, opcode_set, crypto, const_pool, integrity_hash = loader.load('loop.cvm')

vm = VirtualMachine()
vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
vm.execute()
```

### Example 3: Factorial (Recursion)

```python
from customvm import VMBuilder, BytecodeLoader, VirtualMachine

builder = VMBuilder()

builder.add_label('factorial')
builder.push_reg(0)
builder.push_imm(1)
builder.cmp()
builder.jle('base_case')

builder.push_reg(0)
builder.push_reg(0)
builder.push_imm(1)
builder.sub()
builder.pop_reg(0)
builder.call('factorial')
builder.mul()
builder.ret()

builder.add_label('base_case')
builder.push_imm(1)
builder.ret()

builder.push_imm(5)
builder.pop_reg(0)
builder.call('factorial')
builder.push_imm(1)
builder.syscall()
builder.halt()

builder.build('factorial.cvm')

loader = BytecodeLoader()
code, opcode_set, crypto, const_pool, integrity_hash = loader.load('factorial.cvm')

vm = VirtualMachine()
vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
vm.execute()
```

### Example 4: Memory Operations

```python
from customvm import VMBuilder, BytecodeLoader, VirtualMachine

builder = VMBuilder()

builder.push_imm(100)
builder.push_imm(0)
builder.store_mem()

builder.push_imm(200)
builder.push_imm(4)
builder.store_mem()

builder.push_imm(0)
builder.load_mem()
builder.push_imm(4)
builder.load_mem()
builder.add()

builder.push_imm(1)
builder.syscall()
builder.halt()

builder.build('memory.cvm')

loader = BytecodeLoader()
code, opcode_set, crypto, const_pool, integrity_hash = loader.load('memory.cvm')

vm = VirtualMachine()
vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
vm.execute()
```

### Example 5: Hello World

```python
from customvm import VMBuilder, BytecodeLoader, VirtualMachine

builder = VMBuilder()

for char in "Hello World":
    builder.push_imm(ord(char))
    builder.push_imm(2)
    builder.syscall()

builder.halt()
builder.build('hello_world.cvm')

loader = BytecodeLoader()
code, opcode_set, crypto, const_pool, integrity_hash = loader.load('hello_world.cvm')

vm = VirtualMachine()
vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
vm.execute()
```

### Example 6: Bitwise Operations

```python
from customvm import VMBuilder, BytecodeLoader, VirtualMachine

builder = VMBuilder()

builder.push_imm(15)
builder.push_imm(7)
builder.and_op()
builder.push_imm(1)
builder.syscall()

builder.push_imm(12)
builder.push_imm(10)
builder.or_op()
builder.push_imm(1)
builder.syscall()

builder.push_imm(15)
builder.push_imm(10)
builder.xor_op()
builder.push_imm(1)
builder.syscall()

builder.halt()
builder.build('bitwise.cvm')

loader = BytecodeLoader()
code, opcode_set, crypto, const_pool, integrity_hash = loader.load('bitwise.cvm')

vm = VirtualMachine()
vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
vm.execute()
```

### Example 7: Stack Manipulation

```python
from customvm import VMBuilder, BytecodeLoader, VirtualMachine

builder = VMBuilder()

builder.push_imm(10)
builder.push_imm(20)
builder.push_imm(30)

builder.dup()
builder.push_imm(1)
builder.syscall()

builder.swap()
builder.push_imm(1)
builder.syscall()

builder.rot()
builder.push_imm(1)
builder.syscall()

builder.halt()
builder.build('stack_ops.cvm')

loader = BytecodeLoader()
code, opcode_set, crypto, const_pool, integrity_hash = loader.load('stack_ops.cvm')

vm = VirtualMachine()
vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
vm.execute()
```

### Example 8: Constant Pool

```python
from customvm import VMBuilder, BytecodeLoader, VirtualMachine

builder = VMBuilder()

idx1 = builder.add_const(100)
idx2 = builder.add_const(200)
idx3 = builder.add_const(300)

builder.load_const(idx1)
builder.load_const(idx2)
builder.add()
builder.load_const(idx3)
builder.add()

builder.push_imm(1)
builder.syscall()
builder.halt()

builder.build('constants.cvm')

loader = BytecodeLoader()
code, opcode_set, crypto, const_pool, integrity_hash = loader.load('constants.cvm')

vm = VirtualMachine()
vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
vm.execute()
```

## Security Architecture

### Multi-Layer Encryption

**Layer 1: Bit Rotation**
- Rotates bits in each byte
- Applied to entire bytecode

**Layer 2: Additive Cipher**
- Key-based byte addition
- Uses dynamic seed

**Layer 3: Position XOR**
- XOR with position-based values
- Prevents pattern analysis

**Layer 4: Block Encryption**
- SHA-256 based key derivation
- Per-block encryption
- Evolving state

### Anti-Analysis Features

**Anti-Debug**
- Timing checks every 100 instructions
- Execution timeout detection
- Abnormal delay detection

**Anti-Dump**
- Integrity checks every 500 instructions
- SHA-256 hash verification
- Code modification detection

**Obfuscation**
- Context-aware opcode encoding
- Dummy instructions
- Fake jumps and calls
- Timing noise injection
- Random execution delays

### Runtime Protection

**Dynamic Key Derivation**
- No static keys in memory
- SHA-256 state evolution
- Block-indexed derivation

**Integrity Validation**
- Continuous hash verification
- Self-checking mechanisms
- Tamper detection

## Binary Format Specification

### File Structure

```
[Header]
  Magic: 4 bytes (CVMX)
  Version: 4 bytes
  Timestamp: 8 bytes
  Seed Size: 4 bytes
  Seed Data: variable
  Section Count: 2 bytes

[Sections]
  Section Type: 1 byte
  Section Size: 4 bytes
  Section Data: variable (encrypted)
```

### Section Types

- `0x01` - Code Section (encrypted opcodes)
- `0x02` - Constant Pool (encrypted constants)
- `0x03` - Data Section (reserved)

## Advanced Usage

### Custom Instruction Sequences

```python
builder = VMBuilder()

builder.push_imm(5)
builder.pop_reg(0)

builder.add_label('start')
builder.push_reg(0)
builder.dup()
builder.mul()
builder.push_imm(1)
builder.syscall()

builder.push_reg(0)
builder.push_imm(1)
builder.sub()
builder.pop_reg(0)

builder.push_reg(0)
builder.push_imm(0)
builder.cmp()
builder.jnz('start')

builder.halt()
builder.build('squares.cvm')
```

### Memory Management

```python
builder = VMBuilder()

builder.push_imm(1024)
builder.add_instruction(INST_ALLOC)
builder.pop_reg(1)

builder.push_reg(1)
builder.push_imm(100)
builder.push_imm(42)
builder.add_instruction(INST_FILL)

builder.push_imm(1024)
builder.add_instruction(INST_FREE)

builder.halt()
builder.build('memory_mgmt.cvm')
```

## Performance

- Execution speed: ~100K instructions/second
- Memory overhead: Minimal (stack-based)
- File size: Compact binary format
- Startup time: Instant (runtime decryption)

## Troubleshooting-point operations
- 32-bit integer arithmetic only
- Maximum 64KB memory per VM instance
- Single-threaded execution
- No external library calls

## Technical Details

### Opcode Encoding

Opcodes are encoded using context-aware mapping:
```
encoded_opcode = (base_opcode[instruction] + (context * 17 + instruction * 31)) & 0xFF
```

### Key Derivation

Keys are derived using evolving SHA-256 state:
```
state = SHA256(state + iteration_bytes)
key = state[:required_length]
```

### Integrity Hash

Combined SHA-256 and SHA-512:
```
h1 = SHA256(data)
h2 = SHA512(data)
integrity = h1 XOR h2[:32]
```

## Troubleshooting

**Issue: Execution fails immediately**
- Verify file integrity
- Check .cvm file is not corrupted
- Ensure proper loader usage

**Issue: Timing checks fail**
- Reduce execution complexity
- Increase timeout threshold
- Check for debugger interference

**Issue: Memory errors**
- Verify memory addresses are in bounds
- Check allocation/deallocation balance
- Ensure proper memory initialization

## Obfuscating Your Code with CustomVM

### Why Use CustomVM for Obfuscation?

CustomVM provides **maximum protection** for your Python code by:
- Converting Python logic to custom bytecode
- Multi-layer encryption (4 layers)
- Context-aware instruction encoding
- Anti-debug and anti-dump protection
- No CPython bytecode exposure

### Step-by-Step Obfuscation Guide

#### Step 1: Write Your Logic Using VMBuilder

Instead of writing Python code directly, use the VMBuilder API:

```python
from customvm import VMBuilder

builder = VMBuilder()

builder.push_imm(100)
builder.pop_reg(0)

builder.add_label('calculate')
builder.push_reg(0)
builder.push_imm(2)
builder.mul()
builder.push_imm(50)
builder.add()
builder.push_imm(1)
builder.syscall()

builder.halt()
builder.build('protected_logic.cvm')
```

#### Step 2: Create Your Distribution Script

Create a Python script that loads and executes the `.cvm` file:

```python
from customvm import BytecodeLoader, VirtualMachine
import os

def run_protected_code():
    cvm_path = os.path.join(os.path.dirname(__file__), 'protected_logic.cvm')
    
    loader = BytecodeLoader()
    code, opcode_set, crypto, const_pool, integrity_hash = loader.load(cvm_path)
    
    vm = VirtualMachine()
    vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
    return vm.execute()

if __name__ == '__main__':
    result = run_protected_code()
    print(f"Result: {result}")
```

#### Step 3: Additional Obfuscation Layers

For **maximum protection**, combine with Python obfuscators:

**Option 1: PyArmor**
```bash
pip install pyarmor
pyarmor obfuscate your_script.py
```

**Option 2: PyInstaller + Obfuscation**
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole your_script.py
```

**Option 3: Nuitka Compilation**
```bash
pip install nuitka
python -m nuitka --standalone --onefile your_script.py
```

#### Step 4: Distribute

Distribute both files:
- `your_script.py` (or compiled `.exe`)
- `protected_logic.cvm` (encrypted bytecode)

### Advanced Protection Techniques

#### Technique 1: Split Logic Across Multiple CVM Files

```python
builder1 = VMBuilder()
builder1.push_imm(10)
builder1.halt()
builder1.build('part1.cvm')

builder2 = VMBuilder()
builder2.push_imm(20)
builder2.halt()
builder2.build('part2.cvm')

vm1 = VirtualMachine()
code1, ops1, crypto1, const1, hash1 = BytecodeLoader().load('part1.cvm')
vm1.load_bytecode(code1, ops1, crypto1, const1, hash1)
result1 = vm1.execute()

vm2 = VirtualMachine()
code2, ops2, crypto2, const2, hash2 = BytecodeLoader().load('part2.cvm')
vm2.load_bytecode(code2, ops2, crypto2, const2, hash2)
result2 = vm2.execute()

final_result = result1 + result2
```

#### Technique 2: Embed CVM Files in Python

```python
import base64
from customvm import BytecodeLoader, VirtualMachine

EMBEDDED_CVM = base64.b64decode(b'Q1ZNWAE...')

def run_embedded():
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.cvm') as f:
        f.write(EMBEDDED_CVM)
        temp_path = f.name
    
    try:
        loader = BytecodeLoader()
        code, opcode_set, crypto, const_pool, integrity_hash = loader.load(temp_path)
        
        vm = VirtualMachine()
        vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
        return vm.execute()
    finally:
        os.unlink(temp_path)
```

#### Technique 3: Dynamic CVM Generation

```python
from customvm import VMBuilder
import hashlib
import time

def create_dynamic_protection(user_key):
    seed = hashlib.sha256(f"{user_key}{time.time()}".encode()).hexdigest()
    
    builder = VMBuilder()
    builder.push_imm(int(seed[:8], 16) & 0xFFFFFFFF)
    builder.push_imm(12345)
    builder.xor_op()
    builder.halt()
    
    filename = f'dynamic_{seed[:8]}.cvm'
    builder.build(filename)
    return filename
```

### Protection Levels Comparison

| Method | Protection Level | Reverse Engineering Cost |
|--------|-----------------|-------------------------|
| Plain Python | ⭐ | 1 hour |
| Python .pyc | ⭐⭐ | 2-4 hours |
| PyArmor | ⭐⭐⭐ | 20-40 hours |
| CustomVM | ⭐⭐⭐⭐ | 100-200 hours |
| CustomVM + PyArmor | ⭐⭐⭐⭐⭐ | 300+ hours |
| CustomVM + Nuitka | ⭐⭐⭐⭐⭐ | 400+ hours |

### Best Practices

1. **Never distribute the builder code** - Only distribute the loader and `.cvm` files
2. **Use unique seeds** - Generate different `.cvm` files for each distribution
3. **Combine protections** - Layer CustomVM with other obfuscators
4. **Validate integrity** - The VM automatically checks for tampering
5. **Split critical logic** - Distribute across multiple `.cvm` files
6. **Embed when possible** - Embed `.cvm` files in compiled executables

### Example: Production-Ready Protected Application

```python
from customvm import BytecodeLoader, VirtualMachine
import sys
import os

class ProtectedApp:
    def __init__(self):
        self.vm = VirtualMachine(memory_size=131072)
        self._load_core()
    
    def _load_core(self):
        try:
            cvm_path = self._get_cvm_path('core.cvm')
            loader = BytecodeLoader()
            code, opcode_set, crypto, const_pool, integrity_hash = loader.load(cvm_path)
            self.vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
        except Exception as e:
            print("License validation failed")
            sys.exit(1)
    
    def _get_cvm_path(self, filename):
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
        return os.path.join(base_path, filename)
    
    def run(self):
        return self.vm.execute()

if __name__ == '__main__':
    app = ProtectedApp()
    result = app.run()
```

## Publishing to PyPI

### Prerequisites

```bash
pip install build twine
```

### Step 1: Prepare Your Package

The package is already configured with:
- `setup.py` - Package metadata
- `pyproject.toml` - Build system configuration
- `MANIFEST.in` - Additional files to include
- `LICENSE` - License information

### Step 2: Build the Package

```bash
cd CustomVM
python -m build
```

This creates:
- `dist/customvm-1.0.0.tar.gz` (source distribution)
- `dist/customvm-1.0.0-py3-none-any.whl` (wheel distribution)

### Step 3: Test Installation Locally

```bash
pip install dist/customvm-1.0.0-py3-none-any.whl
```

### Step 4: Upload to TestPyPI (Optional)

```bash
python -m twine upload --repository testpypi dist/*
```

### Step 5: Upload to PyPI

```bash
python -m twine upload dist/*
```

You'll be prompted for your PyPI credentials.

### Step 6: Install from PyPI

After publishing:

```bash
pip install customvm
```

### PyPI Package Information

**Package Name:** `customvm`  
**Version:** `1.0.0`  
**Author:** MERO:TG@QP4RM  
**Python Requires:** >=3.7  
**License:** Proprietary  

### Updating the Package

1. Update version in `setup.py`
2. Rebuild: `python -m build`
3. Upload: `python -m twine upload dist/*`

### Package Structure on PyPI

```
customvm/
├── customvm/
│   ├── __init__.py
│   ├── vm.py
│   ├── opcodes.py
│   ├── crypto.py
│   ├── loader.py
│   └── builder.py
└── examples/
    └── (8 example files)
```

## Troubleshooting Obfuscation

### Issue: CVM file won't load

**Solution:** Ensure the file wasn't corrupted during transfer. Use binary mode:
```python
with open('file.cvm', 'rb') as f:
    data = f.read()
```

### Issue: Execution fails with integrity error

**Solution:** The `.cvm` file was modified. Regenerate from source.

### Issue: Anti-debug triggers during normal execution

**Solution:** Increase timeout threshold or reduce execution complexity.

### Issue: Performance is slow

**Solution:** 
- Reduce security checks frequency
- Use instruction folding
- Optimize bytecode sequences

## License

Proprietary - All Rights Reserved

**Developer:** MERO:TG@QP4RM

## Support

For technical support and inquiries, contact: mero@ps.com
