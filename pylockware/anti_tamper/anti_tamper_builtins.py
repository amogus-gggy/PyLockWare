"""
Anti-Tamper Module for Python Builtins — Realtime Call-Interposition

Changes vs previous:
  - No sampling: checks every function call (event='call' only)
  - Inspects caller frame (f_back) to catch local/global shadowing immediately
  - Sentinel object to distinguish "key missing" from "value is None"
  - Minimal overhead: returns None from tracer to skip line-by-line tracing
"""

import sys
import os
import builtins
import ctypes
import threading
import time
import inspect

# ── Snapshot at import time ─────────────────────────────────────────────────

_ORIGINAL_BUILTINS: dict = {
    name: getattr(builtins, name)
    for name in dir(builtins)
    if not name.startswith("_")
}

_CRITICAL_NAMES = (
    "open", "eval", "exec", "compile", "__import__",
    "input", "print", "exit", "quit", "breakpoint",
)

_CRITICAL_CHECKS: tuple = tuple(
    (name, _ORIGINAL_BUILTINS[name])
    for name in _CRITICAL_NAMES
    if name in _ORIGINAL_BUILTINS
)

_ALL_CHECKS: tuple = tuple(_ORIGINAL_BUILTINS.items())

_QUALNAME_CHECKS: tuple = tuple(
    (name, getattr(_ORIGINAL_BUILTINS[name], "__qualname__", None))
    for name in ("open", "eval", "exec", "compile", "__import__")
    if name in _ORIGINAL_BUILTINS
    and hasattr(_ORIGINAL_BUILTINS[name], "__qualname__")
)

_getattr = getattr
_builtins_module = builtins
_MODULE_GLOBALS: dict | None = None
_MISSING = object()  # sentinel to tell "no key" from "value is None"

# Standard library modules that legitimately shadow builtin names
_STDLIB_MODULES = frozenset({
    're', 'os', 'sys', 'io', 'pathlib', 'subprocess', 'shutil',
    'ast', 'dis', 'inspect', 'importlib', 'types', 'typing',
    'collections', 'itertools', 'functools', 'operator',
    'contextlib', 'abc', 'copy', 'pickle', 'json', 'xml',
    'html', 'email', 'urllib', 'http', 'ftplib', 'smtplib',
    'sqlite3', 'dbm', 'csv', 'configparser', 'logging',
    'argparse', 'getopt', 'readline', 'cmd', 'shlex',
    'threading', 'multiprocessing', 'concurrent', 'queue',
    'socket', 'ssl', 'select', 'asyncio', 'signal',
    'struct', 'codecs', 'encodings', 'locale', 'gettext',
    'platform', 'ctypes', 'array', 'mmap', 'resource',
    'gc', 'weakref', 'copyreg', 'traceback', 'linecache',
    'tokenize', 'keyword', 'token', 'tabnanny', 'pydoc',
    'doctest', 'unittest', 'test', 'lib2to3', 'distutils',
    'ensurepip', 'venv', 'zipapp', 'zipfile', 'tarfile',
    'gzip', 'bz2', 'lzma', 'zlib', 'hashlib', 'hmac',
    'secrets', 'random', 'statistics', 'decimal', 'fractions',
    'numbers', 'math', 'cmath', 'time', 'datetime', 'calendar',
    'heapq', 'bisect', 'reprlib', 'pprint', 'textwrap',
    'string', 'difflib', 'stringprep', 'unicodedata',
    'rlcompleter', 'pdb', 'profile', 'pstats', 'timeit',
    'trace', 'cProfile', 'warnings', 'dataclasses', 'enum',
    'graphlib', 'fileinput', 'tempfile', 'glob', 'fnmatch',
    'pkgutil', 'modulefinder', 'runpy', 'importlib.util',
    'importlib.machinery', 'importlib.resources', 'sysconfig',
    '_thread', 'dummy_threading', 'contextvars', 'decimal',
    'importlib.resources.abc', 'importlib.resources',
    'os.path', 'ntpath', 'posixpath',
})

# Check if a filename belongs to the Python standard library
import sys as _sys
def _is_stdlib_file(filename: str) -> bool:
    """Check if a file is part of the Python standard library."""
    if not filename:
        return False
    
    # Normalize path
    filename_lower = filename.lower().replace('\\', '/')
    
    # Check against known stdlib paths
    stdlib_paths = [
        _sys.prefix.lower().replace('\\', '/'),
        _sys.base_prefix.lower().replace('\\', '/'),
    ]
    
    for sp in stdlib_paths:
        if filename_lower.startswith(sp + '/') or filename_lower.startswith(sp + '\\'):
            return True
    
    # Also check for Python installation directories
    python_lib_patterns = [
        '/lib/python', '\\lib\\python',
        '/Lib/', '\\Lib\\',
        '/Lib/site-packages/', '\\Lib\\site-packages\\',  # but NOT site-packages
    ]
    
    for pattern in python_lib_patterns:
        if pattern.lower() in filename_lower:
            return True
    
    return False

# ── Crash handler ────────────────────────────────────────────────────────────

def _hard_crash(reason: str) -> None:
    sys.stderr.write(f"\n[ANTI-TAMPER] Tampered runtime detected: {reason}\n")
    sys.stderr.flush()
    try:
        ctypes.memset(0, 1, 1)
    except Exception:
        os._exit(137)


# ── Fast check — runs on every function call (caller frame) ──────────────────

