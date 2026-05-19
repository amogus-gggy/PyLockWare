"""
Remove PyLockWare Annotations Module
Удаляет аннотации PyLockWare из обфусцированного кода
"""

import ast
from pathlib import Path
from typing import Set

from pylockware.core.module_base import ModuleBase


class RemoveAnnotationsTransformer(ast.NodeTransformer):
    """
    Удаляет декораторы PyLockWare (@external, @skip_obf) из AST
    и импорты pylockware
    """
    
    PYLOCKWARE_DECORATORS = {'external', 'skip_obf', 'preserve_name'}
    
    def __init__(self):
        self.removed_count = 0
    
    def visit_FunctionDef(self, node):
        """Удаляет PyLockWare декораторы из функций"""
        node.decorator_list = self._filter_decorators(node.decorator_list)
        self.generic_visit(node)
        return node
    
    def visit_AsyncFunctionDef(self, node):
        """Удаляет PyLockWare декораторы из async функций"""
        node.decorator_list = self._filter_decorators(node.decorator_list)
        self.generic_visit(node)
        return node
    
    def visit_ClassDef(self, node):
        """Удаляет PyLockWare декораторы из классов"""
        node.decorator_list = self._filter_decorators(node.decorator_list)
        self.generic_visit(node)
        return node
    
    def visit_Import(self, node):
        """Удаляет импорты pylockware"""
        # Фильтруем импорты
        node.names = [
            alias for alias in node.names
            if not self._is_pylockware_import(alias.name)
        ]
        
        # Если все импорты удалены, возвращаем None (удаляем узел)
        if not node.names:
            return None
        
        return node
    
    def visit_ImportFrom(self, node):
        """Удаляет импорты from pylockware import ..."""
        # Если импорт из pylockware, удаляем весь узел
        if node.module and self._is_pylockware_import(node.module):
            return None
        
        # Фильтруем отдельные импорты
        original_count = len(node.names)
        node.names = [
            alias for alias in node.names
            if alias.name not in self.PYLOCKWARE_DECORATORS
        ]
        
        # Если все импорты удалены, возвращаем None
        if not node.names:
            return None
        
        return node
    
    def _filter_decorators(self, decorator_list):
        """Фильтрует список декораторов, удаляя PyLockWare декораторы"""
        filtered = []
        
        for decorator in decorator_list:
            if self._is_pylockware_decorator(decorator):
                self.removed_count += 1
                continue
            filtered.append(decorator)
        
        return filtered
    
    def _is_pylockware_decorator(self, decorator):
        """Проверяет, является ли декоратор PyLockWare декоратором"""
        # Простой декоратор: @external
        if isinstance(decorator, ast.Name):
            return decorator.id in self.PYLOCKWARE_DECORATORS
        
        # Декоратор с модулем: @pylockware.external
        if isinstance(decorator, ast.Attribute):
            if decorator.attr in self.PYLOCKWARE_DECORATORS:
                # Проверяем, что это из pylockware
                if isinstance(decorator.value, ast.Name):
                    return decorator.value.id == 'pylockware'
        
        return False
    
    def _is_pylockware_import(self, module_name):
        """Проверяет, является ли импорт импортом pylockware"""
        return module_name == 'pylockware' or module_name.startswith('pylockware.')


class RemoveAnnotationsModule(ModuleBase):
    """
    Модуль для удаления аннотаций PyLockWare из обфусцированного кода.
    
    Этот модуль должен запускаться ПОСЛЕДНИМ, после всех трансформаций,
    чтобы удалить декораторы и импорты pylockware из финального кода.
    """
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.name = "RemoveAnnotations"
        self.description = "Removes PyLockWare annotations from obfuscated code"
        self.total_removed = 0
    
    def validate_config(self) -> bool:
        """Валидация конфигурации (не требуется для этого модуля)"""
        return True
    
    def process(self, project_path: Path, output_path: Path) -> bool:
        """
        Обрабатывает проект, удаляя аннотации PyLockWare
        
        Args:
            project_path: Путь к оригинальному проекту (не используется)
            output_path: Путь к выходной директории
        
        Returns:
            True если успешно
        """
        print(f"\n[{self.name}] Removing PyLockWare annotations...")
        
        if not output_path or not output_path.exists():
            print(f"Error: Output directory does not exist: {output_path}")
            return False
        
        # Обрабатываем все Python файлы в выходной директории
        python_files = list(output_path.rglob("*.py"))
        
        if not python_files:
            print("No Python files found to process")
            return True
        
        for py_file in python_files:
            try:
                # Читаем файл
                with open(py_file, 'r', encoding='utf-8') as f:
                    source = f.read()
                
                # Парсим AST
                tree = ast.parse(source)
                
                # Удаляем аннотации
                new_tree = self.process_file(py_file, tree)
                
                # Генерируем код обратно
                new_source = ast.unparse(new_tree)
                
                # Сохраняем
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(new_source)
                
            except Exception as e:
                print(f"Error processing {py_file}: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        print(f"[{self.name}] Total annotations removed: {self.total_removed}")
        print(f"[{self.name}] Processed {len(python_files)} files")
        
        return True
    
    def process_file(self, file_path: Path, tree: ast.AST) -> ast.AST:
        """
        Удаляет аннотации PyLockWare из файла
        
        Args:
            file_path: Путь к файлу
            tree: AST дерево
        
        Returns:
            Модифицированное AST дерево без аннотаций
        """
        transformer = RemoveAnnotationsTransformer()
        new_tree = transformer.visit(tree)
        
        if transformer.removed_count > 0:
            self.total_removed += transformer.removed_count
            print(f"  Removed {transformer.removed_count} PyLockWare annotations from {file_path.name}")
        
        return new_tree
