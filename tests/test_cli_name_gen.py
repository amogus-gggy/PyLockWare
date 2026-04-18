"""
Tests for CLI name generation options
"""
import subprocess
import sys
from pathlib import Path
import pytest


class TestCLINameGen:
    """Tests for name generation CLI options"""

    def test_cli_name_gen_english(self, example_project_path, temp_dir):
        """Test CLI with English name generation"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--remap",
                "--name-gen", "english"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_name_gen_chinese(self, example_project_path, temp_dir):
        """Test CLI with Chinese name generation"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--remap",
                "--name-gen", "chinese"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_name_gen_mixed(self, example_project_path, temp_dir):
        """Test CLI with mixed name generation"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--remap",
                "--name-gen", "mixed"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_name_gen_numbers(self, example_project_path, temp_dir):
        """Test CLI with numbers-only name generation"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--remap",
                "--name-gen", "numbers"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_name_gen_hex(self, example_project_path, temp_dir):
        """Test CLI with hex name generation"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--remap",
                "--name-gen", "hex"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_name_gen_default(self, example_project_path, temp_dir):
        """Test CLI with default name generation"""
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
