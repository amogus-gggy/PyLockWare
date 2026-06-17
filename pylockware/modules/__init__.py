"""
PyLockWare Modules Package
Contains all the specific obfuscation modules
"""
from .remap_module import RemapModule
from .string_protect_module import StringProtectModule
from .number_obf_module import NumberObfModule
from .anti_debug_module import AntiDebugModule
from .import_obf_module import ImportObfuscateModule
from .state_machine_module import StateMachineModule
from .crypt_module import CryptModule
from .expr_virtualize_module import ExprVirtualizeModule

__all__ = [
    'RemapModule',
    'StringProtectModule',
    'NumberObfModule',
    'AntiDebugModule',
    'ImportObfuscateModule',
    'StateMachineModule',
    'CryptModule',
    'ExprVirtualizeModule',
]