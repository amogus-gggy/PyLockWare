"""
PyLockWare SDK Configuration Management
Управление конфигурацией через pyproject.toml
"""

import tomli
import tomli_w
from pathlib import Path
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass, asdict, field


@dataclass
class BuildConfig:
    """Конфигурация сборки PyLockWare"""
    
    # Основные параметры
    project_path: str = "."
    entry_point: str = "main.py"
    entry_function: str = "main"
    output_dir: str = "dist"
    
    # Опции обфускации
    remap: bool = False
    string_prot: bool = True
    num_obf: bool = True
    import_obf: bool = False
    state_machine: bool = True
    builtin_dispatcher: bool = True
    junk_code: bool = True
    decorator_obf: bool = True
    call_obf: bool = False
    crypt: bool = False
    disable_traceback: bool = True
    anti_tamper_builtins: bool = True
    
    # Параметры обфускации
    junk_density: float = 0.5
    opaque_complexity: str = "high"
    name_gen: str = "english"
    banner: str = "Obfuscated by PyLockWare"
    
    # Анти-отладка
    anti_debug: Optional[Union[str, bool]] = None  # None/False, True, 'native', 'crossplatform'
    anti_debug_mode: str = "crossplatform"
    
    # Nuitka опции
    enable_nuitka: bool = False
    nuitka_onefile: bool = True
    nuitka_standalone: bool = True
    nuitka_output_name: Optional[str] = None
    nuitka_disable_console: bool = True
    nuitka_icon: Optional[str] = None
    nuitka_admin: bool = False
    nuitka_plugins: list = field(default_factory=list)
    nuitka_extra_imports: list = field(default_factory=list)
    nuitka_options: list = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертирует конфиг в словарь, удаляя None значения для TOML"""
        data = asdict(self)
        # Удаляем None значения, так как TOML их не поддерживает
        return {k: v for k, v in data.items() if v is not None}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BuildConfig':
        """Создает конфиг из словаря"""
        # Фильтруем только известные поля
        valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        # Создаем конфиг с дефолтными значениями, затем обновляем
        config = cls()
        for key, value in filtered_data.items():
            setattr(config, key, value)
        
        return config


def load_config(pyproject_path: Optional[Path] = None) -> BuildConfig:
    """
    Загружает конфигурацию из pyproject.toml
    
    Args:
        pyproject_path: Путь к pyproject.toml (по умолчанию ищет в текущей директории)
    
    Returns:
        BuildConfig с загруженными настройками
    """
    if pyproject_path is None:
        pyproject_path = Path.cwd() / "pyproject.toml"
    
    if not pyproject_path.exists():
        print(f"Warning: {pyproject_path} not found, using default configuration")
        return BuildConfig()
    
    with open(pyproject_path, 'rb') as f:
        data = tomli.load(f)
    
    # Извлекаем секцию [tool.pylockware]
    pylockware_config = data.get('tool', {}).get('pylockware', {})
    
    if not pylockware_config:
        print("Warning: [tool.pylockware] section not found in pyproject.toml")
        return BuildConfig()
    
    return BuildConfig.from_dict(pylockware_config)


def save_config(config: BuildConfig, pyproject_path: Optional[Path] = None, pretty: bool = True) -> None:
    """
    Сохраняет конфигурацию в pyproject.toml
    
    Args:
        config: Конфигурация для сохранения
        pyproject_path: Путь к pyproject.toml
        pretty: Использовать красивое форматирование
    """
    if pyproject_path is None:
        pyproject_path = Path.cwd() / "pyproject.toml"
    
    # Загружаем существующий файл или создаем новый
    if pyproject_path.exists():
        with open(pyproject_path, 'rb') as f:
            data = tomli.load(f)
    else:
        data = {}
    
    # Обновляем секцию [tool.pylockware]
    if 'tool' not in data:
        data['tool'] = {}
    
    data['tool']['pylockware'] = config.to_dict()
    
    if pretty:
        # Сохраняем с красивым форматированием
        _save_pretty_toml(data, pyproject_path, config)
    else:
        # Обычное сохранение
        with open(pyproject_path, 'wb') as f:
            tomli_w.dump(data, f)
    
    print(f"Configuration saved to {pyproject_path}")


def _save_pretty_toml(data: dict, path: Path, config: BuildConfig) -> None:
    """Сохраняет TOML с красивым форматированием и комментариями"""
    lines = []
    
    # Сохраняем существующие секции (если есть)
    for key in data:
        if key != 'tool':
            lines.append(f"[{key}]")
            for subkey, value in data[key].items():
                lines.append(f"{subkey} = {_format_toml_value(value)}")
            lines.append("")
    
    # Добавляем секцию [tool.pylockware] с комментариями
    lines.append("[tool.pylockware]")
    lines.append("")
    
    lines.append("# Basic Settings")
    lines.append(f'project_path = "{config.project_path}"')
    lines.append(f'entry_point = "{config.entry_point}"')
    lines.append(f'entry_function = "{config.entry_function}"')
    lines.append(f'output_dir = "{config.output_dir}"')
    lines.append("")
    
    lines.append("# Obfuscation Options")
    lines.append(f"remap = {str(config.remap).lower()}")
    lines.append(f"string_prot = {str(config.string_prot).lower()}")
    lines.append(f"num_obf = {str(config.num_obf).lower()}")
    lines.append(f"import_obf = {str(config.import_obf).lower()}")
    lines.append(f"state_machine = {str(config.state_machine).lower()}")
    lines.append(f"builtin_dispatcher = {str(config.builtin_dispatcher).lower()}")
    lines.append(f"junk_code = {str(config.junk_code).lower()}")
    lines.append(f"decorator_obf = {str(config.decorator_obf).lower()}")
    lines.append(f"call_obf = {str(config.call_obf).lower()}")
    lines.append(f"crypt = {str(config.crypt).lower()}")
    lines.append(f"disable_traceback = {str(config.disable_traceback).lower()}")
    lines.append(f"anti_tamper_builtins = {str(config.anti_tamper_builtins).lower()}")
    lines.append(f"anti_debug = {str(bool(config.anti_debug)).lower()}")
    lines.append("")

    
    lines.append("# Obfuscation Parameters")
    lines.append(f"junk_density = {config.junk_density}")
    lines.append(f'opaque_complexity = "{config.opaque_complexity}"')
    lines.append(f'name_gen = "{config.name_gen}"')
    lines.append(f'banner = "{config.banner}"')
    lines.append("")
    
    lines.append("# Anti-Debug (leave commented to disable)")
    lines.append(f'anti_debug_mode = "{config.anti_debug_mode}"')
    lines.append("")
    
    lines.append("# Nuitka Options (for compiling to executable)")
    lines.append(f"enable_nuitka = {str(config.enable_nuitka).lower()}")
    if config.enable_nuitka:
        lines.append(f"nuitka_onefile = {str(config.nuitka_onefile).lower()}")
        lines.append(f"nuitka_standalone = {str(config.nuitka_standalone).lower()}")
        lines.append(f"nuitka_disable_console = {str(config.nuitka_disable_console).lower()}")
        lines.append(f"nuitka_admin = {str(config.nuitka_admin).lower()}")
        if config.nuitka_output_name:
            lines.append(f'nuitka_output_name = "{config.nuitka_output_name}"')
        if config.nuitka_icon:
            lines.append(f'nuitka_icon = "{config.nuitka_icon}"')
        lines.append(f"nuitka_plugins = {config.nuitka_plugins}")
        lines.append(f"nuitka_extra_imports = {config.nuitka_extra_imports}")
        lines.append(f"nuitka_options = {config.nuitka_options}")
    
    # Сохраняем
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))


def _format_toml_value(value):
    """Форматирует значение для TOML"""
    if isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, (list, dict)):
        import json
        return json.dumps(value)
    else:
        return str(value)


def init_config(pyproject_path: Optional[Path] = None, force: bool = False, 
                scaffold: bool = True) -> BuildConfig:
    """
    Инициализирует конфигурацию PyLockWare в pyproject.toml
    
    Args:
        pyproject_path: Путь к pyproject.toml
        force: Перезаписать существующую конфигурацию
        scaffold: Создать scaffold проекта (main.py и структуру)
    
    Returns:
        Созданная конфигурация
    """
    if pyproject_path is None:
        pyproject_path = Path.cwd() / "pyproject.toml"
    
    project_dir = pyproject_path.parent
    
    # Проверяем существующую конфигурацию
    if pyproject_path.exists() and not force:
        with open(pyproject_path, 'rb') as f:
            data = tomli.load(f)
        
        if 'tool' in data and 'pylockware' in data['tool']:
            print(f"✓ PyLockWare configuration already exists in {pyproject_path}")
            print("  Use --force to overwrite")
            return BuildConfig.from_dict(data['tool']['pylockware'])
    
    # Создаем дефолтную конфигурацию
    config = BuildConfig()
    save_config(config, pyproject_path, pretty=True)
    
    print(f"✓ Initialized PyLockWare configuration in {pyproject_path}")
    
    # Создаем scaffold если нужно
    if scaffold:
        _create_scaffold(project_dir, config)
    
    return config


def _create_scaffold(project_dir: Path, config: BuildConfig) -> None:
    """Создает scaffold структуру проекта"""
    print("\n📦 Creating project scaffold...")
    
    # Создаем main.py если его нет
    main_file = project_dir / config.entry_point
    if not main_file.exists():
        main_content = _get_main_template(config.entry_function)
        main_file.write_text(main_content, encoding='utf-8')
        print(f"  ✓ Created {config.entry_point}")
    else:
        print(f"  ⊘ {config.entry_point} already exists, skipping")
    
    # Создаем .gitignore если его нет
    gitignore_file = project_dir / ".gitignore"
    if not gitignore_file.exists():
        gitignore_content = _get_gitignore_template(config.output_dir)
        gitignore_file.write_text(gitignore_content, encoding='utf-8')
        print(f"  ✓ Created .gitignore")
    else:
        print(f"  ⊘ .gitignore already exists, skipping")
    
    # Создаем README.md если его нет
    readme_file = project_dir / "README.md"
    if not readme_file.exists():
        readme_content = _get_readme_template()
        readme_file.write_text(readme_content, encoding='utf-8')
        print(f"  ✓ Created README.md")
    else:
        print(f"  ⊘ README.md already exists, skipping")
    
    print("\n✨ Project initialized successfully!")
    print("\nNext steps:")
    print(f"  1. Edit {config.entry_point} with your code")
    print("  2. Add @external decorator to public APIs")
    print("  3. Add @crypt decorator to sensitive functions")
    print("  4. Run: pylockware build")
    print(f"  5. Your protected code will be in {config.output_dir}/")


def _get_main_template(entry_function: str) -> str:
    """Returns main.py template"""
    lines = [
        '"""',
        'PyLockWare Protected Application',
        '"""',
        '',
        'from pylockware import external, skip_obf, crypt',
        '',
        '',
        '# === PUBLIC API (names preserved) ===',
        '',
        '@external',
        'def greet(name: str) -> str:',
        '    """Public — visible from outside"""',
        '    return _format_greeting(name)',
        '',
        '',
        '@external',
        'def add(a: int, b: int) -> int:',
        '    """Public — visible from outside"""',
        '    return _calculate(a, b)',
        '',
        '',
        '# === INTERNAL (will be obfuscated) ===',
        '',
        'def _format_greeting(name: str) -> str:',
        '    """Internal — will be obfuscated"""',
        '    return f"Hello, {name.title()}!"',
        '',
        '',
        'def _calculate(x: int, y: int) -> int:',
        '    """Internal — will be obfuscated"""',
        '    return (x * 2 + y * 3) % 1000',
        '',
        '',
        '# === CRYPT (machine-locked encryption) ===',
        '',
        '@crypt',
        'def authenticate(user: str, password: str) -> dict:',
        '    """Sensitive — encrypted with machine fingerprint"""',
        '    secret = "admin123"',
        '    if user == "admin" and password == secret:',
        '        result = {"status": "ok"}',
        '    else:',
        '        result = {"status": "denied"}',
        '    return result',
        '',
        '',
        '# === DEBUG (remove @skip_obf in production!) ===',
        '',
        '@skip_obf',
        'def debug_status():',
        '    """DEBUG: not obfuscated! Remove @skip_obf before release."""',
        '    print("[DEBUG] App running — internal logic exposed for debugging")',
        '',
        '',
        '# === ENTRY POINT ===',
        '',
        '@external',
        f'def {entry_function}():',
        '    """Main entry point"""',
        '    print("=" * 40)',
        '    print("PyLockWare Protected App")',
        '    print("=" * 40)',
        '',
        '    # Public API demo',
        '    print(greet("world"))',
        '    print(f"Result: {add(10, 20)}")',
        '',
        '    # Crypt demo',
        '    print(authenticate("admin", "admin123"))',
        '    print(authenticate("x", "y"))',
        '',
        '    # Debug (remove in production)',
        '    debug_status()',
        '',
        '    print("=" * 40)',
        '',
        '',
        'if __name__ == "__main__":',
        f'    {entry_function}()',
    ]
    return '\n'.join(lines)


def _get_gitignore_template(output_dir: str) -> str:
    """Возвращает шаблон .gitignore"""
    return f'''# PyLockWare
{output_dir}/
*.pyc
__pycache__/

# Python
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/
.venv

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
'''


def _get_readme_template() -> str:
    """Возвращает шаблон README.md"""
    return '''# PyLockWare Protected Project

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
'''
