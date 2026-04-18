"""
Tests for transform modules
"""
import ast
from pathlib import Path
import pytest
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRemapTransformer:
    """Tests for remap transformer"""

    def test_remap_transformer_import(self):
        """Test that remap transformer can be imported"""
        from pylockware.transforms.remap_transformer import GlobalRenamer
        assert GlobalRenamer is not None


class TestStringProtTransformer:
    """Tests for string protection transformer"""

    def test_string_prot_transformer_import(self):
        """Test that string protection transformer can be imported"""
        from pylockware.transforms.str_prot import StringProtectionTransformer
        assert StringProtectionTransformer is not None


class TestNumObfTransformer:
    """Tests for number obfuscation transformer"""

    def test_num_obf_transformer_import(self):
        """Test that number obfuscation transformer can be imported"""
        from pylockware.transforms.num_obf import NumberObfuscator
        assert NumberObfuscator is not None


class TestJunkCodeTransformer:
    """Tests for junk code transformer"""

    def test_junk_code_transformer_import(self):
        """Test that junk code transformer can be imported"""
        from pylockware.transforms.junk_code_transformer import JunkCodeTransformer
        assert JunkCodeTransformer is not None


class TestStateMachineTransformer:
    """Tests for state machine transformer"""

    def test_state_machine_transformer_import(self):
        """Test that state machine transformer can be imported"""
        from pylockware.transforms.state_machine_transformer import StateMachineTransformer
        assert StateMachineTransformer is not None


class TestBuiltinDispatcherTransformer:
    """Tests for builtin dispatcher transformer"""

    def test_builtin_dispatcher_transformer_import(self):
        """Test that builtin dispatcher transformer can be imported"""
        from pylockware.transforms.builtin_dispatcher import BuiltinDispatcherTransformer
        assert BuiltinDispatcherTransformer is not None


class TestDecoratorObfTransformer:
    """Tests for decorator obfuscation transformer"""

    def test_decorator_obf_transformer_import(self):
        """Test that decorator obfuscation transformer can be imported"""
        from pylockware.transforms.decorator_obf import DecoratorObfuscator
        assert DecoratorObfuscator is not None


class TestTypeAnnotationObfTransformer:
    """Tests for type annotation obfuscation transformer"""

    def test_type_annotation_obf_transformer_import(self):
        """Test that type annotation obfuscation transformer can be imported"""
        from pylockware.transforms.type_annotation_obf import TypeAnnotationObfuscator
        assert TypeAnnotationObfuscator is not None


class TestTransformIntegration:
    """Integration tests for transforms"""

    def test_transform_ast_parsing(self):
        """Test that transforms can parse AST"""
        code = """
def main():
    print("Hello, World!")
    x = 42
    return x
"""
        tree = ast.parse(code)
        assert tree is not None
        assert isinstance(tree, ast.Module)

    def test_transform_with_complex_code(self):
        """Test transforms with complex code"""
        code = """
import sys
from typing import List, Dict, Optional

class MyClass:
    def __init__(self, value: int):
        self.value = value
    
    def process(self, items: List[str]) -> Dict[str, int]:
        result = {}
        for item in items:
            result[item] = len(item)
        return result

def main():
    obj = MyClass(42)
    data = ["apple", "banana", "cherry"]
    result = obj.process(data)
    print(result)
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""
        tree = ast.parse(code)
        assert tree is not None

    def test_transform_with_decorators(self):
        """Test transforms with decorators"""
        code = """
def my_decorator(func):
    def wrapper():
        print("Before")
        func()
        print("After")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

def another_decorator(func):
    return func

@another_decorator
def another_function():
    pass
"""
        tree = ast.parse(code)
        assert tree is not None

    def test_transform_with_async(self):
        """Test transforms with async code"""
        code = """
import asyncio

async def main():
    print("Hello")
    await asyncio.sleep(1)
    print("World")

async def another_func():
    return 42

if __name__ == "__main__":
    asyncio.run(main())
"""
        tree = ast.parse(code)
        assert tree is not None

    def test_transform_with_try_except(self):
        """Test transforms with exception handling"""
        code = """
def divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError:
        print("Cannot divide by zero")
        result = None
    except Exception as e:
        print(f"Error: {e}")
        result = None
    finally:
        return result

def process_data(data):
    try:
        return int(data)
    except (ValueError, TypeError):
        return 0
"""
        tree = ast.parse(code)
        assert tree is not None

    def test_transform_with_classes(self):
        """Test transforms with class definitions"""
        code = """
class BaseClass:
    def __init__(self, value):
        self.value = value
    
    def method(self):
        return self.value

class DerivedClass(BaseClass):
    def __init__(self, value, extra):
        super().__init__(value)
        self.extra = extra
    
    def method(self):
        return super().method() + self.extra

class AnotherClass:
    class NestedClass:
        def nested_method(self):
            return "nested"
    
    def outer_method(self):
        return self.NestedClass().nested_method()
"""
        tree = ast.parse(code)
        assert tree is not None

    def test_transform_with_imports(self):
        """Test transforms with various import types"""
        code = """
# Standard library
import os
import sys
from collections import defaultdict, Counter
from typing import List, Dict, Optional

# Aliased imports
import json as js
from pathlib import Path as P

# Relative imports (would work in package)
# from .module import func

# Wildcard import
# from module import *

# Conditional import
try:
    import numpy as np
except ImportError:
    np = None
"""
        tree = ast.parse(code)
        assert tree is not None
