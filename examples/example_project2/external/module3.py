"""
External module - demonstrates various import types
"""

# Standard library imports
import math
import random
from collections import defaultdict, Counter
from typing import Any, Union, List, Dict

# Absolute imports from project (changed from relative)
from package1.module1 import helper_function
from package2.subpackage.module2 import nested_function

# Absolute imports from project
from package1 import Class1
from package2.subpackage import Class2
from utils.helpers import format_data, process_list

EXTERNAL_CONSTANT = "external_module_constant"

class ExternalClass:
    def __init__(self):
        self.data = defaultdict(list)
        self.counter = Counter()
    
    def process_with_helpers(self, items: List[str]) -> Dict[str, Any]:
        processed = process_list(items)
        formatted = format_data({"items": items, "processed": processed})
        return {"formatted": formatted, "count": len(items)}
    
    def use_relative_imports(self):
        return f"Helper: {helper_function()}, Nested: {nested_function()}"

def complex_function(x: Union[int, float]) -> float:
    return math.sqrt(abs(x)) * random.random()
