"""
Tests for CLI incompatibility checks
"""
import subprocess
import sys
from pathlib import Path
import pytest


class TestCLIIncompatibility:
    """Tests for CLI incompatibility checks"""

    def test_cli_import_and_call_obf_conflict(self, example_project_path, temp_dir):
        """Test that import and call obfuscation cannot be used together in CLI"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--import-obf",
                "--call-obf"
            ],
            capture_output=True,
            text=True
        )
        
        # Should fail with error message about incompatibility
        assert result.returncode != 0
        assert "incompatible" in result.stdout.lower() or "ERROR" in result.stdout
