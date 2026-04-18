"""
Tests for CLI output directory options
"""
import subprocess
import sys
from pathlib import Path
import pytest


class TestCLIOutputDir:
    """Tests for output directory CLI options"""

    def test_cli_output_dir_default(self, example_project_path, temp_dir):
        """Test CLI with default output directory"""
        cli_path = Path(__file__).parent.parent / "cli.py"
        result = subprocess.run(
            [
                sys.executable, str(cli_path),
                str(example_project_path),
                "--entry-point", "main.py"
            ],
            capture_output=True,
            text=True,
            cwd=str(temp_dir)
        )
        
        # Default output is "dist" directory
        # The test passes if the command runs without error
        assert result.returncode == 0, f"CLI failed: {result.stderr}"

    def test_cli_output_dir_custom(self, example_project_path, temp_dir):
        """Test CLI with custom output directory"""
        output_dir = temp_dir / "custom_output"
        
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
        assert output_dir.exists()

    def test_cli_output_dir_nested(self, example_project_path, temp_dir):
        """Test CLI with nested output directory"""
        output_dir = temp_dir / "level1" / "level2" / "output"
        
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
        assert output_dir.exists()

    def test_cli_output_dir_overwrite(self, example_project_path, temp_dir):
        """Test CLI overwriting existing output directory"""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        (output_dir / "old_file.py").write_text("old content")
        
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
        # Old file should be removed
        assert not (output_dir / "old_file.py").exists()
        # New files should exist
        assert (output_dir / "main.py").exists()
