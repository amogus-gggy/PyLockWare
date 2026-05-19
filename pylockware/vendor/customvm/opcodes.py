import random
import time

class OpcodeSet:
    def __init__(self, seed=None):
        self._seed = seed or int(time.time() * 1000000) & 0xFFFFFFFF
        self._rng = random.Random(self._seed)
        self._base_opcodes = self._generate_base_opcodes()
        self._context_map = {}
        
    def _generate_base_opcodes(self):
        opcodes = list(range(256))
        self._rng.shuffle(opcodes)
        return opcodes
    
    def get_opcode(self, instruction, context=0):
        ctx_key = (instruction, context & 0xFF)
        if ctx_key not in self._context_map:
            # Simple rotation by context preserves bijection:
            #   base[] is a permutation → adding a constant keeps it a permutation.
            # This guarantees NO collisions, unlike the old offset approach.
            rotated = (self._base_opcodes[instruction] + context * 13) & 0xFF
            self._context_map[ctx_key] = rotated
        return self._context_map[ctx_key]
    
    def decode_opcode(self, byte_val, context=0):
        for inst in range(256):
            if self.get_opcode(inst, context) == byte_val:
                return inst
        return 0xFF

INST_NOP = 0x00
INST_PUSH_IMM = 0x01
INST_PUSH_REG = 0x02
INST_POP_REG = 0x03
INST_LOAD_MEM = 0x04
INST_STORE_MEM = 0x05
INST_ADD = 0x06
INST_SUB = 0x07
INST_MUL = 0x08
INST_DIV = 0x09
INST_MOD = 0x0A
INST_AND = 0x0B
INST_OR = 0x0C
INST_XOR = 0x0D
INST_NOT = 0x0E
INST_SHL = 0x0F
INST_SHR = 0x10
INST_CMP = 0x11
INST_JMP = 0x12
INST_JZ = 0x13
INST_JNZ = 0x14
INST_JG = 0x15
INST_JL = 0x16
INST_JGE = 0x17
INST_JLE = 0x18
INST_CALL = 0x19
INST_RET = 0x1A
INST_SYSCALL = 0x1B
INST_HALT = 0x1C
INST_DUP = 0x1D
INST_SWAP = 0x1E
INST_ROT = 0x1F
INST_LOAD_CONST = 0x20
INST_STORE_CONST = 0x21
INST_ALLOC = 0x22
INST_FREE = 0x23
INST_COPY = 0x24
INST_FILL = 0x25
INST_RAND = 0x26
INST_TIME = 0x27
INST_CHECK = 0x28
INST_VERIFY = 0x29
INST_NOISE = 0x2A
INST_FAKE_JMP = 0x2B
INST_FAKE_CALL = 0x2C
INST_CONTEXT_SHIFT = 0x2D
INST_FOLD_ADD = 0x2E
INST_FOLD_MUL = 0x2F
INST_DUMMY_1 = 0x30
INST_DUMMY_2 = 0x31
INST_DUMMY_3 = 0x32
INST_DUMMY_4 = 0x33
INST_DUMMY_5 = 0x34
INST_DUMMY_6 = 0x35
INST_DUMMY_7 = 0x36
INST_DUMMY_8 = 0x37
INST_DUMMY_9 = 0x38
INST_DUMMY_10 = 0x39

# String operations (not hookable — use Python native str ops directly)
INST_STR_LOAD = 0x3A    # Push string from string_pool[index]
INST_STR_CMP = 0x3B     # Compare two strings → sets flags z/n/c (not hookable)
INST_STR_CONCAT = 0x3C  # Concatenate two strings
INST_STR_LEN = 0x3D     # Get string length → push int
INST_STR_GET = 0x3E     # Get character at index → push str
INST_STR_SLICE = 0x3F   # Slice string [start:end] → push str
