"""
PyLockWare Crypter Module
AST-based function encryption using machine fingerprinting
"""

import ast
import base64
import hashlib
import os
import platform
import secrets
import socket
import sys
import textwrap
import uuid
from typing import List, Any

from pylockware.transforms.state_machine_transformer import StateMachineTransformer
from pylockware.transforms.num_obf import NumberObfuscator
from pylockware.transforms.str_prot import StringProtectionTransformer


# ============================================================================
# XOR Encryption Utilities
# ============================================================================

def xor_encrypt(data: bytes, key: bytes) -> bytes:
    """XOR encrypt data with a repeating key."""
    return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))


def derive_key(seed: bytes, length: int = 32) -> bytes:
    """Derive a key of specified length from a seed using SHA-512."""
    h = hashlib.sha512(seed).digest()
    
    while len(h) < length:
        h += hashlib.sha512(h).digest()
    
    return h[:length]


def generate_seed(func_name: str) -> bytes:
    """Generate a deterministic seed for a function (no machine fingerprint)."""
    return f"pylockware|crypt|{func_name}".encode()


# ============================================================================
# Decorator
# ============================================================================

def crypt(func):
    """Decorator to mark functions for encryption."""
    return func


# ============================================================================
# Transformer
# ============================================================================

class CryptTransformer(ast.NodeTransformer):
    """AST transformer that encrypts functions marked with @crypt decorator."""

    def __init__(self):
        self.encrypted_count = 0

    def visit_FunctionDef(self, node):
        return self._transform(node, False)

    def visit_AsyncFunctionDef(self, node):
        return self._transform(node, True)

    def _transform(self, node, is_async):
        has_crypt = False
        decorators = []

        for dec in node.decorator_list:
            if isinstance(dec, ast.Name) and dec.id == "crypt":
                has_crypt = True
            else:
                decorators.append(dec)

        if not has_crypt:
            self.generic_visit(node)
            return node

        self.encrypted_count += 1

        clean = type(node)(
            name=node.name,
            args=node.args,
            body=node.body,
            decorator_list=[],
            returns=node.returns,
            type_comment=getattr(node, "type_comment", None),
        )

        ast.fix_missing_locations(clean)
        source = ast.unparse(clean).encode()
        seed = generate_seed(node.name)
        key = derive_key(seed)
        encrypted = xor_encrypt(source, key)
        payload_b64 = base64.b64encode(encrypted).decode()
        seed_b64 = base64.b64encode(seed).decode()

        body = self._build_stub(
            node.name,
            payload_b64,
            seed_b64,
            node.args,
            is_async
        )

        new_node = type(node)(
            name=node.name,
            args=node.args,
            body=body,
            decorator_list=decorators,
            returns=node.returns,
            type_comment=getattr(node, "type_comment", None),
        )

        ast.copy_location(new_node, node)
        return ast.fix_missing_locations(new_node)

    # ======================================================================
    def _build_stub(self, func_name, payload_b64, seed_b64, args_node, is_async):
        """Build the decryption and execution stub for an encrypted function."""
        # Generate random variable names for anti-analysis
        import random
        var_names = {
            'seed': self._random_name(),
            'hash_digest': self._random_name(),
            'key': self._random_name(),
            'encrypted': self._random_name(),
            'decrypted': self._random_name(),
            'local_scope': self._random_name(),
            'func_ref': self._random_name(),
            'iterator': self._random_name(),
            'base64_mod': self._random_name(),
            'hashlib_mod': self._random_name(),
            'compile_mod': self._random_name(),
            'xor_op': self._random_name(),
            'range_func': self._random_name(),
            'len_func': self._random_name(),
            'bytes_func': self._random_name(),
            'getattr_func': self._random_name(),
            'globals_func': self._random_name(),
        }
        
        # Build the decryption stub using string replacement (avoiding f-string issues)
        stub_lines = [
            '__b64__=__import__(\'base64\')',
            '__hl__=__import__(\'hashlib\')',
            f'__s__=__b64__.b64decode("{seed_b64}")',
            '__h__=__hl__.sha512(__s__).digest()',
            'while len(__h__)<32:__h__+=__hl__.sha512(__h__).digest()',
            '__k__=__h__[:32]',
            f'__e__=__b64__.b64decode("{payload_b64}")',
            '__kl__=len(__k__)',
            '__d__=bytearray()',
            'for __i__ in range(len(__e__)):',
            '    __d__.append(__e__[__i__]^__k__[__i__%__kl__])',
            '__l__={}',
            '__c__=compile(bytes(__d__),"<x>","exec")',
            'exec(__c__,globals(),__l__)',
            'for __i__ in range(len(__d__)):__d__[__i__]=0',
            f'__f__=__l__.get("{func_name}")',
            'if __f__ is None:',
            '    for __v__ in __l__.values():',
            '        if callable(__v__):',
            '            __f__=__v__',
            '            break',
            'del __b64__,__hl__,__s__,__h__,__k__,__kl__,__e__,__d__,__l__,__c__'
        ]
        stub = '\n'.join(stub_lines)
        body = ast.parse(stub).body
        
        # Note: _obfuscate_bootstrap was removed, bootstrap is already obfuscated with random names
        # body = self._obfuscate_bootstrap(body, var_names)
        
        # The function reference is stored in __f__ variable, so we need to use that directly
        call_args = self._build_call_args(args_node)
        if is_async:
            ret = ast.Return(
                value=ast.Await(
                    value=ast.Call(
                        func=ast.Name("__f__", ast.Load()),
                        args=call_args,
                        keywords=[]
                    )
                )
            )
        else:
            ret = ast.Return(
                value=ast.Call(
                    func=ast.Name("__f__", ast.Load()),
                    args=call_args,
                    keywords=[]
                )
            )

        body.append(ret)
        return body

    # ======================================================================
    def _random_name(self, length=8):
        """Generate a random variable name."""
        import random
        import string
        chars = string.ascii_lowercase + string.ascii_uppercase
        return '_' + ''.join(random.choice(chars) for _ in range(length))

    # ======================================================================
    def _build_call_args(self, args_node):
        """Build argument list for function call."""
        args = []
        if hasattr(args_node, "posonlyargs"):
            for a in args_node.posonlyargs:
                args.append(ast.Name(a.arg, ast.Load()))
        for a in args_node.args:
            args.append(ast.Name(a.arg, ast.Load()))
        if args_node.vararg:
            args.append(
                ast.Starred(
                    value=ast.Name(args_node.vararg.arg, ast.Load()),
                    ctx=ast.Load()
                )
            )
        if hasattr(args_node, "kwonlyargs"):
            for a in args_node.kwonlyargs:
                args.append(ast.Name(a.arg, ast.Load()))
        return args


