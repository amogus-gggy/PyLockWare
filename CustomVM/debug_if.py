"""Debug if/elif/else with instruction limit."""
import io
import os
import sys
import tempfile

sys.path.insert(0, r'C:\Users\fedor\Desktop\CustomVM')

from customvm import VMBuilder, BytecodeLoader, VirtualMachine
from customvm.compiler import PythonCompiler

source = """
x = 5
if x == 0:
    print(0)
elif x == 5:
    print(5)
elif x == 10:
    print(10)
else:
    print(-1)
"""

builder = VMBuilder()
compiler = PythonCompiler(builder)
compiler.compile(source)

print(f"Total instructions: {len(builder.instructions)}")
print(f"Labels: {builder.labels}")
print(f"Label refs: {builder.label_refs}")

with tempfile.NamedTemporaryFile(suffix='.cvm', delete=False) as tmp:
    tmp_path = tmp.name

try:
    builder.build(tmp_path)
    loader = BytecodeLoader()
    code, opcode_set, crypto, const_pool, integrity_hash, func_pool = loader.load(tmp_path)
    
    print(f"Code size: {len(code)} bytes")
    
    vm = VirtualMachine()
    code, opcode_set, crypto, const_pool, integrity_hash, func_pool, string_pool = loader.load(tmp_path)
    
    # Patch: disable noise/checks, add instruction limit
    vm._add_timing_noise = lambda: None
    vm._anti_debug_check = lambda: True
    vm._integrity_check = lambda: True
    
    captured = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    
    # Execute with instruction counter
    vm.running = True
    count = 0
    max_instr = 500
    while vm.running and vm.ip < vm.code_size and count < max_instr:
        count += 1
        raw_opcode = vm._read_byte()
        instruction = vm.opcode_set.decode_opcode(raw_opcode, vm.context)
        
        if instruction == 0x00:  # NOP
            pass
        elif instruction == 0x01:  # PUSH_IMM
            vm._push(vm._read_dword())
        elif instruction == 0x02:  # PUSH_REG
            vm._push(vm.registers[vm._read_byte() & 0x0F])
        elif instruction == 0x03:  # POP_REG
            vm.registers[vm._read_byte() & 0x0F] = vm._pop()
        elif instruction == 0x06:  # ADD
            b = vm._pop(); a = vm._pop()
            r = (a + b) & 0xFFFFFFFF; vm._push(r)
            vm.flags['z'] = r == 0; vm.flags['c'] = (a + b) > 0xFFFFFFFF
        elif instruction == 0x07:  # SUB
            b = vm._pop(); a = vm._pop()
            r = (a - b) & 0xFFFFFFFF; vm._push(r)
            vm.flags['z'] = r == 0; vm.flags['n'] = a < b
        elif instruction == 0x08:  # MUL
            b = vm._pop(); a = vm._pop()
            vm._push((a * b) & 0xFFFFFFFF)
        elif instruction == 0x09:  # DIV
            b = vm._pop(); a = vm._pop()
            vm._push(a // b if b else 0)
        elif instruction == 0x0A:  # MOD
            b = vm._pop(); a = vm._pop()
            vm._push(a % b if b else 0)
        elif instruction == 0x11:  # CMP
            b = vm._pop(); a = vm._pop()
            vm.flags['z'] = a == b; vm.flags['n'] = a < b; vm.flags['c'] = a > b
        elif instruction == 0x12:  # JMP
            addr = vm._read_dword()
            if count > 480:
                print(f"  JMP to {addr}, ip was {vm.ip-5}")
            vm.ip = addr
        elif instruction == 0x13:  # JZ
            addr = vm._read_dword()
            if vm.flags['z']:
                if count > 480:
                    print(f"  JZ (taken) to {addr}, ip was {vm.ip-5}, flags={vm.flags}")
                vm.ip = addr
            elif count > 480:
                print(f"  JZ (not taken) to {addr}, ip now {vm.ip}, flags={vm.flags}")
        elif instruction == 0x14:  # JNZ
            addr = vm._read_dword()
            if not vm.flags['z']:
                if count > 480:
                    print(f"  JNZ (taken) to {addr}, ip was {vm.ip-5}, flags={vm.flags}")
                vm.ip = addr
        elif instruction == 0x15:  # JG
            addr = vm._read_dword()
            if vm.flags['c'] and not vm.flags['z']:
                vm.ip = addr
        elif instruction == 0x16:  # JL
            addr = vm._read_dword()
            if vm.flags['n']:
                vm.ip = addr
        elif instruction == 0x17:  # JGE
            addr = vm._read_dword()
            if vm.flags['c'] or vm.flags['z']:
                vm.ip = addr
        elif instruction == 0x18:  # JLE
            addr = vm._read_dword()
            if vm.flags['n'] or vm.flags['z']:
                vm.ip = addr
        elif instruction == 0x1B:  # SYSCALL
            vm._handle_syscall(vm._pop())
        elif instruction == 0x1C:  # HALT
            vm.running = False
        elif instruction == 0x1D:  # DUP
            if vm.stack: vm._push(vm.stack[-1])
        elif instruction == 0x1E:  # SWAP
            if len(vm.stack) >= 2:
                vm.stack[-1], vm.stack[-2] = vm.stack[-2], vm.stack[-1]
        elif instruction == 0x0E:  # NOT
            a = vm._pop(); vm._push((~a) & 0xFFFFFFFF)
        elif instruction == 0x2B:  # FAKE_JMP
            vm._read_dword()
        elif instruction == 0x2C:  # FAKE_CALL
            vm._read_dword()
        elif instruction == 0x2A:  # NOISE
            pass
        else:
            if instruction >= 0x30 and instruction <= 0x39:  # DUMMY
                for _ in range(__import__('random').randint(0, 3)):
                    vm._read_byte()
            else:
                print(f"  Unknown inst 0x{instruction:02X} at count {count}, ip={vm.ip}")
                break
    
    sys.stdout = old_stdout
    
    if count >= max_instr:
        print(f"STOPPED after {count} instructions (limit)")
        print(f"IP: {vm.ip}, Stack: {vm.stack[-5:] if vm.stack else []}")
        print(f"Registers: {[r for r in vm.registers[:5]]}")
        print(f"Flags: {vm.flags}")
    else:
        print(f"Completed after {count} instructions")
    
    print(f"Captured output: {captured.getvalue()!r}")
finally:
    os.unlink(tmp_path)
