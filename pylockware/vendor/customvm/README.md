# CustomVM - Embedded Virtual Machine

This directory contains essential files from CustomVM that are embedded into PyLockWare for virtualization support.

## Source

Original CustomVM repository: https://github.com/6x-u/CustomVM

## Files

These files are copied from CustomVM and embedded into obfuscated projects:

- `__init__.py` - Package initialization
- `vm.py` - Virtual machine implementation
- `opcodes.py` - VM opcodes definitions
- `crypto.py` - Cryptographic utilities
- `loader.py` - Bytecode loader
- `builder.py` - Bytecode builder
- `compiler.py` - Python to VM bytecode compiler

## Usage

These files are automatically embedded into the `__vm_assets__/customvm/` directory when using the `@virtualize` decorator.

## License

CustomVM is created by MERO:TG@QP4RM
