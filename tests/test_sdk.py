"""
Тесты для PyLockWare SDK
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from pylockware.sdk import Builder, BuildConfig, load_config, save_config, init_config
from pylockware.decorators import external, skip_obf, is_external, should_skip_obfuscation


class TestDecorators:
    """Тесты для декораторов"""
    
    def test_external_decorator(self):
        """Тест декоратора @external"""
        @external
        def test_func():
            pass
        
        assert is_external(test_func)
        assert hasattr(test_func, '__pylockware_attrs__')
        assert test_func.__pylockware_attrs__['external'] is True
    
    def test_skip_obf_decorator(self):
        """Тест декоратора @skip_obf"""
        @skip_obf
        def test_func():
            pass
        
        assert should_skip_obfuscation(test_func)
        assert hasattr(test_func, '__pylockware_attrs__')
        assert test_func.__pylockware_attrs__['skip_obf'] is True
    
    def test_external_on_class(self):
        """Тест @external на классе"""
        @external
        class TestClass:
            pass
        
        assert is_external(TestClass)
    
    def test_skip_obf_on_class(self):
        """Тест @skip_obf на классе"""
        @skip_obf
        class TestClass:
            pass
        
        assert should_skip_obfuscation(TestClass)


class TestBuildConfig:
    """Тесты для BuildConfig"""
    
    def test_default_config(self):
        """Тест дефолтной конфигурации"""
        config = BuildConfig()
        
        assert config.project_path == "."
        assert config.entry_point == "main.py"
        assert config.entry_function == "main"
        assert config.output_dir == "dist"
        assert config.string_prot is True
        assert config.state_machine is True
    
    def test_custom_config(self):
        """Тест кастомной конфигурации"""
        config = BuildConfig(
            entry_point="app.py",
            output_dir="build",
            string_prot=False,
            remap=True
        )
        
        assert config.entry_point == "app.py"
        assert config.output_dir == "build"
        assert config.string_prot is False
        assert config.remap is True
    
    def test_config_to_dict(self):
        """Тест конвертации в словарь"""
        config = BuildConfig(entry_point="test.py")
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert config_dict['entry_point'] == "test.py"
    
    def test_config_from_dict(self):
        """Тест создания из словаря"""
        data = {
            'entry_point': 'app.py',
            'output_dir': 'build',
            'string_prot': False
        }
        
        config = BuildConfig.from_dict(data)
        
        assert config.entry_point == 'app.py'
        assert config.output_dir == 'build'
        assert config.string_prot is False


class TestConfigManagement:
    """Тесты для управления конфигурацией"""
    
    def test_init_config(self):
        """Тест инициализации конфигурации"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            
            config = init_config(pyproject_path)
            
            assert pyproject_path.exists()
            assert isinstance(config, BuildConfig)
    
    def test_save_and_load_config(self):
        """Тест сохранения и загрузки конфигурации"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            
            # Создаем и сохраняем конфиг
            original_config = BuildConfig(
                entry_point="test.py",
                output_dir="custom_dist",
                string_prot=False
            )
            save_config(original_config, pyproject_path)
            
            # Загружаем обратно
            loaded_config = load_config(pyproject_path)
            
            assert loaded_config.entry_point == "test.py"
            assert loaded_config.output_dir == "custom_dist"
            assert loaded_config.string_prot is False
    
    def test_load_nonexistent_config(self):
        """Тест загрузки несуществующего конфига"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "nonexistent.toml"
            
            config = load_config(pyproject_path)
            
            # Должен вернуть дефолтный конфиг
            assert isinstance(config, BuildConfig)
            assert config.entry_point == "main.py"


class TestBuilder:
    """Тесты для Builder"""
    
    def test_builder_creation(self):
        """Тест создания билдера"""
        config = BuildConfig()
        builder = Builder(config)
        
        assert builder.config == config
    
    def test_builder_with_default_config(self):
        """Тест билдера с дефолтным конфигом"""
        builder = Builder()
        
        assert isinstance(builder.config, BuildConfig)
    
    def test_builder_update_config(self):
        """Тест обновления конфигурации"""
        builder = Builder()
        
        builder.update_config(
            entry_point="new.py",
            string_prot=False
        )
        
        assert builder.config.entry_point == "new.py"
        assert builder.config.string_prot is False
    
    def test_builder_from_pyproject(self):
        """Тест создания билдера из pyproject.toml"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject_path = Path(tmpdir) / "pyproject.toml"
            
            # Создаем конфиг
            config = BuildConfig(entry_point="test.py")
            save_config(config, pyproject_path)
            
            # Создаем билдер
            builder = Builder.from_pyproject(pyproject_path)
            
            assert builder.config.entry_point == "test.py"
    
    def test_builder_validation_conflict(self):
        """Тест валидации конфликтующих опций"""
        config = BuildConfig(
            import_obf=True,
            call_obf=True
        )
        
        with pytest.raises(ValueError):
            Builder(config)


class TestIntegration:
    """Интеграционные тесты"""
    
    def test_full_workflow(self):
        """Тест полного workflow"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Создаем тестовый проект
            project_dir = tmpdir / "test_project"
            project_dir.mkdir()
            
            # Создаем main.py
            main_file = project_dir / "main.py"
            main_file.write_text("""
from pylockware import external, skip_obf

@external
def public_api():
    return "Hello"

@skip_obf
def debug_func():
    print("Debug")

def main():
    print(public_api())
    debug_func()

if __name__ == "__main__":
    main()
""")
            
            # Создаем pyproject.toml
            pyproject_path = project_dir / "pyproject.toml"
            config = BuildConfig(
                project_path=".",
                entry_point="main.py",
                output_dir="dist",
                string_prot=False,  # Отключаем для простоты теста
                state_machine=False,
                junk_code=False
            )
            save_config(config, pyproject_path)
            
            # Создаем билдер и собираем
            builder = Builder.from_pyproject(pyproject_path)
            
            # Проверяем, что конфиг загрузился
            assert builder.config.entry_point == "main.py"
            
            # Note: Полная сборка требует всех зависимостей,
            # поэтому здесь мы только проверяем создание билдера


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
