"""
Tests for obfuscating example projects
"""
import shutil
from pathlib import Path
import pytest
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from pylockware.core.obfuscator import PyObfuscator


class TestExampleProject:
    """Tests for example_project"""

    def test_obfuscate_example_project_basic(self, example_project_path, temp_dir):
        """Test basic obfuscation of example_project"""
        output_dir = temp_dir / "example_project_output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir)
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True
        assert output_dir.exists()

    def test_obfuscate_example_project_with_remap(self, example_project_path, temp_dir):
        """Test obfuscation of example_project with name remapping"""
        output_dir = temp_dir / "example_project_output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_obfuscate_example_project_with_all_options(self, example_project_path, temp_dir):
        """Test obfuscation of example_project with all options"""
        output_dir = temp_dir / "example_project_output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True,
            string_prot=True,
            num_obf=True,
            junk_code=True,
            junk_density=0.5,
            disable_traceback=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True


class TestExampleProject2:
    """Tests for example_project2 - complex import structure"""

    def test_obfuscate_example_project2_basic(self, example_project2_path, temp_dir):
        """Test basic obfuscation of example_project2"""
        output_dir = temp_dir / "example_project2_output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project2_path),
            entry_point="main.py",
            output_dir=str(output_dir)
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True
        assert output_dir.exists()

    def test_obfuscate_example_project2_with_remap(self, example_project2_path, temp_dir):
        """Test obfuscation of example_project2 with name remapping"""
        output_dir = temp_dir / "example_project2_output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project2_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_obfuscate_example_project2_with_string_prot(self, example_project2_path, temp_dir):
        """Test obfuscation of example_project2 with string protection"""
        output_dir = temp_dir / "example_project2_output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project2_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            string_prot=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_obfuscate_example_project2_complex(self, example_project2_path, temp_dir):
        """Test obfuscation of example_project2 with multiple options"""
        output_dir = temp_dir / "example_project2_output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project2_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True,
            string_prot=True,
            num_obf=True,
            junk_code=True,
            junk_density=0.4,
            disable_traceback=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True


class TestExampleProject3:
    """Tests for example_project3"""

    def test_obfuscate_example_project3_basic(self, example_project3_path, temp_dir):
        """Test basic obfuscation of example_project3"""
        output_dir = temp_dir / "example_project3_output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project3_path),
            entry_point="main.py",
            output_dir=str(output_dir)
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True


class TestExampleProject4:
    """Tests for example_project4"""

    def test_obfuscate_example_project4_basic(self, example_project4_path, temp_dir):
        """Test basic obfuscation of example_project4"""
        output_dir = temp_dir / "example_project4_output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project4_path),
            entry_point="main.py",
            output_dir=str(output_dir)
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True


class TestExampleAsyncProject:
    """Tests for example_async_project"""

    def test_obfuscate_example_async_project_basic(self, example_async_project_path, temp_dir):
        """Test basic obfuscation of example_async_project"""
        output_dir = temp_dir / "example_async_project_output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_async_project_path),
            entry_point="main.py",
            output_dir=str(output_dir)
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True


class TestExampleFastAPIProject:
    """Tests for example_fastapi_project"""

    def test_obfuscate_example_fastapi_project_basic(self, example_fastapi_project_path, temp_dir):
        """Test basic obfuscation of example_fastapi_project"""
        output_dir = temp_dir / "example_fastapi_project_output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_fastapi_project_path),
            entry_point="main.py",
            output_dir=str(output_dir)
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True


class TestExamplePySide6Project:
    """Tests for example_pyside6_project"""

    def test_obfuscate_example_pyside6_project_basic(self, example_pyside6_project_path, temp_dir):
        """Test basic obfuscation of example_pyside6_project"""
        output_dir = temp_dir / "example_pyside6_project_output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_pyside6_project_path),
            entry_point="main.py",
            output_dir=str(output_dir)
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True


class TestCrackmeProject:
    """Tests for crackme project"""

    @pytest.mark.skip(reason="Crackme project test disabled")
    def test_obfuscate_crackme_basic(self, crackme_project_path, temp_dir):
        """Test basic obfuscation of crackme project"""
        output_dir = temp_dir / "crackme_output"
        
        obfuscator = PyObfuscator(
            project_path=str(crackme_project_path),
            entry_point="main.py",
            output_dir=str(output_dir)
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    @pytest.mark.skip(reason="Crackme project test disabled")
    def test_obfuscate_crackme_with_all_options(self, crackme_project_path, temp_dir):
        """Test obfuscation of crackme project with all options"""
        output_dir = temp_dir / "crackme_output"
        
        obfuscator = PyObfuscator(
            project_path=str(crackme_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True,
            string_prot=True,
            num_obf=True,
            junk_code=True,
            junk_density=0.5,
            disable_traceback=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True
