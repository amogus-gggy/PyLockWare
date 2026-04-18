"""
Tests for CLI junk density options
"""
import subprocess
import sys
from pathlib import Path
import pytest


class TestCLIJunkDensity:
    """Tests for junk density CLI options"""

    def test_cli_junk_density_0(self, example_project_path, temp_dir):
        """Test CLI with junk density 0.0"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--junk-code",
                "--junk-density", "0.0"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_junk_density_025(self, example_project_path, temp_dir):
        """Test CLI with junk density 0.25"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--junk-code",
                "--junk-density", "0.25"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_junk_density_05(self, example_project_path, temp_dir):
        """Test CLI with junk density 0.5"""
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

    def test_cli_junk_density_075(self, example_project_path, temp_dir):
        """Test CLI with junk density 0.75"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--junk-code",
                "--junk-density", "0.75"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_junk_density_1(self, example_project_path, temp_dir):
        """Test CLI with junk density 1.0"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--junk-code",
                "--junk-density", "1.0"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
