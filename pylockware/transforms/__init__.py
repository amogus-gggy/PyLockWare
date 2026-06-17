"""
PyLockWare Transforms Module
"""

from .num_obf import NumberObfuscator
from .remap_transformer import GlobalRenamer
from .str_prot import StringProtectionTransformer
from .builtin_dispatcher import BuiltinDispatcherTransformer, BUILTIN_FUNCTIONS
from .crypter import (
    CryptTransformer,
    crypt,
    process_file,
    xor_encrypt,
    derive_key,
    generate_seed,
)
from .expr_virtualize import virtualize_code, VM_RUNTIME_CODE

__all__ = [
    'NumberObfuscator',
    'GlobalRenamer',
    'StringProtectionTransformer',
    'BuiltinDispatcherTransformer',
    'BUILTIN_FUNCTIONS',
    'CryptTransformer',
    'crypt',
    'process_file',
    'xor_encrypt',
    'derive_key',
    'generate_seed',
    'virtualize_code',
    'VM_RUNTIME_CODE',
]