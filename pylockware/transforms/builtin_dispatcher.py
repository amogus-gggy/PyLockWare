
"""
Builtin Dispatcher Transformer for PyLockWare
Replaces built-in function calls with calls via a dispatcher.
Всё встраивается прямо в обрабатываемый модуль — никаких внешних файлов.
"""
import ast
from typing import Dict, Any
from pylockware.core.name_generator import generate_random_name


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
    на вызовы через dispatcher с обфусцированным именем.
    Весь код dispatcher встраивается прямо в обрабатываемый модуль.
    """

    def __init__(self, name_gen_settings: str = 'english'):
        self.name_gen_settings = name_gen_settings
        # ★ Два РАЗНЫХ имени: класс и экземпляр
        self.dispatcher_class_name = generate_random_name('_', name_gen_settings)
        self.dispatcher_name = generate_random_name('_', name_gen_settings)
        self.builtins_map: Dict[str, str] = {}
        self.imported_builtins = set()
        self.skip_obf_depth = 0

    def _has_skip_obf_decorator(self, node):
        if not hasattr(node, 'decorator_list'):
            return False
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'skip_obf':
                return True
            elif isinstance(decorator, ast.Attribute) and decorator.attr == 'skip_obf':
                return True
        return False

    def visit_FunctionDef(self, node):
        if self._has_skip_obf_decorator(node):
            self.skip_obf_depth += 1
            self.generic_visit(node)
            self.skip_obf_depth -= 1
            return node
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        if self._has_skip_obf_decorator(node):
            self.skip_obf_depth += 1
            self.generic_visit(node)
            self.skip_obf_depth -= 1
            return node
        return self.generic_visit(node)

    def visit_ClassDef(self, node):
        if self._has_skip_obf_decorator(node):
            self.skip_obf_depth += 1
            self.generic_visit(node)
            self.skip_obf_depth -= 1
            return node
        return self.generic_visit(node)

    def _get_builtin_attr(self, builtin_name: str) -> ast.Attribute:
        """
        dispatcher_name.obfuscated_name  →  _instance._xyz
        """
        return ast.Attribute(
            value=ast.Name(id=self.dispatcher_name, ctx=ast.Load()),
            attr=self.builtins_map[builtin_name],
            ctx=ast.Load()
        )

    def visit_Import(self, node: ast.Import) -> ast.AST:
        for alias in node.names:
            if alias.name == 'builtins':
                self.imported_builtins.add(alias.asname or 'builtins')
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
        if node.module == 'builtins':
            for alias in node.names:
                self.imported_builtins.add(alias.asname or alias.name)
        return node

    def visit_Call(self, node: ast.Call) -> ast.AST:
        if self.skip_obf_depth > 0:
            return self.generic_visit(node)

        # print() → _dispatcher.ghjfkd()
        if isinstance(node.func, ast.Name):
            if node.func.id in BUILTIN_FUNCTIONS:
                if node.func.id not in self.builtins_map:
                    self.builtins_map[node.func.id] = generate_random_name(
                        '_', self.name_gen_settings
                    )
                new_call = ast.Call(
                    func=self._get_builtin_attr(node.func.id),
                    args=node.args,
                    keywords=node.keywords
                )
                ast.copy_location(new_call, node)
                return new_call

        # builtins.print() → _dispatcher.ghjfkd()
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id in self.imported_builtins:
                    if node.func.attr in BUILTIN_FUNCTIONS:
                        if node.func.attr not in self.builtins_map:
                            self.builtins_map[node.func.attr] = generate_random_name(
                                '_', self.name_gen_settings
                            )
                        new_call = ast.Call(
                            func=self._get_builtin_attr(node.func.attr),
                            args=node.args,
                            keywords=node.keywords
                        )
                        ast.copy_location(new_call, node)
                        return new_call

        return self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id in BUILTIN_FUNCTIONS and isinstance(node.ctx, ast.Load):
            if node.id not in self.builtins_map:
                self.builtins_map[node.id] = generate_random_name(
                    '_', self.name_gen_settings
                )
            new_name = self._get_builtin_attr(node.id)
            ast.copy_location(new_name, node)
            return new_name
        return node

    # ──────────────────────────────────────────────
    #  Ключевой метод: встраивание dispatcher в модуль
    # ──────────────────────────────────────────────

    def get_dispatcher_code(self) -> str:
        """
        Генерирует код dispatcher-класса + создание экземпляра.
        Этот код встраивается в начало обрабатываемого модуля.
        """
        mappings = []
        for original, obfuscated in self.builtins_map.items():
            mappings.append(f"        '{obfuscated}': {original},")

        mappings_code = '\n'.join(mappings) if mappings else '        # no builtins replaced'

        # ★ Класс и экземпляр — РАЗНЫЕ имена
        # ★ После class ... идёт строка создания экземпляра
        dispatcher_code = f'''
class {self.dispatcher_class_name}:
    _m = {{
{mappings_code}
    }}
    def __getattr__(self, n):
        try:
            return self._m[n]
        except KeyError:
            raise AttributeError(n)

{self.dispatcher_name} = {self.dispatcher_class_name}()
'''
        return dispatcher_code

    def transform_module(self, tree: ast.Module) -> ast.Module:
        """
        Полный цикл: обходит AST, затем внедряет dispatcher-код
        прямо в body модуля (в начало, после __future__ импортов).
        """
        # 1. Трансформируем все вызовы
        tree = self.visit(tree)
        ast.fix_missing_locations(tree)

        if not self.builtins_map:
            # Нечего обфусцировать — возвращаем как есть
            return tree

        # 2. Парсим сгенерированный dispatcher-код в AST
        dispatcher_src = self.get_dispatcher_code()
        dispatcher_tree = ast.parse(dispatcher_src)

        # 3. Вставляем после __future__-импортов, но до остального кода
        insert_pos = 0
        for i, node in enumerate(tree.body):
            if isinstance(node, ast.ImportFrom) and node.module == '__future__':
                insert_pos = i + 1
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                insert_pos = i + 1
            else:
                break

        tree.body[insert_pos:insert_pos] = dispatcher_tree.body
        ast.fix_missing_locations(tree)

        return tree