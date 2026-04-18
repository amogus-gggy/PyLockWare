"""
Tests for CLI disable traceback
"""
import subprocess
import sys
from pathlib import Path
import pytest


class TestCLIDisableTraceback:
    """Tests for disable traceback CLI options"""

    def test_cli_disable_traceback_basic(self, example_project_path, temp_dir):
        """Test CLI with disable traceback"""
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

    def test_cli_disable_traceback_with_all(self, example_project_path, temp_dir):
        """Test CLI with disable traceback in --all mode"""
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
