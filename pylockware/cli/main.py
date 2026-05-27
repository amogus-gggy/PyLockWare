#!/usr/bin/env python3
"""
PyLockWare CLI Main Entry Point
Основная точка входа для CLI (старый интерфейс)
"""

import argparse
import sys
import platform
from pathlib import Path

from pylockware.core.obfuscator import PyObfuscator


def main_cli():
    """Главная функция CLI (совместимость со старым интерфейсом)"""
    parser = argparse.ArgumentParser(description="PyLockWare - Python Obfuscation Suite")
    parser.add_argument("project_path", help="Path to the project to obfuscate")
    parser.add_argument("--entry-point", required=True, help="Entry point file of the project (e.g., main.py)")
    parser.add_argument("--entry-function", default="main", help="Main function name in the entry point (default: main)")
    parser.add_argument("--banner", default="Obfuscated by PyLockWare Obfuscator", help="Banner text to add to modules")
    parser.add_argument("--output-dir", default="dist", help="Output directory for obfuscated project (default: dist)")
    parser.add_argument("--remap", action="store_true", help="Enable renaming of functions, variables, etc. to random names")
    parser.add_argument("--anti-debug", action="store_true", help="Enable anti-debug and anti-injection protection")
    parser.add_argument("--anti-debug-mode", choices=['native', 'crossplatform'], default='native',
                       help="Anti-debug mode: native (Windows AMD64 only, high performance), crossplatform (all platforms, Python-level checks)")
    parser.add_argument("--string-prot", action="store_true", help="Enable string protection using base64 and zlib encoding")
    parser.add_argument("--num-obf", action="store_true", help="Enable number obfuscation using arithmetic expressions")
    parser.add_argument("--import-obf", action="store_true", help="Enable import obfuscation using dynamic execution techniques")
    parser.add_argument("--state-machine", action="store_true", help="Enable state machine obfuscation to transform functions into state machines")
    parser.add_argument("--builtin-dispatcher", action="store_true", help="Enable builtin dispatcher obfuscation to replace built-in calls with dispatcher calls")
    parser.add_argument("--junk-code", action="store_true", help="Enable junk code generation with fake if/elif branches (true/false conditions)")
    parser.add_argument("--junk-density", type=float, default=0.5, help="Junk code density from 0.0 to 1.0 (default: 0.5)")
    parser.add_argument("--opaque-complexity", choices=['low', 'medium', 'high'], default='high', help="Complexity level of opaque predicates (default: high)")
    parser.add_argument("--disable-traceback", action="store_true", help="Disable traceback by setting sys.tracebacklimit = 0 at the start of each file")
    parser.add_argument("--name-gen", choices=['english', 'chinese', 'mixed', 'numbers', 'hex'],
                       default='english', help="Character set for name generation (default: english)")
    parser.add_argument("--decorator-obf", action="store_true", help="Enable decorator obfuscation (converts @decorator to func = decorator(func))")
    parser.add_argument("--call-obf", action="store_true", help="Enable call obfuscation using getattr(sys.modules[\"__main__\"], \"func_name\")() pattern")
    parser.add_argument("--crypt", action="store_true", help="Enable function encryption using machine fingerprinting and XOR encryption")
    parser.add_argument("--anti-tamper-builtins", action=argparse.BooleanOptionalAction, default=True,
                        help="Enable runtime anti-tamper guard that crashes on patched Python builtins (default: enabled)")
    parser.add_argument("--all", action="store_true", help="Enable all obfuscation options (except Nuitka)")

    # Nuitka EXE packaging options
    nuitka_group = parser.add_argument_group("Nuitka EXE Packaging Options")
    nuitka_group.add_argument("--nuitka", action="store_true", help="Enable packaging into EXE using Nuitka")
    nuitka_group.add_argument("--nuitka-onefile", action="store_true", default=True, help="Create a single executable file with --onefile (default: True)")
    nuitka_group.add_argument("--nuitka-no-onefile", action="store_false", dest="nuitka_onefile", help="Disable --onefile option")
    nuitka_group.add_argument("--nuitka-standalone", action="store_true", default=True, help="Create a standalone distribution with --standalone (default: True)")
    nuitka_group.add_argument("--nuitka-no-standalone", action="store_false", dest="nuitka_standalone", help="Disable --standalone option")
    nuitka_group.add_argument("--nuitka-output-name", type=str, help="Custom name for the output executable")
    nuitka_group.add_argument("--nuitka-disable-console", action="store_true", default=True, help="Disable console window for GUI applications (Windows only, default: True)")
    nuitka_group.add_argument("--nuitka-enable-console", action="store_false", dest="nuitka_disable_console", help="Enable console window")
    nuitka_group.add_argument("--nuitka-icon", type=str, help="Path to .ico file for the executable icon (Windows only)")
    nuitka_group.add_argument("--nuitka-admin", action="store_true", help="Request administrator privileges (Windows UAC)")
    nuitka_group.add_argument("--nuitka-plugins", type=str, nargs='+', help="List of Nuitka plugins to enable (e.g., tk-inter, pyside6, numpy, multiprocessing)")
    nuitka_group.add_argument("--nuitka-extra-imports", type=str, nargs='+', help="List of additional modules to include explicitly")
    nuitka_group.add_argument("--nuitka-options", type=str, nargs='+', help="Additional custom Nuitka command-line options")

    args = parser.parse_args()

    # Check for conflicts between import obfuscation and call obfuscation
    if args.import_obf and args.call_obf:
        print("ERROR: Import obfuscation and call obfuscation are incompatible.")
        print("       Please use only one of these options at a time.")
        sys.exit(1)

    # If --all is specified, enable all obfuscation options (except Nuitka)
    if args.all:
        args.remap = False
        args.string_prot = True
        args.num_obf = True
        args.import_obf = False
        args.state_machine = True
        args.builtin_dispatcher = True
        args.junk_code = True
        args.disable_traceback = True
        args.decorator_obf = True
        args.call_obf = False

    # Determine anti_debug mode
    anti_debug_value = None
    if args.anti_debug:
        is_windows_amd64 = sys.platform == 'win32' and platform.machine().lower() in ['amd64', 'x86_64']
        if args.anti_debug_mode == 'native' and not is_windows_amd64:
            print("Warning: Native anti-debug mode is only available for Windows AMD64.")
            print("         Falling back to cross-platform mode.")
            anti_debug_value = 'crossplatform'
        elif args.anti_debug_mode == 'crossplatform':
            anti_debug_value = 'crossplatform'
        else:
            anti_debug_value = 'native'

    obfuscator = PyObfuscator(
        project_path=args.project_path,
        entry_point=args.entry_point,
        entry_function=args.entry_function,
        output_dir=args.output_dir,
        remap=args.remap,
        anti_debug=anti_debug_value,
        string_prot=args.string_prot,
        num_obf=args.num_obf,
        import_obf=args.import_obf,
        state_machine=args.state_machine,
        builtin_dispatcher=args.builtin_dispatcher,
        junk_code=args.junk_code,
        junk_density=args.junk_density,
        opaque_complexity=args.opaque_complexity,
        name_gen=args.name_gen,
        disable_traceback=args.disable_traceback,
        decorator_obf=args.decorator_obf,
        call_obf=args.call_obf,
        crypt=args.crypt,
        anti_tamper_builtins=args.anti_tamper_builtins,
        enable_nuitka=args.nuitka,
        nuitka_onefile=args.nuitka_onefile,
        nuitka_standalone=args.nuitka_standalone,
        nuitka_output_name=args.nuitka_output_name,
        nuitka_disable_console=args.nuitka_disable_console,
        nuitka_icon=args.nuitka_icon,
        nuitka_admin=args.nuitka_admin,
        nuitka_plugins=args.nuitka_plugins,
        nuitka_extra_imports=args.nuitka_extra_imports,
        nuitka_options=args.nuitka_options,
    )

    obfuscator.run_obfuscation(args.banner)


if __name__ == "__main__":
    main_cli()
