"""
Tests for CLI --all flag
"""
import subprocess
import sys
from pathlib import Path
import pytest


class TestCLIAllFlag:
    """Tests for --all flag"""

    def test_cli_all_flag_basic(self, example_project_path, temp_dir):
        """Test CLI with --all flag"""
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

    def test_cli_all_flag_with_example_project2(self, example_project2_path, temp_dir):
        """Test CLI with --all flag on complex project"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project2_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--all"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_all_flag_with_crackme(self, crackme_project_path, temp_dir):
        """Test CLI with --all flag on crackme"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(crackme_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--all"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_all_flag_with_async(self, example_async_project_path, temp_dir):
        """Test CLI with --all flag on async project"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_async_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--all"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_all_flag_with_fastapi(self, example_fastapi_project_path, temp_dir):
        """Test CLI with --all flag on FastAPI project"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_fastapi_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--all"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_all_flag_with_pyside6(self, example_pyside6_project_path, temp_dir):
        """Test CLI with --all flag on PySide6 project"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_pyside6_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--all"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
