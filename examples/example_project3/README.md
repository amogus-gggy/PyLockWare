# PyLockWare Protected Project

This project is protected using PyLockWare SDK.

## Setup

1. Install dependencies:
```bash
pip install pylockware
```

2. Build protected version:
```bash
pylockware build
```

3. Run protected application:
```bash
python dist/main.py
```

## Configuration

Edit `pyproject.toml` to customize obfuscation settings:

```toml
[tool.pylockware]
entry_point = "main.py"
string_prot = true
state_machine = true
# ... more options
```

## Using Annotations

### @external
Use for public APIs that need to keep their names:

```python
from pylockware import external

@external
def public_function():
    pass
```

### @skip_obf
Use for debugging (remove in production):

```python
from pylockware import skip_obf

@skip_obf
def debug_function():
    pass
```

## Documentation

See [PyLockWare Documentation](https://github.com/yourusername/pylockware) for more information.
