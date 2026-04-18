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
                "--anti-debug", "normal"
            ],
            capture_output=True,
            text=True
        )
        
        # Only run if on Windows AMD64
        if sys.platform == 'win32' and platform.machine().lower() in ['amd64', 'x86_64']:
            assert result.returncode == 0
        else:
            # Should warn and ignore on non-Windows
            assert "Warning" in result.stdout or "Warning" in result.stderr

    def test_cli_anti_debug_strict(self, example_project_path, temp_dir):
        """Test CLI with anti-debug strict mode"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--anti-debug", "strict"
            ],
            capture_output=True,
            text=True
        )
        
        # Only run if on Windows AMD64
        if sys.platform == 'win32' and platform.machine().lower() in ['amd64', 'x86_64']:
            assert result.returncode == 0
        else:
            # Should warn and ignore on non-Windows
            assert "Warning" in result.stdout or "Warning" in result.stderr

    def test_cli_anti_debug_native(self, example_project_path, temp_dir):
        """Test CLI with anti-debug native mode"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--anti-debug", "native"
            ],
            capture_output=True,
            text=True
        )
        
        # Only run if on Windows AMD64
        if sys.platform == 'win32' and platform.machine().lower() in ['amd64', 'x86_64']:
            assert result.returncode == 0
        else:
            # Should warn and ignore on non-Windows
            assert "Warning" in result.stdout or "Warning" in result.stderr

    def test_cli_anti_debug_non_windows(self, example_project_path, temp_dir):
        """Test CLI with anti-debug on non-Windows platform"""
        output_dir = temp_dir / "cli_output"
        
        result = subprocess.run(
            [
                sys.executable, "cli.py",
                str(example_project_path),
                "--entry-point", "main.py",
                "--output-dir", str(output_dir),
                "--anti-debug", "normal"
            ],
            capture_output=True,
            text=True
        )
        
        # On non-Windows, should warn and ignore
        if sys.platform != 'win32' or platform.machine().lower() not in ['amd64', 'x86_64']:
            assert "Warning" in result.stdout or "Warning" in result.stderr
