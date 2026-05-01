#!/usr/bin/.venv python3
"""
PyLockWare GUI Entry Point
Graphical user interface for the Python obfuscation suite
"""

import sys
import os
from pathlib import Path

# Add the project root to the path so we can import pylockware
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication
from pylockware.gui.obfuscator_gui import ObfuscatorGUI


def main():
    app = QApplication(sys.argv)
    window = ObfuscatorGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()