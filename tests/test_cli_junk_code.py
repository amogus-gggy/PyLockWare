"""
Tests for CLI junk code
"""
import subprocess
import sys
from pathlib import Path
import pytest


class TestCLIJunkCode:
    """Tests for junk code CLI options"""

    def test_cli_junk_code_basic(self, example_project_path, temp_dir):
        """Test CLI with junk code"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--junk-code"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_junk_code_with_remap(self, example_project_path, temp_dir):
        """Test CLI with junk code and remap"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--junk-code",
                "--remap"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_junk_code_with_all(self, example_project_path, temp_dir):
        """Test CLI with junk code in --all mode"""
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
