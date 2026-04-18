"""
Tests for ModuleManager class
"""
import shutil
from pathlib import Path
import pytest
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from pylockware.core.module_manager import ModuleManager
from pylockware.core.module_base import ModuleBase


class TestModuleManager:
    """Tests for ModuleManager class"""

    def test_module_manager_initialization(self):
        """Test ModuleManager initialization"""
        manager = ModuleManager()
        
        assert manager.modules == []
        assert manager.project_path is None
        assert manager.output_path is None

    def test_module_manager_add_module(self):
        """Test adding modules to manager"""
        manager = ModuleManager()
        
        class DummyModule(ModuleBase):
            def process(self, project_path: Path, output_path: Path) -> bool:
                return True
            def validate_config(self) -> bool:
                return True
        
        module = DummyModule()
        manager.add_module(module)
        
        assert len(manager.modules) == 1
        assert manager.modules[0] is module

    def test_module_manager_add_multiple_modules(self):
        """Test adding multiple modules to manager"""
        manager = ModuleManager()
        
        class DummyModule(ModuleBase):
            def process(self, project_path: Path, output_path: Path) -> bool:
                return True
            def validate_config(self) -> bool:
                return True
        
        module1 = DummyModule()
        module2 = DummyModule()
        module3 = DummyModule()
        
        manager.add_module(module1)
        manager.add_module(module2)
        manager.add_module(module3)
        
        assert len(manager.modules) == 3

    def test_module_manager_add_invalid_module(self):
        """Test adding invalid module raises TypeError"""
        manager = ModuleManager()
        
        with pytest.raises(TypeError):
            manager.add_module("not a module")

    def test_module_manager_remove_module(self):
        """Test removing modules from manager"""
        manager = ModuleManager()
        
        class DummyModule(ModuleBase):
            def process(self, project_path: Path, output_path: Path) -> bool:
                return True
            def validate_config(self) -> bool:
                return True
        
        module1 = DummyModule()
        module1.name = "Module1"
        
        module2 = DummyModule()
        module2.name = "Module2"
        
        manager.add_module(module1)
        manager.add_module(module2)
        
        assert len(manager.modules) == 2
        
        manager.remove_module("Module1")
        assert len(manager.modules) == 1
        assert manager.modules[0].name == "Module2"

    def test_module_manager_set_project_paths(self):
        """Test setting project paths"""
        manager = ModuleManager()
        
        project_path = Path("/test/project")
        output_path = Path("/test/output")
        
        manager.set_project_paths(project_path, output_path)
        
        assert manager.project_path == project_path
        assert manager.output_path == output_path

    def test_module_manager_get_info(self):
        """Test getting module info"""
        manager = ModuleManager()
        
        class DummyModule(ModuleBase):
            def process(self, project_path: Path, output_path: Path) -> bool:
                return True
            def validate_config(self) -> bool:
                return True
        
        module = DummyModule()
        manager.add_module(module)
        
        info = manager.get_module_info()
        
        assert len(info) == 1
        assert "name" in info[0]
        assert "description" in info[0]
        assert "config" in info[0]

    def test_module_manager_run_modules_without_paths(self):
        """Test running modules without setting paths raises ValueError"""
        manager = ModuleManager()
        
        class DummyModule(ModuleBase):
            def process(self, project_path: Path, output_path: Path) -> bool:
                return True
            def validate_config(self) -> bool:
                return True
        
        module = DummyModule()
        manager.add_module(module)
        
        with pytest.raises(ValueError):
            manager.run_modules()

    def test_module_manager_run_modules_with_validation_failure(self, temp_dir):
        """Test running modules with validation failure"""
        manager = ModuleManager()
        
        class FailingValidationModule(ModuleBase):
            def process(self, project_path: Path, output_path: Path) -> bool:
                return True
            def validate_config(self) -> bool:
                return False
        
        project_path = temp_dir / "project"
        project_path.mkdir()
        
        output_path = temp_dir / "output"
        
        manager.set_project_paths(project_path, output_path)
        
        module = FailingValidationModule()
        manager.add_module(module)
        
        result = manager.run_modules()
        assert result is False

    def test_module_manager_run_modules_with_process_failure(self, temp_dir):
        """Test running modules with process failure"""
        manager = ModuleManager()
        
        class FailingProcessModule(ModuleBase):
            def process(self, project_path: Path, output_path: Path) -> bool:
                return False
            def validate_config(self) -> bool:
                return True
        
        project_path = temp_dir / "project"
        project_path.mkdir()
        
        output_path = temp_dir / "output"
        
        manager.set_project_paths(project_path, output_path)
        
        module = FailingProcessModule()
        manager.add_module(module)
        
        result = manager.run_modules()
        assert result is False

    def test_module_manager_run_modules_success(self, temp_dir):
        """Test successful module execution"""
        manager = ModuleManager()
        
        class SuccessModule(ModuleBase):
            def process(self, project_path: Path, output_path: Path) -> bool:
                return True
            def validate_config(self) -> bool:
                return True
        
        project_path = temp_dir / "project"
        project_path.mkdir()
        
        output_path = temp_dir / "output"
        
        manager.set_project_paths(project_path, output_path)
        
        module = SuccessModule()
        manager.add_module(module)
        
        result = manager.run_modules()
        assert result is True

    def test_module_manager_copy_project(self, temp_dir):
        """Test copying project to output directory"""
        manager = ModuleManager()
        
        # Create source project
        project_path = temp_dir / "project"
        project_path.mkdir()
        (project_path / "main.py").write_text("print('hello')")
        (project_path / "utils.py").write_text("def helper(): pass")
        
        # Create subdirectory
        subdir = project_path / "subdir"
        subdir.mkdir()
        (subdir / "nested.py").write_text("# nested")
        
        output_path = temp_dir / "output"
        
        manager.set_project_paths(project_path, output_path)
        manager.copy_project_to_output()
        
        assert output_path.exists()
        assert (output_path / "main.py").exists()
        assert (output_path / "utils.py").exists()
        assert (output_path / "subdir" / "nested.py").exists()

    def test_module_manager_copy_project_overwrites(self, temp_dir):
        """Test that copying project overwrites existing output"""
        manager = ModuleManager()
        
        # Create source project
        project_path = temp_dir / "project"
        project_path.mkdir()
        (project_path / "main.py").write_text("print('hello')")
        
        # Create output directory with existing file
        output_path = temp_dir / "output"
        output_path.mkdir()
        (output_path / "main.py").write_text("print('old')")
        (output_path / "extra.py").write_text("print('extra')")
        
        manager.set_project_paths(project_path, output_path)
        manager.copy_project_to_output()
        
        # Original file should be overwritten
        assert (output_path / "main.py").read_text() == "print('hello')"
        # Extra file should be removed
        assert not (output_path / "extra.py").exists()
