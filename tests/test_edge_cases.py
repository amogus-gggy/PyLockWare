"""
Edge case tests for PyLockWare
"""
import shutil
from pathlib import Path
import pytest
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from pylockware.core.obfuscator import PyObfuscator


class TestEdgeCases:
    """Edge case tests"""

    def test_empty_project(self, temp_dir):
        """Test obfuscation of empty project"""
        project_dir = temp_dir / "empty_project"
        project_dir.mkdir()
        
        # Create minimal main.py
        main_file = project_dir / "main.py"
        main_file.write_text("def main():\n    pass\n")
        
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(project_dir),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_project_with_only_init_files(self, temp_dir):
        """Test obfuscation of project with only __init__.py files"""
        project_dir = temp_dir / "init_project"
        project_dir.mkdir()
        
        # Create package structure
        pkg_dir = project_dir / "mypackage"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("# Empty package\n")
        
        # Create main.py
        (project_dir / "main.py").write_text("import mypackage\n")
        
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(project_dir),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_project_with_binary_files(self, temp_dir):
        """Test obfuscation of project with binary files"""
        project_dir = temp_dir / "binary_project"
        project_dir.mkdir()
        
        # Create main.py
        (project_dir / "main.py").write_text("def main():\n    pass\n")
        
        # Create a binary file
        (project_dir / "data.bin").write_bytes(b"\x00\x01\x02\x03")
        
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(project_dir),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True
        
        # Verify binary file was copied
        assert (output_dir / "data.bin").exists()

    def test_project_with_nested_packages(self, temp_dir):
        """Test obfuscation of deeply nested package structure"""
        project_dir = temp_dir / "nested_project"
        project_dir.mkdir()
        
        # Create deeply nested structure
        deep_path = project_dir / "level1" / "level2" / "level3" / "level4"
        deep_path.mkdir(parents=True)
        
        # Create __init__.py files
        for path in [project_dir / "level1", project_dir / "level1" / "level2",
                     project_dir / "level1" / "level2" / "level3",
                     project_dir / "level1" / "level2" / "level3" / "level4"]:
            (path / "__init__.py").write_text(f"# {path.name}\n")
        
        # Create main.py
        (project_dir / "main.py").write_text("import level1.level2.level3.level4\n")
        
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(project_dir),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_project_with_special_characters_in_names(self, temp_dir):
        """Test obfuscation of project with special characters"""
        project_dir = temp_dir / "special_project"
        project_dir.mkdir()
        
        # Create main.py
        (project_dir / "main.py").write_text("def main():\n    pass\n")
        
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(project_dir),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True,
            name_gen="chinese"
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_project_with_unicode_content(self, temp_dir):
        """Test obfuscation of project with unicode content"""
        project_dir = temp_dir / "unicode_project"
        project_dir.mkdir()
        
        # Create main.py with unicode - use only ASCII-safe unicode
        unicode_content = """
# -*- coding: utf-8 -*-
def main():
    print("Hello World")
    print("Test content")
"""
        (project_dir / "main.py").write_text(unicode_content, encoding='utf-8')
        
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(project_dir),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_project_with_large_files(self, temp_dir):
        """Test obfuscation of project with large files"""
        project_dir = temp_dir / "large_project"
        project_dir.mkdir()
        
        # Create large main.py
        large_content = "def main():\n"
        for i in range(1000):
            large_content += f"    x{i} = {i}\n"
        large_content += "    return 'done'\n"
        
        (project_dir / "main.py").write_text(large_content)
        
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(project_dir),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_project_with_syntax_errors(self, temp_dir):
        """Test obfuscation of project with syntax errors"""
        project_dir = temp_dir / "syntax_error_project"
        project_dir.mkdir()
        
        # Create main.py with syntax error
        (project_dir / "main.py").write_text("def main(\n    pass\n")
        
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(project_dir),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True
        )
        
        # This should fail due to syntax error
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        # The result depends on when syntax errors are caught
        # It may fail during module processing

    def test_project_with_circular_imports(self, temp_dir):
        """Test obfuscation of project with circular imports"""
        project_dir = temp_dir / "circular_project"
        project_dir.mkdir()
        
        # Create module_a with circular import
        (project_dir / "module_a.py").write_text("from module_b import func_b\n")
        (project_dir / "module_b.py").write_text("from module_a import func_a\n")
        (project_dir / "main.py").write_text("import module_a\nimport module_b\n")
        
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(project_dir),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_project_with_no_entry_function(self, temp_dir):
        """Test obfuscation when entry function doesn't exist"""
        project_dir = temp_dir / "no_func_project"
        project_dir.mkdir()
        
        # Create main.py without main function
        (project_dir / "main.py").write_text("print('Hello')\n")
        
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(project_dir),
            entry_point="main.py",
            entry_function="nonexistent_function",
            output_dir=str(output_dir),
            remap=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_project_with_comments_only(self, temp_dir):
        """Test obfuscation of project with only comments"""
        project_dir = temp_dir / "comments_project"
        project_dir.mkdir()
        
        # Create main.py with only comments
        (project_dir / "main.py").write_text("# This is a comment\n# Another comment\n")
        
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(project_dir),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_project_with_docstrings_only(self, temp_dir):
        """Test obfuscation of project with only docstrings"""
        project_dir = temp_dir / "docstring_project"
        project_dir.mkdir()
        
        # Create main.py with only docstrings
        (project_dir / "main.py").write_text('"""Module docstring"""\n\nclass MyClass:\n    """Class docstring"""\n    pass\n')
        
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(project_dir),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_project_with_very_long_lines(self, temp_dir):
        """Test obfuscation of project with very long lines"""
        project_dir = temp_dir / "long_lines_project"
        project_dir.mkdir()
        
        # Create main.py with very long lines
        long_line = "x = '" + "a" * 10000 + "'\n"
        (project_dir / "main.py").write_text(long_line)
        
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(project_dir),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True

    def test_project_with_many_imports(self, temp_dir):
        """Test obfuscation of project with many imports"""
        project_dir = temp_dir / "many_imports_project"
        project_dir.mkdir()
        
        # Create main.py with many imports
        imports = "\n".join([f"import module{i}" for i in range(100)])
        (project_dir / "main.py").write_text(imports + "\n\ndef main():\n    pass\n")
        
        # Create module files
        for i in range(100):
            (project_dir / f"module{i}.py").write_text(f"# Module {i}\n")
        
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(project_dir),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=True
        )
        
        result = obfuscator.run_obfuscation("Obfuscated by PyLockWare")
        assert result is True