# ============================================================================
# File Processing
# ============================================================================

def process_file(input_path: str, output_path: str = None) -> str:
    """
    Process a Python file, encrypting functions marked with @crypt.
    
    Args:
        input_path: Path to the input Python file
        output_path: Path to the output file (defaults to input.enc.py)
    
    Returns:
        Path to the output file
    """
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = base + ".enc" + ext

    with open(input_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    transformer = CryptTransformer()
    tree = transformer.visit(tree)
    ast.fix_missing_locations(tree)
    output = ast.unparse(tree)

    header = f"""# encrypted
# source: {os.path.basename(input_path)}
# functions: {transformer.encrypted_count}

"""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header + output)

    print(f"[+] encrypted {transformer.encrypted_count} function(s)")
    print(f"[+] output -> {output_path}")

    return output_path


# ============================================================================
# CLI
# ============================================================================

def main():
    """CLI entry point for the crypter."""
    if len(sys.argv) < 2:
        print("usage: crypter.py input.py [output.py]")
        print()
        print('''
from crypter import crypt

@crypt
def authenticate(user,password):
    secret="admin123"
    if user=="admin" and password==secret:
        return {"status":"ok"}
    return {"status":"denied"}

@crypt
def compute(x,y):
    r=0
    for i in range(x):
        r+=i*y
    return r

def public():
    return "hello"
''')
        return

    process_file(
        sys.argv[1],
        sys.argv[2] if len(sys.argv) > 2 else None
    )


# ============================================================================
# Self Test
# ============================================================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        demo_source = '''
from crypter import crypt

@crypt
def authenticate(user,password):
    secret="admin123"
    if user=="admin" and password==secret:
        return {"status":"ok"}
    return {"status":"denied"}

@crypt
def compute(x,y):
    r=0
    for i in range(x):
        r+=i*y
    return r*r

def public():
    return "hello"
'''

        with open("demo.py", "w", encoding="utf-8") as f:
            f.write(demo_source)

        process_file("demo.py", "demo_encrypted.py")

        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "demo_encrypted",
            "demo_encrypted.py"
        )

        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        print(mod.authenticate("admin", "admin123"))
        print(mod.authenticate("x", "y"))
        print(mod.compute(10, 5))
        print(mod.public())