"""
Tests for ModuleBase class
"""
import pytest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from pylockware.core.module_base import ModuleBase


class TestModuleBase:
    """Tests for ModuleBase class"""

    def test_module_base_initialization(self):
        """Test ModuleBase initialization - should fail since it's abstract"""
        with pytest.raises(TypeError):
            ModuleBase()

    def test_module_base_with_config(self):
        """Test ModuleBase initialization with config - should fail since it's abstract"""
        with pytest.raises(TypeError):
            ModuleBase({"key": "value"})

    def test_module_base_set_config(self):
        """Test set_config method on concrete implementation"""
        class ConcreteModule(ModuleBase):
            def process(self, project_path: Path, output_path: Path) -> bool:
                return True
            def validate_config(self) -> bool:
                return True
        
        module = ConcreteModule()
        module.set_config({"key1": "value1"})
        assert module.config == {"key1": "value1"}

    def test_module_base_get_info(self):
        """Test get_info method on concrete implementation"""
        class ConcreteModule(ModuleBase):
            def process(self, project_path: Path, output_path: Path) -> bool:
                return True
            def validate_config(self) -> bool:
                return True
        
        module = ConcreteModule()
        info = module.get_info()
        
        assert "name" in info
        assert "description" in info
        assert "config" in info
        assert info["name"] == "ConcreteModule"


class ConcreteModule(ModuleBase):
    """Concrete implementation of ModuleBase for testing"""
    
    def process(self, project_path: Path, output_path: Path) -> bool:
        return True
    
    def validate_config(self) -> bool:
        return True


class TestConcreteModule:
    """Tests for concrete module implementations"""

    def test_concrete_module_initialization(self):
        """Test concrete module initialization"""
        module = ConcreteModule()
        
        assert module.name == "ConcreteModule"
        assert module.config == {}

    def test_concrete_module_with_config(self):
        """Test concrete module initialization with config"""
        config = {"test": True}
        module = ConcreteModule(config)
        
        assert module.config == config

    def test_concrete_module_process(self):
        """Test concrete module process method"""
        module = ConcreteModule()
        
        result = module.process(Path("."), Path("."))
        assert result is True

    def test_concrete_module_validate_config(self):
        """Test concrete module validate_config method"""
        module = ConcreteModule()
        
        result = module.validate_config()
        assert result is True
