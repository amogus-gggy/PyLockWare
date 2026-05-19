# PyLockWare SDK

**Python Code Protection SDK** with advanced obfuscation, anti-debug features, and annotation-based control.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🚀 Features

### Annotation-Based Control
- `@external` - Preserve function/class names (for public APIs)
- `@skip_obf` - Skip all obfuscation steps (for debugging)
- `@preserve_name` - Alias for `@external`
- **Annotations are automatically removed after obfuscation**

### Obfuscation Techniques
- **String Protection** - Base64 + zlib encoding
- **Number Obfuscation** - Arithmetic expressions
- **State Machine** - Transform functions into state machines
- **Junk Code** - Fake branches with opaque predicates
- **Builtin Dispatcher** - Replace built-in calls
- **Import Obfuscation** - Dynamic import execution
- **Call Obfuscation** - Indirect function calls
- **Name Remapping** - Rename identifiers

### Anti-Debug Protection
- **Native Mode** - Windows AMD64 DLL injection
- **Cross-platform Mode** - Python-level checks

### Build System
- **pyproject.toml Integration** - Standard Python configuration
- **Nuitka Support** - Compile to native executables
- **CLI & GUI** - Multiple interfaces
- **Programmatic API** - Use from Python code

## 📦 Installation

### Via pip (Recommended)

```bash
# Basic installation
pip install pylockware

# With GUI support
pip install pylockware[gui]

# With Nuitka support
pip install pylockware[nuitka]

# Full installation (all features)
pip install pylockware[full]
```

### From Source

```bash
git clone https://github.com/yourusername/pylockware.git
cd pylockware
pip install -e .
```

### Verify Installation

```bash
# SDK CLI
pylockware --help

# Legacy CLI
pylockware-cli --help

# GUI (if installed with [gui])
pylockware-gui
```

## 🎯 Quick Start

### 1. Initialize Project

```bash
cd your_project
pylockware init
```

This creates a `[tool.pylockware]` section in your `pyproject.toml`:

```toml
[tool.pylockware]
project_path = "."
entry_point = "main.py"
entry_function = "main"
output_dir = "dist"

# Obfuscation options
string_prot = true
state_machine = true
junk_code = true
# ... more options
```

### 2. Add Annotations to Your Code

```python
from pylockware import external, skip_obf

# Public API - name will be preserved
@external
def public_api_function(data: str) -> str:
    return process_data(data)

# Internal function - will be obfuscated
def process_data(data: str) -> str:
    return data.upper()

# Debug function - will not be obfuscated
@skip_obf
def debug_log(message: str):
    print(f"[DEBUG] {message}")

# Public class
@external
class PublicAPI:
    @external
    def public_method(self):
        pass
    
    def _internal_method(self):
        # Will be obfuscated
        pass
```

### 3. Build Your Project

```bash
# Basic build
pylockware build

# With custom options
pylockware build --entry-point app.py --output-dir build

# Clean before build
pylockware build --clean

# With Nuitka compilation
pylockware build --enable-nuitka
```

### 4. Run Protected Application

```bash
python dist/main.py
```

## 📚 Documentation

### Annotations

#### `@external`
Marks function/class as external API. Name is preserved during remapping, but other transformations are applied.

```python
@external
def api_function():
    pass

@external
class APIClass:
    pass
```

**Note:** Annotations are automatically removed from the final obfuscated code.

#### `@skip_obf`
Completely skips obfuscation for function/class. Code remains in original form.

```python
@skip_obf
def debug_function():
    pass

@skip_obf
class DebugClass:
    pass
```

**Warning:** Use only for debugging. Do not leave in production code.

### Configuration (pyproject.toml)

```toml
[tool.pylockware]
# Basic settings
project_path = "."              # Project path
entry_point = "main.py"         # Entry point file
entry_function = "main"         # Main function name
output_dir = "dist"             # Output directory

# Obfuscation options
remap = false                   # Name remapping
string_prot = true              # String protection
num_obf = true                  # Number obfuscation
import_obf = false              # Import obfuscation
state_machine = true            # State machine transformation
builtin_dispatcher = true       # Builtin dispatcher
junk_code = true                # Junk code generation
decorator_obf = true            # Decorator obfuscation
call_obf = false                # Call obfuscation
disable_traceback = true        # Disable traceback

# Obfuscation parameters
junk_density = 0.5              # Junk code density (0.0-1.0)
opaque_complexity = "high"      # Opaque predicate complexity (low/medium/high)
name_gen = "english"            # Name generator (english/chinese/mixed/numbers/hex)
banner = "Protected by PyLockWare"  # Banner text

# Anti-debug
anti_debug = null               # null, "native", "crossplatform"
anti_debug_mode = "native"      # Anti-debug mode

# Nuitka options
enable_nuitka = false           # Enable Nuitka
nuitka_onefile = true           # Single file
nuitka_standalone = true        # Standalone build
nuitka_output_name = null       # Output name
nuitka_disable_console = true   # Disable console
nuitka_icon = null              # Icon path
nuitka_admin = false            # Require admin
nuitka_plugins = []             # Nuitka plugins
nuitka_extra_imports = []       # Extra imports
nuitka_options = []             # Extra options
```

### Programmatic API

#### Builder

```python
from pylockware.sdk import Builder, BuildConfig

# Create builder
builder = Builder(config)
builder = Builder.from_pyproject(path)

# Build
success = builder.build()
success = builder.build(banner="Custom Banner")

# Clean
builder.clean()

# Update configuration
builder.update_config(
    string_prot=True,
    state_machine=True
)
```

#### BuildConfig

