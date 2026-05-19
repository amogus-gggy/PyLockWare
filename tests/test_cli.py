"""
Tests for CLI interface
"""
import subprocess
import sys
from pathlib import Path
import pytest


class TestCLI:
    """Tests for CLI interface"""

    def test_cli_help(self):
        """Test CLI help output"""
        result = subprocess.run(
            [sys.executable, "cli.py", "--help"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "PyLockWare" in result.stdout
        assert "--entry-point" in result.stdout
        assert "--output-dir" in result.stdout

    def test_cli_basic_obfuscation(self, example_project_path, temp_dir):
        """Test basic CLI obfuscation"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir)
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert output_dir.exists()

    def test_cli_with_remap(self, example_project_path, temp_dir):
        """Test CLI obfuscation with remap"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--remap"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_with_string_prot(self, example_project_path, temp_dir):
        """Test CLI obfuscation with string protection"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--string-prot"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_with_num_obf(self, example_project_path, temp_dir):
        """Test CLI obfuscation with number obfuscation"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--num-obf"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_with_junk_code(self, example_project_path, temp_dir):
        """Test CLI obfuscation with junk code"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--junk-code",
                "--junk-density", "0.5"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_with_state_machine(self, example_project_path, temp_dir):
        """Test CLI obfuscation with state machine"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--state-machine"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_with_builtin_dispatcher(self, example_project_path, temp_dir):
        """Test CLI obfuscation with builtin dispatcher"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--builtin-dispatcher"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_with_decorator_obf(self, example_project_path, temp_dir):
        """Test CLI obfuscation with decorator obfuscation"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--decorator-obf"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_with_call_obf(self, example_project_path, temp_dir):
        """Test CLI obfuscation with call obfuscation"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--call-obf"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_with_disable_traceback(self, example_project_path, temp_dir):
        """Test CLI obfuscation with disable traceback"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--disable-traceback"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_with_name_gen_chinese(self, example_project_path, temp_dir):
        """Test CLI obfuscation with Chinese name generation"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--remap",
                "--name-gen", "chinese"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_with_name_gen_hex(self, example_project_path, temp_dir):
        """Test CLI obfuscation with hex name generation"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--remap",
                "--name-gen", "hex"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_with_all_options(self, example_project_path, temp_dir):
        """Test CLI obfuscation with all options"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--remap",
                "--string-prot",
                "--num-obf",
                "--state-machine",
                "--builtin-dispatcher",
                "--junk-code",
                "--junk-density", "0.5",
                "--disable-traceback",
                "--decorator-obf"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_with_all_flag(self, example_project_path, temp_dir):
        """Test CLI obfuscation with --all flag"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--all"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_invalid_project_path(self, temp_dir):
        """Test CLI with invalid project path"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                "/nonexistent/path",
                "--entry-point", "main.py",
                "--output-dir", str(output_dir)
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0

    def test_cli_invalid_entry_point(self, example_project_path, temp_dir):
        """Test CLI with invalid entry point"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "nonexistent.py",
                "--output-dir", str(output_dir)
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0

    def test_cli_example_project2(self, example_project2_path, temp_dir):
        """Test CLI obfuscation of example_project2"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project2_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--remap",
                "--string-prot"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    @pytest.mark.skip(reason="Crackme project test disabled")
    def test_cli_crackme(self, crackme_project_path, temp_dir):
        """Test CLI obfuscation of crackme project"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(crackme_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--remap"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
