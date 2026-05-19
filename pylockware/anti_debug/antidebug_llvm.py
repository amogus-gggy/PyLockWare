from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import json
import os
import platform
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import Callable, List, Set


try:
    from llvmlite import ir, binding as llvm
except ImportError:
    raise ImportError("llvmlite is required. Install: pip install llvmlite")



ntdll    = ctypes.WinDLL("ntdll.dll")
kernel32 = ctypes.WinDLL("kernel32.dll")

NTSTATUS = ctypes.c_long
ULONG    = ctypes.c_ulong
ULONG_PTR = ctypes.c_uint64 if platform.machine().endswith('64') else ctypes.c_uint32
PVOID    = ctypes.c_void_p

NtQIP = ntdll.NtQueryInformationProcess
NtQIP.restype  = NTSTATUS
NtQIP.argtypes = [wt.HANDLE, ULONG, PVOID, ULONG, ctypes.POINTER(ULONG)]

NtQIT = ntdll.NtQueryInformationThread
NtQIT.restype  = NTSTATUS
NtQIT.argtypes = [wt.HANDLE, ULONG, PVOID, ULONG, ctypes.POINTER(ULONG)]

OpenThread = kernel32.OpenThread
OpenThread.restype  = wt.HANDLE
OpenThread.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]

THREAD_QUERY_INFORMATION = 0x0040
THREAD_GET_CONTEXT       = 0x0008

GetThreadContext = kernel32.GetThreadContext
GetThreadContext.restype  = wt.BOOL

CloseHandle = kernel32.CloseHandle
CloseHandle.restype  = wt.BOOL
CloseHandle.argtypes = [wt.HANDLE]

CheckRemoteDebuggerPresent = kernel32.CheckRemoteDebuggerPresent
CheckRemoteDebuggerPresent.restype  = wt.BOOL
CheckRemoteDebuggerPresent.argtypes = [wt.HANDLE, ctypes.POINTER(wt.BOOL)]

GetModuleFileNameA = kernel32.GetModuleFileNameA
GetModuleFileNameA.restype  = wt.DWORD
GetModuleFileNameA.argtypes = [wt.HMODULE, ctypes.c_char_p, wt.DWORD]

IS_64BIT = platform.machine().endswith('64')

# Toolhelp32
TH32CS_SNAPTHREAD = 0x00000004
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPMODULE32 = 0x00000010

class THREADENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize",             wt.DWORD),
        ("cntUsage",           wt.DWORD),
        ("th32ThreadID",       wt.DWORD),
        ("th32OwnerProcessID", wt.DWORD),
        ("tpBasePri",          ctypes.c_long),
        ("tpDeltaPri",         ctypes.c_long),
        ("dwFlags",            wt.DWORD),
    ]

class MODULEENTRY32(ctypes.Structure):
    _fields_ = [
        ("dwSize",        wt.DWORD),
        ("th32ModuleID",  wt.DWORD),
        ("th32ProcessID", wt.DWORD),
        ("GlblcntUsage",  wt.DWORD),
        ("ProccntUsage",  wt.DWORD),
        ("modBaseAddr",   ctypes.POINTER(ctypes.c_byte)),
        ("modBaseSize",   wt.DWORD),
        ("hModule",       wt.HMODULE),
        ("szModule",      ctypes.c_char * 256),
        ("szExePath",     ctypes.c_char * 260),
    ]

_CreateToolhelp32Snapshot = kernel32.CreateToolhelp32Snapshot
_CreateToolhelp32Snapshot.restype  = wt.HANDLE
_CreateToolhelp32Snapshot.argtypes = [wt.DWORD, wt.DWORD]

_Thread32First = kernel32.Thread32First
_Thread32First.restype  = wt.BOOL
_Thread32First.argtypes = [wt.HANDLE, ctypes.POINTER(THREADENTRY32)]

_Thread32Next = kernel32.Thread32Next
_Thread32Next.restype  = wt.BOOL
_Thread32Next.argtypes = [wt.HANDLE, ctypes.POINTER(THREADENTRY32)]

_Module32First = kernel32.Module32First
_Module32First.restype  = wt.BOOL
_Module32First.argtypes = [wt.HANDLE, ctypes.POINTER(MODULEENTRY32)]

_Module32Next = kernel32.Module32Next
_Module32Next.restype  = wt.BOOL
_Module32Next.argtypes = [wt.HANDLE, ctypes.POINTER(MODULEENTRY32)]

INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value

