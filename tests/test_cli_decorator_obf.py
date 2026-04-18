"""
Tests for CLI decorator obfuscation
"""
import subprocess
import sys
from pathlib import Path
import pytest


class TestCLIDecoratorObf:
    """Tests for decorator obfuscation CLI options"""

    def test_cli_decorator_obf_basic(self, example_project_path, temp_dir):
        """Test CLI with decorator obfuscation"""
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

    def test_cli_decorator_obf_with_remap(self, example_project_path, temp_dir):
        """Test CLI with decorator obfuscation and remap"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--decorator-obf",
                "--remap"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_decorator_obf_with_string_prot(self, example_project_path, temp_dir):
        """Test CLI with decorator obfuscation and string protection"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--decorator-obf",
                "--string-prot"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_decorator_obf_with_all(self, example_project_path, temp_dir):
        """Test CLI with decorator obfuscation in --all mode"""
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
