"""
PyLockWare SDK Setup
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="pylockware",
    version="3.0.0",
    author="PyLockWare Team",
    description="Python Code Protection SDK with obfuscation and anti-debug features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pylockware",
    packages=find_packages(exclude=["tests", "examples", "tools", "native_src"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Security",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "tomli>=2.0.0; python_version<'3.11'",
        "tomli-w>=1.0.0",
        "psutil>=5.0.0",
    ],
    extras_require={
        "gui": [
            "PySide6>=6.0.0",
            "pyside6-fluent-widgets",
        ],
        "nuitka": [
            "nuitka>=1.0.0",
            "ordered-set",
            "zstandard",
        ],
        "full": [
            "PySide6>=6.0.0",
            "pyside6-fluent-widgets",
            "nuitka>=1.0.0",
            "ordered-set",
            "zstandard",
            "pywin32; platform_system=='Windows'",
        ],
    },
    entry_points={
        "console_scripts": [
            "pylockware=pylockware.cli.build:main",
            "pylockware-cli=pylockware.cli.main:main_cli",
        ],
        "gui_scripts": [
            "pylockware-gui=pylockware.gui.main:main_gui",
        ],
    },
    include_package_data=True,
    package_data={
        "pylockware": [
            "anti_debug/*.dll",
            "anti_debug/*.py",
        ],
    },
)
