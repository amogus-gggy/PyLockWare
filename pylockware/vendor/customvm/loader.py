import struct
import hashlib
import time
import builtins
from .opcodes import OpcodeSet
from .crypto import RuntimeCrypto, ObfuscationLayer, compute_integrity_hash

MAGIC = b'CVMX'
VERSION = 0x01000000

class BytecodeLoader:
    def __init__(self):
        self.header = None
        self.sections = []
        self.code_section = None
        self.const_section = None
        self.data_section = None
        self.opcode_set = None
        self.crypto = None

    def load(self, filepath):
        with open(filepath, 'rb') as f:
            data = f.read()

        return self._parse(data)

    def _parse(self, data):
        offset = 0

        magic = data[offset:offset+4]
        offset += 4
        if magic != MAGIC:
            raise ValueError("Invalid file format")

        version = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        if version != VERSION:
            raise ValueError("Unsupported version")

        timestamp = struct.unpack('<Q', data[offset:offset+8])[0]
        offset += 8

        seed_size = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        seed_data = data[offset:offset+seed_size]
        offset += seed_size

        self.opcode_set = OpcodeSet(int.from_bytes(seed_data[:4], 'little'))
        self.crypto = RuntimeCrypto(seed_data)

        num_sections = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2

        sections = []
        for _ in range(num_sections):
            section_type = struct.unpack('<B', data[offset:offset+1])[0]
            offset += 1
            section_size = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            section_data = data[offset:offset+section_size]
            offset += section_size
            sections.append((section_type, section_data))

        code = None
        const_pool = []
        integrity_hash = None
        func_pool = []
        string_pool = []

        # Map section types to their block indices for encryption
        section_block_map = {
            0x01: 0,  # code section
            0x02: 1,  # const pool
            0x04: 2,  # func pool
            0x05: 3,  # string pool
        }

        for section_type, section_data in sections:
            block_idx = section_block_map.get(section_type, 0)
            
            if section_type == 0x01:
                decrypted = self.crypto.decrypt_block(section_data, block_idx)
                decrypted = ObfuscationLayer.remove_layer_3(decrypted)
                decrypted = ObfuscationLayer.remove_layer_2(decrypted, seed_data)
                decrypted = ObfuscationLayer.remove_layer_1(decrypted)
                code = decrypted
                integrity_hash = hashlib.sha256(code).digest()
            elif section_type == 0x02:
                decrypted = self.crypto.decrypt_block(section_data, block_idx)
                num_consts = struct.unpack('<H', decrypted[0:2])[0]
                offset_const = 2
                for _ in range(num_consts):
                    val = struct.unpack('<I', decrypted[offset_const:offset_const+4])[0]
                    offset_const += 4
                    const_pool.append(val)
            elif section_type == 0x04:
                decrypted = self.crypto.decrypt_block(section_data, block_idx)
                num_funcs = struct.unpack('<H', decrypted[0:2])[0]
                offset_f = 2
                func_infos = []
                for _ in range(num_funcs):
                    name_len = struct.unpack('<B', decrypted[offset_f:offset_f+1])[0]
                    offset_f += 1
                    name = decrypted[offset_f:offset_f+name_len].decode('utf-8')
                    offset_f += name_len
                    kind = struct.unpack('<B', decrypted[offset_f:offset_f+1])[0]
                    offset_f += 1
                    source = None
                    if kind == 1:  # user-defined
                        source_len = struct.unpack('<I', decrypted[offset_f:offset_f+4])[0]
                        offset_f += 4
                        source = decrypted[offset_f:offset_f+source_len].decode('utf-8')
                        offset_f += source_len
                    func_infos.append((name, kind, source))

                for name, kind, source in func_infos:
                    if kind == 0:  # builtin
                        # Try to get from builtins first
                        func = getattr(builtins, name, None)
                        
                        # If not in builtins, check if it's a string method
                        if func is None:
                            # String methods
                            string_methods = {
                                'upper': lambda s: s.upper(),
                                'lower': lambda s: s.lower(),
                                'strip': lambda s: s.strip(),
                                'lstrip': lambda s: s.lstrip(),
                                'rstrip': lambda s: s.rstrip(),
                                'capitalize': lambda s: s.capitalize(),
                                'title': lambda s: s.title(),
                                'swapcase': lambda s: s.swapcase(),
                                'replace': lambda s, old, new: s.replace(old, new),
                                'split': lambda s, *args: s.split(*args) if args else s.split(),
                                'join': lambda sep, iterable: sep.join(iterable),
                                'startswith': lambda s, prefix: s.startswith(prefix),
                                'endswith': lambda s, suffix: s.endswith(suffix),
                                'find': lambda s, sub: s.find(sub),
                                'count': lambda s, sub: s.count(sub),
                            }
                            
                            if name in string_methods:
                                func = string_methods[name]
                            else:
                                raise ValueError(f"Builtin function '{name}' not found")
                        
                        func_pool.append(func)
                    elif kind == 1:  # user-defined
                        local_ns = {}
                        exec(source, {"__builtins__": builtins}, local_ns)
                        if name not in local_ns:
                            raise ValueError(f"Function '{name}' not defined after exec")
                        func_pool.append(local_ns[name])
            elif section_type == 0x03:
                pass
            elif section_type == 0x05:
                decrypted = self.crypto.decrypt_block(section_data, block_idx)
                num_strings = struct.unpack('<H', decrypted[0:2])[0]
                offset_s = 2
                for _ in range(num_strings):
                    str_len = struct.unpack('<H', decrypted[offset_s:offset_s+2])[0]
                    offset_s += 2
                    s = decrypted[offset_s:offset_s+str_len].decode('utf-8')
                    offset_s += str_len
                    string_pool.append(s)

        return code, self.opcode_set, self.crypto, const_pool, integrity_hash, func_pool, string_pool
