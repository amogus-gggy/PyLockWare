"""
Tests for CLI banner options
"""
import subprocess
import sys
from pathlib import Path
import pytest


class TestCLIBanner:
    """Tests for banner CLI options"""

    def test_cli_banner_default(self, example_project_path, temp_dir):
        """Test CLI with default banner"""
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

    def test_cli_banner_custom(self, example_project_path, temp_dir):
        """Test CLI with custom banner"""
        output_dir = temp_dir / "cli_output"
        custom_banner = "Custom Banner: Protected by PyLockWare"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--banner", custom_banner
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_banner_multiline(self, example_project_path, temp_dir):
        """Test CLI with multiline banner"""
        output_dir = temp_dir / "cli_output"
        multiline_banner = "Line 1\nLine 2\nLine 3"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--banner", multiline_banner
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