_VirtualQuery = kernel32.VirtualQuery
_VirtualQuery.restype  = ctypes.c_size_t
_VirtualQuery.argtypes = [PVOID, ctypes.c_void_p, ctypes.c_size_t]

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress",       PVOID),
        ("AllocationBase",    PVOID),
        ("AllocationProtect", wt.DWORD),
        ("PartitionId",       wt.WORD),
        ("RegionSize",        ctypes.c_size_t),
        ("State",             wt.DWORD),
        ("Protect",           wt.DWORD),
        ("Type",              wt.DWORD),
    ]


class CONTEXT_x64(ctypes.Structure):
    _fields_ = [
        ("P1Home",   ctypes.c_uint64), ("P2Home",   ctypes.c_uint64),
        ("P3Home",   ctypes.c_uint64), ("P4Home",   ctypes.c_uint64),
        ("P5Home",   ctypes.c_uint64), ("P6Home",   ctypes.c_uint64),
        ("ContextFlags", ctypes.c_uint32), ("MxCsr", ctypes.c_uint32),
        ("SegCs", ctypes.c_uint16), ("SegDs", ctypes.c_uint16),
        ("SegEs", ctypes.c_uint16), ("SegFs", ctypes.c_uint16),
        ("SegGs", ctypes.c_uint16), ("SegSs", ctypes.c_uint16),
        ("EFlags", ctypes.c_uint32),
        ("Dr0", ctypes.c_uint64), ("Dr1", ctypes.c_uint64),
        ("Dr2", ctypes.c_uint64), ("Dr3", ctypes.c_uint64),
        ("Dr6", ctypes.c_uint64), ("Dr7", ctypes.c_uint64),
        ("Rax", ctypes.c_uint64), ("Rcx", ctypes.c_uint64),
        ("Rdx", ctypes.c_uint64), ("Rbx", ctypes.c_uint64),
        ("Rsp", ctypes.c_uint64), ("Rbp", ctypes.c_uint64),
        ("Rsi", ctypes.c_uint64), ("Rdi", ctypes.c_uint64),
        ("R8",  ctypes.c_uint64), ("R9",  ctypes.c_uint64),
        ("R10", ctypes.c_uint64), ("R11", ctypes.c_uint64),
        ("R12", ctypes.c_uint64), ("R13", ctypes.c_uint64),
        ("R14", ctypes.c_uint64), ("R15", ctypes.c_uint64),
        ("Rip", ctypes.c_uint64),
    ]

CONTEXT_DEBUG_REGISTERS = 0x00000010



_PySys_WriteStderr = ctypes.pythonapi.PySys_WriteStderr
_PySys_WriteStderr.argtypes = [ctypes.c_char_p]
_PySys_WriteStderr.restype = None


_PyErr_PrintEx = ctypes.pythonapi.PyErr_PrintEx
_PyErr_PrintEx.argtypes = [ctypes.c_int]
_PyErr_PrintEx.restype = None


_os_exit = os._exit

@ctypes.CFUNCTYPE(None, ctypes.c_char_p)
def _native_kill(reason_cstr: bytes) -> None:
    """Вызывается из JIT-кода при обнаружении отладчика/инжекции."""
    try:
        reason = reason_cstr.decode('utf-8', errors='replace')
    except Exception:
        reason = str(reason_cstr)

    
    msg = (
        f"\n[ANTIDEBUG] VIOLATION DETECTED\n"
        f"[ANTIDEBUG] Reason: {reason}\n"
        f"[ANTIDEBUG] Terminating process...\n"
    )
    _PySys_WriteStderr(msg.encode('utf-8'))
    _os_exit(1)


# ---------------------------------------------------------------------------
# LLVM IR генератор для нативных проверок
# ---------------------------------------------------------------------------

