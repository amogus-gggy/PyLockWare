"""
Tests for CLI entry point options
"""
import subprocess
import sys
from pathlib import Path
import pytest


class TestCLIEntryPoint:
    """Tests for entry point CLI options"""

    def test_cli_entry_point_basic(self, example_project_path, temp_dir):
        """Test CLI with basic entry point"""
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

    def test_cli_entry_point_with_subdirectory(self, example_project2_path, temp_dir):
        """Test CLI with entry point in subdirectory"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project2_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir)
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_entry_point_with_entry_function(self, example_project_path, temp_dir):
        """Test CLI with custom entry function"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--entry-function", "main",
                "--output-dir", str(output_dir)
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_entry_point_with_custom_function(self, example_project_path, temp_dir):
        """Test CLI with custom entry function name"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--entry-function", "main",
                "--output-dir", str(output_dir)
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
