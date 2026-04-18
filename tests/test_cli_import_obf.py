"""
Tests for CLI import obfuscation
"""
import subprocess
import sys
from pathlib import Path
import pytest


class TestCLIImportObf:
    """Tests for import obfuscation CLI options"""

    def test_cli_import_obf_basic(self, example_project_path, temp_dir):
        """Test CLI with import obfuscation"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--import-obf"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_import_obf_with_remap(self, example_project_path, temp_dir):
        """Test CLI with import obfuscation and remap"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--import-obf",
                "--remap"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_import_obf_with_all(self, example_project_path, temp_dir):
        """Test CLI with import obfuscation in --all mode"""
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
