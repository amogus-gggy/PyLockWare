"""
PyLockWare SDK Decorators
Аннотации для управления обфускацией
"""

from typing import Callable, TypeVar, Any
from functools import wraps

F = TypeVar('F', bound=Callable[..., Any])


def external(func_or_class: F) -> F:
    """
    Помечает функцию/класс как внешний API.
    Исключает из ремапа имен, сохраняя оригинальное имя.
    
    Использование:
        @external
        def public_api():
            pass
        
        @external
        class PublicClass:
            pass
    """
    if not hasattr(func_or_class, '__pylockware_attrs__'):
        func_or_class.__pylockware_attrs__ = {}
    func_or_class.__pylockware_attrs__['external'] = True
    return func_or_class


def skip_obf(func_or_class: F) -> F:
    """
    Пропускает все шаги обфускации для функции/класса.
    Код остается в оригинальном виде.
    
    Использование:
        @skip_obf
        def debug_function():
            pass
        
        @skip_obf
        class DebugClass:
            pass
    """
    if not hasattr(func_or_class, '__pylockware_attrs__'):
        func_or_class.__pylockware_attrs__ = {}
    func_or_class.__pylockware_attrs__['skip_obf'] = True
    return func_or_class


def preserve_name(func_or_class: F) -> F:
    """
    Сохраняет оригинальное имя, но применяет остальные трансформации.
    Алиас для @external.
    """
    return external(func_or_class)


def crypt(func_or_class: F) -> F:
    """
    Помечает функцию/класс для шифрования с использованием отпечатка машины.
    Код будет зашифрован и расшифровываться только на той же машине.
    
    Использование:
        @crypt
        def secret_function():
            # sensitive code here
            pass
        
        @crypt
        class SecretClass:
            pass
    """
    if not hasattr(func_or_class, '__pylockware_attrs__'):
        func_or_class.__pylockware_attrs__ = {}
    func_or_class.__pylockware_attrs__['crypt'] = True
    return func_or_class


# Вспомогательные функции для проверки атрибутов
def is_external(obj: Any) -> bool:
    """Проверяет, помечен ли объект как external"""
    return getattr(obj, '__pylockware_attrs__', {}).get('external', False)


def should_skip_obfuscation(obj: Any) -> bool:
    """Проверяет, нужно ли пропустить обфускацию"""
    return getattr(obj, '__pylockware_attrs__', {}).get('skip_obf', False)


def get_pylockware_attrs(obj: Any) -> dict:
    """Получает все PyLockWare атрибуты объекта"""
    return getattr(obj, '__pylockware_attrs__', {})


def is_crypt(obj: Any) -> bool:
    """Проверяет, помечен ли объект как crypt"""
    return getattr(obj, '__pylockware_attrs__', {}).get('crypt', False)
