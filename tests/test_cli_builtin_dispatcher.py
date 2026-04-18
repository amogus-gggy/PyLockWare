"""
Tests for CLI builtin dispatcher
"""
import subprocess
import sys
from pathlib import Path
import pytest


class TestCLIBuiltinDispatcher:
    """Tests for builtin dispatcher CLI options"""

    def test_cli_builtin_dispatcher_basic(self, example_project_path, temp_dir):
        """Test CLI with builtin dispatcher"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--builtin-dispatcher"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_builtin_dispatcher_with_remap(self, example_project_path, temp_dir):
        """Test CLI with builtin dispatcher and remap"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--builtin-dispatcher",
                "--remap"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_builtin_dispatcher_with_all(self, example_project_path, temp_dir):
        """Test CLI with builtin dispatcher in --all mode"""
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
