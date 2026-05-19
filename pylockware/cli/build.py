"""
PyLockWare CLI Build Command
Команда для сборки проектов через CLI
"""

import argparse
import sys
from pathlib import Path

from pylockware.sdk import Builder, BuildConfig, init_config, load_config


def add_build_parser(subparsers):
    """Добавляет парсер для команды build"""
    parser = subparsers.add_parser(
        'build',
        help='Build protected application from pyproject.toml'
    )
    
    parser.add_argument(
        '--config',
        type=Path,
        help='Path to pyproject.toml (default: ./pyproject.toml)'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean output directory before build'
    )
    
    # Опции для переопределения конфига
    parser.add_argument('--entry-point', help='Override entry point')
    parser.add_argument('--output-dir', help='Override output directory')
    parser.add_argument('--remap', action='store_true', help='Enable remap')
    parser.add_argument('--no-string-prot', action='store_true', help='Disable string protection')
    parser.add_argument('--no-state-machine', action='store_true', help='Disable state machine')
    parser.add_argument('--enable-nuitka', action='store_true', help='Enable Nuitka packaging')
    
    parser.set_defaults(func=build_command)


def build_command(args):
    """Выполняет команду build"""
    config_path = args.config or Path.cwd() / 'pyproject.toml'
    
    if not config_path.exists():
        print(f"Error: {config_path} not found")
        print("Run 'pylockware init' to create configuration")
        sys.exit(1)
    
    # Загружаем конфиг
    builder = Builder.from_pyproject(config_path)
    
    # Применяем переопределения из CLI
    overrides = {}
    if args.entry_point:
        overrides['entry_point'] = args.entry_point
    if args.output_dir:
        overrides['output_dir'] = args.output_dir
    if args.remap:
        overrides['remap'] = True
    if args.no_string_prot:
        overrides['string_prot'] = False
    if args.no_state_machine:
        overrides['state_machine'] = False
    if args.enable_nuitka:
        overrides['enable_nuitka'] = True
    
    if overrides:
        builder.update_config(**overrides)
    
    # Очистка если нужно
    if args.clean:
        builder.clean()
    
    # Запускаем сборку
    success = builder.build()
    
    sys.exit(0 if success else 1)


def add_init_parser(subparsers):
    """Добавляет парсер для команды init"""
    parser = subparsers.add_parser(
        'init',
        help='Initialize PyLockWare configuration in pyproject.toml'
    )
    
    parser.add_argument(
        '--config',
        type=Path,
        help='Path to pyproject.toml (default: ./pyproject.toml)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Overwrite existing configuration'
    )
    
    parser.set_defaults(func=init_command)


def init_command(args):
    """Выполняет команду init"""
    config_path = args.config or Path.cwd() / 'pyproject.toml'
    
    try:
        config = init_config(config_path, force=args.force, scaffold=True)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def add_clean_parser(subparsers):
    """Добавляет парсер для команды clean"""
    parser = subparsers.add_parser(
        'clean',
        help='Clean output directory'
    )
    
    parser.add_argument(
        '--config',
        type=Path,
        help='Path to pyproject.toml (default: ./pyproject.toml)'
    )
    
    parser.set_defaults(func=clean_command)


def clean_command(args):
    """Выполняет команду clean"""
    config_path = args.config or Path.cwd() / 'pyproject.toml'
    
    if not config_path.exists():
        print(f"Error: {config_path} not found")
        sys.exit(1)
    
    builder = Builder.from_pyproject(config_path)
    builder.clean()


def main():
    """Главная функция CLI"""
    parser = argparse.ArgumentParser(
        prog='pylockware',
        description='PyLockWare SDK - Python Code Protection'
    )
    
    subparsers = parser.add_subparsers(
        title='commands',
        description='Available commands',
        dest='command'
    )
    
    # Добавляем команды
    add_init_parser(subparsers)
    add_build_parser(subparsers)
    add_clean_parser(subparsers)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Выполняем команду
    args.func(args)


if __name__ == '__main__':
    main()