```python
from pylockware.sdk import BuildConfig

# Create configuration
config = BuildConfig(
    entry_point="main.py",
    output_dir="dist",
    string_prot=True
)

# Convert to dict
config_dict = config.to_dict()

# Create from dict
config = BuildConfig.from_dict(config_dict)
```

#### Configuration Functions

```python
from pylockware.sdk import load_config, save_config, init_config

# Load configuration
config = load_config()
config = load_config(Path("custom/pyproject.toml"))

# Save configuration
save_config(config)
save_config(config, Path("custom/pyproject.toml"))

# Initialize configuration
config = init_config()
config = init_config(force=True)  # Overwrite existing
```

## 🔧 CLI Commands

### init
Initialize PyLockWare configuration in pyproject.toml

```bash
pylockware init
pylockware init --config path/to/pyproject.toml
pylockware init --force  # Overwrite existing
```

### build
Build protected application

```bash
pylockware build
pylockware build --config path/to/pyproject.toml
pylockware build --clean
pylockware build --entry-point app.py
pylockware build --output-dir build
pylockware build --remap
pylockware build --enable-nuitka
```

### clean
Clean output directory

```bash
pylockware clean
pylockware clean --config path/to/pyproject.toml
```

## 📝 Examples

### Example 1: Simple Build

```python
from pylockware.sdk import Builder

builder = Builder.from_pyproject()
builder.build()
```

### Example 2: Custom Configuration

```python
from pylockware.sdk import Builder, BuildConfig

config = BuildConfig(
    entry_point="app.py",
    output_dir="protected",
    string_prot=True,
    state_machine=True,
    junk_code=True,
    junk_density=0.7,
    banner="My Protected App"
)

builder = Builder(config)
builder.build()
```

### Example 3: Build with Nuitka

```python
from pylockware.sdk import Builder, BuildConfig

config = BuildConfig(
    entry_point="main.py",
    string_prot=True,
    state_machine=True,
    enable_nuitka=True,
    nuitka_onefile=True,
    nuitka_disable_console=True,
    nuitka_icon="icon.ico"
)

builder = Builder(config)
builder.build()
```

### Example 4: Using Annotations

```python
from pylockware import external, skip_obf

@external
class MyAPI:
    """Public API class"""
    
    @external
    def public_method(self, data):
        """Public method"""
        return self._process(data)
    
    def _process(self, data):
        """Private method - will be obfuscated"""
        return data.upper()

@skip_obf
def debug_helper():
    """Debug function - will not be obfuscated"""
    print("Debug info")
```

## 🎓 Complete Example

See `examples/sdk_example/` for a complete working example:

```bash
cd examples/sdk_example

# Initialize (pyproject.toml already exists)
pylockware init

# Build via CLI
pylockware build

# Or programmatically
python build.py --mode pyproject
python build.py --mode config
python build.py --mode overrides

# Run protected application
python dist/main.py
```

## 🔒 Security Recommendations

1. **Use @external for public APIs** - Preserves function/class names that must be accessible externally
2. **Use @skip_obf only for debugging** - Do not leave these annotations in production code
3. **Combine multiple obfuscation techniques** - string_prot + state_machine + junk_code provides better protection
4. **Use Nuitka for final builds** - Compiles Python to native code
5. **Don't store secrets in code** - Obfuscation is not a replacement for proper secret management

## ⚠️ Known Limitations

- `import_obf` and `call_obf` are incompatible with each other
- `import_obf` does not work with Nuitka
- Native anti-debug only works on Windows AMD64
- Annotations work only at function and class level

## 🔄 Migration from v2.x

### Old Way (CLI)

```bash
python cli.py examples/example_project \
    --entry-point main.py \
    --string-prot \
    --state-machine
```

### New Way (SDK)

1. **Initialize configuration:**

```bash
cd examples/example_project
pylockware init
```

2. **Edit `pyproject.toml`:**

```toml
[tool.pylockware]
entry_point = "main.py"
string_prot = true
state_machine = true
```

3. **Build:**

```bash
pylockware build
```

### Backward Compatibility

The old CLI still works:

```bash
# Legacy CLI
python cli.py project_path --entry-point main.py --string-prot

# Or via installed command
pylockware-cli project_path --entry-point main.py --string-prot
```

## 🛠️ Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/pylockware.git
cd pylockware
pip install -e .[dev]
```

### Run Tests

```bash
pytest
pytest tests/test_sdk.py -v
```

### Code Formatting

```bash
black pylockware
```

### Type Checking

```bash
mypy pylockware
```

## 📋 System Requirements

- Python 3.8 or higher
- Windows, Linux, or macOS
- For native anti-debug: Windows AMD64

## 📦 Optional Dependencies

### GUI
- PySide6 >= 6.0.0
- pyside6-fluent-widgets

### Nuitka
- nuitka >= 1.0.0
- ordered-set
- zstandard

### Windows (for native anti-debug)
- pywin32

## 🐛 Troubleshooting

### Command not found: pylockware

Ensure pip installed the package in the correct environment:

```bash
python -m pip install pylockware
python -m pylockware.cli.build --help
```

### GUI dependencies not installed

Install GUI dependencies:

```bash
pip install pylockware[gui]
```

### Import error: tomli

For Python < 3.11, tomli is required:

```bash
pip install tomli
```

### Nuitka issues

Install Nuitka dependencies:

```bash
pip install pylockware[nuitka]
```

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

- GitHub Issues: [Report bugs or request features](https://github.com/yourusername/pylockware/issues)
- Documentation: See this README and inline code documentation

## 🙏 Acknowledgments

- Nuitka project for Python compilation
- PySide6 for GUI framework
- All contributors and users

---

**Note:** PyLockWare is a code protection tool. While it provides multiple layers of obfuscation, no obfuscation is unbreakable. Use it as part of a comprehensive security strategy, not as the only protection mechanism.
