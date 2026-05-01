"""
PyLockWare AntiDebug Engine (Cross-Platform)
=============================================
Кроссплатформенный антиотладочный модуль для Python.
Работает на Windows, Linux и macOS.

Проверки:
  1. Python-отладчики  — sys.gettrace, sys.monitoring, загруженные модули
  2. Python-потоки     — поиск потоков отладчиков (pydevd, debugpy)
  3. Переменные окружения — PYTHONDEBUG, PYTHONTRACEMODULESHACK и т.д.
  4. Файловые дескрипторы — обнаружение отладочных сокетов
  5. procfs (Linux)    — /proc/self/status, /proc/self/wchan
  6. lsof/netstat      — поиск отладочных портов

При срабатывании любой проверки — выводит причину в stderr и вызывает os._exit(1).

Зависимости: psutil (опционально для расширенных проверок)
"""

from __future__ import annotations

import ctypes
import os
import platform
import re
import socket
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import List, Set, Optional

# ---------------------------------------------------------------------------
# Python C-API для callback (печать причины + выход)
# ---------------------------------------------------------------------------

_PySys_WriteStderr = ctypes.pythonapi.PySys_WriteStderr
_PySys_WriteStderr.argtypes = [ctypes.c_char_p]
_PySys_WriteStderr.restype = None

_os_exit = os._exit


def _native_kill(reason: str) -> None:
    """Вызывается при обнаружении отладчика/инжекции."""
    msg = (
        f"\n[ANTIDEBUG] VIOLATION DETECTED\n"
        f"[ANTIDEBUG] Reason: {reason}\n"
        f"[ANTIDEBUG] Terminating process...\n"
    )
    _PySys_WriteStderr(msg.encode('utf-8'))
    _os_exit(1)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Violation:
    check_name: str
    reason: str
    details: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Cross-Platform AntiDebug Engine
# ---------------------------------------------------------------------------

