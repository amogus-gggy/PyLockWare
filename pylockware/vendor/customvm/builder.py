import struct
import time
import hashlib
from .opcodes import *
from .crypto import RuntimeCrypto

MAGIC = b'CVMX'
VERSION = 0x01000002  # v2: random opcodes + full-block XOR decrypt


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
        self.func_pool = []   # list of (name, kind, source_or_none)
        self.string_pool = []

    def add_instruction(self, opcode, *operands):
        self.instructions.append(Instruction(opcode, list(operands)))
        return self

    def add_label(self, name):
        self.labels[name] = len(self._estimate_bytecode())
        return self

    def add_const(self, value):
        if value not in self.const_pool:
            self.const_pool.append(value)
        return self.const_pool.index(value)

    def add_string(self, value):
        if value not in self.string_pool:
            self.string_pool.append(value)
        return self.string_pool.index(value)

    # ---- Instruction helpers ----

    def nop(self):          return self.add_instruction(INST_NOP)
    def push_imm(self, v):  return self.add_instruction(INST_PUSH_IMM, v)
    def push_reg(self, r):  return self.add_instruction(INST_PUSH_REG, r)
    def pop_reg(self, r):   return self.add_instruction(INST_POP_REG, r)
    def load_mem(self):     return self.add_instruction(INST_LOAD_MEM)
    def store_mem(self):    return self.add_instruction(INST_STORE_MEM)
    def add(self):          return self.add_instruction(INST_ADD)
    def sub(self):          return self.add_instruction(INST_SUB)
    def mul(self):          return self.add_instruction(INST_MUL)
    def div(self):          return self.add_instruction(INST_DIV)
    def mod(self):          return self.add_instruction(INST_MOD)
    def and_op(self):       return self.add_instruction(INST_AND)
    def or_op(self):        return self.add_instruction(INST_OR)
    def xor_op(self):       return self.add_instruction(INST_XOR)
    def not_op(self):       return self.add_instruction(INST_NOT)
    def shl(self):          return self.add_instruction(INST_SHL)
    def shr(self):          return self.add_instruction(INST_SHR)
    def cmp(self):          return self.add_instruction(INST_CMP)
    def halt(self):         return self.add_instruction(INST_HALT)
    def dup(self):          return self.add_instruction(INST_DUP)
    def swap(self):         return self.add_instruction(INST_SWAP)
    def rot(self):          return self.add_instruction(INST_ROT)
    def ret(self):          return self.add_instruction(INST_RET)
    def syscall(self):      return self.add_instruction(INST_SYSCALL)
    def str_concat(self):   return self.add_instruction(INST_STR_CONCAT)
    def str_cmp(self):      return self.add_instruction(INST_STR_CMP)
    def str_len(self):      return self.add_instruction(INST_STR_LEN)
    def str_get(self):      return self.add_instruction(INST_STR_GET)
    def str_slice(self):    return self.add_instruction(INST_STR_SLICE)

    def load_const(self, idx):
        return self.add_instruction(INST_LOAD_CONST, idx)

    def str_load(self, idx):
        return self.add_instruction(INST_STR_LOAD, idx)

    def jmp(self, label):
        self.label_refs.append((len(self.instructions), label))
        return self.add_instruction(INST_JMP, 0)

    def jz(self, label):
        self.label_refs.append((len(self.instructions), label))
        return self.add_instruction(INST_JZ, 0)

    def jnz(self, label):
        self.label_refs.append((len(self.instructions), label))
        return self.add_instruction(INST_JNZ, 0)

    def jg(self, label):
        self.label_refs.append((len(self.instructions), label))
        return self.add_instruction(INST_JG, 0)

    def jl(self, label):
        self.label_refs.append((len(self.instructions), label))
        return self.add_instruction(INST_JL, 0)

    def jge(self, label):
        self.label_refs.append((len(self.instructions), label))
        return self.add_instruction(INST_JGE, 0)

    def jle(self, label):
        self.label_refs.append((len(self.instructions), label))
        return self.add_instruction(INST_JLE, 0)

    def call(self, label):
        self.label_refs.append((len(self.instructions), label))
        return self.add_instruction(INST_CALL, 0)

    # ---- Internal helpers ----

    def _estimate_bytecode(self):
        """Return raw (unencoded) bytecode bytes for size estimation."""
        buf = bytearray()
        for inst in self.instructions:
            buf.append(inst.opcode)
            if inst.opcode == INST_PUSH_IMM:
                buf.extend(b'\x00' * 4)
            elif inst.opcode in (INST_PUSH_REG, INST_POP_REG):
                buf.append(0)
            elif inst.opcode in (INST_JMP, INST_JZ, INST_JNZ,
                                  INST_JG, INST_JL, INST_JGE, INST_JLE, INST_CALL):
                buf.extend(b'\x00' * 4)
            elif inst.opcode in (INST_LOAD_CONST, INST_STR_LOAD):
                buf.extend(b'\x00' * 2)
        return buf

    def _encode_bytecode(self, opcode_set):
        """Encode instructions using the randomized opcode set."""
        bytecode = bytearray()
        offset_map = {}

        for idx, inst in enumerate(self.instructions):
            offset_map[idx] = len(bytecode)
            # context changes every 16 instructions
            context = (idx // 16) & 0xFF
            encoded = opcode_set.get_opcode(inst.opcode, context)
            bytecode.append(encoded)

            if inst.opcode == INST_PUSH_IMM:
                bytecode.extend(struct.pack('<I', inst.operands[0] & 0xFFFFFFFF))
            elif inst.opcode in (INST_PUSH_REG, INST_POP_REG):
                bytecode.append(inst.operands[0] & 0xFF)
            elif inst.opcode in (INST_JMP, INST_JZ, INST_JNZ,
                                  INST_JG, INST_JL, INST_JGE, INST_JLE, INST_CALL):
                bytecode.extend(struct.pack('<I', inst.operands[0]))
            elif inst.opcode in (INST_LOAD_CONST, INST_STR_LOAD):
                bytecode.extend(struct.pack('<H', inst.operands[0]))

        # Patch label references
        for inst_idx, label in self.label_refs:
            if label in self.labels:
                target = self.labels[label]
                patch_offset = offset_map[inst_idx] + 1
                struct.pack_into('<I', bytecode, patch_offset, target)

        return bytes(bytecode)

    # ---- Public build ----

    def build(self, output_path, use_keyflow=False):
        """Compile instructions to a .cvmx file.

        Encryption: full-block XOR with SHA-256 derived key.
        Opcodes:    randomized per-build permutation.
        """
        # Unique seed per build
        seed_data = hashlib.sha256(
            (str(time.time()) + str(id(self))).encode()
        ).digest()

        opcode_set = OpcodeSet(int.from_bytes(seed_data[:4], 'little'))
        crypto = RuntimeCrypto(seed_data)

        # --- Code section ---
        raw_bytecode = self._encode_bytecode(opcode_set)
        code_section = crypto.encrypt_block(raw_bytecode, 0)

        # --- Const pool section ---
        const_data = bytearray()
        const_data.extend(struct.pack('<H', len(self.const_pool)))
        for c in self.const_pool:
            const_data.extend(struct.pack('<I', c & 0xFFFFFFFF))
        const_section = crypto.encrypt_block(bytes(const_data), 1)

        # --- Func pool section ---
        func_section = None
        if self.func_pool:
            func_data = bytearray()
            func_data.extend(struct.pack('<H', len(self.func_pool)))
            for func_name, kind, source in self.func_pool:
                name_bytes = func_name.encode('utf-8')
                func_data.extend(struct.pack('<B', len(name_bytes)))
                func_data.extend(name_bytes)
                if kind == 'builtin':
                    func_data.extend(struct.pack('<B', 0))
                else:
                    func_data.extend(struct.pack('<B', 1))
                    src_bytes = source.encode('utf-8')
                    func_data.extend(struct.pack('<I', len(src_bytes)))
                    func_data.extend(src_bytes)
            func_section = crypto.encrypt_block(bytes(func_data), 2)

        # --- String pool section ---
        str_section = None
        if self.string_pool:
            str_data = bytearray()
            str_data.extend(struct.pack('<H', len(self.string_pool)))
            for s in self.string_pool:
                enc = s.encode('utf-8')
                str_data.extend(struct.pack('<H', len(enc)))
                str_data.extend(enc)
            str_section = crypto.encrypt_block(bytes(str_data), 3)

        # --- Assemble file ---
        sections = [(0x01, code_section), (0x02, const_section)]
        if func_section:
            sections.append((0x04, func_section))
        if str_section:
            sections.append((0x05, str_section))

        out = bytearray()
        out.extend(MAGIC)
        out.extend(struct.pack('<I', VERSION))
        out.extend(struct.pack('<Q', int(time.time())))
        out.extend(struct.pack('<I', len(seed_data)))
        out.extend(seed_data)
        out.extend(struct.pack('<H', len(sections)))
        for stype, sdata in sections:
            out.append(stype)
            out.extend(struct.pack('<I', len(sdata)))
            out.extend(sdata)

        with open(output_path, 'wb') as f:
            f.write(out)

        return output_path
