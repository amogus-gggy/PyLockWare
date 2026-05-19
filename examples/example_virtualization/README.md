# CustomVM Virtualization Example

This example demonstrates the most powerful protection feature in PyLockWare: **CustomVM Virtualization**.

## What is Virtualization?

Virtualization converts your Python functions into **custom virtual machine bytecode**. Instead of Python bytecode that can be easily decompiled, your code runs in a proprietary VM with:

- **Custom instruction set** - Unique opcodes for each build
- **Multi-layer encryption** - 4 layers of obfuscation
- **Runtime-only decryption** - Code is never visible in memory
- **Anti-debug protection** - Built into the VM
- **Unique per build** - Each build generates different VM

## Protection Levels

| Method | Reverse Engineering Difficulty |
|--------|-------------------------------|
| Plain Python | ⭐ Easy (1 hour) |
| PyLockWare Obfuscation | ⭐⭐⭐ Hard (50-100 hours) |
| **PyLockWare + CustomVM** | ⭐⭐⭐⭐⭐ **Extreme (500+ hours)** |

## Usage

### 1. Mark Functions for Virtualization

```python
from pylockware import virtualize

@virtualize
def secret_algorithm(x, y):
    # This code will be converted to CVM bytecode
    return (x * 31337 + y) ^ 0xDEADBEEF
```

### 2. Build with Virtualization Enabled

```bash
# Using SDK
pylockware build

# Using CLI
python cli.py . --entry-point main.py --virtualization
```

### 3. Result

The function is replaced with:
```python
def secret_algorithm(x, y):
    return vmentry('secret_algorithm_abc123.cvm', x, y)
```

The actual logic is in encrypted `secret_algorithm_abc123.cvm` file.

## When to Use Virtualization

✅ **Use for:**
- License validation logic
- Encryption/decryption algorithms
- Authentication checks
- Critical business logic
- Anti-cheat mechanisms

❌ **Don't use for:**
- Performance-critical code (VM has overhead)
- I/O operations
- Code that uses external libraries
- Simple utility functions

## Limitations

Virtualized functions support:
- ✅ Basic arithmetic (+, -, *, /, %)
- ✅ Bitwise operations (&, |, ^, <<, >>)
- ✅ Comparisons (==, !=, <, >, <=, >=)
- ✅ Control flow (if/else, while, for)
- ✅ Function calls (limited)
- ✅ Integers, strings, booleans

Not supported:
- ❌ External imports inside virtualized functions
- ❌ Complex data structures (lists, dicts)
- ❌ Classes and objects
- ❌ Generators and async
- ❌ Exception handling

## How It Works

1. **Compilation Phase**
   - PyLockWare finds `@virtualize` decorated functions
   - Compiles them to CustomVM bytecode using AST analysis
   - Generates unique `.cvm` files with encrypted bytecode

2. **Build Phase**
   - Original function is replaced with `vmentry()` wrapper
   - VM runtime is embedded in `__vm_assets__/` directory
   - Each build gets unique VM with different opcodes

3. **Runtime Phase**
   - `vmentry()` loads the `.cvm` file
   - VM decrypts and executes bytecode
   - Result is returned to Python

## Example Output Structure

```
dist/
├── main.py                          # Obfuscated code
└── __vm_assets__/                   # VM runtime
    ├── __init__.py
    ├── _vm_runtime.py               # VM loader
    ├── secret_algorithm_abc123.cvm  # Encrypted bytecode
    └── validate_license_def456.cvm  # Encrypted bytecode
```

## Testing This Example

```bash
# 1. Build the protected version
cd examples/example_virtualization
pylockware build

# 2. Run the original (for comparison)
python main.py

# 3. Run the protected version
cd dist
python main.py

# 4. Try to decompile (you'll see vmentry calls, not the logic!)
```

## Performance Impact

- **Compilation**: +2-5 seconds per virtualized function
- **Runtime**: 10-50x slower than native Python
- **Memory**: +1-2 MB per virtualized function

**Recommendation**: Virtualize only critical functions (5-10% of code).

## Security Notes

1. **Combine with other protections**: Use virtualization WITH obfuscation for maximum security
2. **Unique per build**: Each build generates different VM opcodes
3. **No source exposure**: Even with debugger, logic is hidden
4. **Anti-tamper**: VM validates bytecode integrity

## Advanced Configuration

In `pyproject.toml`:

```toml
[tool.pylockware]
# Enable virtualization
virtualization = true

# Combine with other protections
string_prot = true
state_machine = true
junk_code = true
```

## Troubleshooting

**Issue**: Function fails to virtualize
- **Solution**: Check if function uses only supported Python constructs

**Issue**: Runtime error in vmentry
- **Solution**: Ensure CustomVM is accessible in the build

**Issue**: Performance is too slow
- **Solution**: Virtualize fewer functions, only critical ones

## Learn More

- [CustomVM Documentation](../../CustomVM/README.md)
- [PyLockWare SDK Guide](../../README.md)
- [Security Best Practices](../../docs/security.md)
