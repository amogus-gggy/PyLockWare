"""
Tests for CLI string protection
"""
import subprocess
import sys
from pathlib import Path
import pytest


class TestCLIStringProt:
    """Tests for string protection CLI options"""

    def test_cli_string_prot_basic(self, example_project_path, temp_dir):
        """Test CLI with string protection"""
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

    def test_cli_string_prot_with_remap(self, example_project_path, temp_dir):
        """Test CLI with string protection and remap"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--string-prot",
                "--remap"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_string_prot_with_all(self, example_project_path, temp_dir):
        """Test CLI with string protection in --all mode"""
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
