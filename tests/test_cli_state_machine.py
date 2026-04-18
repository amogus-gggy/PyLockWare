"""
Tests for CLI state machine
"""
import subprocess
import sys
from pathlib import Path
import pytest


class TestCLIStateMachine:
    """Tests for state machine CLI options"""

    def test_cli_state_machine_basic(self, example_project_path, temp_dir):
        """Test CLI with state machine"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--state-machine"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_state_machine_with_remap(self, example_project_path, temp_dir):
        """Test CLI with state machine and remap"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--state-machine",
                "--remap"
            ],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0

    def test_cli_state_machine_with_all(self, example_project_path, temp_dir):
        """Test CLI with state machine in --all mode"""
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
