"""
PyLockWare SDK Builder
Основной класс для сборки защищенных приложений
"""

import sys
import platform
from pathlib import Path
from typing import Optional, List

from pylockware.core.obfuscator import PyObfuscator
from pylockware.sdk.config import BuildConfig, load_config


class Builder:
    """
    Билдер для создания защищенных Python приложений
    
    Использование:
        # Из кода
        builder = Builder()
        builder.build()
        
        # С кастомной конфигурацией
        config = BuildConfig(
            entry_point="app.py",
            string_prot=True,
            state_machine=True
        )
        builder = Builder(config)
        builder.build()
        
        # Из pyproject.toml
        builder = Builder.from_pyproject()
        builder.build()
    """
    
    def __init__(self, config: Optional[BuildConfig] = None):
        """
        Инициализирует билдер
        
        Args:
            config: Конфигурация сборки (если None, используется дефолтная)
        """
        self.config = config or BuildConfig()
        self._validate_config()
    
    @classmethod
    def from_pyproject(cls, pyproject_path: Optional[Path] = None) -> 'Builder':
        """
        Создает билдер из pyproject.toml
        
        Args:
            pyproject_path: Путь к pyproject.toml
        
        Returns:
            Настроенный Builder
        """
        config = load_config(pyproject_path)
        return cls(config)
    
    def _validate_config(self) -> None:
        """Валидирует конфигурацию"""
        # Проверка конфликтов
        if self.config.import_obf and self.config.call_obf:
            raise ValueError(
                "Import obfuscation and call obfuscation are incompatible. "
                "Please use only one of these options."
            )
        
        # Проверка anti-debug режима
        if self.config.anti_debug:
            is_windows_amd64 = (
                sys.platform == 'win32' and 
                platform.machine().lower() in ['amd64', 'x86_64']
            )
            
            if self.config.anti_debug_mode == 'native' and not is_windows_amd64:
                print("Warning: Native anti-debug mode is only available for Windows AMD64.")
                print("         Falling back to cross-platform mode.")
                self.config.anti_debug = 'crossplatform'
            elif self.config.anti_debug_mode == 'crossplatform':
                self.config.anti_debug = 'crossplatform'
            else:
                self.config.anti_debug = 'native'
        
        # Проверка Nuitka совместимости
        if self.config.enable_nuitka and self.config.import_obf:
            print("WARNING: Import obfuscation is incompatible with Nuitka EXE packaging.")
            print("         Import obfuscation will be disabled.")
            self.config.import_obf = False
    
    def build(self, banner: Optional[str] = None) -> bool:
        """
        Запускает процесс сборки
        
        Args:
            banner: Баннер для добавления в файлы (переопределяет config.banner)
        
        Returns:
            True если сборка успешна, False иначе
        """
        banner_text = banner or self.config.banner
        
        print("=" * 60)
        print("PyLockWare SDK - Building Protected Application")
        print("=" * 60)
        print(f"Project: {self.config.project_path}")
        print(f"Entry point: {self.config.entry_point}")
        print(f"Output: {self.config.output_dir}")
        print("=" * 60)
        
        # Создаем обфускатор с настройками из конфига
        obfuscator = PyObfuscator(
            project_path=self.config.project_path,
            entry_point=self.config.entry_point,
            entry_function=self.config.entry_function,
            output_dir=self.config.output_dir,
            remap=self.config.remap,
            anti_debug=self.config.anti_debug,
            string_prot=self.config.string_prot,
            num_obf=self.config.num_obf,
            import_obf=self.config.import_obf,
            state_machine=self.config.state_machine,
            builtin_dispatcher=self.config.builtin_dispatcher,
            junk_code=self.config.junk_code,
            junk_density=self.config.junk_density,
            opaque_complexity=self.config.opaque_complexity,
            name_gen=self.config.name_gen,
            disable_traceback=self.config.disable_traceback,
            decorator_obf=self.config.decorator_obf,
            call_obf=self.config.call_obf,
            virtualization=self.config.virtualization,
            enable_nuitka=self.config.enable_nuitka,
            nuitka_onefile=self.config.nuitka_onefile,
            nuitka_standalone=self.config.nuitka_standalone,
            nuitka_output_name=self.config.nuitka_output_name,
            nuitka_disable_console=self.config.nuitka_disable_console,
            nuitka_icon=self.config.nuitka_icon,
            nuitka_admin=self.config.nuitka_admin,
            nuitka_plugins=self.config.nuitka_plugins,
            nuitka_extra_imports=self.config.nuitka_extra_imports,
            nuitka_options=self.config.nuitka_options,
        )
        
        # Запускаем обфускацию
        success = obfuscator.run_obfuscation(banner_text)
        
        if success:
            print("=" * 60)
            print("Build completed successfully!")
            print(f"Output directory: {self.config.output_dir}")
            print("=" * 60)
        else:
            print("=" * 60)
            print("Build failed!")
            print("=" * 60)
        
        return success
    
    def clean(self) -> None:
        """Очищает директорию сборки"""
        import shutil
        output_path = Path(self.config.output_dir)
        
        if output_path.exists():
            shutil.rmtree(output_path)
            print(f"Cleaned output directory: {output_path}")
        else:
            print(f"Output directory does not exist: {output_path}")
    
    def update_config(self, **kwargs) -> None:
        """
        Обновляет параметры конфигурации
        
        Args:
            **kwargs: Параметры для обновления
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                print(f"Warning: Unknown config parameter '{key}'")
        
        self._validate_config()


# Удобные функции для быстрого использования
def build(config: Optional[BuildConfig] = None, **kwargs) -> bool:
    """
    Быстрая сборка с опциональной конфигурацией
    
    Args:
        config: Конфигурация сборки
        **kwargs: Параметры для переопределения конфига
    
    Returns:
        True если сборка успешна
    """
    if config is None:
        config = BuildConfig()
    
    # Применяем переопределения
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    
    builder = Builder(config)
    return builder.build()


def build_from_pyproject(pyproject_path: Optional[Path] = None, **kwargs) -> bool:
    """
    Сборка из pyproject.toml с опциональными переопределениями
    
    Args:
        pyproject_path: Путь к pyproject.toml
        **kwargs: Параметры для переопределения конфига
    
    Returns:
        True если сборка успешна
    """
    builder = Builder.from_pyproject(pyproject_path)
    
    if kwargs:
        builder.update_config(**kwargs)
    
    return builder.build()
