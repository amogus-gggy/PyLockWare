#!/usr/bin/env python3
"""
PyLockWare CLI Entry Point (Legacy)
Command-line interface for the Python obfuscation suite

Note: This is the legacy CLI. For new projects, use:
    pip install pylockware
    pylockware-cli --help
"""

import sys
from pathlib import Path

# Add the project root to the path so we can import pylockware
sys.path.insert(0, str(Path(__file__).parent))

from pylockware.cli.main import main_cli

if __name__ == "__main__":
    main_cli()
