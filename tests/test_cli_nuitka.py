"""
Tests for CLI Nuitka options
"""
import subprocess
import sys
from pathlib import Path
import pytest


class TestCLINuitkaOptions:
    """Tests for Nuitka-related CLI options"""

    def test_cli_nuitka_onefile(self, example_project_path, temp_dir):
        """Test CLI with Nuitka onefile option"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--nuitka",
                "--nuitka-onefile"
            ],
            capture_output=True,
            text=True
        )
        
        # Nuitka may not be installed, so we just check the option is parsed
        # The test passes if the option is recognized (no "unrecognized arguments" error)
        assert "unrecognized arguments" not in result.stderr

    def test_cli_nuitka_standalone(self, example_project_path, temp_dir):
        """Test CLI with Nuitka standalone option"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--nuitka",
                "--nuitka-standalone"
            ],
            capture_output=True,
            text=True
        )
        
        assert "unrecognized arguments" not in result.stderr

    def test_cli_nuitka_output_name(self, example_project_path, temp_dir):
        """Test CLI with Nuitka output name option"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--nuitka",
                "--nuitka-output-name", "myapp"
            ],
            capture_output=True,
            text=True
        )
        
        assert "unrecognized arguments" not in result.stderr

    def test_cli_nuitka_disable_console(self, example_project_path, temp_dir):
        """Test CLI with Nuitka disable console option"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--nuitka",
                "--nuitka-disable-console"
            ],
            capture_output=True,
            text=True
        )
        
        assert "unrecognized arguments" not in result.stderr

    def test_cli_nuitka_enable_console(self, example_project_path, temp_dir):
        """Test CLI with Nuitka enable console option"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--nuitka",
                "--nuitka-enable-console"
            ],
            capture_output=True,
            text=True
        )
        
        assert "unrecognized arguments" not in result.stderr

    def test_cli_nuitka_icon(self, example_project_path, temp_dir):
        """Test CLI with Nuitka icon option"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--nuitka",
                "--nuitka-icon", "icon.ico"
            ],
            capture_output=True,
            text=True
        )
        
        assert "unrecognized arguments" not in result.stderr

    def test_cli_nuitka_admin(self, example_project_path, temp_dir):
        """Test CLI with Nuitka admin option"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--nuitka",
                "--nuitka-admin"
            ],
            capture_output=True,
            text=True
        )
        
        assert "unrecognized arguments" not in result.stderr

    def test_cli_nuitka_plugins(self, example_project_path, temp_dir):
        """Test CLI with Nuitka plugins option"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--nuitka",
                "--nuitka-plugins", "pyside6", "multiprocessing"
            ],
            capture_output=True,
            text=True
        )
        
        assert "unrecognized arguments" not in result.stderr

    def test_cli_nuitka_extra_imports(self, example_project_path, temp_dir):
        """Test CLI with Nuitka extra imports option"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--nuitka",
                "--nuitka-extra-imports", "requests", "numpy"
            ],
            capture_output=True,
            text=True
        )
        
        assert "unrecognized arguments" not in result.stderr

    def test_cli_nuitka_options(self, example_project_path, temp_dir):
        """Test CLI with Nuitka custom options"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--nuitka",
                "--nuitka-options", "--clang", "--noinclude-pytest"
            ],
            capture_output=True,
            text=True
        )
        
        assert "unrecognized arguments" not in result.stderr

    def test_cli_nuitka_all_options(self, example_project_path, temp_dir):
        """Test CLI with all Nuitka options"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--nuitka",
                "--nuitka-onefile",
                "--nuitka-standalone",
                "--nuitka-output-name", "myapp",
                "--nuitka-disable-console",
                "--nuitka-icon", "icon.ico",
                "--nuitka-admin",
                "--nuitka-plugins", "pyside6",
                "--nuitka-extra-imports", "requests",
                "--nuitka-options", "--clang"
            ],
            capture_output=True,
            text=True
        )
        
        assert "unrecognized arguments" not in result.stderr

    def test_cli_nuitka_no_onefile(self, example_project_path, temp_dir):
        """Test CLI with Nuitka no-onefile option"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--nuitka",
                "--nuitka-no-onefile"
            ],
            capture_output=True,
            text=True
        )
        
        assert "unrecognized arguments" not in result.stderr

    def test_cli_nuitka_no_standalone(self, example_project_path, temp_dir):
        """Test CLI with Nuitka no-standalone option"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--nuitka",
                "--nuitka-no-standalone"
            ],
            capture_output=True,
            text=True
        )
        
        assert "unrecognized arguments" not in result.stderr
