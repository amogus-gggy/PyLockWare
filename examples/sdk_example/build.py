"""
Пример программной сборки с использованием PyLockWare SDK
"""

import sys
from pathlib import Path

# Добавляем путь к PyLockWare
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pylockware.sdk import Builder, BuildConfig


def build_with_config():
    """Сборка с использованием BuildConfig"""
    print("Building with BuildConfig...")
    
    config = BuildConfig(
        project_path=".",
        entry_point="main.py",
        entry_function="main",
        output_dir="dist",
        string_prot=True,
        state_machine=True,
        junk_code=True,
        banner="Protected by PyLockWare SDK Example"
    )
    
    builder = Builder(config)
    success = builder.build()
    
    if success:
        print("\n✓ Build completed successfully!")
    else:
        print("\n✗ Build failed!")
    
    return success


def build_from_pyproject():
    """Сборка из pyproject.toml"""
    print("Building from pyproject.toml...")
    
    builder = Builder.from_pyproject()
    success = builder.build()
    
    if success:
        print("\n✓ Build completed successfully!")
    else:
        print("\n✗ Build failed!")
    
    return success


def build_with_overrides():
    """Сборка с переопределением параметров"""
    print("Building with overrides...")
    
    builder = Builder.from_pyproject()
    
    # Переопределяем некоторые параметры
    builder.update_config(
        output_dir="dist_custom",
        junk_density=0.8,
        banner="Custom Build"
    )
    
    success = builder.build()
    
    if success:
        print("\n✓ Build completed successfully!")
    else:
        print("\n✗ Build failed!")
    
    return success


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build SDK example")
    parser.add_argument(
        '--mode',
        choices=['config', 'pyproject', 'overrides'],
        default='pyproject',
        help='Build mode'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'config':
        build_with_config()
    elif args.mode == 'pyproject':
        build_from_pyproject()
    elif args.mode == 'overrides':
        build_with_overrides()
