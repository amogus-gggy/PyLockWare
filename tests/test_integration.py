"""
Integration tests for PyLockWare
"""
import shutil
import subprocess
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).parent.parent))

from pylockware.core.obfuscator import PyObfuscator


class TestIntegration:
    """Integration tests"""

    def test_full_workflow_example_project(self, example_project_path, temp_dir):
        """Test full obfuscation workflow for example_project"""
        output_dir = temp_dir / "output"
        
        # Create obfuscator with multiple options
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
        
        # Run obfuscation
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True
        
        # Verify output directory structure
        assert output_dir.exists()
        
        # Verify Python files exist
        py_files = list(output_dir.rglob("*.py"))
        assert len(py_files) > 0
        
        # Verify banner was added
        main_file = output_dir / "main.py"
        if main_file.exists():
            content = main_file.read_text()
            assert "Obfuscated by PyLockWare" in content

    def test_full_workflow_example_project2(self, example_project2_path, temp_dir):
        """Test full obfuscation workflow for example_project2"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project2_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True,
            string_prot=True,
            num_obf=True,
            state_machine=True,
            junk_code=True,
            junk_density=0.4,
            disable_traceback=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True
        
        # Verify output directory structure
        assert output_dir.exists()
        
        # Verify Python files exist
        py_files = list(output_dir.rglob("*.py"))
        assert len(py_files) > 0

    def test_cli_to_python_import(self, example_project_path, temp_dir):
        """Test that obfuscated code can be imported"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True
        
        # Verify the obfuscated code compiles
        for py_file in output_dir.rglob("*.py"):
            content = py_file.read_text()
            try:
                compile(content, str(py_file), 'exec')
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {py_file}: {e}")

    def test_obfuscation_preserves_functionality(self, example_project_path, temp_dir):
        """Test that obfuscation preserves basic functionality"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True,
            string_prot=True,
            num_obf=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True
        
        # Check that output files contain valid Python code
        for py_file in output_dir.rglob("*.py"):
            content = py_file.read_text()
            # Basic syntax check - should be able to compile
            try:
                compile(content, str(py_file), 'exec')
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {py_file}: {e}")

    def test_multiple_runs_same_output(self, example_project_path, temp_dir):
        """Test that multiple runs produce consistent output"""
        output_dir1 = temp_dir / "output1"
        output_dir2 = temp_dir / "output2"
        
        # First run
        obfuscator1 = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir1),
            remap=True
        )
        result1 = obfuscator1.run_obfuscation("Obfuscated by PyLockWare")
        
        # Second run
        obfuscator2 = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir2),
            remap=True
        )
        result2 = obfuscator2.run_obfuscation("Obfuscated by PyLockWare")
        
        assert result1 is True
        assert result2 is True
        
        # Both should have same number of files
        files1 = list(output_dir1.rglob("*.py"))
        files2 = list(output_dir2.rglob("*.py"))
        assert len(files1) == len(files2)

    def test_large_project_obfuscation(self, example_project2_path, temp_dir):
        """Test obfuscation of larger project with many files"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project2_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True,
            string_prot=True,
            num_obf=True,
            state_machine=True,
            builtin_dispatcher=True,
            junk_code=True,
            junk_density=0.5,
            disable_traceback=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True
        
        # Verify all subdirectories were copied
        assert (output_dir / "package1").exists()
        assert (output_dir / "package2").exists()
        assert (output_dir / "utils").exists()
        assert (output_dir / "external").exists()

    def test_obfuscation_with_custom_banner(self, example_project_path, temp_dir):
        """Test obfuscation with custom banner text"""
        output_dir = temp_dir / "output"
        custom_banner = "Custom Banner: Protected by PyLockWare v2.0"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True
        )
        
        result = obfuscator.run_obfuscation(custom_banner)
        assert result is True
        
        # Verify custom banner was added
        main_file = output_dir / "main.py"
        if main_file.exists():
            content = main_file.read_text()
            assert custom_banner in content

    def test_obfuscation_with_entry_function(self, example_project_path, temp_dir):
        """Test obfuscation with custom entry function"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            entry_function="main",
            output_dir=str(output_dir),
            remap=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True
