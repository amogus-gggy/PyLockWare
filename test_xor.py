import base64, zlib

# Test XOR encryption
def xor_encrypt(data, key):
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

data = b'Hello'
key = bytes([234, 156, 89])  # Random key
encrypted = xor_encrypt(data, key)
encoded = base64.b64encode(encrypted).decode('ascii')
print(f'Original: {data}')
print(f'Key: {list(key)}')
print(f'Encrypted: {encoded}')

# Decode
decoded_data = base64.b64decode(encoded.encode('utf-8'))
print(f'Decoded data: {decoded_data}')
key2 = bytes([234, 156, 89])
decrypted = bytes(b ^ key2[i % len(key2)] for i, b in enumerate(decoded_data))
print(f'Decrypted: {decrypted}')
