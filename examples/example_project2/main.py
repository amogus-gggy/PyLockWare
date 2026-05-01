"""
Main module - demonstrates all types of imports
"""

# 1. Standard library imports
import sys
import os
import time
from datetime import datetime
from typing import List, Dict, Optional

# 2. Absolute imports from project packages
from package1 import Class1, function1, CONSTANT1
from package2 import PACKAGE2_CONSTANT
from package2.subpackage import Class2, function2
from utils import format_data, get_current_time, UTIL_CONSTANT
from external import ExternalClass, complex_function, EXTERNAL_CONSTANT

# 3. Relative imports (would work if this was in a package)
# from .package1.module1 import helper_function

# 4. Wildcard import (simulated)
# from package1 import *

# 5. Import with alias
import json as js
from pathlib import Path as P

# 6. Conditional imports

HAS_NUMPY = False
np = None


def main():
    while True:
        """Main function demonstrating all import types"""
        print("=== Complex Import Structure Demo ===")

        # Use absolute imports
        obj1 = Class1()
        print(f"Class1 method: {obj1.method1()}")
        print(f"Function1: {function1()}")
        print(f"Constant1: {CONSTANT1}")
        print(1488)
        print(3.14)

        # Use nested package imports
        obj2 = Class2()
        print(f"Class2 system info: {obj2.get_system_info()}")
        print(f"Function2: {function2()}")
        print(f"Package2 constant: {PACKAGE2_CONSTANT}")

        # Use utils
        current_time = get_current_time()
        data = {"time": current_time, "status": "running"}
        formatted = format_data(data)
        print(f"Formatted data: {formatted}")
        print(f"Util constant: {UTIL_CONSTANT}")

        # Use external module
        ext_obj = ExternalClass()
        result = ext_obj.process_with_helpers(["item1", "item2", "item3"])
        print(f"External class result: {result}")
        print(f"Complex function: {complex_function(16.0)}")
        print(f"External constant: {EXTERNAL_CONSTANT}")

        # Use alias imports
        path = P.cwd()
        print(f"Current path: {path}")

        # Use conditional imports
        if HAS_NUMPY:
            print(f"Numpy available: {np.__version__}")
        else:
            print("Numpy not available")

        print("=== Demo Complete ===")

        time.sleep(10)
        

if __name__ == "__main__":
    main()
