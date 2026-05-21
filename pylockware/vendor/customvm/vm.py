import time
import random
import hashlib
from .opcodes import *
from .crypto import RuntimeCrypto, verify_timing

class VirtualMachine:
    def __init__(self, memory_size=65536):
        self.memory = bytearray(memory_size)
        self.stack = []
        self.registers = [0] * 256  # 256 registers (0-255)
        self.ip = 0
        self.sp = 0
        self.flags = {'z': False, 'c': False, 'n': False}
        self.running = False
        self.code = b''
        self.code_size = 0
        self.const_pool = []
        self.call_stack = []
        self.opcode_set = None
        self.crypto = None
        self.context = 0
        self.start_time = 0
        self.check_counter = 0
        self.integrity_hash = None
        self.func_pool = []
        self.string_pool = []
        
        # Keyflow support
        self.keyflow = None
        self.use_keyflow = False
        self.prev_opcode = 0
        self.inst_index = 0   # instruction counter for context  # Track previous opcode for keyflow
    def load_bytecode(self, code, opcode_set, crypto, const_pool, integrity_hash, func_pool=None, string_pool=None, keyflow=None):
        self.code = code
        self.code_size = len(code)
        self.opcode_set = opcode_set
        self.crypto = crypto
        self.const_pool = const_pool
        self.integrity_hash = integrity_hash
        self.ip = 0
        self.inst_index = 0
        self.start_time = time.time()
        self.prev_opcode = 0
        self.use_keyflow = False
        self.keyflow = None
        self.globals_ctx = None  # caller globals for resolving user functions

        if func_pool is not None:
            self.func_pool = func_pool
        if string_pool is not None:
            self.string_pool = string_pool

    def _read_byte(self):
        if self.ip >= self.code_size:
            return 0
        b = self.code[self.ip]
        self.ip += 1
        return b

    def _read_word(self):
        b1 = self._read_byte()
        b2 = self._read_byte()
        return (b2 << 8) | b1

    def _read_dword(self):
        w1 = self._read_word()
        w2 = self._read_word()
        return (w2 << 16) | w1

    def _push(self, value):
        if isinstance(value, str):
            self.stack.append(value)
        else:
            self.stack.append(value & 0xFFFFFFFF)

    def _pop(self):
        if not self.stack:
            return 0
        return self.stack.pop()

    def _anti_debug_check(self):
        self.check_counter += 1
        if self.check_counter % 100 == 0:
            if not verify_timing(self.start_time, 300.0):
                self.running = False
                return False
        return True

    def _integrity_check(self):
        if self.check_counter % 500 == 0:
            current_hash = hashlib.sha256(self.code).digest()
            if current_hash != self.integrity_hash:
                self.running = False
                return False
        return True

    def _add_timing_noise(self):
        if random.random() < 0.1:
            time.sleep(random.uniform(0.0001, 0.001))

    def execute(self):
        self.running = True

        while self.running and self.ip < self.code_size:
            if not self._anti_debug_check():
                break
            if not self._integrity_check():
                break

            self._add_timing_noise()

            raw_opcode = self._read_byte()
            # Context matches builder: changes every 16 instructions
            context = (self.inst_index // 16) & 0xFF
            instruction = self.opcode_set.decode_opcode(raw_opcode, context)
            self.inst_index += 1

            if instruction == INST_NOP:
                pass

            elif instruction == INST_PUSH_IMM:
                val = self._read_dword()
                self._push(val)

            elif instruction == INST_PUSH_REG:
                reg = self._read_byte() & 0xFF
                self._push(self.registers[reg])

            elif instruction == INST_POP_REG:
                reg = self._read_byte() & 0xFF
                self.registers[reg] = self._pop()

            elif instruction == INST_LOAD_MEM:
                addr = self._pop()
                if addr < len(self.memory) - 3:
                    val = int.from_bytes(self.memory[addr:addr+4], 'little')
                    self._push(val)

            elif instruction == INST_STORE_MEM:
                addr = self._pop()
                val = self._pop()
                if addr < len(self.memory) - 3:
                    self.memory[addr:addr+4] = val.to_bytes(4, 'little')

            elif instruction == INST_ADD:
                b = self._pop()
                a = self._pop()
                # Handle string concatenation
                if isinstance(a, str) or isinstance(b, str):
                    result = str(a) + str(b)
                    self._push(result)
                else:
                    result = (a + b) & 0xFFFFFFFF
                    self._push(result)
                    self.flags['z'] = result == 0
                    self.flags['c'] = (a + b) > 0xFFFFFFFF

            elif instruction == INST_SUB:
                b = self._pop()
                a = self._pop()
                result = (a - b) & 0xFFFFFFFF
                self._push(result)
                self.flags['z'] = result == 0
                self.flags['n'] = a < b

            elif instruction == INST_MUL:
                b = self._pop()
                a = self._pop()
                result = (a * b) & 0xFFFFFFFF
                self._push(result)

            elif instruction == INST_DIV:
                b = self._pop()
                a = self._pop()
                if b != 0:
                    result = a // b
                    self._push(result)
                else:
                    self._push(0)

            elif instruction == INST_MOD:
                b = self._pop()
                a = self._pop()
                if b != 0:
                    result = a % b
                    self._push(result)
                else:
                    self._push(0)

            elif instruction == INST_AND:
                b = self._pop()
                a = self._pop()
                self._push(a & b)

            elif instruction == INST_OR:
                b = self._pop()
                a = self._pop()
                self._push(a | b)

            elif instruction == INST_XOR:
                b = self._pop()
                a = self._pop()
                self._push(a ^ b)

            elif instruction == INST_NOT:
                a = self._pop()
                self._push((~a) & 0xFFFFFFFF)

            elif instruction == INST_SHL:
                shift = self._pop()
                val = self._pop()
                self._push((val << shift) & 0xFFFFFFFF)

            elif instruction == INST_SHR:
                shift = self._pop()
                val = self._pop()
                self._push(val >> shift)

            elif instruction == INST_CMP:
                b = self._pop()
                a = self._pop()
                # Handle string/int comparison
                a_val = self._to_comparable(a)
                b_val = self._to_comparable(b)
                self.flags['z'] = a_val == b_val
                self.flags['n'] = a_val < b_val
                self.flags['c'] = a_val > b_val

            elif instruction == INST_JMP:
                addr = self._read_dword()
                self.ip = addr

            elif instruction == INST_JZ:
                addr = self._read_dword()
                if self.flags['z']:
                    self.ip = addr

            elif instruction == INST_JNZ:
                addr = self._read_dword()
                if not self.flags['z']:
                    self.ip = addr

            elif instruction == INST_JG:
                addr = self._read_dword()
                if self.flags['c'] and not self.flags['z']:
                    self.ip = addr

            elif instruction == INST_JL:
                addr = self._read_dword()
                if self.flags['n']:
                    self.ip = addr

            elif instruction == INST_JGE:
                addr = self._read_dword()
                if self.flags['c'] or self.flags['z']:
                    self.ip = addr

            elif instruction == INST_JLE:
                addr = self._read_dword()
                if self.flags['n'] or self.flags['z']:
                    self.ip = addr

            elif instruction == INST_CALL:
                addr = self._read_dword()
                self.call_stack.append(self.ip)
                self.ip = addr

            elif instruction == INST_RET:
                if self.call_stack:
                    self.ip = self.call_stack.pop()
                else:
                    self.running = False

            elif instruction == INST_SYSCALL:
                syscall_num = self._pop()
                self._handle_syscall(syscall_num)

            elif instruction == INST_HALT:
                self.running = False

            elif instruction == INST_DUP:
                if self.stack:
                    self._push(self.stack[-1])

            elif instruction == INST_SWAP:
                if len(self.stack) >= 2:
                    self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]

            elif instruction == INST_ROT:
                if len(self.stack) >= 3:
                    val = self.stack.pop(-3)
                    self.stack.append(val)

            elif instruction == INST_LOAD_CONST:
                idx = self._read_word()
                if idx < len(self.const_pool):
                    self._push(self.const_pool[idx])

            elif instruction == INST_STORE_CONST:
                idx = self._read_word()
                val = self._pop()
                if idx < len(self.const_pool):
                    self.const_pool[idx] = val

            elif instruction == INST_ALLOC:
                size = self._pop()
                addr = self.sp
                self.sp += size
                self._push(addr)

            elif instruction == INST_FREE:
                size = self._pop()
                self.sp -= size
                if self.sp < 0:
                    self.sp = 0

            elif instruction == INST_COPY:
                size = self._pop()
                src = self._pop()
                dst = self._pop()
                if dst + size <= len(self.memory) and src + size <= len(self.memory):
                    self.memory[dst:dst+size] = self.memory[src:src+size]

            elif instruction == INST_FILL:
                val = self._pop()
                size = self._pop()
                addr = self._pop()
                if addr + size <= len(self.memory):
                    self.memory[addr:addr+size] = bytes([val & 0xFF] * size)

            elif instruction == INST_RAND:
                self._push(random.randint(0, 0xFFFFFFFF))

            elif instruction == INST_TIME:
                self._push(int(time.time() * 1000) & 0xFFFFFFFF)

            elif instruction == INST_CHECK:
                if not self._anti_debug_check():
                    self.running = False

            elif instruction == INST_VERIFY:
                if not self._integrity_check():
                    self.running = False

            elif instruction == INST_NOISE:
                self._add_timing_noise()

            elif instruction == INST_FAKE_JMP:
                self._read_dword()

            elif instruction == INST_FAKE_CALL:
                self._read_dword()

            elif instruction == INST_CONTEXT_SHIFT:
                shift = self._read_byte()
                self.context = (self.context + shift) & 0xFF

            elif instruction == INST_FOLD_ADD:
                c = self._pop()
                b = self._pop()
                a = self._pop()
                result = (a + b + c) & 0xFFFFFFFF
                self._push(result)

            elif instruction == INST_FOLD_MUL:
                c = self._pop()
                b = self._pop()
                a = self._pop()
                result = (a * b * c) & 0xFFFFFFFF
                self._push(result)

            elif instruction >= INST_DUMMY_1 and instruction <= INST_DUMMY_10:
                dummy_ops = random.randint(0, 3)
                for _ in range(dummy_ops):
                    self._read_byte()

            elif instruction == INST_STR_LOAD:
                idx = self._read_word()
                if 0 <= idx < len(self.string_pool):
                    self._push(self.string_pool[idx])
                else:
                    self._push("")

            elif instruction == INST_STR_CMP:
                """Using Python str native comparison directly.
                This is NOT hookable — Python str comparison is used directly,
                no VM-level mechanism can override it."""
                b = self._pop()
                a = self._pop()
                if isinstance(a, str) and isinstance(b, str):
                    self.flags['z'] = a == b
                    self.flags['n'] = a < b
                    self.flags['c'] = a > b
                else:
                    self.flags['z'] = a == b
                    self.flags['n'] = a < b
                    self.flags['c'] = a > b

            elif instruction == INST_STR_CONCAT:
                b = self._pop()
                a = self._pop()
                result = str(a) + str(b)
                self._push(result)

            elif instruction == INST_STR_LEN:
                s = self._pop()
                if isinstance(s, str):
                    self._push(len(s))
                else:
                    self._push(0)

            elif instruction == INST_STR_GET:
                idx = self._pop()
                s = self._pop()
                if isinstance(s, str) and isinstance(idx, int) and 0 <= idx < len(s):
                    self._push(s[idx])
                else:
                    self._push("")

            elif instruction == INST_STR_SLICE:
                end = self._pop()
                start = self._pop()
                s = self._pop()
                if isinstance(s, str):
                    # Use 0x7FFFFFFF to represent None (full slice)
                    SLICE_NONE = 0x7FFFFFFF
                    start_idx = None if start == SLICE_NONE else start
                    end_idx = None if end == SLICE_NONE else end
                    self._push(s[start_idx:end_idx])
                else:
                    self._push("")

        return self.stack[-1] if self.stack else 0

    def _convert_to_vm_value(self, val):
        """Convert a Python value to a VM-compatible value."""
        if val is None:
            return 0
        if isinstance(val, bool):
            return 1 if val else 0
        if isinstance(val, str):
            return val  # Keep strings as strings
        try:
            return int(val) & 0xFFFFFFFF
        except (TypeError, ValueError):
            return 0

    def _to_comparable(self, val):
        """Convert a value to a comparable form for CMP instruction.
        Strings are converted to their boolean value (empty=0, non-empty=1) when compared with ints.
        """
        if isinstance(val, str):
            # When comparing string with int, convert string to bool (0 or 1)
            return 1 if val else 0
        return val

    def _handle_syscall(self, num):
        if num == 1:
            val = self._pop()
            print(val)
        elif num == 2:
            val = self._pop()
            print(chr(val & 0xFF), end='')
        elif num == 3:
            if self.stack:
                print(self.stack[-1])
        elif num == 10:
            func_index = self._pop()
            num_args = self._pop()
            args = []
            for _ in range(num_args):
                args.insert(0, self._pop())
            if 0 <= func_index < len(self.func_pool):
                func = self.func_pool[func_index]
                try:
                    result = func(*args)
                    self._push(self._convert_to_vm_value(result))
                except Exception:
                    self._push(0)
            else:
                self._push(0)
    
    def _handle_string_method(self, func, args):
        """Handle string methods that aren't in func_pool"""
        if not args:
            return None
        
        obj = args[0]
        if not isinstance(obj, str):
            return None
        
        # Map function names to string methods
        method_map = {
            'upper': lambda s: s.upper(),
            'lower': lambda s: s.lower(),
            'strip': lambda s: s.strip(),
            'lstrip': lambda s: s.lstrip(),
            'rstrip': lambda s: s.rstrip(),
            'capitalize': lambda s: s.capitalize(),
            'title': lambda s: s.title(),
            'swapcase': lambda s: s.swapcase(),
        }
        
        # Try to get method name from func if it's callable
        method_name = None
        if callable(func):
            method_name = getattr(func, '__name__', None)
        
        if method_name in method_map:
            try:
                return method_map[method_name](obj)
            except:
                return None
        
        # Handle methods with additional arguments
        if method_name == 'replace' and len(args) >= 3:
            try:
                return obj.replace(str(args[1]), str(args[2]))
            except:
                return None
        elif method_name == 'split':
            try:
                if len(args) > 1:
                    return obj.split(str(args[1]))
                else:
                    return obj.split()
            except:
                return None
        elif method_name == 'join' and len(args) >= 2:
            try:
                return obj.join(args[1])
            except:
                return None
        elif method_name == 'startswith' and len(args) >= 2:
            try:
                return 1 if obj.startswith(str(args[1])) else 0
            except:
                return None
        elif method_name == 'endswith' and len(args) >= 2:
            try:
                return 1 if obj.endswith(str(args[1])) else 0
            except:
                return None
        elif method_name == 'find' and len(args) >= 2:
            try:
                return obj.find(str(args[1]))
            except:
                return None
        elif method_name == 'count' and len(args) >= 2:
            try:
                return obj.count(str(args[1]))
            except:
                return None
        
        return None
