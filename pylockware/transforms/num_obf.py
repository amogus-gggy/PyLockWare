#!/usr/bin/.venv python3
import random
import ast
import operator
import sys
import os
from functools import partial

OPS = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '//': operator.floordiv,
    '%': operator.mod,
    '^': operator.xor,
    '<<': operator.lshift,
    '>>': operator.rshift,
    '&': operator.and_,
    '|': operator.or_,
}

# Maximum recursion depth to prevent stack overflow
MAX_DEPTH = 3
# Maximum absolute value for target to prevent huge factorization
MAX_TARGET = 10000
# Timeout-like protection: max attempts per number
MAX_ATTEMPTS = 50


def atomic_expr(n: int) -> str:
    """
    Гарантированно возвращает выражение != литералу,
    которое вычисляется в n
    """
    if n == 0:
        choices = [
            "(~(-1))",
            "(lambda: 0)()",
            "len([])",
            "hash('') % 1",
            "sys.getsizeof(()) - sys.getsizeof(())",
        ]
        return random.choice(choices)

    if n == 1:
        choices = [
            "(2 >> 1)",
            "len([None])",
            "bool([None])",
            "hash('a') % 2",
            "(os.getpid() % 2) ^ (os.getpid() % 2) ^ 1",
        ]
        return random.choice(choices)

    if n == -1:
        choices = [
            "(~0)",
            "-(len([None]))",
            "-(bool([None]))",
            "hash('') % 1 - 1",
        ]
        return random.choice(choices)

    if n < 0:
        return f"(-{atomic_expr(-n)})"

    k = random.randint(1, 10)
    noise_techniques = [
        f"(({n + k}) - {k})",
        f"(({n + k}) ^ {random.randint(1, 255)} ^ {random.randint(1, 255)}) - {k}",
        f"(({n + k} + (hash(str({k})) % {k})) - (hash(str({k})) % {k}) - {k})",
        f"(({n + k} + (os.getpid() % {k})) - (os.getpid() % {k}) - {k})",
    ]
    return random.choice(noise_techniques)


# Cache to prevent infinite recursion on same values
_build_expr_cache = {}
_build_expr_call_count = [0]

