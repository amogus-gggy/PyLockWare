"""
Builtin Dispatcher Transformer for PyLockWare
Replaces built-in function calls with calls via a dispatcher
"""
import ast
from typing import Dict, Any
from pylockware.core.name_generator import generate_random_name


# Список built-in функций для обфускации
BUILTIN_FUNCTIONS = [
    'abs', 'all', 'any', 'ascii', 'bin', 'bool', 'breakpoint', 'bytearray', 'bytes',
    'callable', 'chr', 'classmethod', 'compile', 'complex', 'delattr', 'dict', 'dir',
    'divmod', 'enumerate', 'eval', 'exec', 'filter', 'float', 'format', 'frozenset',
    'getattr', 'globals', 'hasattr', 'hash', 'help', 'hex', 'id', 'input', 'int',
    'isinstance', 'issubclass', 'iter', 'len', 'list', 'locals', 'map', 'max',
    'memoryview', 'min', 'next', 'object', 'oct', 'open', 'ord', 'pow', 'print',
    'property', 'range', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
    'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type', 'vars', 'zip',
    '__import__'
]


class BuiltinDispatcherTransformer(ast.NodeTransformer):
    """
    AST трансформер, который заменяет вызовы built-in функций
    на вызовы через dispatcher с обфусцированным именем
    """

    def __init__(self, name_gen_settings: str = 'english'):
        """
        Инициализация трансформера

        Args:
            name_gen_settings: Набор символов для генерации имён
        """
        self.name_gen_settings = name_gen_settings
        self.dispatcher_name = generate_random_name('_', name_gen_settings)
        self.builtins_map: Dict[str, str] = {}
        self.imported_builtins = set()
        
        # Track if we're inside a @skip_obf function/class
        self.skip_obf_depth = 0
    
    def _has_skip_obf_decorator(self, node):
        """Check if node has @skip_obf decorator"""
        if not hasattr(node, 'decorator_list'):
            return False
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'skip_obf':
                return True
            elif isinstance(decorator, ast.Attribute) and decorator.attr == 'skip_obf':
                return True
        return False
    
    def visit_FunctionDef(self, node):
        """Track when entering/exiting functions with @skip_obf"""
        if self._has_skip_obf_decorator(node):
            self.skip_obf_depth += 1
            self.generic_visit(node)
            self.skip_obf_depth -= 1
            return node
        return self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        """Track when entering/exiting async functions with @skip_obf"""
        if self._has_skip_obf_decorator(node):
            self.skip_obf_depth += 1
            self.generic_visit(node)
            self.skip_obf_depth -= 1
            return node
        return self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Track when entering/exiting classes with @skip_obf"""
        if self._has_skip_obf_decorator(node):
            self.skip_obf_depth += 1
            self.generic_visit(node)
            self.skip_obf_depth -= 1
            return node
        return self.generic_visit(node)

    def _get_builtin_attr(self, builtin_name: str) -> ast.Attribute:
        """
        Создает AST узел для доступа к dispatcher.builtin_name

        Args:
            builtin_name: Имя built-in функции

        Returns:
            AST Attribute узел
        """
        return ast.Attribute(
            value=ast.Name(id=self.dispatcher_name, ctx=ast.Load()),
            attr=self.builtins_map[builtin_name],
            ctx=ast.Load()
        )

    def visit_Import(self, node: ast.Import) -> ast.AST:
        """
        Обрабатывает импорт builtins модуля
        """
        # Сохраняем информацию об импорте builtins
        for alias in node.names:
            if alias.name == 'builtins':
                self.imported_builtins.add(alias.asname or 'builtins')
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
        """
        Обрабатывает импорт из builtins модуля
        """
        if node.module == 'builtins':
            for alias in node.names:
                self.imported_builtins.add(alias.asname or alias.name)
        return node

    def visit_Call(self, node: ast.Call) -> ast.AST:
        """
        Заменяет вызовы built-in функций на вызовы через dispatcher
        """
        # Skip if inside @skip_obf context
        if self.skip_obf_depth > 0:
            return self.generic_visit(node)
        
        # Прямой вызов: print() -> _dispatcher.ghjfkd()
        if isinstance(node.func, ast.Name):
            if node.func.id in BUILTIN_FUNCTIONS:
                if node.func.id not in self.builtins_map:
                    self.builtins_map[node.func.id] = generate_random_name('_', self.name_gen_settings)
                new_call = ast.Call(
                    func=self._get_builtin_attr(node.func.id),
                    args=node.args,
                    keywords=node.keywords
                )
                ast.copy_location(new_call, node)
                return new_call

        # Вызов через builtins: builtins.print() -> _dispatcher.ghjfkd()
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id in self.imported_builtins:
                    if node.func.attr in BUILTIN_FUNCTIONS:
                        if node.func.attr not in self.builtins_map:
                            self.builtins_map[node.func.attr] = generate_random_name('_', self.name_gen_settings)
                        new_call = ast.Call(
                            func=self._get_builtin_attr(node.func.attr),
                            args=node.args,
                            keywords=node.keywords
                        )
                        ast.copy_location(new_call, node)
                        return new_call

        return node

    def visit_Name(self, node: ast.Name) -> ast.AST:
        """
        Обрабатывает ссылки на built-in функции без вызова
        (например, когда print передаётся как аргумент)
        """
        if node.id in BUILTIN_FUNCTIONS and isinstance(node.ctx, ast.Load):
            # Для ссылок на built-in функции тоже используем dispatcher
            if node.id not in self.builtins_map:
                self.builtins_map[node.id] = generate_random_name('_', self.name_gen_settings)
            new_name = self._get_builtin_attr(node.id)
            ast.copy_location(new_name, node)
            return new_name
        return node

    def get_dispatcher_code(self) -> str:
        """
        Генерирует код для dispatcher класса

        Returns:
            Строка с кодом dispatcher класса
        """
        mappings = []
        for original, obfuscated in self.builtins_map.items():
            mappings.append(f"            '{obfuscated}': {original},")

        mappings_code = '\n'.join(mappings)

        dispatcher_code = f'''
class {self.dispatcher_name}:
    """Dispatcher for built-in functions"""
    _builtins = {{
{mappings_code}
    }}

    def __getattr__(self, name):
        if name in self._builtins:
            return self._builtins[name]
        raise AttributeError(f"Unknown builtin: {{name}}")

'''
        return dispatcher_code