class AntiDebugLLVM:

    def __init__(self):
        if not IS_64BIT:
            raise RuntimeError("Only x64 Windows is supported")

        self.module = ir.Module(name="antidebug")
        self.builder = None
        self.funcs = {}
        self._declare_external_funcs()
        self._build_all_checks()
        self._compile()

    def _declare_external_funcs(self):
        """Объявляем внешние функции, которые будем вызывать из JIT-кода."""
        i8p = ir.PointerType(ir.IntType(8))
        i32 = ir.IntType(32)
        i64 = ir.IntType(64)

        
        ir.Function(self.module, ir.FunctionType(i64, []), name="get_peb_address")

        
        ir.Function(self.module, ir.FunctionType(i8p, []), name="GetCurrentProcess")

        
        ir.Function(self.module, ir.FunctionType(i32, []), name="IsDebuggerPresent")

        
        ir.Function(self.module, ir.FunctionType(i32, [i8p, ir.PointerType(i32)]),
                    name="CheckRemoteDebuggerPresent")

        
        ir.Function(self.module, ir.FunctionType(i32, [i8p, i32, i8p, i32, ir.PointerType(i32)]),
                    name="NtQueryInformationProcess")

        
        ir.Function(self.module, ir.FunctionType(i8p, []), name="GetCurrentThread")

        
        ir.Function(self.module, ir.FunctionType(i32, [i8p, i8p]), name="GetThreadContext")

    def _build_all_checks(self):
        self._build_check_peb()
        self._build_check_ntquery()
        self._build_check_hw_bp()
        self._build_check_debugger_present()
        self._build_check_nt_global_flag()

    def _build_check_peb(self):
        i8p = ir.PointerType(ir.IntType(8))
        i64 = ir.IntType(64)

        fnty = ir.FunctionType(i64, [])
        func = ir.Function(self.module, fnty, name="check_peb_debug")
        block = func.append_basic_block(name="entry")
        builder = ir.IRBuilder(block)

        get_peb_fn = self.module.globals["get_peb_address"]
        peb_int = builder.call(get_peb_fn, [], name="peb_int")

        # BeingDebugged @ PEB+0x02  (i8)
        bd_ptr = builder.inttoptr(
            builder.add(peb_int, ir.Constant(i64, 0x02)),
            ir.PointerType(ir.IntType(8)), name="bd_ptr"
        )
        bd = builder.load(bd_ptr, name="bd")
        result = builder.zext(bd, i64, name="result")
        builder.ret(result)
        self.funcs["check_peb_debug"] = func

    def _build_check_nt_global_flag(self):
        i8p = ir.PointerType(ir.IntType(8))
        i32 = ir.IntType(32)
        i64 = ir.IntType(64)

        fnty = ir.FunctionType(i64, [])
        func = ir.Function(self.module, fnty, name="check_nt_global_flag")
        block = func.append_basic_block(name="entry")
        builder = ir.IRBuilder(block)

        get_peb_fn = self.module.globals["get_peb_address"]
        peb_int = builder.call(get_peb_fn, [], name="peb_int")

        # NtGlobalFlag @ PEB+0xBC (i32)
        ngf_ptr = builder.inttoptr(
            builder.add(peb_int, ir.Constant(i64, 0xBC)),
            ir.PointerType(i32), name="ngf_ptr"
        )
        ngf = builder.load(ngf_ptr, name="ngf")
        masked = builder.and_(ngf, ir.Constant(i32, 0x70), name="masked")
        is_set = builder.icmp_unsigned("!=", masked, ir.Constant(i32, 0), name="is_set")
        result = builder.zext(is_set, i64, name="result")
        builder.ret(result)
        self.funcs["check_nt_global_flag"] = func

    def _build_check_ntquery(self):
        i8p = ir.PointerType(ir.IntType(8))
        i32 = ir.IntType(32)
        i64 = ir.IntType(64)

        fnty = ir.FunctionType(i64, [])
        func = ir.Function(self.module, fnty, name="check_ntquery_debug")

        entry_bb      = func.append_basic_block(name="entry")
        dp_check_bb   = func.append_basic_block(name="dp_check")
        flags_bb      = func.append_basic_block(name="flags")
        flags_eval_bb = func.append_basic_block(name="flags_eval")
        detected_bb   = func.append_basic_block(name="detected")
        clean_bb      = func.append_basic_block(name="clean")

        ntqip_fn = self.module.globals["NtQueryInformationProcess"]
        gcp_fn   = self.module.globals["GetCurrentProcess"]

        # --- entry: query DebugPort ---
        b = ir.IRBuilder(entry_bb)
        dp_buf = b.alloca(i64, name="dp_buf")
        rl_buf = b.alloca(i32, name="rl_buf")
        hproc  = b.call(gcp_fn, [], name="hproc")
        st1 = b.call(ntqip_fn, [
            hproc,
            ir.Constant(i32, 7),
            b.bitcast(dp_buf, i8p),
            ir.Constant(i32, 8),
            rl_buf,
        ], name="st1")
        st1_ok = b.icmp_signed("==", st1, ir.Constant(i32, 0))
        b.cbranch(st1_ok, dp_check_bb, flags_bb)

        # --- dp_check: DebugPort != 0 → detected ---
        b = ir.IRBuilder(dp_check_bb)
        dp_val = b.load(dp_buf, name="dp_val")
        dp_nz  = b.icmp_signed("!=", dp_val, ir.Constant(i64, 0))
        b.cbranch(dp_nz, detected_bb, flags_bb)

        # --- flags: query ProcessDebugFlags ---
        b = ir.IRBuilder(flags_bb)
        fl_buf  = b.alloca(i32, name="fl_buf")
        rl2_buf = b.alloca(i32, name="rl2_buf")
        hproc2  = b.call(gcp_fn, [], name="hproc2")
        st2 = b.call(ntqip_fn, [
            hproc2,
            ir.Constant(i32, 0x1F),
            b.bitcast(fl_buf, i8p),
            ir.Constant(i32, 4),
            rl2_buf,
        ], name="st2")
        st2_ok = b.icmp_signed("==", st2, ir.Constant(i32, 0))
        b.cbranch(st2_ok, flags_eval_bb, detected_bb)

        # --- flags_eval: flags == 0 → detected (no HEAP_NO_DEBUG flag) ---
        b = ir.IRBuilder(flags_eval_bb)
        fl_val  = b.load(fl_buf, name="fl_val")
        fl_zero = b.icmp_signed("==", fl_val, ir.Constant(i32, 0))
        b.cbranch(fl_zero, detected_bb, clean_bb)

        # --- detected ---
        b = ir.IRBuilder(detected_bb)
        b.ret(ir.Constant(i64, 1))

        # --- clean ---
        b = ir.IRBuilder(clean_bb)
        b.ret(ir.Constant(i64, 0))

        self.funcs["check_ntquery_debug"] = func

    def _build_check_hw_bp(self):
        fnty = ir.FunctionType(ir.IntType(64), [])
        func = ir.Function(self.module, fnty, name="check_hw_bp")
        block = func.append_basic_block(name="entry")
        builder = ir.IRBuilder(block)
        builder.ret(ir.Constant(ir.IntType(64), 0))
        self.funcs["check_hw_bp"] = func

    def _build_check_debugger_present(self):
        i8p = ir.PointerType(ir.IntType(8))
        i32 = ir.IntType(32)
        i64 = ir.IntType(64)

        fnty = ir.FunctionType(i64, [])
        func = ir.Function(self.module, fnty, name="check_debugger_present")
        block = func.append_basic_block(name="entry")
        builder = ir.IRBuilder(block)

        idp_fn  = self.module.globals["IsDebuggerPresent"]
        crdp_fn = self.module.globals["CheckRemoteDebuggerPresent"]
        gcp_fn  = self.module.globals["GetCurrentProcess"]

        # IsDebuggerPresent()
        idp_result = builder.call(idp_fn, [], name="idp")
        idp_bool   = builder.icmp_signed("!=", idp_result, ir.Constant(i32, 0))

        # CheckRemoteDebuggerPresent(hProc, &flag)
        flag_ptr = builder.alloca(i32, name="flag")
        builder.store(ir.Constant(i32, 0), flag_ptr)
        builder.call(crdp_fn, [builder.call(gcp_fn, [], name="hproc"), flag_ptr])
        crdp_val  = builder.load(flag_ptr, name="crdp_val")
        crdp_bool = builder.icmp_signed("!=", crdp_val, ir.Constant(i32, 0))

        any_det = builder.or_(idp_bool, crdp_bool, name="any")
        result  = builder.zext(any_det, i64, name="result")
        builder.ret(result)
        self.funcs["check_debugger_present"] = func

    def _compile(self):
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()
        llvm.initialize_native_asmparser()

        
        @ctypes.CFUNCTYPE(ctypes.c_uint64)
        def _get_peb_address_impl():
            
            class _PBI(ctypes.Structure):
                _fields_ = [
                    ("Reserved1",      ctypes.c_void_p),
                    ("PebBaseAddress", ctypes.c_uint64),
                    ("Reserved2",      ctypes.c_uint64 * 2),
                    ("UniqueProcessId",ctypes.c_uint64),
                    ("Reserved3",      ctypes.c_void_p),
                ]
            pbi = _PBI()
            rl  = ULONG(0)
            NtQIP(kernel32.GetCurrentProcess(), 0,
                  ctypes.byref(pbi), ctypes.sizeof(pbi), ctypes.byref(rl))
            return pbi.PebBaseAddress

        
        self._get_peb_address_impl = _get_peb_address_impl
        fn_ptr = ctypes.cast(_get_peb_address_impl, ctypes.c_void_p).value
        llvm.add_symbol("get_peb_address", fn_ptr)

        
        def _reg(name, fn):
            llvm.add_symbol(name, ctypes.cast(fn, ctypes.c_void_p).value)

        _reg("GetCurrentProcess",            kernel32.GetCurrentProcess)
        _reg("IsDebuggerPresent",            kernel32.IsDebuggerPresent)
        _reg("CheckRemoteDebuggerPresent",   kernel32.CheckRemoteDebuggerPresent)
        _reg("NtQueryInformationProcess",    ntdll.NtQueryInformationProcess)
        _reg("GetCurrentThread",             kernel32.GetCurrentThread)
        _reg("GetThreadContext",             kernel32.GetThreadContext)

        target = llvm.Target.from_default_triple()
        target_machine = target.create_target_machine()

        llvm_mod = llvm.parse_assembly(str(self.module))
        llvm_mod.verify()

        self.engine = llvm.create_mcjit_compiler(llvm_mod, target_machine)
        self.engine.finalize_object()

        
        self.check_peb            = ctypes.CFUNCTYPE(ctypes.c_uint64)(
            self.engine.get_function_address("check_peb_debug"))
        self.check_nt_global_flag = ctypes.CFUNCTYPE(ctypes.c_uint64)(
            self.engine.get_function_address("check_nt_global_flag"))
        self.check_ntquery        = ctypes.CFUNCTYPE(ctypes.c_uint64)(
            self.engine.get_function_address("check_ntquery_debug"))
        self.check_hw_bp          = ctypes.CFUNCTYPE(ctypes.c_uint64)(
            self.engine.get_function_address("check_hw_bp"))
        self.check_dbg_present    = ctypes.CFUNCTYPE(ctypes.c_uint64)(
            self.engine.get_function_address("check_debugger_present"))



