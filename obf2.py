#!/usr/bin/env python3
"""
Python Recursive Exec Obfuscator v2
Случайное чередование: zlib, lzma, fernet, xor(0xFF)
"""
import base64
import sys
import random
import zlib
import lzma
import argparse
from cryptography.fernet import Fernet


def generate_stub(method: str, data_b64: str, key_b64: str = None) -> str:
    """Генерирует слой с жёстко зашитой логикой обратного преобразования"""
    if method == 'fernet':
        return (f'import base64\n'
                f'from cryptography.fernet import Fernet\n'
                f'exec(Fernet(base64.urlsafe_b64decode("{key_b64}"))'
                f'.decrypt(base64.urlsafe_b64decode("{data_b64}"))'
                f'.decode("utf-8"))')
    elif method == 'zlib':
        return (f'import base64, zlib\n'
                f'exec(zlib.decompress(base64.urlsafe_b64decode("{data_b64}"))'
                f'.decode("utf-8"))')
    elif method == 'lzma':
        return (f'import base64, lzma\n'
                f'exec(lzma.decompress(base64.urlsafe_b64decode("{data_b64}"))'
                f'.decode("utf-8"))')
    elif method == 'xor':
        return (f'import base64\n'
                f'exec(bytes(b ^ 0xFF for b in base64.urlsafe_b64decode("{data_b64}"))'
                f'.decode("utf-8"))')
    return ''


def obfuscate_layer(code: str, method: str) -> str:
    """Обрабатывает код выбранным методом и возвращает stub"""
    code_bytes = code.encode('utf-8')

    if method == 'fernet':
        key = Fernet.generate_key()
        data = Fernet(key).encrypt(code_bytes)
        key_b64 = base64.urlsafe_b64encode(key).decode('ascii')
    elif method == 'zlib':
        key_b64 = None
        data = zlib.compress(code_bytes)
    elif method == 'lzma':
        key_b64 = None
        data = lzma.compress(code_bytes)
    elif method == 'xor':
        key_b64 = None
        data = bytes(b ^ 0xFF for b in code_bytes)
    else:
        raise ValueError(f"Unknown method: {method}")

    data_b64 = base64.urlsafe_b64encode(data).decode('ascii')
    return generate_stub(method, data_b64, key_b64)


def recursive_obfuscate(source_code: str, layers: int = 3) -> str:
    methods = ['zlib', 'lzma', 'fernet', 'xor']
    chosen = [random.choice(methods) for _ in range(layers)]

    # Гарантия хотя бы одного слоя шифрования
    if 'fernet' not in chosen:
        chosen[random.randint(0, layers - 1)] = 'fernet'

    print(f"[*] Начинаем обфускацию: {layers} слоев ({', '.join(chosen)})...")

    current = source_code
    for m in chosen:
        current = obfuscate_layer(current, m)

    header = (f'#!/usr/bin/env python3\n'
              f'# Obfuscated by PyLockWare')
    return header + current


def create_launcher(source_file: str, layers: int = 5, output_file: str = None):
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except Exception as e:
        print(f"[!] Ошибка чтения файла: {e}")
        sys.exit(1)

    obfuscated = recursive_obfuscate(source_code, layers)

    if not output_file:
        output_file = source_file.replace('.py', '_obfuscated.py')

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(obfuscated)
        print(f"\n[+] Обфускация завершена!")
        print(f"[+] Сохранено в: {output_file}")
        print(f"[+] Размер: {len(obfuscated)} символов")
    except Exception as e:
        print(f"[!] Ошибка записи: {e}")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Python Recursive Exec Obfuscator')
    parser.add_argument('file', nargs='?', help='Python файл для обфускации')
    parser.add_argument('-l', '--layers', type=int, default=5, help='Количество слоев (default: 5)')
    parser.add_argument('-o', '--output', help='Выходной файл')
    args = parser.parse_args()

    if args.file:
        create_launcher(args.file, args.layers, args.output)
    else:
        parser.print_help()