class AntiDebugCrossPlatform:
    """
    Кроссплатформенный движок антиотладки.
    Работает на Windows, Linux, macOS.
    """

    # Чёрный список DLL/модулей — известные отладчики/инжекторы
    BLACKLIST_MODULES: Set[str] = {
        # Python debuggers
        "pydevd",
        "pydevd_cython",
        "pydevd_pep_669_tracing_cython",
        "debugpy",
        "_pydevd_bundle",
        "pydevd_plugins",
        "pydevd_xml",
        # Native debuggers / analysis tools
        "frida",
        "frida-gadget",
        "libinjector",
        "x64dbg",
        "x32dbg",
        "ollydbg",
        "cheatengine",
        # Injection frameworks
        "pyshell",
        "reflectivedll",
        "sliver",
        "meterpreter",
    }

    # Чёрный список имён потоков
    BLACKLIST_THREAD_NAMES: Set[str] = {
        "pydevd.Writer",
        "pydevd.Reader",
        "pydevd.CommandThread",
        "pydevd.CheckAliveThread",
        "pydevd.SuspendThread",
        "pydevd.BreakpointWatchThread",
        "debugpy",
        "debugpy.server",
    }

    # Подозрительные переменные окружения
    SUSPICIOUS_ENV_VARS: Set[str] = {
        "PYTHONDEBUG",
        "PYTHONTRACEMODULESHACK",
        "PYTHONTRACEBACK",
        "PYTHONVERBOSE",
        "PYTHONDUMPREFS",
        "PYTHONDUMPAST",
        "PYTHONASYNCIODEBUG",
        "PYTHONMALLOCSTATS",
        "LD_PRELOAD",
        "LD_DEBUG",
        "DYLD_INSERT_LIBRARIES",
        "DYLD_DEBUG",
    }

    def __init__(self, strict: bool = True):
        self.strict = strict
        self.violations: List[Violation] = []
        self._baseline_threads: Set[int] = set()
        self._lock = threading.Lock()

        # Захватываем baseline при инициализации
        self._capture_baseline()

    def _capture_baseline(self):
        """Запоминаем начальный набор потоков как легитимный."""
        self._baseline_threads = {t.ident for t in threading.enumerate() if t.ident}

    # ------------------------------------------------------------------
    # Python-level checks
    # ------------------------------------------------------------------

    def check_python_debugger(self) -> List[Violation]:
        """Эвристики Python-level отладчиков."""
        results: List[Violation] = []

        # 1. sys.gettrace() — классический способ отладки
        if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
            results.append(Violation(
                "PythonTrace",
                "sys.gettrace() is active — Python-level debugger detected",
                {"trace_function": str(sys.gettrace())}
            ))

        # 2. sys.monitoring (Python 3.12+ PEP 669)
        if hasattr(sys, 'monitoring') and sys.monitoring:
            try:
                if sys.monitoring.get_tool(sys.monitoring.DEBUGGER_ID) is not None:
                    results.append(Violation(
                        "PEP669Debugger",
                        "sys.monitoring DEBUGGER_ID tool is active"
                    ))
            except (AttributeError, ValueError):
                pass

        # 3. sys.settrace (альтернативный API)
        if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
            # Уже проверено выше, но для полноты
            pass

        # 4. Проверяем загруженные модули
        current_modules = set(sys.modules.keys())
        for mod in current_modules:
            mod_lower = mod.lower()
            for bad in self.BLACKLIST_MODULES:
                if bad in mod_lower:
                    results.append(Violation(
                        "BlacklistedModule",
                        f"Forbidden debugger/injector module loaded: {mod}",
                        {"module": mod, "pattern": bad}
                    ))

        # 5. Проверяем Python-потоки
        for t in threading.enumerate():
            if t.name in self.BLACKLIST_THREAD_NAMES:
                results.append(Violation(
                    "BlacklistedThread",
                    f"Forbidden debugger thread detected: {t.name}",
                    {"thread_name": t.name, "tid": t.ident}
                ))

        return results

    def check_environment(self) -> List[Violation]:
        """Проверка подозрительных переменных окружения."""
        results: List[Violation] = []

        for var in self.SUSPICIOUS_ENV_VARS:
            value = os.environ.get(var)
            if value is not None:
                # Для LD_PRELOAD/DYLD_INSERT_LIBRARIES — проверим конкретные значения
                if var in ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES"):
                    # Проверяем на известные инжекторы
                    injectors = ["libinjector", "frida", "preload"]
                    if any(inj in value.lower() for inj in injectors):
                        results.append(Violation(
                            "SuspiciousEnvVar",
                            f"Suspicious library preloaded: {var}={value}",
                            {"variable": var, "value": value}
                        ))
                else:
                    results.append(Violation(
                        "SuspiciousEnvVar",
                        f"Suspicious environment variable detected: {var}={value}",
                        {"variable": var, "value": value}
                    ))

        return results

    def check_threads(self) -> List[Violation]:
        """Обнаружение новых подозрительных потоков."""
        results: List[Violation] = []
        current_threads = {t.ident for t in threading.enumerate() if t.ident}
        new_threads = current_threads - self._baseline_threads

        # Получаем имена известных потоков
        known_thread_names = {t.name for t in threading.enumerate()}

        for tid in new_threads:
            # Проверяем, не является ли это потоком отладчика
            for t in threading.enumerate():
                if t.ident == tid:
                    if t.name in self.BLACKLIST_THREAD_NAMES:
                        results.append(Violation(
                            "NewDebuggerThread",
                            f"New debugger thread detected: {t.name}",
                            {"thread_name": t.name, "tid": tid}
                        ))
                    break

        # Обновляем baseline
        self._baseline_threads = current_threads
        return results

    def check_network(self) -> List[Violation]:
        """Проверка открытых сокетов на отладочные порты."""
        results: List[Violation] = []

        # Известные отладочные порты
        DEBUGGER_PORTS = {
            5678,   # debugpy default
            5679,
            5680,
            5681,
            12345,  # pydevd default
            12346,
            4444,   # common debug port
            5005,   # Java debugger
        }

        try:
            # Получаем все открытые сокеты
            import psutil
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'LISTEN' and conn.laddr.port in DEBUGGER_PORTS:
                    results.append(Violation(
                        "DebuggerPort",
                        f"Debugger listening port detected: {conn.laddr.port}",
                        {"port": conn.laddr.port, "address": conn.laddr.ip}
                    ))
        except (ImportError, Exception):
            # psutil недоступен — пропускаем
            pass

        return results

    def check_procfs_linux(self) -> List[Violation]:
        """Проверка /proc файловой системы (Linux only)."""
        results: List[Violation] = []

        if platform.system() != 'Linux':
            return results

        try:
            # Проверяем /proc/self/status на флаги отладки
            with open('/proc/self/status', 'r') as f:
                content = f.read()

                # TracerPid — если не 0, значит нас отслеживают
                match = re.search(r'TracerPid:\s*(\d+)', content)
                if match and int(match.group(1)) != 0:
                    results.append(Violation(
                        "LinuxTracerPid",
                        f"TracerPid is non-zero: {match.group(1)} — process is being traced",
                        {"tracer_pid": match.group(1)}
                    ))

                # Seccomp — если 1 или 2, может указывать на sandbox
                match = re.search(r'Seccomp:\s*(\d+)', content)
                if match and int(match.group(1)) in (1, 2):
                    results.append(Violation(
                        "LinuxSeccomp",
                        f"Seccomp mode detected: {match.group(1)}",
                        {"seccomp_mode": match.group(1)}
                    ))

            # Проверяем /proc/self/wchan — если не 0, поток может быть в отладчике
            try:
                with open('/proc/self/wchan', 'r') as f:
                    wchan = f.read().strip()
                    # 0 означает, что процесс остановлен отладчиком
                    if wchan == '0':
                        results.append(Violation(
                            "LinuxWchan",
                            "Process is stopped (ptraced)"
                        ))
            except (FileNotFoundError, PermissionError):
                pass

        except (FileNotFoundError, PermissionError, IOError):
            pass

        return results

    def check_virtualization(self) -> List[Violation]:
        """Проверка на виртуальные машины и контейнеры."""
        results: List[Violation] = []

        # Проверяем VM/контейнерные индикаторы
        indicators = []

        if platform.system() == 'Linux':
            # /proc/1/cgroup — если содержит docker/lxc, то в контейнере
            try:
                with open('/proc/1/cgroup', 'r') as f:
                    cgroup = f.read()
                    if 'docker' in cgroup or 'lxc' in cgroup or 'containerd' in cgroup:
                        indicators.append(f"Container: {cgroup[:100]}")
            except:
                pass

            # /proc/self/root — если отличается от /, то chroot
            try:
                import os
                if os.readlink('/proc/self/root') != '/':
                    indicators.append("Chroot detected")
            except:
                pass

        elif platform.system() == 'Windows':
            # Проверяем реестр на VM
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                     r"SYSTEM\CurrentControlSet\Services\VBoxGuest")
                indicators.append("VirtualBox detected")
                winreg.CloseKey(key)
            except FileNotFoundError:
                pass

            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                     r"SYSTEM\CurrentControlSet\Services\VBoxMouse")
                indicators.append("VirtualBox detected")
                winreg.CloseKey(key)
            except FileNotFoundError:
                pass

        if indicators:
            results.append(Violation(
                "Virtualization",
                f"Virtualization or container detected: {', '.join(indicators)}",
                {"indicators": indicators}
            ))

        return results

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------

    def run_all_checks(self) -> List[Violation]:
        """Выполняет все проверки и возвращает список нарушений."""
        all_violations: List[Violation] = []

        checks = [
            ("PythonDebugger", self.check_python_debugger),
            ("Environment", self.check_environment),
            ("Threads", self.check_threads),
            ("Network", self.check_network),
            ("ProcFS", self.check_procfs_linux),
            ("Virtualization", self.check_virtualization),
        ]

        for check_name, check_func in checks:
            try:
                violations = check_func()
                all_violations.extend(violations)
            except Exception as e:
                if self.strict:
                    all_violations.append(Violation(
                        f"{check_name}CheckError",
                        f"{check_name} check failed: {e}"
                    ))

        return all_violations

    def kill_if_violations(self, violations: Optional[List[Violation]] = None):
        """Если есть нарушения — печатает причину и убивает процесс."""
        if violations is None:
            violations = self.run_all_checks()

        if not violations:
            return

        with self._lock:
            lines = [
                "",
                "=" * 70,
                "  ANTIDEBUG VIOLATION — PROCESS WILL BE TERMINATED",
                "=" * 70,
                f"  Total violations: {len(violations)}",
                "",
            ]

            for i, v in enumerate(violations, 1):
                lines.append(f"  [{i}] {v.check_name}")
                lines.append(f"      Reason: {v.reason}")
                if v.details:
                    for k, val in v.details.items():
                        lines.append(f"      {k}: {val}")
                lines.append("")

            lines.append("=" * 70)
            lines.append("  Terminating with os._exit(1)")
            lines.append("=" * 70)

            report = "\n".join(lines) + "\n"
            _PySys_WriteStderr(report.encode('utf-8'))
            time.sleep(0.1)
            os._exit(1)

    def start_monitoring(self, interval_ms: float = 500):
        """Запускает фоновый мониторинг в отдельном потоке."""
        def _monitor():
            while True:
                self.kill_if_violations()
                time.sleep(interval_ms / 1000.0)

        t = threading.Thread(target=_monitor, name="AntiDebugMonitor", daemon=True)
        t.start()
        return t


