"""
Nuitka Builder Module for PyLockWare
Packages obfuscated Python applications into standalone EXE files using Nuitka
"""
import ast
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Set, List

from pylockware.core.module_base import ModuleBase


class ImportAnalyzer:
    """
    Analyzes Python files to extract all imported modules
    """

    def __init__(self):
        self.imports: Set[str] = set()
        self.local_modules: Set[str] = set()

    def analyze_file(self, file_path: Path) -> Set[str]:
        """
        Analyze a single Python file and extract imports

        Args:
            file_path: Path to the Python file

        Returns:
            Set of imported module names
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return set()

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            print(f"Warning: Syntax error in {file_path}: {e}")
            return set()

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Get the top-level module name
                    module_name = alias.name.split('.')[0]
                    imports.add(module_name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # Get the top-level module name
                    module_name = node.module.split('.')[0]
                    imports.add(module_name)

        return imports

    def analyze_directory(self, directory: Path, exclude_patterns: Optional[List[str]] = None) -> Set[str]:
        """
        Analyze all Python files in a directory

        Args:
            directory: Path to the directory
            exclude_patterns: List of patterns to exclude (e.g., ['__pycache__', 'test_*'])

        Returns:
            Set of all imported module names
        """
        exclude_patterns = exclude_patterns or ['__pycache__', '.git', 'venv', '.venv', '.venv']
        all_imports = set()

        for py_file in directory.rglob('*.py'):
            # Check if any exclude pattern matches
            parts = py_file.parts
            if any(pattern in str(py_file) for pattern in exclude_patterns):
                continue

            imports = self.analyze_file(py_file)
            all_imports.update(imports)

        return all_imports

    def filter_standard_library(self, imports: Set[str]) -> Set[str]:
        """
        Filter out standard library modules from the imports

        Args:
            imports: Set of all imported module names

        Returns:
            Set of third-party module names
        """
        # List of common standard library modules
        stdlib_modules = {
            'abc', 'aifc', 'argparse', 'array', 'ast', 'asynchat', 'asyncio', 'asyncore',
            'atexit', 'audioop', 'base64', 'bdb', 'binascii', 'binhex', 'bisect',
            'builtins', 'bz2', 'calendar', 'cgi', 'cgitb', 'chunk', 'cmath', 'cmd',
            'code', 'codecs', 'codeop', 'collections', 'colorsys', 'compileall',
            'concurrent', 'configparser', 'contextlib', 'contextvars', 'copy', 'copyreg',
            'cProfile', 'crypt', 'csv', 'ctypes', 'curses', 'dataclasses', 'datetime',
            'dbm', 'decimal', 'difflib', 'dis', 'distutils', 'doctest', 'email',
            'encodings', 'enum', 'errno', 'faulthandler', 'fcntl', 'filecmp', 'fileinput',
            'fnmatch', 'fractions', 'ftplib', 'functools', 'gc', 'getopt', 'getpass',
            'gettext', 'glob', 'graphlib', 'grp', 'gzip', 'hashlib', 'heapq', 'hmac',
            'html', 'http', 'idlelib', 'imaplib', 'imghdr', 'imp', 'importlib', 'inspect',
            'io', 'ipaddress', 'itertools', 'json', 'keyword', 'lib2to3', 'linecache',
            'locale', 'logging', 'lzma', 'mailbox', 'mailcap', 'marshal', 'math',
            'mimetypes', 'mmap', 'modulefinder', 'multiprocessing', 'netrc', 'nis',
            'nntplib', 'numbers', 'operator', 'optparse', 'os', 'ossaudiodev', 'pathlib',
            'pdb', 'pickle', 'pickletools', 'pipes', 'pkgutil', 'platform', 'plistlib',
            'poplib', 'posix', 'posixpath', 'pprint', 'profile', 'pstats', 'pty', 'pwd',
            'py_compile', 'pyclbr', 'pydoc', 'queue', 'quopri', 'random', 're', 'readline',
            'reprlib', 'resource', 'rlcompleter', 'runpy', 'sched', 'secrets', 'select',
            'selectors', 'shelve', 'shlex', 'shutil', 'signal', 'site', 'smtpd', 'smtplib',
            'sndhdr', 'socket', 'socketserver', 'spwd', 'sqlite3', 'ssl', 'stat',
            'statistics', 'string', 'stringprep', 'struct', 'subprocess', 'sunau',
            'symtable', 'sys', 'sysconfig', 'syslog', 'tabnanny', 'tarfile', 'telnetlib',
            'tempfile', 'termios', 'test', 'textwrap', 'threading', 'time', 'timeit',
            'tkinter', 'token', 'tokenize', 'trace', 'traceback', 'tracemalloc', 'tty',
            'turtle', 'turtledemo', 'types', 'typing', 'unicodedata', 'unittest', 'urllib',
            'uu', 'uuid', 'venv', 'warnings', 'wave', 'weakref', 'webbrowser', 'winreg',
            'winsound', 'wsgiref', 'xdrlib', 'xml', 'xmlrpc', 'zipapp', 'zipfile',
            'zipimport', 'zlib', '_thread', '__future__', 'typing_extensions',
            # Python 3.10+
            'zoneinfo', 'tomllib',
        }

        return imports - stdlib_modules

    def detect_frameworks(self, imports: Set[str]) -> Dict[str, bool]:
        """
        Detect which frameworks/plugins are needed based on imports

        Args:
            imports: Set of imported module names

        Returns:
            Dictionary mapping framework names to whether they're detected
        """
        frameworks = {
            'tkinter': 'tkinter' in imports or 'tkinter' in str(imports).lower(),
            'pyside6': any(x in imports for x in ['PySide6', 'PySide2', 'QtWidgets', 'QtCore', 'QtGui']),
            'pyqt5': any(x in imports for x in ['PyQt5', 'PyQt6', 'QtWidgets', 'QtCore', 'QtGui']),
            'numpy': 'numpy' in imports or 'np' in imports,
            'multiprocessing': 'multiprocessing' in imports,
            'asyncio': 'asyncio' in imports,
            'flask': 'flask' in imports,
            'django': 'django' in imports,
            'sqlalchemy': 'sqlalchemy' in imports,
            'requests': 'requests' in imports,
            'pillow': 'PIL' in imports or 'pillow' in str(imports).lower(),
            'matplotlib': 'matplotlib' in imports,
            'pandas': 'pandas' in imports,
            'cv2': 'cv2' in imports,  # OpenCV
        }
        return frameworks


class NuitkaBuilderModule(ModuleBase):
    """
    Nuitka Builder Module that packages obfuscated Python applications into EXE files
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        default_config = {
            'enable_nuitka': False,
            'output_name': None,
            'onefile': True,
            'standalone': True,
            'windows_disable_console': True,
            'windows_icon': None,
            'windows_uac_admin': False,
            'enable_plugins': True,
            'plugins': [],
            'extra_imports': [],
            'nuitka_options': [],
            'python_version': None,
            'detected_imports': set(),
            'detected_frameworks': {},
        }
        default_config.update(config or {})
        super().__init__(default_config)

        self.import_analyzer = ImportAnalyzer()
        # Use detected_imports from config if provided, otherwise initialize empty
        self.detected_imports: Set[str] = self.config.get('detected_imports', set())
        self.detected_frameworks: Dict[str, bool] = self.config.get('detected_frameworks', {})

    def analyze_imports(self, project_path: Path) -> Set[str]:
        """
        Analyze imports in the project before obfuscation

        Args:
            project_path: Path to the project directory

        Returns:
            Set of detected third-party imports
        """
        # Skip if imports already detected (from config)
        if self.detected_imports:
            print(f"Using pre-configured detected imports: {self.detected_imports}")
            return self.detected_imports

        print(f"Analyzing imports in: {project_path}")
        all_imports = self.import_analyzer.analyze_directory(project_path)
        print(f"Found imports: {all_imports}")

        # Filter out standard library
        third_party_imports = self.import_analyzer.filter_standard_library(all_imports)
        print(f"Third-party imports: {third_party_imports}")

        # Detect frameworks
        self.detected_frameworks = self.import_analyzer.detect_frameworks(all_imports)
        print(f"Detected frameworks: {self.detected_frameworks}")

        self.detected_imports = third_party_imports
        return third_party_imports

    def get_nuitka_plugins(self) -> List[str]:
        """
        Get list of Nuitka plugins to enable based on detected frameworks

        Returns:
            List of Nuitka plugin arguments
        """
        plugins = []

        if not self.config.get('enable_plugins', True):
            return plugins

        # Auto-detect frameworks
        if self.detected_frameworks.get('tkinter'):
            plugins.append('--enable-plugin=tk-inter')

        if self.detected_frameworks.get('pyside6'):
            plugins.append('--enable-plugin=pyside6')

        if self.detected_frameworks.get('pyqt5'):
            plugins.append('--enable-plugin=pyqt5')

        if self.detected_frameworks.get('numpy'):
            plugins.append('--enable-plugin=numpy')

        if self.detected_frameworks.get('multiprocessing'):
            plugins.append('--enable-plugin=multiprocessing')

        # Add manually specified plugins
        for plugin in self.config.get('plugins', []):
            if not plugin.startswith('--enable-plugin='):
                plugin = f'--enable-plugin={plugin}'
            if plugin not in plugins:
                plugins.append(plugin)

        return plugins

    def build_nuitka_command(self, entry_point: Path, output_dir: Path) -> List[str]:
        """
        Build the Nuitka command line arguments

        Args:
            entry_point: Path to the entry point file
            output_dir: Path to the output directory

        Returns:
            List of command line arguments
        """
        cmd = [sys.executable, '-m', 'nuitka', '--lto=yes', '--deployment']

        # Output directory
        cmd.append(f'--output-dir={output_dir}')

        # Output name
        if self.config.get('output_name'):
            cmd.append(f'--output-filename={self.config["output_name"]}')

        # One-file mode
        if self.config.get('onefile', True):
            cmd.append('--onefile')

        # Standalone mode
        if self.config.get('standalone', True):
            cmd.append('--standalone')

        # Windows-specific options
        if sys.platform == 'win32':
            if self.config.get('windows_disable_console', True):
                cmd.append('--windows-disable-console')

            if self.config.get('windows_icon'):
                cmd.append(f'--windows-icon-from-ico={self.config["windows_icon"]}')

            if self.config.get('windows_uac_admin', False):
                cmd.append('--windows-uac-admin')

        # Add plugins
        plugins = self.get_nuitka_plugins()
        cmd.extend(plugins)

        # Add custom Nuitka options
        cmd.extend(self.config.get('nuitka_options', []))

        # Python version
        if self.config.get('python_version'):
            cmd.append(f'--python-version={self.config["python_version"]}')

        # Entry point
        cmd.append(str(entry_point))

        return cmd

    def validate_config(self) -> bool:
        """
        Validate the module's configuration

        Returns:
            True if configuration is valid, False otherwise
        """
        if not self.config.get('enable_nuitka', False):
            return True  # Nuitka is disabled, config is valid

        # Check if Nuitka is installed
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'nuitka', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                print(f"Warning: Nuitka may not be properly installed: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("Warning: Timeout checking Nuitka installation")
        except FileNotFoundError:
            print("Warning: Nuitka is not installed. Install with: pip install nuitka")
            return False

        return True

    def process(self, project_path: Path, output_path: Path) -> bool:
        """
        Package the obfuscated project into an EXE using Nuitka

        Args:
            project_path: Path to the original project (used for initial import analysis)
            output_path: Path to the obfuscated output directory (contains entry point)

        Returns:
            True if packaging was successful, False otherwise
        """
        if not self.config.get('enable_nuitka', False):
            print("Nuitka packaging is disabled")
            return True

        entry_point = Path(self.config.get('entry_point', ''))
        if not entry_point:
            print("Error: Entry point not specified for Nuitka packaging")
            return False

        # The entry point should be in the output_path (already obfuscated)
        full_entry_path = output_path / entry_point
        if not full_entry_path.exists():
            print(f"Error: Entry point not found: {full_entry_path}")
            return False

        # Use already analyzed imports from the ORIGINAL project (before obfuscation)
        # This ensures we capture all real imports before they get obfuscated
        if not self.detected_imports:
            print(f"Analyzing imports from original project: {project_path}")
            self.analyze_imports(project_path)

        print(f"Packaging with Nuitka: {full_entry_path}")
        print(f"Included modules: {self.detected_imports}")

        # Build Nuitka output directory (separate from obfuscated output)
        nuitka_output = output_path.parent / 'nuitka_dist'

        # Clean up existing nuitka_dist folder
        if nuitka_output.exists():
            shutil.rmtree(nuitka_output)

        # Build the command
        cmd = self.build_nuitka_command(full_entry_path, nuitka_output)

        print(f"Running Nuitka command: {' '.join(cmd)}")

        try:
            # Run Nuitka
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.get('timeout', 600)  # 10 minutes default
            )

            if result.returncode != 0:
                print(f"Nuitka error: {result.stderr}")
                print(f"Nuitka output: {result.stdout}")
                return False

            print(f"Nuitka packaging completed successfully!")
            print(f"Output directory: {nuitka_output}")

            # Clean up the output directory (copy EXE or .dist folder)
            self._cleanup_output_directory(output_path, nuitka_output)

            return True

        except subprocess.TimeoutExpired:
            print("Error: Nuitka packaging timed out")
            return False
        except Exception as e:
            print(f"Error during Nuitka packaging: {e}")
            return False

    def _cleanup_output_directory(self, output_path: Path, nuitka_output: Path):
        """
        Clean up the output directory after Nuitka compilation

        For onefile mode: copy only the EXE file from nuitka_dist root
        For standalone mode: copy all contents from nuitka_dist

        Args:
            output_path: Path to the main output directory
            nuitka_output: Path to Nuitka's output directory
        """
        import shutil

        print(f"Cleaning up output directory: {output_path}")

        if self.config.get('onefile', True):
            # Onefile mode: copy only the EXE file
            exe_files = list(nuitka_output.glob('*.exe'))
            if not exe_files:
                print("Warning: No EXE files found")
                return

            main_exe = exe_files[0]
            dest = output_path / main_exe.name
            shutil.copy2(main_exe, dest)
            print(f"EXE copied to: {dest}")

            # Remove all other files from output_path
            for item in output_path.iterdir():
                if item.name != main_exe.name:
                    try:
                        if item.is_file():
                            item.unlink()
                            print(f"Removed: {item}")
                        elif item.is_dir():
                            shutil.rmtree(item)
                            print(f"Removed directory: {item}")
                    except Exception as e:
                        print(f"Warning: Could not remove {item}: {e}")

            print(f"Output directory cleaned. Kept: {main_exe.name}")

        else:
            # Standalone mode: copy all contents from nuitka_dist
            print(f"Contents of nuitka_output ({nuitka_output}):")
            for item in nuitka_output.iterdir():
                print(f"  - {item.name} ({'dir' if item.is_dir() else 'file'})")

            # First, remove old contents from output_path
            for item in output_path.iterdir():
                try:
                    if item.is_file():
                        item.unlink()
                        print(f"Removed: {item}")
                    elif item.is_dir():
                        shutil.rmtree(item)
                        print(f"Removed directory: {item}")
                except Exception as e:
                    print(f"Warning: Could not remove {item}: {e}")

            # Copy all contents from nuitka_dist to output_path
            for item in nuitka_output.iterdir():
                dest = output_path / item.name
                if item.is_file():
                    shutil.copy2(item, dest)
                    print(f"Copied file: {item.name}")
                elif item.is_dir():
                    shutil.copytree(item, dest)
                    print(f"Copied directory: {item.name}")

            print(f"Standalone contents copied from {nuitka_output} to {output_path}")

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about this module

        Returns:
            Dictionary containing module information
        """
        info = super().get_info()
        info['detected_imports'] = list(self.detected_imports)
        info['detected_frameworks'] = self.detected_frameworks
        return info
