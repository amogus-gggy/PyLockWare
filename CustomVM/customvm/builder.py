import struct
import time
import hashlib
from .opcodes import *
from .crypto import RuntimeCrypto, ObfuscationLayer

MAGIC = b'CVMX'
VERSION = 0x01000000

class Instruction:
    def __init__(self, opcode, operands=None):
        self.opcode = opcode
        self.operands = operands or []

class VMBuilder:
    def __init__(self):
        self.instructions = []
        self.const_pool = []
        self.labels = {}
        self.label_refs = []
        self.func_pool = []  # list of (name, kind, source_or_none)
        # kind: 'builtin' or 'user'
        self.string_pool = []

    def add_instruction(self, opcode, *operands):
        self.instructions.append(Instruction(opcode, list(operands)))
        return self

    def add_label(self, name):
        self.labels[name] = len(self._estimate_size())
        return self

    def add_const(self, value):
        if value not in self.const_pool:
            self.const_pool.append(value)
        return self.const_pool.index(value)

    def nop(self):
        return self.add_instruction(INST_NOP)

    def push_imm(self, value):
        return self.add_instruction(INST_PUSH_IMM, value)

    def push_reg(self, reg):
        return self.add_instruction(INST_PUSH_REG, reg)

    def pop_reg(self, reg):
        return self.add_instruction(INST_POP_REG, reg)

    def load_mem(self):
        return self.add_instruction(INST_LOAD_MEM)

    def store_mem(self):
        return self.add_instruction(INST_STORE_MEM)

    def add(self):
        return self.add_instruction(INST_ADD)

    def sub(self):
        return self.add_instruction(INST_SUB)

    def mul(self):
        return self.add_instruction(INST_MUL)

    def div(self):
        return self.add_instruction(INST_DIV)

    def mod(self):
        return self.add_instruction(INST_MOD)

    def and_op(self):
        return self.add_instruction(INST_AND)

    def or_op(self):
        return self.add_instruction(INST_OR)

    def xor_op(self):
        return self.add_instruction(INST_XOR)

    def not_op(self):
        return self.add_instruction(INST_NOT)

    def shl(self):
        return self.add_instruction(INST_SHL)

    def shr(self):
        return self.add_instruction(INST_SHR)

    def cmp(self):
        return self.add_instruction(INST_CMP)

    def jmp(self, label):
        self.label_refs.append((len(self.instructions), label, 'jmp'))
        return self.add_instruction(INST_JMP, 0)

    def jz(self, label):
        self.label_refs.append((len(self.instructions), label, 'jz'))
        return self.add_instruction(INST_JZ, 0)

    def jnz(self, label):
        self.label_refs.append((len(self.instructions), label, 'jnz'))
        return self.add_instruction(INST_JNZ, 0)

    def jg(self, label):
        self.label_refs.append((len(self.instructions), label, 'jg'))
        return self.add_instruction(INST_JG, 0)

    def jl(self, label):
        self.label_refs.append((len(self.instructions), label, 'jl'))
        return self.add_instruction(INST_JL, 0)

    def jge(self, label):
        self.label_refs.append((len(self.instructions), label, 'jge'))
        return self.add_instruction(INST_JGE, 0)

    def jle(self, label):
        self.label_refs.append((len(self.instructions), label, 'jle'))
        return self.add_instruction(INST_JLE, 0)

    def call(self, label):
        self.label_refs.append((len(self.instructions), label, 'call'))
        return self.add_instruction(INST_CALL, 0)

    def ret(self):
        return self.add_instruction(INST_RET)

    def syscall(self):
        return self.add_instruction(INST_SYSCALL)

    def halt(self):
        return self.add_instruction(INST_HALT)

    def dup(self):
        return self.add_instruction(INST_DUP)

    def swap(self):
        return self.add_instruction(INST_SWAP)

    def rot(self):
        return self.add_instruction(INST_ROT)

    def load_const(self, idx):
        return self.add_instruction(INST_LOAD_CONST, idx)

    def add_string(self, value):
        """Add a string to the string pool and return its index."""
        if value not in self.string_pool:
            self.string_pool.append(value)
        return self.string_pool.index(value)

    def str_load(self, idx):
        return self.add_instruction(INST_STR_LOAD, idx)

    def str_cmp(self):
        return self.add_instruction(INST_STR_CMP)

    def str_concat(self):
        return self.add_instruction(INST_STR_CONCAT)

    def str_len(self):
        return self.add_instruction(INST_STR_LEN)

    def str_get(self):
        return self.add_instruction(INST_STR_GET)

    def str_slice(self):
        return self.add_instruction(INST_STR_SLICE)

    def str_cmp(self):
        return self.add_instruction(INST_STR_CMP)

    def _estimate_size(self):
        size = 0
        bytecode = bytearray()
        for inst in self.instructions:
            bytecode.append(0)
            size += 1
            if inst.opcode == INST_PUSH_IMM:
                bytecode.extend([0, 0, 0, 0])
                size += 4
            elif inst.opcode in [INST_PUSH_REG, INST_POP_REG]:
                bytecode.append(0)
                size += 1
            elif inst.opcode in [INST_JMP, INST_JZ, INST_JNZ, INST_JG, INST_JL, INST_JGE, INST_JLE, INST_CALL]:
                bytecode.extend([0, 0, 0, 0])
                size += 4
            elif inst.opcode == INST_LOAD_CONST:
                bytecode.extend([0, 0])
                size += 2
            elif inst.opcode == INST_STR_LOAD:
                bytecode.extend([0, 0])
                size += 2
        return bytecode

    def build(self, output_path):
        seed_data = hashlib.sha256(str(time.time()).encode()).digest()
        opcode_set = OpcodeSet(int.from_bytes(seed_data[:4], 'little'))
        crypto = RuntimeCrypto(seed_data)

        bytecode = bytearray()
        offset_map = {}

        for idx, inst in enumerate(self.instructions):
            offset_map[idx] = len(bytecode)

            context = 0
            encoded_opcode = opcode_set.get_opcode(inst.opcode, context)
            bytecode.append(encoded_opcode)

            if inst.opcode == INST_PUSH_IMM:
                bytecode.extend(struct.pack('<I', inst.operands[0] & 0xFFFFFFFF))
            elif inst.opcode in [INST_PUSH_REG, INST_POP_REG]:
                bytecode.append(inst.operands[0] & 0xFF)
            elif inst.opcode in [INST_JMP, INST_JZ, INST_JNZ, INST_JG, INST_JL, INST_JGE, INST_JLE, INST_CALL]:
                bytecode.extend(struct.pack('<I', inst.operands[0]))
            elif inst.opcode == INST_LOAD_CONST:
                bytecode.extend(struct.pack('<H', inst.operands[0]))
            elif inst.opcode == INST_STR_LOAD:
                bytecode.extend(struct.pack('<H', inst.operands[0]))

        for inst_idx, label, jmp_type in self.label_refs:
            if label in self.labels:
                target_offset = self.labels[label]
                bytecode_offset = offset_map[inst_idx] + 1
                struct.pack_into('<I', bytecode, bytecode_offset, target_offset)

        encrypted = ObfuscationLayer.apply_layer_1(bytes(bytecode))
        encrypted = ObfuscationLayer.apply_layer_2(encrypted, seed_data)
        encrypted = ObfuscationLayer.apply_layer_3(encrypted)
        encrypted = crypto.encrypt_block(encrypted, 0)

        code_section = encrypted

        const_data = bytearray()
        const_data.extend(struct.pack('<H', len(self.const_pool)))
        for c in self.const_pool:
            const_data.extend(struct.pack('<I', c & 0xFFFFFFFF))
        encrypted_const = crypto.encrypt_block(bytes(const_data), 1)

        header = bytearray()
        header.extend(MAGIC)
        header.extend(struct.pack('<I', VERSION))
        header.extend(struct.pack('<Q', int(time.time())))
        header.extend(struct.pack('<I', len(seed_data)))
        header.extend(seed_data)

        sections = []

        # Section 0x01: code
        sections.append((0x01, code_section))
        # Section 0x02: const pool
        sections.append((0x02, encrypted_const))

        # Section 0x04: function pool (if any)
        if self.func_pool:
            func_data = bytearray()
            func_data.extend(struct.pack('<H', len(self.func_pool)))
            for func_name, kind, source in self.func_pool:
                name_bytes = func_name.encode('utf-8')
                func_data.extend(struct.pack('<B', len(name_bytes)))
                func_data.extend(name_bytes)
                if kind == 'builtin':
                    func_data.extend(struct.pack('<B', 0))
                else:  # user
                    func_data.extend(struct.pack('<B', 1))
                    source_bytes = source.encode('utf-8')
                    func_data.extend(struct.pack('<I', len(source_bytes)))
                    func_data.extend(source_bytes)
            encrypted_func = crypto.encrypt_block(bytes(func_data), 2)
            sections.append((0x04, encrypted_func))

        # Section 0x05: string pool (if any)
        if self.string_pool:
            str_data = bytearray()
            str_data.extend(struct.pack('<H', len(self.string_pool)))
            for s in self.string_pool:
                encoded = s.encode('utf-8')
                str_data.extend(struct.pack('<H', len(encoded)))
                str_data.extend(encoded)
            encrypted_str = crypto.encrypt_block(bytes(str_data), 3)
            sections.append((0x05, encrypted_str))

        header.extend(struct.pack('<H', len(sections)))

        for section_type, section_data in sections:
            header.append(section_type)
            header.extend(struct.pack('<I', len(section_data)))
            header.extend(section_data)

        with open(output_path, 'wb') as f:
            f.write(header)

        return output_path