@dataclass
class Violation:
    check_name: str
    reason: str
    details: dict = field(default_factory=dict)


class AntiDebugEngine:
    """
    Основной движок антиотладки. Комбинирует JIT-проверки с Python-level эвристиками.
    """

    # Чёрный список DLL — известные отладчики/инжекторы
    BLACKLIST_DLLS: Set[str] = {
        # Python debuggers
        "pydevd",
        "pydevd_cython",
        "pydevd_pep_669_tracing_cython",
        "debugpy",
        "_pydevd_bundle",
        # Native debuggers
        "x64dbg",
        "x32dbg",
        "ollydbg",
        "ida",
        "ida64",
        "windbg",
        "cheatengine",
        # Injection frameworks
        "pyshell",           # de4py
        "reflectivedll",
        "sliver",
        "meterpreter",
        # Analysis tools
        "frida",
        "frida-gadget",
        "libinjector",
    }

    # Чёрный список имён потоков
    BLACKLIST_THREAD_NAMES: Set[str] = {
        "pydevd.Writer",
        "pydevd.Reader",
        "pydevd.CommandThread",
        "pydevd.CheckAliveThread",
        "debugpy",
    }

    
    MODULE_WHITELIST: Set[str] = set()

    def __init__(self, strict: bool = True):
        self.strict = strict
        self.llvm = AntiDebugLLVM()
        self.violations: List[Violation] = []
        self._baseline_modules: Set[str] = set()
        self._baseline_tids: Set[int] = set()
        self._lock = threading.Lock()

        # Заполняем baseline модулей при инициализации
        self._capture_baseline()

    def _capture_baseline(self):
        """Запоминаем начальный набор модулей и потоков как легитимный."""
        self._baseline_modules = self._enum_modules_toolhelp()
        self._baseline_tids = self._snapshot_tids()

        
        exe_lower = sys.executable.lower()
        if self._is_nuitka_temp_path(exe_lower) or "onefile" in exe_lower:
            self._nuitka_onefile = True
        else:
            
            self._nuitka_onefile = bool(
                os.environ.get("NUITKA_ONEFILE_PARENT") or
                os.environ.get("NUITKA_ONEFILE_BINARY")
            )
            # Также проверяем: если exe в temp — точно onefile
            if not self._nuitka_onefile:
                temp = os.environ.get("TEMP", "").lower()
                if temp and temp in exe_lower:
                    self._nuitka_onefile = True

    # ------------------------------------------------------------------
    # Toolhelp32 helpers
    # ------------------------------------------------------------------

    def _snapshot_tids(self) -> Set[int]:
        tids: Set[int] = set()
        pid = os.getpid()
        hSnap = _CreateToolhelp32Snapshot(TH32CS_SNAPTHREAD, 0)
        if hSnap == INVALID_HANDLE_VALUE or hSnap is None:
            return tids
        try:
            entry = THREADENTRY32()
            entry.dwSize = ctypes.sizeof(THREADENTRY32)
            if _Thread32First(hSnap, ctypes.byref(entry)):
                while True:
                    if entry.th32OwnerProcessID == pid:
                        tids.add(entry.th32ThreadID)
                    entry.dwSize = ctypes.sizeof(THREADENTRY32)
                    if not _Thread32Next(hSnap, ctypes.byref(entry)):
                        break
        finally:
            CloseHandle(hSnap)
        return tids

    def _enum_modules_toolhelp(self) -> Set[str]:
        mods: Set[str] = set()
        pid = os.getpid()
        hSnap = _CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, pid)
        if hSnap == INVALID_HANDLE_VALUE or hSnap is None:
            return mods
        try:
            entry = MODULEENTRY32()
            entry.dwSize = ctypes.sizeof(MODULEENTRY32)
            if _Module32First(hSnap, ctypes.byref(entry)):
                while True:
                    name = entry.szModule.decode('utf-8', errors='replace').lower()
                    path = entry.szExePath.decode('utf-8', errors='replace').lower()
                    mods.add(name)
                    mods.add(path)
                    entry.dwSize = ctypes.sizeof(MODULEENTRY32)
                    if not _Module32Next(hSnap, ctypes.byref(entry)):
                        break
        finally:
            CloseHandle(hSnap)
        return mods

    def _enum_modules_pywin32(self) -> Set[str]:
        """Fallback через pywin32 (точнее, даёт базовые адреса)."""
        mods: Set[str] = set()
        try:
            import win32process
            import win32api
            pid = os.getpid()
            hProcess = win32api.OpenProcess(0x0410, False, pid)
            mod_handles = win32process.EnumProcessModulesEx(hProcess, 0x03)
            for hMod in mod_handles:
                try:
                    path = win32process.GetModuleFileNameEx(hProcess, hMod).lower()
                    name = os.path.basename(path)
                    mods.add(name)
                    mods.add(path)
                except Exception:
                    pass
            win32api.CloseHandle(hProcess)
        except ImportError:
            pass
        return mods

    # ------------------------------------------------------------------
    # Проверки
    # ------------------------------------------------------------------

    def check_native_debugger(self) -> List[Violation]:
        """JIT-проверки нативной отладки через PEB и NtQuery."""
        results = []

        # PEB.BeingDebugged
        if self.llvm.check_peb():
            results.append(Violation(
                "PEB.BeingDebugged",
                "Native debugger detected via PEB.BeingDebugged"
            ))

        # PEB.NtGlobalFlag
        if self.llvm.check_nt_global_flag():
            results.append(Violation(
                "PEB.NtGlobalFlag",
                "Debug heap flags detected (NtGlobalFlag & 0x70 != 0)"
            ))

        # NtQuery DebugPort / DebugFlags
        if self.llvm.check_ntquery():
            results.append(Violation(
                "NtQueryInformationProcess",
                "Non-zero DebugPort or zero ProcessDebugFlags detected"
            ))

        # IsDebuggerPresent / CheckRemoteDebuggerPresent
        if self.llvm.check_dbg_present():
            results.append(Violation(
                "DebuggerPresent",
                "IsDebuggerPresent() or CheckRemoteDebuggerPresent() returned TRUE"
            ))

        return results

    def check_python_debugger(self) -> List[Violation]:
        """Эвристики Python-level отладчиков (модули, потоки)."""
        results = []

        # Проверяем загруженные модули
        current_modules = self._enum_modules_toolhelp() | self._enum_modules_pywin32()

        for mod in current_modules:
            mod_lower = mod.lower()
            for bad in self.BLACKLIST_DLLS:
                if bad in mod_lower:
                    results.append(Violation(
                        "BlacklistedModule",
                        f"Forbidden debugger/injector module loaded: {mod}",
                        {"module": mod, "pattern": bad}
                    ))

        # Проверяем Python-потоки
        for t in threading.enumerate():
            if t.name in self.BLACKLIST_THREAD_NAMES:
                results.append(Violation(
                    "BlacklistedThread",
                    f"Forbidden debugger thread detected: {t.name}",
                    {"thread_name": t.name, "tid": t.ident}
                ))

        # Проверяем sys.monitoring / sys.gettrace
        if hasattr(sys, 'gettrace') and sys.gettrace() is not None:
            results.append(Violation(
                "PythonTrace",
                "sys.gettrace() is active — Python-level debugger detected"
            ))

        if hasattr(sys, 'monitoring') and sys.monitoring:
            # Python 3.12+ PEP 669
            try:
                if sys.monitoring.get_tool(sys.monitoring.DEBUGGER_ID) is not None:
                    results.append(Violation(
                        "PEP669Debugger",
                        "sys.monitoring DEBUGGER_ID tool is active"
                    ))
            except (AttributeError, ValueError):
                pass

        return results

    def check_dll_injection(self) -> List[Violation]:
        """Обнаружение новых/подозрительных DLL в процессе."""
        results = []
        current_modules = self._enum_modules_toolhelp() | self._enum_modules_pywin32()

        new_modules = current_modules - self._baseline_modules
        for mod in new_modules:
            mod_lower = mod.lower()
            # Любой новый модуль из чёрного списка
            for bad in self.BLACKLIST_DLLS:
                if bad in mod_lower:
                    results.append(Violation(
                        "DllInjection",
                        f"Injected blacklisted DLL detected: {mod}",
                        {"module": mod, "pattern": bad}
                    ))
            # Любой новый модуль в нестандартных путях (эвристика)
            # Пропускаем если это Nuitka onefile — все temp-пути легитимны
            if getattr(self, "_nuitka_onefile", False):
                continue
            if any(p in mod_lower for p in ["\\temp\\", "\\tmp\\", "\\downloads\\"]):
                # Исключаем Nuitka onefile: распаковывает в %TEMP%\onefile_<pid>_* и ONEFIL~N
                if self._is_nuitka_temp_path(mod_lower):
                    continue
                if not any(w in mod_lower for w in ["python", "vcruntime", "ucrtbase"]):
                    results.append(Violation(
                        "SuspiciousDllPath",
                        f"DLL loaded from temporary path: {mod}",
                        {"module": mod}
                    ))

        return results

    @staticmethod
    def _is_nuitka_temp_path(path_lower: str) -> bool:
        """
        Возвращает True если путь принадлежит Nuitka onefile temp-директории.
        Паттерны:
          - \\temp\\onefile_<pid>_<timestamp>\\...
          - \\temp\\onefil~N\\...   (8.3 short name)
          - \\temp\\nuitka_<...>\\...
        """
        import re
        # onefile_12345_134220108822537160
        if re.search(r'\\temp\\onefile_\d+_\d+\\', path_lower):
            return True
        # ONEFIL~N (8.3 alias для onefile_*)
        if re.search(r'\\temp\\onefil~\d+\\', path_lower):
            return True
        # nuitka_<hash> или nuitka-<hash>
        if re.search(r'\\temp\\nuitka[-_]', path_lower):
            return True
        return False

    def check_stealth_threads(self) -> List[Violation]:
        """Обнаружение «стелс»-потоков (manual mapped, StartAddr = None)."""
        results = []
        current_tids = self._snapshot_tids()
        new_tids = current_tids - self._baseline_tids

        python_tids = {t.ident for t in threading.enumerate() if t.ident}

        for tid in new_tids:
            if tid in python_tids:
                continue  # Python-потоки — норма

            # Пытаемся получить стартовый адрес
            start_addr = self._get_thread_start_address(tid)

            if start_addr is None:
                # Не удалось прочитать — потенциальный manual mapped thread
                results.append(Violation(
                    "StealthThread",
                    f"New native thread with unresolvable start address (possible manual map): TID={tid}",
                    {"tid": tid, "start_address": None}
                ))
            else:
                # Проверяем, к какому модулю относится адрес
                mod = self._resolve_module_for_address(start_addr)
                if mod == "unknown":
                    results.append(Violation(
                        "StealthThread",
                        f"New native thread from unknown module: TID={tid}, addr={start_addr}",
                        {"tid": tid, "start_address": hex(start_addr), "module": mod}
                    ))

        # Обновляем baseline
        self._baseline_tids = current_tids
        return results

    def check_hardware_breakpoints(self) -> List[Violation]:
        """Проверка hardware breakpoints (DR0-DR3) для всех потоков."""
        results = []

        for tid in self._snapshot_tids():
            hw = self._get_hw_breakpoints_for_thread(tid)
            if hw.get("any_set"):
                results.append(Violation(
                    "HardwareBreakpoint",
                    f"Hardware breakpoint detected on TID={tid}: DR0={hw['dr0']} DR1={hw['dr1']} DR2={hw['dr2']} DR3={hw['dr3']}",
                    {"tid": tid, **{f"dr{i}": hw[f"dr{i}"] for i in range(4)}}
                ))

        return results

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    def _get_thread_start_address(self, tid: int) -> int | None:
        hThread = OpenThread(THREAD_QUERY_INFORMATION, False, tid)
        if not hThread:
            return None
        try:
            start_addr = ULONG_PTR(0)
            ret_len = ULONG(0)
            status = NtQIT(
                hThread, 9,
                ctypes.byref(start_addr),
                ctypes.sizeof(start_addr),
                ctypes.byref(ret_len),
            )
            if status == 0:
                return start_addr.value
            return None
        finally:
            CloseHandle(hThread)

    def _resolve_module_for_address(self, addr: int) -> str:
        if addr is None:
            return "unknown"
        try:
            mbi = MEMORY_BASIC_INFORMATION()
            if _VirtualQuery(addr, ctypes.byref(mbi), ctypes.sizeof(mbi)):
                alloc_base = mbi.AllocationBase
                if alloc_base:
                    buf = ctypes.create_string_buffer(512)
                    n = GetModuleFileNameA(alloc_base, buf, 512)
                    if n > 0:
                        return buf.value.decode("utf-8", errors="replace")
        except Exception:
            pass
        return "unknown"

    def _get_hw_breakpoints_for_thread(self, tid: int) -> dict:
        result = {"dr0": None, "dr1": None, "dr2": None, "dr3": None,
                  "dr6": None, "dr7": None, "any_set": False, "error": None}

        if not IS_64BIT:
            result["error"] = "x86 not supported"
            return result

        hThread = OpenThread(THREAD_QUERY_INFORMATION | THREAD_GET_CONTEXT, False, tid)
        if not hThread:
            result["error"] = f"OpenThread failed: {ctypes.GetLastError()}"
            return result

        try:
            ctx = CONTEXT_x64()
            ctx.ContextFlags = CONTEXT_DEBUG_REGISTERS
            if GetThreadContext(hThread, ctypes.byref(ctx)):
                result["dr0"] = ctx.Dr0
                result["dr1"] = ctx.Dr1
                result["dr2"] = ctx.Dr2
                result["dr3"] = ctx.Dr3
                result["dr6"] = ctx.Dr6
                result["dr7"] = ctx.Dr7
                result["any_set"] = bool(ctx.Dr0 or ctx.Dr1 or ctx.Dr2 or ctx.Dr3)
            else:
                result["error"] = f"GetThreadContext failed: {ctypes.GetLastError()}"
        finally:
            CloseHandle(hThread)

        return result

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------

    def run_all_checks(self) -> List[Violation]:
        """Выполняет все проверки и возвращает список нарушений."""
        all_violations = []

        try:
            all_violations.extend(self.check_native_debugger())
        except Exception as e:
            if self.strict:
                all_violations.append(Violation("NativeCheckError", f"Native check failed: {e}"))

        try:
            all_violations.extend(self.check_python_debugger())
        except Exception as e:
            if self.strict:
                all_violations.append(Violation("PythonCheckError", f"Python check failed: {e}"))

        try:
            all_violations.extend(self.check_dll_injection())
        except Exception as e:
            if self.strict:
                all_violations.append(Violation("DllCheckError", f"DLL check failed: {e}"))

        try:
            all_violations.extend(self.check_stealth_threads())
        except Exception as e:
            if self.strict:
                all_violations.append(Violation("ThreadCheckError", f"Thread check failed: {e}"))

        try:
            all_violations.extend(self.check_hardware_breakpoints())
        except Exception as e:
            if self.strict:
                all_violations.append(Violation("HwBpCheckError", f"HW BP check failed: {e}"))

        return all_violations

    def kill_if_violations(self, violations: List[Violation] | None = None):
        """Если есть нарушения — печатает причину и убивает процесс."""
        if violations is None:
            violations = self.run_all_checks()

        if not violations:
            return

        with self._lock:
            # Формируем подробный отчёт
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

            # Печатаем через PySys_WriteStderr для надёжности (даже если stdout перехвачен)
            _PySys_WriteStderr(report.encode('utf-8'))

            # Небольшая задержка чтобы stderr успел сброситься
            time.sleep(0.1)

            # Жёсткий выход — не даём отладчику перехватить SystemExit
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

_engine: AntiDebugEngine | None = None

def init(strict: bool = True) -> AntiDebugEngine:
    """Инициализирует движок (один на процесс)."""
    global _engine
    if _engine is None:
        _engine = AntiDebugEngine(strict=strict)
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
    print("[PyLockWare AntiDebug] Running self-test...")
    import os
    print(os.getpid())
    engine = init(strict=True)

    monitor(interval_ms=500)
    print("started monitoring")
    input()
