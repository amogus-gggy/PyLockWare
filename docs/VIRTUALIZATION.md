# CustomVM Virtualization

## Overview

CustomVM Virtualization is the most powerful protection feature in PyLockWare. It converts Python functions into encrypted custom virtual machine bytecode, providing **extreme protection** against reverse engineering.

## Key Features

- **Custom Instruction Set**: Unique opcodes generated for each build
- **Multi-Layer Encryption**: 4 layers of obfuscation (bit rotation, additive cipher, XOR, block encryption)
- **Runtime-Only Decryption**: Code is never visible in memory unencrypted
- **Anti-Debug Protection**: Built-in timing checks and integrity validation
- **Unique Per Build**: Each build generates different VM with different opcodes
- **No CPython Bytecode**: Original Python bytecode is completely eliminated

## Quick Start

### 1. Install PyLockWare with CustomVM

```bash
pip install -e .
```

CustomVM is included in the `CustomVM/` directory.

### 2. Mark Functions for Virtualization

```python
from pylockware import virtualize

@virtualize
def calculate_license_key(user_id: int, product_code: int) -> int:
    """This function will be converted to CVM bytecode"""
    secret = 0x1337BEEF
    result = ((user_id ^ product_code) * 31337) ^ secret
    return result % 1000000
```

### 3. Enable Virtualization in Build

**Option A: Using pyproject.toml**

```toml
[tool.pylockware]
entry_point = "main.py"
virtualization = true
```

**Option B: Using SDK**

```python
from pylockware import Builder, BuildConfig

config = BuildConfig(
    entry_point="main.py",
    virtualization=True
)
builder = Builder(config)
builder.build()
```

**Option C: Using CLI**

```bash
python cli.py . --entry-point main.py --virtualization
```

### 4. Build and Run

```bash
pylockware build
cd dist
python main.py
```

## How It Works

### Compilation Phase

1. PyLockWare scans for `@virtualize` decorated functions
2. Extracts function AST and converts to CustomVM bytecode
3. Generates unique `.cvm` file with encrypted bytecode
4. Creates unique VM runtime for this build

### Build Phase

Original function:
```python
@virtualize
def secret(x):
    return x * 2 + 10
```

Becomes:
```python
def secret(x):
    return vmentry('secret_abc123.cvm', x)
```

### Runtime Phase

1. `vmentry()` loads the `.cvm` file
2. VM decrypts bytecode using build-specific keys
3. Executes in custom VM with unique opcodes
4. Returns result to Python

## Output Structure

```
dist/
├── main.py                          # Your obfuscated code
└── __vm_assets__/                   # VM runtime (auto-generated)
    ├── __init__.py
    ├── _vm_runtime.py               # VM loader
    ├── function1_abc123.cvm         # Encrypted bytecode
    └── function2_def456.cvm         # Encrypted bytecode
```

## Supported Python Constructs

### ✅ Supported

- **Arithmetic**: `+`, `-`, `*`, `/`, `//`, `%`
- **Bitwise**: `&`, `|`, `^`, `~`, `<<`, `>>`
- **Comparison**: `==`, `!=`, `<`, `>`, `<=`, `>=`
- **Boolean**: `and`, `or`, `not`
- **Control Flow**: `if`/`elif`/`else`, `while`, `for` (with `range()`)
- **Loop Control**: `break`, `continue`
- **Data Types**: `int`, `str`, `bool`
- **Variables**: Local variables and assignments
- **Function Calls**: Limited support for builtins and user functions

### ❌ Not Supported

- External imports inside virtualized functions
- Complex data structures (`list`, `dict`, `set`, `tuple`)
- Classes and objects
- Generators and `yield`
- `async`/`await`
- Exception handling (`try`/`except`)
- Context managers (`with`)
- Decorators inside virtualized functions
- Global variables (use parameters instead)

## Best Practices

### ✅ DO

```python
@virtualize
def validate_license(user_id: int, key: int) -> bool:
    """Good: Self-contained, uses only supported constructs"""
    expected = (user_id * 31337) ^ 0xDEADBEEF
    return expected == key

@virtualize
def calculate_hash(data: int) -> int:
    """Good: Pure computation"""
    result = data
    for i in range(10):
        result = (result * 31 + i) & 0xFFFFFFFF
    return result
```

### ❌ DON'T

```python
import hashlib  # ❌ Don't import inside module with virtualized functions

@virtualize
def bad_example(data: str) -> str:
    # ❌ Don't use external libraries
    return hashlib.sha256(data.encode()).hexdigest()

@virtualize
def another_bad_example(items: list) -> int:
    # ❌ Don't use complex data structures
    return sum(items)
```

## Performance Considerations

| Aspect | Impact |
|--------|--------|
| **Compilation Time** | +2-5 seconds per function |
| **Runtime Speed** | 10-50x slower than native Python |
| **Memory Usage** | +1-2 MB per virtualized function |
| **File Size** | +50-200 KB per virtualized function |

