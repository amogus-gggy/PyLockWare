"""
Пример использования PyLockWare SDK с аннотациями

После установки pylockware через pip:
    pip install pylockware

Используйте аннотации для управления обфускацией.
Аннотации автоматически удаляются после обфускации.
"""

from pylockware import external, skip_obf


# Публичный API - имя не будет изменено при ремапе
@external
def public_api_function(data: str) -> str:
    """Эта функция доступна как публичный API"""
    return process_internal(data)


# Внутренняя функция - будет обфусцирована
def process_internal(data: str) -> str:
    """Внутренняя логика - будет полностью обфусцирована"""
    result = data.upper()
    return encrypt_data(result)


# Функция для отладки - пропускает все шаги обфускации
@skip_obf
def debug_function(message: str) -> None:
    """Эта функция останется в оригинальном виде для отладки"""
    print(f"[DEBUG] {message}")


def encrypt_data(data: str) -> str:
    """Простое шифрование - будет обфусцировано"""
    return ''.join(chr(ord(c) + 1) for c in data)


# Публичный класс
@external
class PublicAPI:
    """Публичный класс API - имя класса сохранится"""
    
    def __init__(self, name: str):
        self.name = name
        self._internal_data = []
    
    @external
    def get_name(self) -> str:
        """Публичный метод - имя сохранится"""
        return self.name
    
    def _process(self, data):
        """Приватный метод - будет обфусцирован"""
        return data.lower()


# Внутренний класс - будет обфусцирован
class InternalProcessor:
    """Внутренний класс - будет полностью обфусцирован"""
    
    def __init__(self):
        self.counter = 0
    
    def process(self, value):
        self.counter += 1
        return value * 2


# Класс для отладки - не будет обфусцирован
@skip_obf
class DebugHelper:
    """Класс для отладки - останется в оригинальном виде"""
    
    def log(self, message):
        print(f"[LOG] {message}")
    
    def dump_state(self, obj):
        print(f"[STATE] {obj.__dict__}")


def main():
    """Главная функция"""
    # Используем публичный API
    result = public_api_function("hello world")
    print(f"Result: {result}")
    
    # Используем публичный класс
    api = PublicAPI("MyAPI")
    print(f"API Name: {api.get_name()}")
    
    # Используем внутренний процессор
    processor = InternalProcessor()
    print(f"Processed: {processor.process(42)}")
    
    # Используем отладочные функции
    debug_function("Application started")
    
    debugger = DebugHelper()
    debugger.log("Everything works!")
    debugger.dump_state(api)


if __name__ == "__main__":
    main()
