"""
Tests for import obfuscation module
"""
import shutil
from pathlib import Path
import pytest
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from pylockware.core.obfuscator import PyObfuscator


class TestImportObfuscation:
    """Tests for import obfuscation"""

    def test_import_obf_basic(self, example_project_path, temp_dir):
        """Test basic import obfuscation"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            import_obf=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_import_obf_with_example_project2(self, example_project2_path, temp_dir):
        """Test import obfuscation with complex project"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project2_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            import_obf=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_import_obf_with_remap(self, example_project_path, temp_dir):
        """Test import obfuscation combined with remap"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            import_obf=True,
            remap=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_import_obf_with_string_prot(self, example_project_path, temp_dir):
        """Test import obfuscation combined with string protection"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            import_obf=True,
            string_prot=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_import_obf_with_junk_code(self, example_project_path, temp_dir):
        """Test import obfuscation combined with junk code"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            import_obf=True,
            junk_code=True,
            junk_density=0.3
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_import_obf_with_state_machine(self, example_project_path, temp_dir):
        """Test import obfuscation combined with state machine"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            import_obf=True,
            state_machine=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_import_obf_with_builtin_dispatcher(self, example_project_path, temp_dir):
        """Test import obfuscation combined with builtin dispatcher"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            import_obf=True,
            builtin_dispatcher=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_import_obf_with_decorator_obf(self, example_project_path, temp_dir):
        """Test import obfuscation combined with decorator obfuscation"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            import_obf=True,
            decorator_obf=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_import_obf_with_disable_traceback(self, example_project_path, temp_dir):
        """Test import obfuscation combined with disable traceback"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            import_obf=True,
            disable_traceback=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_import_obf_with_all_options(self, example_project_path, temp_dir):
        """Test import obfuscation with all other options"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            import_obf=True,
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
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_import_obf_with_crackme(self, crackme_project_path, temp_dir):
        """Test import obfuscation with crackme project"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(crackme_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            import_obf=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_import_obf_with_async_project(self, example_async_project_path, temp_dir):
        """Test import obfuscation with async project"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_async_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            import_obf=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_import_obf_with_fastapi_project(self, example_fastapi_project_path, temp_dir):
        """Test import obfuscation with FastAPI project"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_fastapi_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            import_obf=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_import_obf_with_pyside6_project(self, example_pyside6_project_path, temp_dir):
        """Test import obfuscation with PySide6 project"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_pyside6_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            import_obf=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True
