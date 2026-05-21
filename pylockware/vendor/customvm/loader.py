import struct
import hashlib
import builtins
from .opcodes import OpcodeSet
from .crypto import RuntimeCrypto

MAGIC = b'CVMX'
SUPPORTED_VERSIONS = {0x01000000, 0x01000001, 0x01000002}


class BytecodeLoader:
    def __init__(self):
        self.opcode_set = None
        self.crypto = None

    def load(self, filepath):
        with open(filepath, 'rb') as f:
            data = f.read()
        return self._parse(data)

    def _parse(self, data):
        offset = 0

        # Magic
        if data[offset:offset+4] != MAGIC:
            raise ValueError("Invalid file format")
        offset += 4

        # Version
        version = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        if version not in SUPPORTED_VERSIONS:
            raise ValueError(f"Unsupported version: {version:#010x}")

        # Timestamp (ignored)
        offset += 8

        # Old versions had a flags byte after timestamp
        if version == 0x01000001:
            offset += 1  # skip flags byte

        # Seed
        seed_size = struct.unpack('<I', data[offset:offset+4])[0]
        offset += 4
        seed_data = data[offset:offset+seed_size]
        offset += seed_size

        self.opcode_set = OpcodeSet(int.from_bytes(seed_data[:4], 'little'))
        self.crypto = RuntimeCrypto(seed_data)

        # Sections
        num_sections = struct.unpack('<H', data[offset:offset+2])[0]
        offset += 2

        sections = []
        for _ in range(num_sections):
            stype = data[offset]
            offset += 1
            ssize = struct.unpack('<I', data[offset:offset+4])[0]
            offset += 4
            sdata = data[offset:offset+ssize]
            offset += ssize
            sections.append((stype, sdata))

        code = None
        const_pool = []
        func_pool = []
        string_pool = []
        integrity_hash = None

        for stype, sdata in sections:
            if stype == 0x01:
                # Code: decrypt entire block, then execute
                code = self.crypto.decrypt_block(sdata, 0)
                integrity_hash = hashlib.sha256(code).digest()

            elif stype == 0x02:
                dec = self.crypto.decrypt_block(sdata, 1)
                n = struct.unpack('<H', dec[0:2])[0]
                pos = 2
                for _ in range(n):
                    val = struct.unpack('<I', dec[pos:pos+4])[0]
                    pos += 4
                    const_pool.append(val)

            elif stype == 0x04:
                dec = self.crypto.decrypt_block(sdata, 2)
                n = struct.unpack('<H', dec[0:2])[0]
                pos = 2
                func_infos = []
                for _ in range(n):
                    name_len = dec[pos]; pos += 1
                    name = dec[pos:pos+name_len].decode('utf-8'); pos += name_len
                    kind = dec[pos]; pos += 1
                    source = None
                    if kind == 1:
                        src_len = struct.unpack('<I', dec[pos:pos+4])[0]; pos += 4
                        source = dec[pos:pos+src_len].decode('utf-8'); pos += src_len
                    func_infos.append((name, kind, source))

                for name, kind, source in func_infos:
                    if kind == 0:
                        func = self._resolve_builtin(name)
                        func_pool.append(func)
                    else:
                        local_ns = {}
                        exec(source, {"__builtins__": builtins}, local_ns)
                        func_pool.append(local_ns[name])

            elif stype == 0x05:
                dec = self.crypto.decrypt_block(sdata, 3)
                n = struct.unpack('<H', dec[0:2])[0]
                pos = 2
                for _ in range(n):
                    slen = struct.unpack('<H', dec[pos:pos+2])[0]; pos += 2
                    string_pool.append(dec[pos:pos+slen].decode('utf-8')); pos += slen

        return code, self.opcode_set, self.crypto, const_pool, integrity_hash, func_pool, string_pool, None

    def _resolve_builtin(self, name):
        """Resolve a function name to a callable. Never raises."""
        import builtins as _builtins

        # Python builtins
        func = getattr(_builtins, name, None)
        if func is not None and callable(func):
            return func

        # String methods
        _str_methods = {
            'upper':      lambda s: s.upper(),
            'lower':      lambda s: s.lower(),
            'strip':      lambda s: s.strip(),
            'lstrip':     lambda s: s.lstrip(),
            'rstrip':     lambda s: s.rstrip(),
            'capitalize': lambda s: s.capitalize(),
            'title':      lambda s: s.title(),
            'swapcase':   lambda s: s.swapcase(),
            'replace':    lambda s, old, new: s.replace(old, new),
            'split':      lambda s, *a: s.split(*a),
            'join':       lambda sep, it: sep.join(it),
            'startswith': lambda s, p: s.startswith(p),
            'endswith':   lambda s, p: s.endswith(p),
            'find':       lambda s, sub: s.find(sub),
            'count':      lambda s, sub: s.count(sub),
        }
        if name in _str_methods:
            return _str_methods[name]

        # Unknown - return a lazy resolver that looks up in caller's globals at runtime
        # We store the name and resolve when called
        def _lazy_resolver(*args, **kwargs):
            import sys
            # Walk up frames to find the name in some globals
            frame = sys._getframe(1)
            while frame is not None:
                if name in frame.f_globals:
                    return frame.f_globals[name](*args, **kwargs)
                frame = frame.f_back
            raise NameError(f"Function '{name}' not found at runtime")

        _lazy_resolver.__vm_func_name__ = name
        return _lazy_resolver
