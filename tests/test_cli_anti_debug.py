"""
Tests for CLI anti-debug
"""
import subprocess
import sys
import platform
from pathlib import Path
import pytest


class TestCLIAntiDebug:
    """Tests for anti-debug CLI options"""

    def test_cli_anti_debug_normal(self, example_project_path, temp_dir):
        """Test CLI with anti-debug normal mode"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--anti-debug"
            ],
            capture_output=True,
            text=True
        )
        
        # Should succeed on all platforms (native on Windows AMD64, crossplatform elsewhere)
        assert result.returncode == 0

    def test_cli_anti_debug_crossplatform(self, example_project_path, temp_dir):
        """Test CLI with anti-debug crossplatform mode"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--anti-debug",
                "--anti-debug-mode", "crossplatform"
            ],
            capture_output=True,
            text=True
        )
        
        # Should succeed on all platforms
        assert result.returncode == 0

    def test_cli_anti_debug_native_windows(self, example_project_path, temp_dir):
        """Test CLI with anti-debug native mode on Windows"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--anti-debug",
                "--anti-debug-mode", "native"
            ],
            capture_output=True,
            text=True
        )
        
        # Should succeed on Windows AMD64, fallback to crossplatform on other platforms
        assert result.returncode == 0
        
        # Check for warning on non-Windows platforms
        if sys.platform != 'win32' or platform.machine().lower() not in ['amd64', 'x86_64']:
            assert "Warning" in result.stdout or "Warning" in result.stderr

    def test_cli_anti_debug_fallback(self, example_project_path, temp_dir):
        """Test CLI with anti-debug fallback behavior"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--anti-debug",
                "--anti-debug-mode", "native"
            ],
            capture_output=True,
            text=True
        )
        
        # Should always succeed (fallback to crossplatform on non-Windows)
        assert result.returncode == 0
