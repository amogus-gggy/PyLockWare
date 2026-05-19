"""
Базовый трансформер с поддержкой аннотаций PyLockWare
"""
import ast
from typing import Set


class AnnotationAwareTransformer(ast.NodeTransformer):
    """
    Базовый класс для трансформеров, которые учитывают аннотации PyLockWare.
    
    Автоматически пропускает функции и классы с декоратором @skip_obf.
    """
    
    def __init__(self):
        super().__init__()
        self.skip_obf_names: Set[str] = set()
        self._collect_skip_obf_names_done = False
    
    def _has_decorator(self, node, decorator_name: str) -> bool:
        """Проверяет наличие декоратора у функции/класса"""
        if not hasattr(node, 'decorator_list'):
            return False
        
        for decorator in node.decorator_list:
            # Простой декоратор: @skip_obf
            if isinstance(decorator, ast.Name) and decorator.id == decorator_name:
                return True
            # Декоратор с модулем: @pylockware.skip_obf
            elif isinstance(decorator, ast.Attribute) and decorator.attr == decorator_name:
                return True
        
        return False
    
    def _collect_skip_obf_names(self, tree):
        """Собирает имена всех функций/классов с @skip_obf"""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if self._has_decorator(node, 'skip_obf'):
                    self.skip_obf_names.add(node.name)
    
    def should_skip_node(self, node) -> bool:
        """Проверяет, нужно ли пропустить узел"""
        # Проверяем декоратор @skip_obf
        if self._has_decorator(node, 'skip_obf'):
            return True
        
        # Проверяем, находимся ли мы внутри функции/класса с @skip_obf
        if hasattr(node, 'name') and node.name in self.skip_obf_names:
            return True
        
        return False
    
    def visit_FunctionDef(self, node):
        """Обрабатывает определение функции"""
        if self.should_skip_node(node):
            return node  # Не трансформируем
        return self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        """Обрабатывает определение async функции"""
        if self.should_skip_node(node):
            return node  # Не трансформируем
        return self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Обрабатывает определение класса"""
        if self.should_skip_node(node):
            return node  # Не трансформируем
        return self.generic_visit(node)
    
    def transform(self, tree):
        """
        Основной метод трансформации.
        Переопределите в подклассах для кастомной логики.
        """
        # Сначала собираем все имена с @skip_obf
        if not self._collect_skip_obf_names_done:
            self._collect_skip_obf_names(tree)
            self._collect_skip_obf_names_done = True
        
        # Затем применяем трансформацию
        return self.visit(tree)


class SkipObfChecker:
    """
    Утилита для проверки, нужно ли пропускать обфускацию узла.
    Используется в модулях обфускации.
    """
    
    @staticmethod
    def has_skip_obf(node) -> bool:
        """Проверяет наличие декоратора @skip_obf"""
        if not hasattr(node, 'decorator_list'):
            return False
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'skip_obf':
                return True
            elif isinstance(decorator, ast.Attribute) and decorator.attr == 'skip_obf':
                return True
        
        return False
    
    @staticmethod
    def has_external(node) -> bool:
        """Проверяет наличие декоратора @external"""
        if not hasattr(node, 'decorator_list'):
            return False
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'external':
                return True
            elif isinstance(decorator, ast.Attribute) and decorator.attr == 'external':
                return True
        
        return False
    
    @staticmethod
    def should_skip(node) -> bool:
        """Проверяет, нужно ли пропустить узел (skip_obf или external)"""
        return SkipObfChecker.has_skip_obf(node) or SkipObfChecker.has_external(node)