def _fast_check(caller_frame) -> None:
    """Realtime check: builtins identity + shadowing in caller's locals/globals."""
    if caller_frame is None:
        return

    # 1. Builtins identity
    for name, original in _CRITICAL_CHECKS:
        if _getattr(_builtins_module, name, None) is not original:
            _hard_crash(f"builtins.{name} replaced")

    # 2. Shadowing in caller locals  (def f(): compile = print; compile(...))
    loc = caller_frame.f_locals
    for name, original in _CRITICAL_CHECKS:
        val = loc.get(name, _MISSING)
        if val is not _MISSING and val is not original:
            # Skip stdlib modules
            filename = caller_frame.f_code.co_filename
            if not _is_stdlib_file(filename):
                _hard_crash(
                    f"local '{name}' shadowed in "
                    f"{caller_frame.f_code.co_filename}:{caller_frame.f_code.co_name}"
                )

    # 3. Shadowing in caller globals (module-level: compile = print)
    # Skip check for standard library modules
    glo = caller_frame.f_globals
    module_name = glo.get('__name__', '')
    
    # Skip check for standard library modules (by name or file path)
    module_base = module_name.split('.')[0]
    filename = glo.get('__file__', '')
    
    if module_base not in _STDLIB_MODULES and not _is_stdlib_file(filename):
        for name, original in _CRITICAL_CHECKS:
            val = glo.get(name, _MISSING)
            if val is not _MISSING and val is not original:
                _hard_crash(
                    f"global '{name}' shadowed in module "
                    f"{module_name}"
                )


# ── Full check — background thread (deep scan) ───────────────────────────────

def _full_check() -> None:
    for name, original in _ALL_CHECKS:
        current = _getattr(_builtins_module, name, None)
        if current is not original:
            _hard_crash(f"builtins.{name} replaced (full check)")
        if type(current) is not type(original):
            _hard_crash(
                f"builtins.{name} type changed: "
                f"{type(original).__name__} -> {type(current).__name__}"
            )

    for name, orig_qn in _QUALNAME_CHECKS:
        current = _getattr(_builtins_module, name, None)
        curr_qn = _getattr(current, "__qualname__", None)
        if curr_qn != orig_qn:
            _hard_crash(f"builtins.{name} qualname changed")

    if _MODULE_GLOBALS is not None:
        for name, original in _CRITICAL_CHECKS:
            val = _MODULE_GLOBALS.get(name, _MISSING)
            if val is not _MISSING and val is not original:
                _hard_crash(f"global '{name}' shadowed in anti_tamper module")

    # Walk entire stack of all threads (expensive, therefore in background)
    frame = inspect.currentframe()
    try:
        while frame:
            loc = frame.f_locals
            for name, original in _CRITICAL_CHECKS:
                val = loc.get(name, _MISSING)
                if val is not _MISSING and val is not original:
                    _hard_crash(
                        f"local '{name}' shadowed in "
                        f"{frame.f_code.co_filename}:{frame.f_code.co_name}"
                    )
            frame = frame.f_back
    finally:
        del frame


# ── sys.settrace path (Python < 3.12 or fallback) ───────────────────────────

def _tracer(frame, event, arg):
    """
    On every 'call' event inspect the *caller* frame for shadowing.
    Returning None disables line-by-line tracing inside the callee,
    keeping overhead minimal.
    """
    if event == 'call':
        caller = frame.f_back
        if caller is not None:
            _fast_check(caller)
    return None


# ── sys.monitoring path (Python 3.12+) ───────────────────────────────────────

_MONITORING_TOOL_ID = 5


def _install_sys_monitoring() -> None:
    mon = sys.monitoring
    mon.use_tool_id(_MONITORING_TOOL_ID, "anti_tamper")

    def _on_call(code, instruction_offset, callable_, arg0):
        # sys._getframe(1) is the Python frame that triggered the call
        try:
            caller = sys._getframe(1)
        except ValueError:
            return
        try:
            _fast_check(caller)
        finally:
            del caller

    mon.set_events(_MONITORING_TOOL_ID, mon.events.CALL)
    mon.register_callback(_MONITORING_TOOL_ID, mon.events.CALL, _on_call)


def _uninstall_sys_monitoring() -> None:
    try:
        mon = sys.monitoring
        mon.set_events(_MONITORING_TOOL_ID, mon.events.NO_EVENTS)
        mon.register_callback(_MONITORING_TOOL_ID, mon.events.CALL, None)
        mon.free_tool_id(_MONITORING_TOOL_ID)
    except Exception:
        pass


# ── Background monitoring thread ─────────────────────────────────────────────

MONITOR_INTERVAL: float = 1.0
_monitoring_active: bool = False
_monitor_thread: threading.Thread | None = None


def _monitor_loop() -> None:
    while _monitoring_active:
        try:
            _full_check()
        except SystemExit:
            raise
        except Exception as exc:
            _hard_crash(f"monitor raised unexpected exception: {exc!r}")
        time.sleep(MONITOR_INTERVAL)


# ── Public API ───────────────────────────────────────────────────────────────

def install() -> None:
    global _monitoring_active, _monitor_thread, _MODULE_GLOBALS
    _MODULE_GLOBALS = globals()
    _full_check()

    if sys.version_info >= (3, 12):
        try:
            _install_sys_monitoring()
        except Exception:
            sys.settrace(_tracer)
            threading.settrace(_tracer)
    else:
        sys.settrace(_tracer)
        threading.settrace(_tracer)

    _monitoring_active = True
    _monitor_thread = threading.Thread(
        target=_monitor_loop,
        name="anti-tamper-monitor",
        daemon=True,
    )
    _monitor_thread.start()


def uninstall() -> None:
    global _monitoring_active
    _monitoring_active = False
    if sys.version_info >= (3, 12):
        _uninstall_sys_monitoring()
    else:
        sys.settrace(None)
        threading.settrace(None)


# ── Auto-install ─────────────────────────────────────────────────────────────

install()


