"""
Basic obfuscator tests
"""
import shutil
from pathlib import Path
import pytest
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from pylockware.core.obfuscator import PyObfuscator


class TestObfuscatorBasic:
    """Basic obfuscator functionality tests"""

    def test_obfuscator_initialization(self, example_project_path, temp_dir):
        """Test obfuscator initialization with basic options"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            remap=False
        )
        
        assert obfuscator.project_path == example_project_path
        assert obfuscator.entry_point == Path("main.py")
        assert obfuscator.output_dir == output_dir
        assert obfuscator.remap is False

    def test_obfuscator_with_all_options(self, example_project_path, temp_dir):
        """Test obfuscator initialization with all options enabled"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            entry_function="main",
            output_dir=str(output_dir),
            remap=True,
            string_prot=True,
            num_obf=True,
            state_machine=True,
            builtin_dispatcher=True,
            junk_code=True,
            junk_density=0.7,
            opaque_complexity="medium",
            name_gen="chinese",
            disable_traceback=True,
            decorator_obf=True,
            call_obf=True,
            anti_debug="normal"
        )
        
        assert obfuscator.remap is True
        assert obfuscator.string_prot is True
        assert obfuscator.num_obf is True
        assert obfuscator.state_machine is True
        assert obfuscator.builtin_dispatcher is True
        assert obfuscator.junk_code is True
        assert obfuscator.junk_density == 0.7
        assert obfuscator.opaque_complexity == "medium"
        assert obfuscator.name_gen == "chinese"
        assert obfuscator.disable_traceback is True
        assert obfuscator.decorator_obf is True
        assert obfuscator.call_obf is True
        assert obfuscator.anti_debug == "normal"

    def test_obfuscator_nuitka_options(self, example_project_path, temp_dir):
        """Test obfuscator with Nuitka packaging options"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            enable_nuitka=True,
            nuitka_onefile=True,
            nuitka_standalone=True,
            nuitka_output_name="myapp",
            nuitka_disable_console=True,
            nuitka_icon="icon.ico",
            nuitka_admin=True,
            nuitka_plugins=["pyside6"],
            nuitka_extra_imports=["requests"],
            nuitka_options=["--clang"]
        )
        
        assert obfuscator.enable_nuitka is True
        assert obfuscator.nuitka_onefile is True
        assert obfuscator.nuitka_standalone is True
        assert obfuscator.nuitka_output_name == "myapp"
        assert obfuscator.nuitka_disable_console is True
        assert obfuscator.nuitka_icon == "icon.ico"
        assert obfuscator.nuitka_admin is True
        assert obfuscator.nuitka_plugins == ["pyside6"]
        assert obfuscator.nuitka_extra_imports == ["requests"]
        assert obfuscator.nuitka_options == ["--clang"]

    def test_invalid_project_path(self, temp_dir):
        """Test obfuscator with invalid project path"""
        output_dir = temp_dir / "output"
        
        with pytest.raises(FileNotFoundError):
            obfuscator = PyObfuscator(
                project_path="/nonexistent/path",
                entry_point="main.py",
                output_dir=str(output_dir)
            )
            obfuscator.validate_paths()

    def test_invalid_entry_point(self, example_project_path, temp_dir):
        """Test obfuscator with invalid entry point"""
        output_dir = temp_dir / "output"
        
        with pytest.raises(FileNotFoundError):
            obfuscator = PyObfuscator(
                project_path=str(example_project_path),
                entry_point="nonexistent.py",
                output_dir=str(output_dir)
            )
            obfuscator.validate_paths()

    def test_incompatible_import_call_obf(self, example_project_path, temp_dir):
        """Test that import and call obfuscation cannot be used together"""
        output_dir = temp_dir / "output"
        
        # This should not raise an error during initialization
        # The check is done in CLI, not in PyObfuscator
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            import_obf=True,
            call_obf=True
        )
        
        # Both should be set
        assert obfuscator.import_obf is True
        assert obfuscator.call_obf is True

    def test_nuitka_disables_anti_debug(self, example_project_path, temp_dir):
        """Test that anti-debug is disabled when Nuitka is enabled"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            enable_nuitka=True,
            anti_debug="normal"
        )
        
        # Anti-debug should be disabled when Nuitka is enabled
        assert obfuscator.anti_debug is None

    def test_nuitka_disables_import_obf(self, example_project_path, temp_dir):
        """Test that import obfuscation is disabled when Nuitka is enabled"""
        output_dir = temp_dir / "output"
        
        obfuscator = PyObfuscator(
            project_path=str(example_project_path),
            entry_point="main.py",
            output_dir=str(output_dir),
            enable_nuitka=True,
            import_obf=True
        )
        
        # Import obfuscation should be disabled when Nuitka is enabled
        assert obfuscator.import_obf is False

    def test_all_flag_simulation(self, example_project_path, temp_dir):
        """Test simulation of --all flag behavior"""
        output_dir = temp_dir / "output"
        
        # Simulate --all flag behavior
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
            disable_traceback=True,
            decorator_obf=True
        )
        
        assert obfuscator.remap is True
        assert obfuscator.string_prot is True
        assert obfuscator.num_obf is True
        assert obfuscator.state_machine is True
        assert obfuscator.builtin_dispatcher is True
        assert obfuscator.junk_code is True
        assert obfuscator.disable_traceback is True
        assert obfuscator.decorator_obf is True
