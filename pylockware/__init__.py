"""
PyLockWare - Python Code Protection SDK
A comprehensive SDK for protecting Python code with multiple obfuscation layers.

Usage:
    # Using decorators
    from pylockware import external, skip_obf
    
    @external
    def public_api():
        pass
    
    @skip_obf
    def debug_function():
        pass
    
    # Using SDK
    from pylockware.sdk import Builder, BuildConfig
    
    config = BuildConfig(entry_point="main.py")
    builder = Builder(config)
    builder.build()
    
    # Using pyproject.toml
    from pylockware.sdk import Builder
    
    builder = Builder.from_pyproject()
    builder.build()
"""

# Core components
from .core import ModuleBase, PyObfuscator

# Modules
from .modules import (
    RemapModule,
    StringProtectModule,
    NumberObfModule,
    AntiDebugModule,
    ImportObfuscateModule,
    StateMachineModule
)

# SDK components
from .decorators import external, skip_obf, preserve_name
from .sdk import Builder, BuildConfig, load_config, save_config, init_config

__version__ = "3.0.0"
__all__ = [
    # Core
    'ModuleBase',
    'PyObfuscator',
    
    # Modules
    'RemapModule',
    'StringProtectModule',
    'NumberObfModule',
    'AntiDebugModule',
    'ImportObfuscateModule',
    'StateMachineModule',
    
    # SDK
    'Builder',
    'BuildConfig',
    'load_config',
    'save_config',
    'init_config',
    
    # Decorators
    'external',
    'skip_obf',
    'preserve_name',
]