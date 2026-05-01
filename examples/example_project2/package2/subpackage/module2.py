"""
Module 2 - Nested package module
"""

import os
import sys
from pathlib import Path

CONSTANT2 = "constant_from_module2"

class Class2:
    def __init__(self):
        self.path = Path.cwd()
    
    def get_system_info(self):
        return f"Python: {sys.version}, OS: {os.name}"

def function2():
    return "function2_from_module2"

def nested_function():
    return "nested_from_module2"
