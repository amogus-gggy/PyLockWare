import hashlib
import time

class RuntimeCrypto:
    def __init__(self, seed_data):
        self._seed = seed_data
        self._state = self._init_state()
        
    def _init_state(self):
        h = hashlib.sha256(self._seed).digest()
        return list(h)
    
    def _evolve_state(self, iteration):
        data = bytes(self._state) + iteration.to_bytes(8, 'little')
        h = hashlib.sha256(data).digest()
        self._state = list(h)
        
    def derive_key(self, index, length=32):
        self._evolve_state(index)
        key = bytes(self._state[:length])
        return key
    
    def decrypt_block(self, data, block_index):
        key_length = max(len(data), 32)
        key = self.derive_key(block_index, key_length)
        result = bytearray(len(data))
        for i in range(len(data)):
            result[i] = data[i] ^ key[i % len(key)]
        return bytes(result)
    
    def encrypt_block(self, data, block_index):
        return self.decrypt_block(data, block_index)

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
    h1 = hashlib.sha256(data).digest()
    h2 = hashlib.sha512(data).digest()
    combined = bytes(a ^ b for a, b in zip(h1, h2[:32]))
    return combined

def verify_timing(start_time, max_delta=5.0):
    elapsed = time.time() - start_time
    return elapsed < max_delta
