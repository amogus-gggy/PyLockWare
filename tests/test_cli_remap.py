"""
Tests for CLI remap
"""
import subprocess
import sys
from pathlib import Path
import pytest


class TestCLIRemap:
    """Tests for remap CLI options"""

    def test_cli_remap_basic(self, example_project_path, temp_dir):
        """Test CLI with remap"""
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

    def test_cli_remap_with_entry_function(self, example_project_path, temp_dir):
        """Test CLI with remap and custom entry function"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--entry-function", "main",
                "--output-dir", str(output_dir),
                "--remap"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_remap_with_banner(self, example_project_path, temp_dir):
        """Test CLI with remap and custom banner"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--remap",
                "--banner", "Custom Banner"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_remap_with_all(self, example_project_path, temp_dir):
        """Test CLI with remap in --all mode"""
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
