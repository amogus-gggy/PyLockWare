"""
Tests for individual obfuscation modules
"""
import shutil
from pathlib import Path
import pytest
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from pylockware.core.obfuscator import PyObfuscator


class TestRemapModule:
    """Tests for remap (name obfuscation) module"""

    def test_remap_module_basic(self, example_project_path, temp_dir):
        """Test basic remap functionality"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True,
            name_gen="english"
        )
        
        # Run obfuscation
        result = obfuscator.run_obfuscation("Test Banner")
        
        assert result is True
        assert output_dir.exists()
        
        # Check that output files exist
        output_files = list(output_dir.rglob("*.py"))
        assert len(output_files) > 0

    def test_remap_module_chinese_names(self, example_project_path, temp_dir):
        """Test remap with Chinese character names"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True,
            name_gen="chinese"
        )
        
        result = obfuscator.run_obfuscation("Test Banner")
        assert result is True


class TestStringProtectionModule:
    """Tests for string protection module"""

    def test_string_prot_basic(self, example_project_path, temp_dir):
        """Test basic string protection"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            string_prot=True
        )
        
        result = obfuscator.run_obfuscation("Test Banner")
        assert result is True


class TestNumberObfuscationModule:
    """Tests for number obfuscation module"""

    def test_num_obf_basic(self, example_project_path, temp_dir):
        """Test basic number obfuscation"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            num_obf=True
        )
        
        result = obfuscator.run_obfuscation("Test Banner")
        assert result is True


class TestJunkCodeModule:
    """Tests for junk code module"""

    def test_junk_code_basic(self, example_project_path, temp_dir):
        """Test basic junk code generation"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            junk_code=True,
            junk_density=0.5
        )
        
        result = obfuscator.run_obfuscation("Test Banner")
        assert result is True

    def test_junk_code_high_density(self, example_project_path, temp_dir):
        """Test junk code with high density"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            junk_code=True,
            junk_density=0.9
        )
        
        result = obfuscator.run_obfuscation("Test Banner")
        assert result is True

    def test_junk_code_low_density(self, example_project_path, temp_dir):
        """Test junk code with low density"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            junk_code=True,
            junk_density=0.1
        )
        
        result = obfuscator.run_obfuscation("Test Banner")
        assert result is True


class TestStateMachineModule:
    """Tests for state machine module"""

    def test_state_machine_basic(self, example_project_path, temp_dir):
        """Test basic state machine obfuscation"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            state_machine=True
        )
        
        result = obfuscator.run_obfuscation("Test Banner")
        assert result is True


class TestBuiltinDispatcherModule:
    """Tests for builtin dispatcher module"""

    def test_builtin_dispatcher_basic(self, example_project_path, temp_dir):
        """Test basic builtin dispatcher"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            builtin_dispatcher=True
        )
        
        result = obfuscator.run_obfuscation("Test Banner")
        assert result is True


class TestDecoratorObfuscationModule:
    """Tests for decorator obfuscation module"""

    def test_decorator_obf_basic(self, example_project_path, temp_dir):
        """Test basic decorator obfuscation"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            decorator_obf=True
        )
        
        result = obfuscator.run_obfuscation("Test Banner")
        assert result is True


class TestCallObfuscationModule:
    """Tests for call obfuscation module"""

    def test_call_obf_basic(self, example_project_path, temp_dir):
        """Test basic call obfuscation"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            call_obf=True
        )
        
        result = obfuscator.run_obfuscation("Test Banner")
        assert result is True


class TestDisableTracebackModule:
    """Tests for disable traceback module"""

    def test_disable_traceback_basic(self, example_project_path, temp_dir):
        """Test basic disable traceback"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            disable_traceback=True
        )
        
        result = obfuscator.run_obfuscation("Test Banner")
        assert result is True


class TestCombinedModules:
    """Tests for combining multiple obfuscation modules"""

    def test_multiple_modules_combined(self, example_project_path, temp_dir):
        """Test combining multiple obfuscation modules"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True,
            string_prot=True,
            num_obf=True,
            junk_code=True,
            junk_density=0.3
        )
        
        result = obfuscator.run_obfuscation("Test Banner")
        assert result is True

    def test_all_modules_except_nuitka(self, example_project_path, temp_dir):
        """Test all obfuscation modules except Nuitka"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True,
            string_prot=True,
            num_obf=True,
            state_machine=True,
            builtin_dispatcher=True,
            junk_code=True,
            junk_density=0.5,
            disable_traceback=True,
            decorator_obf=True
        )
        
        result = obfuscator.run_obfuscation("Test Banner")
        assert result is True
