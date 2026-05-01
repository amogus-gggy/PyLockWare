"""
Utility helpers module
"""

import json
import datetime
from typing import List, Dict, Optional

def format_data(data: Dict) -> str:
    return json.dumps(data, indent=2)

def get_current_time() -> str:
    return datetime.datetime.now().isoformat()

def process_list(items: List[str]) -> Optional[str]:
    if not items:
        return None
    return ", ".join(items)

UTIL_CONSTANT = "utils_constant"
