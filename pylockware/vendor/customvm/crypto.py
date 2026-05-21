import hashlib
import struct
import time


class RuntimeCrypto:
    """Simple XOR-based block encryption using SHA-256 key derivation."""

    def __init__(self, seed_data):
        self._seed = seed_data
        self._key = hashlib.sha256(seed_data).digest()

    def _make_key(self, block_index, length):
        """Derive a key of given length for a block index."""
        key = bytearray()
        counter = 0
        while len(key) < length:
            data = self._key + struct.pack('<I', block_index) + struct.pack('<I', counter)
            key.extend(hashlib.sha256(data).digest())
            counter += 1
        return bytes(key[:length])

    def encrypt_block(self, data, block_index):
        key = self._make_key(block_index, len(data))
        return bytes(b ^ k for b, k in zip(data, key))

    def decrypt_block(self, data, block_index):
        # XOR is symmetric
        return self.encrypt_block(data, block_index)


class KeyflowCrypto:
    """Stub - keyflow disabled, kept for API compatibility."""

    def __init__(self, seed_data):
        self._seed = seed_data

    def encrypt_bytecode(self, bytecode):
        return bytecode

    def decrypt_instruction(self, encrypted_bytecode, ip, prev_opcode, context):
        if ip >= len(encrypted_bytecode):
            return 0
        return encrypted_bytecode[ip]


class ObfuscationLayer:
    @staticmethod
    def apply_layer_1(data):
        result = bytearray(len(data))
        for i in range(len(data)):
            result[i] = ((data[i] << 3) | (data[i] >> 5)) & 0xFF
        return bytes(result)

    @staticmethod
    def remove_layer_1(data):
        result = bytearray(len(data))
        for i in range(len(data)):
            result[i] = ((data[i] >> 3) | (data[i] << 5)) & 0xFF
        return bytes(result)

    @staticmethod
    def apply_layer_2(data, key):
        result = bytearray(len(data))
        for i in range(len(data)):
            k = key[i % len(key)]
            result[i] = (data[i] + k) & 0xFF
        return bytes(result)

    @staticmethod
    def remove_layer_2(data, key):
        result = bytearray(len(data))
        for i in range(len(data)):
            k = key[i % len(key)]
            result[i] = (data[i] - k) & 0xFF
        return bytes(result)

    @staticmethod
    def apply_layer_3(data):
        result = bytearray(len(data))
        for i in range(len(data)):
            result[i] = data[i] ^ ((i * 137) & 0xFF)
        return bytes(result)

    @staticmethod
    def remove_layer_3(data):
        return ObfuscationLayer.apply_layer_3(data)


def compute_integrity_hash(data):
    return hashlib.sha256(data).digest()


def verify_timing(start_time, max_delta=5.0):
    elapsed = time.time() - start_time
    return elapsed < max_delta