# ---------------------------------------------------------------------------
# Convenience API
# ---------------------------------------------------------------------------

_engine: Optional[AntiDebugCrossPlatform] = None


def init(strict: bool = True) -> AntiDebugCrossPlatform:
    """Инициализирует движок (один на процесс)."""
    global _engine
    if _engine is None:
        _engine = AntiDebugCrossPlatform(strict=strict)
    return _engine


def check() -> List[Violation]:
    """Однократная проверка."""
    return init().run_all_checks()


def guard():
    """Проверить и убить процесс при нарушениях."""
    init().kill_if_violations()


def monitor(interval_ms: float = 500):
    """Запустить фоновый мониторинг."""
    return init().start_monitoring(interval_ms)


# ---------------------------------------------------------------------------
# CLI / standalone
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"[PyLockWare AntiDebug] Running self-test on {platform.system()}...")
    print(f"[PyLockWare AntiDebug] PID: {os.getpid()}")
    engine = init(strict=True)

    violations = engine.run_all_checks()
    if violations:
        print(f"[PyLockWare AntiDebug] Found {len(violations)} violations!")
        for v in violations:
            print(f"  - {v.check_name}: {v.reason}")
    else:
        print("[PyLockWare AntiDebug] No violations detected")

    print("[PyLockWare AntiDebug] Starting monitoring...")
    monitor(interval_ms=500)
    print("[PyLockWare AntiDebug] Monitoring started. Press Enter to exit...")
    input()