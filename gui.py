#!/usr/bin/env python3
"""
PyLockWare GUI Entry Point (Legacy)
Graphical user interface for the Python obfuscation suite

Note: This is the legacy GUI launcher. For new projects, use:
    pip install pylockware[gui]
    pylockware-gui
"""

import sys
from pathlib import Path

# Add the project root to the path so we can import pylockware
sys.path.insert(0, str(Path(__file__).parent))

from pylockware.gui.main import main_gui

if __name__ == "__main__":
    main_gui()
