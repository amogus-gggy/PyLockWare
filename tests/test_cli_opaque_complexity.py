"""
Tests for CLI opaque complexity options
"""
import subprocess
import sys
from pathlib import Path
import pytest


class TestCLIOpaqueComplexity:
    """Tests for opaque complexity CLI options"""

    def test_cli_opaque_complexity_low(self, example_project_path, temp_dir):
        """Test CLI with low opaque complexity"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--junk-code",
                "--junk-density", "0.5",
                "--opaque-complexity", "low"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_opaque_complexity_medium(self, example_project_path, temp_dir):
        """Test CLI with medium opaque complexity"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--junk-code",
                "--junk-density", "0.5",
                "--opaque-complexity", "medium"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_opaque_complexity_high(self, example_project_path, temp_dir):
        """Test CLI with high opaque complexity"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--junk-code",
                "--junk-density", "0.5",
                "--opaque-complexity", "high"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_opaque_complexity_default(self, example_project_path, temp_dir):
        """Test CLI with default opaque complexity"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--junk-code",
                "--junk-density", "0.5"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
