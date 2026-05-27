"""
Updated PyLockWare Obfuscator
Uses the new modular system with abstract base classes
"""
import ast
import os
import sys
import argparse
import shutil
import random
import string
from pathlib import Path
from typing import Set, List, Dict, Any

from pylockware.core.module_manager import ModuleManager
from pylockware.modules.remap_module import RemapModule
from pylockware.modules.string_protect_module import StringProtectModule
from pylockware.modules.number_obf_module import NumberObfModule
from pylockware.modules.anti_debug_module import AntiDebugModule
from pylockware.modules.import_obf_module import ImportObfuscateModule
from pylockware.modules.state_machine_module import StateMachineModule
from pylockware.modules.nuitka_builder_module import NuitkaBuilderModule
from pylockware.modules.builtin_dispatcher_module import BuiltinDispatcherModule
from pylockware.modules.junk_code_module import JunkCodeModule
from pylockware.modules.decorator_obf_module import DecoratorObfModule
from pylockware.modules.type_annotation_obf_module import TypeAnnotationObfModule
from pylockware.modules.call_obf_module import CallObfModule
from pylockware.modules.remove_annotations_module import RemoveAnnotationsModule
from pylockware.modules.crypt_module import CryptModule


class PyObfuscator:
    """
    A Python obfuscator using the new modular system

    Note: Anti-debug and import obfuscation are incompatible with Nuitka EXE packaging.
    For production protection, consider using dedicated protectors like Themida, VMProtect, etc.
    """

    def __init__(self, project_path: str, entry_point: str, entry_function: str = "main", output_dir: str = "dist",
                 remap: bool = False, anti_debug: str = None, string_prot: bool = False, num_obf: bool = False,
                 import_obf: bool = False, state_machine: bool = False, builtin_dispatcher: bool = False,
                 junk_code: bool = False, junk_density: float = 0.5, opaque_complexity: str = 'high',
                 name_gen: str = 'english',
                 enable_nuitka: bool = False, nuitka_onefile: bool = True, nuitka_standalone: bool = True,
                 nuitka_output_name: str = None, nuitka_disable_console: bool = True, nuitka_icon: str = None,
                 nuitka_admin: bool = False, nuitka_plugins: List[str] = None, nuitka_extra_imports: List[str] = None,
                 nuitka_options: List[str] = None, disable_traceback: bool = False,
                 decorator_obf: bool = False, type_annotation_obf: bool = False, call_obf: bool = False,
                 crypt: bool = False):
        self.project_path = Path(project_path)
        self.entry_point = Path(entry_point)
        self.entry_function = entry_function
        self.output_dir = Path(output_dir)
        self.remap = remap
        # anti_debug can be: None (disabled), 'native' (Windows AMD64), 'crossplatform' (all platforms)
        self.anti_debug = anti_debug
        self.string_prot = string_prot  # Enable string protection
        self.num_obf = num_obf  # Enable number obfuscation
        self.import_obf = import_obf  # Enable import obfuscation
        self.state_machine = state_machine  # Enable state machine obfuscation
        self.builtin_dispatcher = builtin_dispatcher  # Enable builtin dispatcher
        self.junk_code = junk_code  # Enable junk code generation
        self.junk_density = junk_density  # Junk code density (0.0 to 1.0)
        self.opaque_complexity = opaque_complexity  # Opaque predicate complexity
        self.name_gen = name_gen  # Character set for name generation
        self.disable_traceback = disable_traceback  # Disable traceback by setting sys.tracebacklimit = 0
        self.decorator_obf = decorator_obf  # Enable decorator obfuscation
        self.type_annotation_obf = type_annotation_obf  # Enable type annotation obfuscation
        self.call_obf = call_obf  # Enable call obfuscation using getattr pattern
        self.crypt = crypt  # Enable function encryption using machine fingerprinting

        # Nuitka options
        self.enable_nuitka = enable_nuitka
        self.nuitka_onefile = nuitka_onefile
        self.nuitka_standalone = nuitka_standalone
        self.nuitka_output_name = nuitka_output_name
        self.nuitka_disable_console = nuitka_disable_console
        self.nuitka_icon = nuitka_icon
        self.nuitka_admin = nuitka_admin
        self.nuitka_plugins = nuitka_plugins or []
        self.nuitka_extra_imports = nuitka_extra_imports or []
        self.nuitka_options = nuitka_options or []

        # Initialize module manager
        self.module_manager = ModuleManager()
        self.nuitka_module = None

        # Validate and adjust incompatible options
        self._validate_nuitka_compatibility()

        self.setup_modules()

    def _validate_nuitka_compatibility(self):
        """
        Validate and disable options that are incompatible with Nuitka EXE packaging.

        Note: Anti-debug and import obfuscation do not work with Nuitka because:
        - Nuitka compiles Python to C/C++ and then to native code
        - Dynamic imports and runtime module manipulation break during compilation
        - Native anti-debug DLL cannot be loaded from compiled code

        For production protection, use dedicated protectors like Themida, VMProtect, etc.
        """
        if self.enable_nuitka:
            if self.anti_debug:
                self.anti_debug = None
            
            if self.import_obf:
                self.import_obf = False

    def setup_modules(self):
        """
        Setup the required modules based on configuration
        """
        # Set project paths in the module manager
        self.module_manager.set_project_paths(self.project_path, self.output_dir)

        # Analyze imports BEFORE obfuscation if Nuitka is enabled
        # This captures all real imports before they get transformed
        nuitka_config = None
        if self.enable_nuitka:
            # First, analyze imports from the ORIGINAL project
            self.nuitka_module = NuitkaBuilderModule({})
            self.nuitka_module.analyze_imports(self.project_path)

            # Now build the full config with detected imports
            nuitka_config = {
                'enable_nuitka': True,
                'entry_point': str(self.entry_point),
                'onefile': self.nuitka_onefile,
                'standalone': self.nuitka_standalone,
                'output_name': self.nuitka_output_name,
                'windows_disable_console': self.nuitka_disable_console,
                'windows_icon': self.nuitka_icon,
                'windows_uac_admin': self.nuitka_admin,
                'plugins': self.nuitka_plugins,
                'extra_imports': self.nuitka_extra_imports,
                'nuitka_options': self.nuitka_options,
                'detected_imports': self.nuitka_module.detected_imports,
                'detected_frameworks': self.nuitka_module.detected_frameworks,
            }
            # Re-create the module with the full config (preserving detected imports)
            self.nuitka_module = NuitkaBuilderModule(nuitka_config)





        if self.remap:
            remap_config = {
                'entry_function': self.entry_function,
                'name_gen': self.name_gen
            }
            self.module_manager.add_module(RemapModule(remap_config))

        if self.call_obf:
            call_obf_config = {'name_gen': self.name_gen}
            self.module_manager.add_module(CallObfModule(call_obf_config))

        # Add modules based on configuration
        if self.string_prot:
            string_prot_config = {'name_gen': self.name_gen}
            self.module_manager.add_module(StringProtectModule(string_prot_config))

        if self.anti_debug:
            anti_debug_config = {
                'entry_point': str(self.entry_point),
                'mode': self.anti_debug  # 'native' or 'crossplatform'
            }
            self.module_manager.add_module(AntiDebugModule(anti_debug_config))



        

        # Junk code BEFORE state machine - so state machine transforms the junk code too
        if self.junk_code:
            junk_code_config = {
                'name_gen': self.name_gen,
                'junk_density': self.junk_density,
                'opaque_complexity': self.opaque_complexity
            }
            self.module_manager.add_module(JunkCodeModule(junk_code_config))

        # State machine AFTER junk code - so it transforms functions with junk code included
        if self.state_machine:
            state_machine_config = {
                'name_gen': self.name_gen,
                'entry_point': str(self.entry_point),
                'add_junk_states': True
            }
            self.module_manager.add_module(StateMachineModule(state_machine_config))



        if self.num_obf:
            num_obf_config = {'name_gen': self.name_gen}
            self.module_manager.add_module(NumberObfModule(num_obf_config))

        # Decorator obfuscation - converts @decorator to explicit assignments
        # Module disabled due to conflict with annotations
        # if self.decorator_obf:
        #     decorator_obf_config = {'name_gen': self.name_gen}
        #     self.module_manager.add_module(DecoratorObfModule(decorator_obf_config))

        if self.builtin_dispatcher:
            builtin_dispatcher_config = {'name_gen': self.name_gen}
            self.module_manager.add_module(BuiltinDispatcherModule(builtin_dispatcher_config))

        # Add type annotation obfuscation (DISABLED - breaks type hints)
        # if self.type_annotation_obf:
        #     type_annotation_obf_config = {'name_gen': self.name_gen}
        #     self.module_manager.add_module(TypeAnnotationObfModule(type_annotation_obf_config))

        # Add disable traceback module BEFORE Nuitka (if enabled)
        if self.disable_traceback:
            from pylockware.modules.disable_traceback_module import DisableTracebackModule
            self.module_manager.add_module(DisableTracebackModule({}))
        # Add Nuitka module LAST so it runs after all obfuscation
        if self.enable_nuitka:
            self.module_manager.add_module(self.nuitka_module)
        
        # Add RemoveAnnotations module ABSOLUTELY LAST to clean up decorators
        self.module_manager.add_module(RemoveAnnotationsModule({}))

        # Add crypt module if enabled - runs after all other obfuscation
        if self.crypt:
            self.module_manager.add_module(CryptModule({}))
        # Import obfuscation should happen AFTER remapping to capture remapped names
        if self.import_obf:
            import_obf_config = {'name_gen': self.name_gen}
            self.module_manager.add_module(ImportObfuscateModule(import_obf_config))

    def validate_paths(self):
        """
        Validate that the project path and entry point exist
        """
        if not self.project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {self.project_path}")

        # Convert entry_point to Path if it isn't already
        if isinstance(self.entry_point, str):
            self.entry_point = Path(self.entry_point)

        full_entry_path = self.project_path / self.entry_point
        if not full_entry_path.exists():
            raise FileNotFoundError(f"Entry point does not exist: {full_entry_path}")

    def run_obfuscation(self, banner_text: str = "Obfuscated by PyLockWare Obfuscator"):
        """
        Main method to run the obfuscation process using modules
        """
        self.validate_paths()
        success = self.module_manager.run_modules()

        if not success:
            return False

        modules = []
        for py_file in self.output_dir.rglob("*.py"):
            if py_file.name != "obfuscator.py":
                modules.append(py_file)

        for module in modules:
            self.add_banner_to_module(module, banner_text)

        return True

    def add_banner_to_module(self, module_path: Path, banner: str):
        """
        Add a banner comment at the start of a module
        """
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check if banner already exists
        if banner.strip() in content[:500]:  # Check first 500 chars for efficiency
            return

        # Add banner at the beginning, preserving any existing shebang or encoding declaration
        lines = content.split('\n')
        insert_position = 0

        # Skip shebang and encoding declarations
        for i, line in enumerate(lines):
            if line.startswith('#!') or line.startswith('# -*- coding:'):
                insert_position = i + 1
            else:
                break

        # Insert the banner
        banner_lines = [f"# {line}" for line in banner.split('\n')]
        banner_text = '\n'.join(banner_lines) + '\n\n'

        new_content = '\n'.join(lines[:insert_position]) + banner_text + '\n'.join(lines[insert_position:])

        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(new_content)