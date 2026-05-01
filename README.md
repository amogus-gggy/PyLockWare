# PyLockWare — Python Obfuscation Suite

Advanced Python source code protection: AST-based obfuscation, LLVM JIT anti-debug, and Nuitka EXE packaging.

---

## Features

| Module | Description |
|---|---|
| `--remap` | Renames all identifiers (functions, classes, variables) to random names |
| `--string-prot` | Encodes string literals with base64 + zlib |
| `--num-obf` | Replaces numeric constants with arithmetic expressions |
| `--import-obf` | Hides imports via dynamic execution (`exec`/`__import__`) |
| `--state-machine` | Transforms functions into state machines |
| `--builtin-dispatcher` | Routes built-in calls through an obfuscated dispatcher class |
| `--junk-code` | Injects dead branches with opaque predicates |
| `--decorator-obf` | Converts `@decorator` syntax to explicit assignment form |
| `--call-obf` | Replaces direct calls with `getattr(sys.modules[...], name)()` |
| `--disable-traceback` | Sets `sys.tracebacklimit = 0` in every file |
| `--anti-debug` | LLVM JIT anti-debug engine (Windows x64 only, see below) |

---

## Requirements

- Python 3.10+
- `pip install -r requirements.txt`

Dependencies: `psutil`, `pywin32` (Windows), `PySide6`, `nuitka`, `llvmlite`

---

## Installation

```bash
git clone https://github.com/amogus-gggy/PyLockWare.git
cd PyLockWare
python -m venv .venv
.venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

---

## Usage

### GUI

```bash
python gui.py
```

### CLI — full command with all options

```bash
python cli.py <project_path> \
  --entry-point main.py \
  --entry-function main \
  --output-dir dist \
  --remap \
  --anti-debug \
  --string-prot \
  --num-obf \
  --state-machine \
  --builtin-dispatcher \
  --junk-code \
  --junk-density 0.8 \
  --opaque-complexity high \
  --disable-traceback \
  --decorator-obf \
  --name-gen english \
  --banner "Protected"
```

> `--import-obf` and `--call-obf` are mutually exclusive — pick one or neither.

### CLI — with Nuitka EXE packaging

```bash
python cli.py <project_path> \
  --entry-point main.py \
  --output-dir dist \
  --remap \
  --anti-debug \
  --string-prot \
  --num-obf \
  --state-machine \
  --builtin-dispatcher \
  --junk-code \
  --junk-density 0.8 \
  --opaque-complexity high \
  --disable-traceback \
  --decorator-obf \
  --nuitka \
  --nuitka-onefile \
  --nuitka-standalone \
  --nuitka-output-name myapp \
  --nuitka-enable-console \
  --nuitka-plugins pyside6
```

### CLI — all options reference

| Option | Default | Description |
|---|---|---|
| `project_path` | — | Path to the project directory |
| `--entry-point` | required | Entry point file (e.g. `main.py`) |
| `--entry-function` | `main` | Name of the main function |
| `--output-dir` | `dist` | Output directory |
| `--banner` | `"Obfuscated by PyLockWare Obfuscator"` | Comment added to each file |
| `--remap` | off | Rename all identifiers |
| `--anti-debug` | off | LLVM JIT anti-debug (Windows x64) |
| `--string-prot` | off | Encode string literals |
| `--num-obf` | off | Obfuscate numeric constants |
| `--import-obf` | off | Dynamic import obfuscation *(incompatible with `--call-obf`)* |
| `--state-machine` | off | State machine transformation |
| `--builtin-dispatcher` | off | Builtin call dispatcher |
| `--junk-code` | off | Dead code injection |
| `--junk-density` | `0.5` | Junk code density `0.0–1.0` |
| `--opaque-complexity` | `high` | Predicate complexity: `low` / `medium` / `high` |
| `--disable-traceback` | off | `sys.tracebacklimit = 0` in every file |
| `--decorator-obf` | off | Expand decorator syntax |
| `--call-obf` | off | `getattr`-based call obfuscation *(incompatible with `--import-obf`)* |
| `--name-gen` | `english` | Name charset: `english` / `chinese` / `mixed` / `numbers` / `hex` |
| `--nuitka` | off | Package to EXE via Nuitka |
| `--nuitka-onefile` | on | Single-file EXE (`--onefile`) |
| `--nuitka-no-onefile` | — | Disable onefile |
| `--nuitka-standalone` | on | Standalone distribution |
| `--nuitka-no-standalone` | — | Disable standalone |
| `--nuitka-output-name` | — | EXE filename |
| `--nuitka-disable-console` | on | Hide console window (GUI apps) |
| `--nuitka-enable-console` | — | Show console window |
| `--nuitka-icon` | — | Path to `.ico` file |
| `--nuitka-admin` | off | Request UAC admin elevation |
| `--nuitka-plugins` | — | Nuitka plugins (e.g. `pyside6 numpy`) |
| `--nuitka-extra-imports` | — | Extra modules to include |
| `--nuitka-options` | — | Raw Nuitka CLI flags |

---

## Anti-Debug Engine

The `--anti-debug` flag injects an LLVM JIT-compiled protection engine (`antidebug_llvm.py`) into every output file. It runs two checks at startup and then monitors continuously in a background thread.

**JIT checks (compiled to native x64 via MCJIT):**
- `PEB.BeingDebugged` — direct PEB read
- `PEB.NtGlobalFlag` — debug heap flags (`0x70`)
- `NtQueryInformationProcess(ProcessDebugPort)` — non-zero = debugger attached
- `NtQueryInformationProcess(ProcessDebugFlags)` — zero = debugger attached
- `IsDebuggerPresent` / `CheckRemoteDebuggerPresent`

**Python-level checks (continuous monitoring):**
- Blacklisted DLLs/PYDs loaded in process: `pydevd`, `pydevd_cython`, `debugpy`, `x64dbg`, `ida`, `frida`, `pyshell` (de4py), etc.
- Blacklisted Python thread names: `pydevd.Writer`, `pydevd.Reader`, `pydevd.CommandThread`
- `sys.gettrace()` active
- `sys.monitoring` DEBUGGER_ID set (Python 3.12+ PEP 669)
- New native threads from unknown/unmapped memory (manual map detection)
- Hardware breakpoints (DR0–DR3) on any thread
- New DLLs injected from temp paths (stealth injection detection)

On violation: prints reason to stderr and calls `os._exit(1)`.

**Nuitka onefile** is detected automatically — temp paths from `onefile_<pid>_*` / `ONEFIL~N` are whitelisted.

---

## Compatibility Notes

- `--import-obf` and `--call-obf` are mutually exclusive
- `--import-obf` is disabled automatically when `--nuitka` is used
- `--anti-debug` requires Windows x64; silently skipped on other platforms
- Heavier obfuscation (`--state-machine` + `--junk-code` + `--builtin-dispatcher`) increases file size and startup time

---

## Recommended Workflow

**Python distribution (no EXE):**
```bash
python cli.py myproject --entry-point main.py \
  --remap --anti-debug --string-prot --num-obf \
  --state-machine --builtin-dispatcher --junk-code \
  --disable-traceback --output-dir dist
```

**EXE distribution:**
```bash
python cli.py myproject --entry-point main.py \
  --remap --anti-debug --string-prot --num-obf \
  --state-machine --builtin-dispatcher --junk-code \
  --disable-traceback \
  --nuitka --nuitka-onefile --nuitka-output-name myapp \
  --output-dir dist
```

---

## License

AGPLv3 — see `LICENSE`.
