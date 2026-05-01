# Example Project 2 - Complex Import Structure

Этот проект демонстрирует все возможные типы импортов в Python для тестирования PyLock.

## Структура проекта

```
example_project2/
├── main.py                 # Основной файл со всеми типами импортов
├── package1/              # Первый пакет
│   ├── __init__.py
│   └── module1.py         # Базовый модуль
├── package2/              # Второй пакет с вложенной структурой
│   ├── __init__.py
│   └── subpackage/
│       ├── __init__.py
│       └── module2.py     # Модуль во вложенном пакете
├── utils/                 # Утилиты
│   ├── __init__.py
│   └── helpers.py         # Вспомогательные функции
├── external/              # Внешние модули
│   ├── __init__.py
│   └── module3.py         # Модуль со сложными импортами
└── README.md
```

## Типы импортов, используемых в проекте

### 1. Стандартные импорты стандартной библиотеки
```python
import sys
import os
from datetime import datetime
from typing import List, Dict, Optional
```

### 2. Absolute импорты из пакетов проекта
```python
from package1 import Class1, function1, CONSTANT1
from package2.subpackage import Class2, function2
from utils import format_data, get_current_time
```

### 3. Absolute импорты (вместо relative для запуска как скрипт)
```python
from package1.module1 import helper_function
from package2.subpackage.module2 import nested_function
```

### 4. Импорты с псевдонимами
```python
import json as js
from pathlib import Path as P
```

### 5. Множественные импорты из одного модуля
```python
from collections import defaultdict, Counter
from typing import Any, Union
```

### 6. Условные импорты
```python
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
```

### 7. Wildcard импорты (через __all__)
```python
# В __init__.py файлах:
__all__ = ['Class1', 'function1', 'CONSTANT1']
```

### 8. Вложенные импорты
Импорты из модулей, которые сами используют сложные импорты.

## Запуск

```bash
python main.py
```

Проект ничего не делает полезного, но демонстрирует все возможные типы импортов для тестирования обфускации.
