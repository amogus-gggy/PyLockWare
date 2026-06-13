
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
    'sorted', 'staticmethod', 'str', 'sum', 'tuple', 'type', 'vars', 'zip',
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
        self.scope_stack: list[set[str]] = []
        self.global_declarations: set[str] = set()
        self.nonlocal_declarations: set[str] = set()

    def _push_scope(self) -> None:
        self.scope_stack.append(set())

    def _pop_scope(self) -> None:
        self.scope_stack.pop()

    def _bind_name(self, name: str) -> None:
        if self.scope_stack:
            self.scope_stack[-1].add(name)

    def _bind_target(self, target: ast.AST) -> None:
        for name in self._names_in_target(target):
            self._bind_name(name)

    @staticmethod
    def _names_in_target(node: ast.AST) -> set[str]:
        names: set[str] = set()
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, (ast.Tuple, ast.List)):
            for elt in node.elts:
                names |= BuiltinDispatcherTransformer._names_in_target(elt)
        elif isinstance(node, ast.Starred):
            names |= BuiltinDispatcherTransformer._names_in_target(node.value)
        return names

    @staticmethod
    def _arg_names(args: ast.arguments) -> set[str]:
        names = {a.arg for a in args.args}
        names |= {a.arg for a in args.posonlyargs}
        names |= {a.arg for a in args.kwonlyargs}
        if args.vararg:
            names.add(args.vararg.arg)
        if args.kwarg:
            names.add(args.kwarg.arg)
        return names

    def _is_shadowed(self, name: str) -> bool:
        if name in self.global_declarations or name in self.nonlocal_declarations:
            return False
        return any(name in scope for scope in self.scope_stack)

    def _has_skip_obf_decorator(self, node):
        if not hasattr(node, 'decorator_list'):
            return False
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'skip_obf':
                return True
            elif isinstance(decorator, ast.Attribute) and decorator.attr == 'skip_obf':
                return True
        return False

    def visit_ClassDef(self, node):
        if self._has_skip_obf_decorator(node):
            self.skip_obf_depth += 1
            self.generic_visit(node)
            self.skip_obf_depth -= 1
            return node
        self._push_scope()
        node = self.generic_visit(node)
        self._pop_scope()
        return node

    def visit_Module(self, node):
        self._push_scope()
        node = self.generic_visit(node)
        self._pop_scope()
        return node

    def visit_Lambda(self, node):
        self._push_scope()
        for name in self._arg_names(node.args):
            self._bind_name(name)
        node = self.generic_visit(node)
        self._pop_scope()
        return node

    def visit_Global(self, node):
        self.global_declarations.update(node.names)
        return node

    def visit_Nonlocal(self, node):
        self.nonlocal_declarations.update(node.names)
        return node

    def visit_Import(self, node: ast.Import) -> ast.AST:
        for alias in node.names:
            if alias.name == 'builtins':
                self.imported_builtins.add(alias.asname or 'builtins')
            self._bind_name(alias.asname or alias.name.split('.')[0])
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
        if node.module == 'builtins':
            for alias in node.names:
                self.imported_builtins.add(alias.asname or alias.name)
        for alias in node.names:
            if alias.name != '*':
                self._bind_name(alias.asname or alias.name)
        return node

    def visit_Assign(self, node):
        node.value = self.visit(node.value)
        for target in node.targets:
            self._bind_target(target)
        node.targets = [self.visit(t) for t in node.targets]
        return node

    def visit_AnnAssign(self, node):
        if node.value:
            node.value = self.visit(node.value)
        if node.annotation:
            node.annotation = self.visit(node.annotation)
        self._bind_target(node.target)
        node.target = self.visit(node.target)
        return node

    def visit_For(self, node):
        node.iter = self.visit(node.iter)
        self._bind_target(node.target)
        node.target = self.visit(node.target)
        node.body = [self.visit(stmt) for stmt in node.body]
        node.orelse = [self.visit(stmt) for stmt in node.orelse]
        return node

    def visit_AsyncFor(self, node):
        return self.visit_For(node)

    def visit_With(self, node):
        for item in node.items:
            item.context_expr = self.visit(item.context_expr)
            if item.optional_vars:
                self._bind_target(item.optional_vars)
                item.optional_vars = self.visit(item.optional_vars)
        node.body = [self.visit(stmt) for stmt in node.body]
        return node

    def visit_AsyncWith(self, node):
        return self.visit_With(node)

    def visit_ExceptHandler(self, node):
        if node.type:
            node.type = self.visit(node.type)
        if node.name:
            self._bind_name(node.name)
        node.body = [self.visit(stmt) for stmt in node.body]
        return node

    def visit_comprehension(self, node):
        node.iter = self.visit(node.iter)
        self._bind_target(node.target)
        node.target = self.visit(node.target)
        node.ifs = [self.visit(i) for i in node.ifs]
        return node

    def visit_FunctionDef(self, node):
        saved_global = self.global_declarations
        saved_nonlocal = self.nonlocal_declarations
        self.global_declarations = set()
        self.nonlocal_declarations = set()

        if self._has_skip_obf_decorator(node):
            self.skip_obf_depth += 1
            self.generic_visit(node)
            self.skip_obf_depth -= 1
            self.global_declarations = saved_global
            self.nonlocal_declarations = saved_nonlocal
            return node

        self._push_scope()
        for name in self._arg_names(node.args):
            self._bind_name(name)
        node.decorator_list = [self.visit(d) for d in node.decorator_list]
        node.body = [self.visit(stmt) for stmt in node.body]
        node.returns = self.visit(node.returns) if node.returns else None
        self._pop_scope()

        self.global_declarations = saved_global
        self.nonlocal_declarations = saved_nonlocal
        return node

    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)

    def _get_builtin_attr(self, builtin_name: str) -> ast.Attribute:
        """
        dispatcher_name.obfuscated_name  →  _instance._xyz
        """
        return ast.Attribute(
            value=ast.Name(id=self.dispatcher_name, ctx=ast.Load()),
            attr=self.builtins_map[builtin_name],
            ctx=ast.Load()
        )

    def visit_Call(self, node: ast.Call) -> ast.AST:
        if self.skip_obf_depth > 0:
            return self.generic_visit(node)

        # print() → _dispatcher.ghjfkd()
        if isinstance(node.func, ast.Name):
            if node.func.id in BUILTIN_FUNCTIONS and not self._is_shadowed(node.func.id):
                if node.func.id not in self.builtins_map:
                    self.builtins_map[node.func.id] = generate_random_name(
                        '_', self.name_gen_settings
                    )
                new_call = ast.Call(
                    func=self._get_builtin_attr(node.func.id),
                    args=[self.visit(arg) for arg in node.args],
                    keywords=[self.visit(kw) for kw in node.keywords]
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
                            args=[self.visit(arg) for arg in node.args],
                            keywords=[self.visit(kw) for kw in node.keywords]
                        )
                        ast.copy_location(new_call, node)
                        return new_call

        return self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if self.skip_obf_depth > 0:
            return node
        if (
            node.id in BUILTIN_FUNCTIONS
            and isinstance(node.ctx, ast.Load)
            and not self._is_shadowed(node.id)
        ):
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