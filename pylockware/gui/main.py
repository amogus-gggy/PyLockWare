#!/usr/bin/env python3
"""
PyLockWare GUI Main Entry Point
Основная точка входа для GUI
"""

import sys
from pathlib import Path

try:
    from PySide6.QtWidgets import QApplication
    from pylockware.gui.obfuscator_gui import ObfuscatorGUI
except ImportError:
    print("Error: GUI dependencies not installed.")
    print("Install with: pip install pylockware[gui]")
    sys.exit(1)


def main_gui():
    """Главная функция GUI"""
    app = QApplication(sys.argv)
    window = ObfuscatorGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main_gui()
