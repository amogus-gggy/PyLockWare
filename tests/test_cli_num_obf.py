"""
Tests for CLI number obfuscation
"""
import subprocess
import sys
from pathlib import Path
import pytest


class TestCLINumObf:
    """Tests for number obfuscation CLI options"""

    def test_cli_num_obf_basic(self, example_project_path, temp_dir):
        """Test CLI with number obfuscation"""
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

    def test_cli_num_obf_with_remap(self, example_project_path, temp_dir):
        """Test CLI with number obfuscation and remap"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--num-obf",
                "--remap"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_num_obf_with_all(self, example_project_path, temp_dir):
        """Test CLI with number obfuscation in --all mode"""
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