def build_expr(target: int, depth: int, max_depth: int) -> str:
    # Global call counter to prevent infinite loops
    _build_expr_call_count[0] += 1
    if _build_expr_call_count[0] > MAX_ATTEMPTS * 10:
        return atomic_expr(target)

    # Clamp target to prevent huge computations
    if abs(target) > MAX_TARGET:
        return atomic_expr(target)

    if depth >= max_depth:
        return atomic_expr(target)

    # Cache key to prevent re-computing same (target, depth)
    cache_key = (target, depth, max_depth)
    if cache_key in _build_expr_cache:
        return _build_expr_cache[cache_key]

    # 20% chance to use function-based expression (not at top level)
    if random.random() < 0.2 and depth > 0:
        result = _create_function_based_expr(target)
        _build_expr_cache[cache_key] = result
        return result

    op = random.choice(list(OPS.keys()))

    try:
        if op == '+':
            a = random.randint(-50, 50)  # Reduced range
            b = target - a
        elif op == '-':
            a = random.randint(-50, 50)
            b = a - target
        elif op == '*':
            if target == 0:
                a, b = random.randint(1, 10), 0
            else:
                # FAST factorization: only check up to sqrt(|target|)
                abs_t = abs(target)
                factors = []
                limit = min(int(abs_t ** 0.5) + 1, 1000)
                for d in range(1, limit):
                    if target % d == 0:
                        factors.append(d)
                        if d != target // d:
                            factors.append(target // d)
                if not factors:
                    factors = [1, target]
                a = random.choice(factors)
                b = target // a if a != 0 else target
        elif op == '//':
            b = random.randint(1, 10)
            a = target * b
        elif op == '%':
            if target == 0:
                b = random.randint(1, 50)
                a = 0
            else:
                b = random.randint(abs(target) + 1, abs(target) + 50)
                a = target
        elif op == '<<':
            b = random.randint(1, 4)
            a = target >> b
        elif op == '>>':
            b = random.randint(1, 4)
            a = target << b
        elif op == '^':
            a = random.randint(1, 255)
            b = target ^ a
        elif op == '&':
            a = random.randint(1, 255)
            b = target | a
            left = build_expr(b, depth + 1, max_depth)
            right = build_expr(a, depth + 1, max_depth)
            expr = f"({left} & {right})"
            try:
                if eval(expr) != target:
                    result = atomic_expr(target)
                    _build_expr_cache[cache_key] = result
                    return result
            except:
                result = atomic_expr(target)
                _build_expr_cache[cache_key] = result
                return result
            _build_expr_cache[cache_key] = expr
            return expr
        elif op == '|':
            a = random.randint(0, 255)
            b = target & ~a
            left = build_expr(b, depth + 1, max_depth)
            right = build_expr(a, depth + 1, max_depth)
            expr = f"({left} | {right})"
            try:
                if eval(expr) != target:
                    result = atomic_expr(target)
                    _build_expr_cache[cache_key] = result
                    return result
            except:
                result = atomic_expr(target)
                _build_expr_cache[cache_key] = result
                return result
            _build_expr_cache[cache_key] = expr
            return expr
        else:
            result = atomic_expr(target)
            _build_expr_cache[cache_key] = result
            return result

        left = build_expr(a, depth + 1, max_depth)
        right = build_expr(b, depth + 1, max_depth)
        expr = f"({left} {op} {right})"

        # Add runtime noise (anti-inlining) - 30% chance
        if random.random() < 0.3:
            noise_type = random.choice(['hash', 'pid', 'platform'])
            if noise_type == 'hash':
                noise_val = random.randint(1, 100)
                expr = f"({expr} + (hash(str({noise_val})) % {noise_val}) - (hash(str({noise_val})) % {noise_val}))"
            elif noise_type == 'pid':
                noise_val = random.randint(1, 10)
                expr = f"({expr} + (os.getpid() % {noise_val}) - (os.getpid() % {noise_val}))"
            elif noise_type == 'platform':
                noise_val = random.randint(1, 10)
                expr = f"({expr} + (hash(sys.platform) % {noise_val}) - (hash(sys.platform) % {noise_val}))"

        # Verify the expression evaluates correctly
        try:
            if eval(expr) != target:
                result = atomic_expr(target)
                _build_expr_cache[cache_key] = result
                return result
        except:
            result = atomic_expr(target)
            _build_expr_cache[cache_key] = result
            return result

        _build_expr_cache[cache_key] = expr
        return expr

    except (ZeroDivisionError, ValueError, OverflowError, RecursionError):
        result = atomic_expr(target)
        _build_expr_cache[cache_key] = result
        return result


def _create_function_based_expr(target: int) -> str:
    """Create function-based expressions to prevent compiler inlining"""
    techniques = [
        lambda: f"(lambda: {target})()",
        lambda: f"((lambda x: x)({target}))",
        lambda: f"((lambda x={target}: x)())",
        lambda: f"type('_', (), {{'v': {target}}})().v",
        lambda: f"property(lambda self: {target}).fget(None)",
        lambda: f"[{target}][0]",
        lambda: f"({target},)[0]",
        lambda: f"{{0: {target}}}[0]",
        lambda: f"{{'v': {target}}}['v']",
        lambda: f"next(iter([{target}]))",
        lambda: f"[x for x in [{target}]][0]",
        lambda: f"(x for x in [{target}]).__next__()",
        lambda: f"{target} + (os.getpid() % 100 - os.getpid() % 100)",
        lambda: f"{target} + (hash(sys.platform) % 10 - hash(sys.platform) % 10)",
    ]

    return random.choice(techniques)()


def obfuscate_number(n: int) -> str:
    # Reset call counter for each number
    _build_expr_call_count[0] = 0
    _build_expr_cache.clear()

    # For very large numbers, use atomic expression directly
    if abs(n) > MAX_TARGET:
        return atomic_expr(n)

    for attempt in range(MAX_ATTEMPTS):
        try:
            if random.random() < 0.1:
                expr = _create_function_based_expr(n)
            else:
                expr = build_expr(n, 0, random.randint(1, MAX_DEPTH))

            try:
                if eval(expr) == n:
                    return expr
            except:
                pass
        except RecursionError:
            pass

    # Fallback to atomic expression after max attempts
    return atomic_expr(n)


def obfuscate_float(n: float) -> str:
    """
    Обфусцирует float значение путем преобразования его в строку,
    а затем в выражение, которое воссоздает это значение.
    """
    s = str(n)
    ascii_codes = [ord(c) for c in s]

    obfuscated_codes = []
    for code in ascii_codes:
        obfuscated_codes.append(obfuscate_number(code))

    codes_str = ', '.join(obfuscated_codes)

    float_techniques = [
        f"float(''.join(chr(x) for x in [{codes_str}]))",
        f"(lambda s: float(s))(''.join(chr(x) for x in [{codes_str}]))",
        f"type(0.0)(''.join(chr(x) for x in [{codes_str}]))",
    ]

    return random.choice(float_techniques)


class NumberObfuscator(ast.NodeTransformer):
    """AST transformer to obfuscate integer and float literals in Python code."""

    def __init__(self, use_parallel=False):
        self.number_counter = 0
        self.required_imports = set()
        self.use_parallel = False  # ALWAYS disabled
        self.skip_obf_depth = 0
        self.numbers_to_obfuscate = []
        self.obfuscated_cache = {}

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

    def collect_numbers(self, tree):
        collector = NumberCollector()
        collector.visit(tree)
        return collector.numbers

    def preprocess_numbers(self, tree):
        pass  # No parallel processing

    def visit_Constant(self, node):
        if self.skip_obf_depth > 0:
            return node

        if isinstance(node.value, int) and not isinstance(node.value, bool):
            obfuscated_expr = obfuscate_number(node.value)

            if 'os.getpid()' in obfuscated_expr:
                self.required_imports.add('os')
            if 'sys.platform' in obfuscated_expr or 'sys.getsizeof' in obfuscated_expr:
                self.required_imports.add('sys')

            try:
                obfuscated_node = ast.parse(obfuscated_expr, mode='eval').body
                return obfuscated_node
            except:
                return node

        elif isinstance(node.value, float):
            obfuscated_expr = obfuscate_float(node.value)

            if 'os.getpid()' in obfuscated_expr:
                self.required_imports.add('os')
            if 'sys.platform' in obfuscated_expr:
                self.required_imports.add('sys')

            try:
                obfuscated_node = ast.parse(obfuscated_expr, mode='eval').body
                return obfuscated_node
            except:
                return node

        return node

    def visit_Num(self, node):
        if isinstance(node.n, int):
            obfuscated_expr = obfuscate_number(node.n)

            if 'os.getpid()' in obfuscated_expr:
                self.required_imports.add('os')
            if 'sys.platform' in obfuscated_expr or 'sys.getsizeof' in obfuscated_expr:
                self.required_imports.add('sys')

            try:
                obfuscated_node = ast.parse(obfuscated_expr, mode='eval').body
                return obfuscated_node
            except:
                return node

        elif isinstance(node.n, float):
            obfuscated_expr = obfuscate_float(node.n)

            if 'os.getpid()' in obfuscated_expr:
                self.required_imports.add('os')
            if 'sys.platform' in obfuscated_expr:
                self.required_imports.add('sys')

            try:
                obfuscated_node = ast.parse(obfuscated_expr, mode='eval').body
                return obfuscated_node
            except:
                return node

        return node

    def get_required_imports(self) -> str:
        imports = []
        if 'os' in self.required_imports:
            imports.append('import os')
        if 'sys' in self.required_imports:
            imports.append('import sys')
        return '\n'.join(imports) if imports else ''


class NumberCollector(ast.NodeVisitor):
    """Visitor to collect all numbers in the AST for batch processing"""

    def __init__(self):
        self.numbers = []
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
            return
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        if self._has_skip_obf_decorator(node):
            self.skip_obf_depth += 1
            self.generic_visit(node)
            self.skip_obf_depth -= 1
            return
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        if self._has_skip_obf_decorator(node):
            self.skip_obf_depth += 1
            self.generic_visit(node)
            self.skip_obf_depth -= 1
            return
        self.generic_visit(node)

    def visit_Constant(self, node):
        if self.skip_obf_depth == 0:
            if isinstance(node.value, int) and not isinstance(node.value, bool):
                self.numbers.append(node.value)
        self.generic_visit(node)

    def visit_Num(self, node):
        if self.skip_obf_depth == 0:
            if isinstance(node.n, int):
                self.numbers.append(node.n)
        self.generic_visit(node)