**Recommendation**: Virtualize only 5-10% of your code (critical functions only).

### What to Virtualize

✅ **High Priority**:
- License validation
- Authentication checks
- Encryption/decryption algorithms
- Anti-cheat logic
- Critical business rules

❌ **Low Priority**:
- I/O operations
- UI rendering
- Data processing loops
- Utility functions
- Logging

## Security Analysis

### Protection Levels

| Method | Reverse Engineering Time |
|--------|-------------------------|
| Plain Python | 1 hour |
| Python .pyc | 2-4 hours |
| PyLockWare Obfuscation | 50-100 hours |
| **PyLockWare + CustomVM** | **500+ hours** |

### What Attackers See

**Without Virtualization**:
```python
def validate_license(user_id, key):
    _a = user_id * 31337
    _b = _a ^ 3735928559
    return _b == key
```

**With Virtualization**:
```python
def validate_license(user_id, key):
    return vmentry('validate_license_a1b2c3.cvm', user_id, key)
```

The `.cvm` file contains:
- Encrypted bytecode (4 layers)
- Context-aware opcodes (unique per build)
- Integrity checksums
- Anti-debug checks

## Advanced Configuration

### Combining with Other Protections

```toml
[tool.pylockware]
# Maximum protection
virtualization = true
string_prot = true
state_machine = true
junk_code = true
builtin_dispatcher = true
disable_traceback = true

junk_density = 0.7
opaque_complexity = "high"
name_gen = "hex"
```

### Selective Virtualization

```python
from pylockware import virtualize, skip_obf, external

@virtualize  # Maximum protection
def critical_algorithm():
    pass

@external  # Obfuscated but not virtualized
def public_api():
    pass

@skip_obf  # No protection (for debugging)
def debug_helper():
    pass
```

## Troubleshooting

### Function Fails to Compile

**Error**: `NotImplementedError: Python construct not supported`

**Solution**: Check if your function uses only supported constructs. Simplify the function or split it into multiple functions.

### Runtime Error in vmentry

**Error**: `FileNotFoundError: VM bytecode not found`

**Solution**: Ensure `__vm_assets__/` directory is included in your distribution.

### Performance Issues

**Problem**: Application is too slow

**Solution**: 
1. Virtualize fewer functions (only critical ones)
2. Profile to identify bottlenecks
3. Consider using regular obfuscation for non-critical code

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'customvm'`

**Solution**: Ensure CustomVM is accessible. Check that `CustomVM/` directory is in the correct location.

## Examples

See `examples/example_virtualization/` for a complete working example with:
- License key generation (virtualized)
- License validation (virtualized)
- Public API (obfuscated but not virtualized)
- Debug helpers (not obfuscated)

## Technical Details

### VM Architecture

- **Stack-based execution model**
- **16 virtual registers**
- **64KB virtual memory**
- **Custom instruction pointer**
- **Flag register** (zero, carry, negative)
- **Call stack** for function management

### Encryption Layers

1. **Bit Rotation**: Rotates bits in each byte
2. **Additive Cipher**: Key-based byte addition
3. **Position XOR**: XOR with position-based values
4. **Block Encryption**: SHA-256 based key derivation

### Anti-Analysis Features

- **Timing checks** every 100 instructions
- **Integrity validation** every 500 instructions
- **Dummy instructions** for obfuscation
- **Fake execution paths**
- **Random execution delays**

## Limitations

1. **Python Version**: Requires Python 3.7+
2. **Platform**: Works on Windows, Linux, macOS
3. **Performance**: Not suitable for performance-critical code
4. **Debugging**: Difficult to debug virtualized functions
5. **Dependencies**: CustomVM must be accessible at runtime

## FAQ

**Q: Can I virtualize all my code?**
A: Technically yes, but not recommended. Virtualize only critical functions (5-10% of code) due to performance overhead.

**Q: Is the VM source code included?**
A: Yes, CustomVM source is in `CustomVM/` directory. However, each build generates unique opcodes.

**Q: Can virtualized functions call regular Python functions?**
A: Limited support. Best to keep virtualized functions self-contained.

**Q: How do I distribute the protected code?**
A: Include both `dist/` directory contents and `__vm_assets__/` directory.

**Q: Can I use this with Nuitka?**
A: Yes, but ensure CustomVM is properly packaged with the executable.

**Q: Is this compatible with PyInstaller?**
A: Yes, include `__vm_assets__/` in the bundle.

## Learn More

- [CustomVM Documentation](../CustomVM/README.md)
- [Example Project](../examples/example_virtualization/)
- [PyLockWare SDK Guide](../README.md)

## Support

For issues related to virtualization:
1. Check if your function uses only supported constructs
2. Review the example project
3. Check CustomVM documentation
4. Open an issue on GitHub with minimal reproducible example
