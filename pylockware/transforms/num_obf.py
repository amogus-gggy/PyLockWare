#!/usr/bin/.venv python3
import random
import ast
import operator
import time
import sys
import os
from multiprocessing import Pool, cpu_count
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

def atomic_expr(n: int) -> str:
    """
    Гарантированно возвращает выражение != литералу,
    которое вычисляется в n
    """
    if n == 0:
        # Multiple anti-inlining techniques for 0
        choices = [
            "(~(-1))",                    # Bitwise: ~(-1)
            "(lambda: 0)()",              # Function call
            "len([])",                    # Empty list length
            "hash('') % 1",               # Hash modulo 1
            "sys.getsizeof(()) - sys.getsizeof(())",  # Runtime calculation
        ]
        return random.choice(choices)

    if n == 1:
        # Anti-inlining techniques for 1
        choices = [
            "(2 >> 1)",                   # Bit shift
            "len([None])",                # List with one element
            "bool([None])",               # Boolean conversion
            "hash('a') % 2",              # Hash modulo 2
            "(os.getpid() % 2) ^ (os.getpid() % 2) ^ 1",  # Runtime XOR
        ]
        return random.choice(choices)

    if n == -1:
        # Anti-inlining techniques for -1
        choices = [
            "(~0)",                       # Bitwise NOT
            "-(len([None]))",             # Negative length
            "-(bool([None]))",            # Negative boolean
            "hash('') % 1 - 1",           # Hash calculation
            "(time.time_ns() % 2) - (time.time_ns() % 2) - 1",  # Runtime
        ]
        return random.choice(choices)

    if n < 0:
        return f"(-{atomic_expr(-n)})"

    # Anti-inlining: add runtime noise that cancels out
    k = random.randint(1, 10)
    noise_techniques = [
        f"(({n + k}) - {k})",  # Basic arithmetic
        f"(({n + k}) ^ {random.randint(1, 255)} ^ {random.randint(1, 255)}) - {k}",  # XOR noise
        f"(({n + k} + (hash(str({k})) % {k})) - (hash(str({k})) % {k}) - {k})",  # Hash noise
        f"(({n + k} + (os.getpid() % {k})) - (os.getpid() % {k}) - {k})",  # PID noise
    ]
    return random.choice(noise_techniques)

def build_expr(target: int, depth: int, max_depth: int) -> str:
    if depth >= max_depth:
        return atomic_expr(target)

    # Sometimes use function-based expressions to prevent inlining
    if random.random() < 0.2 and depth > 0:  # 20% chance, but not at top level
        return _create_function_based_expr(target)

    op = random.choice(list(OPS.keys()))

    try:
        if op == '+':
            a = random.randint(-100, 100)
            b = target - a
        elif op == '-':
            a = random.randint(-100, 100)
            b = a - target
        elif op == '*':
            if target == 0:
                a, b = random.randint(1, 10), 0
            else:
                factors = [d for d in range(1, abs(target) + 1) if target % d == 0]
                a = random.choice(factors) if factors else 1
                b = target // a if a != 0 else target
        elif op == '//':
            b = random.randint(1, 10)  # Ensure b is never 0
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
            b = target | a  # Will be ANDed with a
            # Create expression: (b & a) = target
            left = build_expr(b, depth + 1, max_depth)
            right = build_expr(a, depth + 1, max_depth)
            expr = f"({left} & {right})"
            if eval(expr) != target:
                return atomic_expr(target)
            return expr
        elif op == '|':
            a = random.randint(0, 255)
            b = target & ~a  # Will be ORed with a
            left = build_expr(b, depth + 1, max_depth)
            right = build_expr(a, depth + 1, max_depth)
            expr = f"({left} | {right})"
            if eval(expr) != target:
                return atomic_expr(target)
            return expr
        else:
            return atomic_expr(target)

        left = build_expr(a, depth + 1, max_depth)
        right = build_expr(b, depth + 1, max_depth)
        expr = f"({left} {op} {right})"

        # Add runtime noise that cancels out (anti-inlining)
        if random.random() < 0.3:  # 30% chance to add noise
            noise_type = random.choice(['hash', 'pid', 'time', 'platform'])
            if noise_type == 'hash':
                noise_val = random.randint(1, 100)
                expr = f"({expr} + (hash(str({noise_val})) % {noise_val}) - (hash(str({noise_val})) % {noise_val}))"
            elif noise_type == 'pid':
                noise_val = random.randint(1, 10)
                expr = f"({expr} + (os.getpid() % {noise_val}) - (os.getpid() % {noise_val}))"
            elif noise_type == 'time':
                noise_val = random.randint(1, 10)
                expr = f"({expr} + (int(time.time()) % {noise_val}) - (int(time.time()) % {noise_val}))"
            elif noise_type == 'platform':
                noise_val = random.randint(1, 10)
                expr = f"({expr} + (hash(sys.platform) % {noise_val}) - (hash(sys.platform) % {noise_val}))"

        # жёсткая проверка
        if eval(expr) != target:
            return atomic_expr(target)

        return expr

    except (ZeroDivisionError, ValueError, OverflowError) as e:
        # Fallback to atomic expression on any arithmetic error
        return atomic_expr(target)

def _create_function_based_expr(target: int) -> str:
    """Create function-based expressions to prevent compiler inlining"""
    techniques = [
        # Lambda functions
        lambda: f"(lambda: {target})()",
        lambda: f"((lambda x: x)({target}))",
        lambda: f"((lambda x={target}: x)())",

        # Class-based
        lambda: f"type('_', (), {{'v': {target}}})().v",
        lambda: f"property(lambda self: {target}).fget(None)",

        # Container-based
        lambda: f"[{target}][0]",
        lambda: f"({target},)[0]",
        lambda: f"{{0: {target}}}[0]",
        lambda: f"{{'v': {target}}}['v']",

        # Generator/iterator
        lambda: f"next(iter([{target}]))",
        lambda: f"[x for x in [{target}]][0]",
        lambda: f"(x for x in [{target}]).__next__()",

        # Runtime-dependent with cancellation
        lambda: f"{target} + (os.getpid() % 100 - os.getpid() % 100)",
        lambda: f"{target} + (hash(sys.platform) % 10 - hash(sys.platform) % 10)",
        lambda: f"{target} + (int(time.time()) % 10 - int(time.time()) % 10)",
    ]

    return random.choice(techniques)()

def obfuscate_number(n: int) -> str:
    try:
        # Sometimes use pure function-based expressions for better anti-inlining
        if random.random() < 0.1:  # 10% chance for pure function-based
            expr = _create_function_based_expr(n)
        else:
            expr = build_expr(n, 0, random.randint(2, 4))

        # Verify the expression evaluates correctly
        try:
            assert eval(expr) == n, f"Expression {expr} doesn't evaluate to {n}"
        except:
            # Fallback to atomic expression if verification fails
            expr = atomic_expr(n)

        return expr
    except Exception as e:
        # Ultimate fallback: return the number as-is
        return str(n)

def _obfuscate_number_worker(n: int) -> tuple:
    """Worker function for parallel number obfuscation"""
    try:
        expr = obfuscate_number(n)
        # Verify the result
        if eval(expr) == n:
            return (n, expr, True)
        else:
            return (n, str(n), False)
    except Exception as e:
        # Return original number on any error
        return (n, str(n), False)

def obfuscate_numbers_parallel(numbers: list) -> dict:
    """
    Obfuscate multiple numbers in parallel using multiprocessing.

    Args:
        numbers: List of integers to obfuscate

    Returns:
        Dictionary mapping original numbers to obfuscated expressions
    """
    if not numbers:
        return {}

    # Use all available CPU cores, but cap at 8 to avoid overhead
    num_workers = min(cpu_count(), 8, len(numbers))

    # For small number of items, don't use multiprocessing (overhead not worth it)
    if len(numbers) < 10:
        result = {}
        for n in numbers:
            result[n] = obfuscate_number(n)
        return result

    # Use multiprocessing for larger batches
    try:
        with Pool(processes=num_workers) as pool:
            results = pool.map(_obfuscate_number_worker, numbers)

        # Convert results to dictionary
        return {n: expr for n, expr, success in results if success}
    except Exception as e:
        # Fallback to sequential processing if multiprocessing fails
        print(f"Warning: Parallel processing failed, falling back to sequential: {e}")
        result = {}
        for n in numbers:
            result[n] = obfuscate_number(n)
        return result

def get_imports_for_obfuscated_code() -> str:
    """
    Returns import statements needed for the obfuscated code to work.
    These imports are required for runtime-dependent expressions.
    """
    return "import os\nimport time\nimport sys\n"

def obfuscate_float(n: float) -> str:
    """
    Обфусцирует float значение путем преобразования его в строку,
    а затем в выражение, которое воссоздает это значение.
    """
    s = str(n)
    # Преобразуем строку в список ASCII кодов
    ascii_codes = [ord(c) for c in s]

    # Obfuscate each ASCII code with anti-inlining techniques
    obfuscated_codes = []
    for code in ascii_codes:
        # Use obfuscate_number for integers
        obfuscated_codes.append(obfuscate_number(code))

    codes_str = ', '.join(obfuscated_codes)

    # Use function-based float conversion for extra obfuscation
    float_techniques = [
        f"float(''.join(chr(x) for x in [{codes_str}]))",
        f"(lambda s: float(s))(''.join(chr(x) for x in [{codes_str}]))",
        f"type(0.0)(''.join(chr(x) for x in [{codes_str}]))",
    ]

    return random.choice(float_techniques)

class NumberObfuscator(ast.NodeTransformer):
    """AST transformer to obfuscate integer and float literals in Python code."""

    def __init__(self, use_parallel=True):
        self.number_counter = 0
        self.required_imports = set()  # Track required imports
        self.use_parallel = use_parallel

        # Track if we're inside a @skip_obf function/class
        self.skip_obf_depth = 0

        # Collect all numbers for batch processing
        self.numbers_to_obfuscate = []
        self.obfuscated_cache = {}

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

    def collect_numbers(self, tree):
        """First pass: collect all numbers that need obfuscation"""
        collector = NumberCollector()
        collector.visit(tree)
        return collector.numbers

    def preprocess_numbers(self, tree):
        """Collect and obfuscate all numbers in parallel before transformation"""
        if not self.use_parallel:
            return

        # Collect all unique numbers
        numbers = self.collect_numbers(tree)
        unique_numbers = list(set(numbers))

        if unique_numbers:
            # Obfuscate in parallel
            self.obfuscated_cache = obfuscate_numbers_parallel(unique_numbers)

    def visit_Constant(self, node):
        """Handle numeric constants in newer Python versions."""
        # Skip if inside @skip_obf context
        if self.skip_obf_depth > 0:
            return node

        if isinstance(node.value, int) and not isinstance(node.value, bool):
            # Use cached obfuscation if available
            if self.use_parallel and node.value in self.obfuscated_cache:
                obfuscated_expr = self.obfuscated_cache[node.value]
            else:
                # Obfuscate the number
                obfuscated_expr = obfuscate_number(node.value)

            # Check if the expression uses runtime modules
            if 'os.getpid()' in obfuscated_expr:
                self.required_imports.add('os')
            if 'time.time()' in obfuscated_expr or 'time.time_ns()' in obfuscated_expr:
                self.required_imports.add('time')
            if 'sys.platform' in obfuscated_expr or 'sys.getsizeof' in obfuscated_expr:
                self.required_imports.add('sys')

            # Parse the obfuscated expression back to an AST node
            try:
                obfuscated_node = ast.parse(obfuscated_expr, mode='eval').body
                return obfuscated_node
            except:
                # If parsing fails, return the original node
                return node

        elif isinstance(node.value, float):
            # Obfuscate the float value
            obfuscated_expr = obfuscate_float(node.value)

            # Check if the expression uses runtime modules
            if 'os.getpid()' in obfuscated_expr:
                self.required_imports.add('os')
            if 'time.time()' in obfuscated_expr or 'time.time_ns()' in obfuscated_expr:
                self.required_imports.add('time')
            if 'sys.platform' in obfuscated_expr:
                self.required_imports.add('sys')

            # Parse the obfuscated expression back to an AST node
            try:
                obfuscated_node = ast.parse(obfuscated_expr, mode='eval').body
                return obfuscated_node
            except:
                # If parsing fails, return the original node
                return node

        return node

    def visit_Num(self, node):
        """Handle numeric literals in older Python versions."""

        if isinstance(node.n, int):
            # Use cached obfuscation if available
            if self.use_parallel and node.n in self.obfuscated_cache:
                obfuscated_expr = self.obfuscated_cache[node.n]
            else:
                # Obfuscate the number
                obfuscated_expr = obfuscate_number(node.n)

            # Check if the expression uses runtime modules
            if 'os.getpid()' in obfuscated_expr:
                self.required_imports.add('os')
            if 'time.time()' in obfuscated_expr or 'time.time_ns()' in obfuscated_expr:
                self.required_imports.add('time')
            if 'sys.platform' in obfuscated_expr or 'sys.getsizeof' in obfuscated_expr:
                self.required_imports.add('sys')

            # Parse the obfuscated expression back to an AST node
            try:
                obfuscated_node = ast.parse(obfuscated_expr, mode='eval').body
                return obfuscated_node
            except:
                # If parsing fails, return the original node
                return node

        elif isinstance(node.n, float):
            # Obfuscate the float value
            obfuscated_expr = obfuscate_float(node.n)

            # Check if the expression uses runtime modules
            if 'os.getpid()' in obfuscated_expr:
                self.required_imports.add('os')
            if 'time.time()' in obfuscated_expr or 'time.time_ns()' in obfuscated_expr:
                self.required_imports.add('time')
            if 'sys.platform' in obfuscated_expr:
                self.required_imports.add('sys')

            # Parse the obfuscated expression back to an AST node
            try:
                obfuscated_node = ast.parse(obfuscated_expr, mode='eval').body
                return obfuscated_node
            except:
                # If parsing fails, return the original node
                return node

        return node

    def get_required_imports(self) -> str:
        """Get the import statements needed for the obfuscated code."""
        imports = []
        if 'os' in self.required_imports:
            imports.append('import os')
        if 'time' in self.required_imports:
            imports.append('import time')
        if 'sys' in self.required_imports:
            imports.append('import sys')
        return '\n'.join(imports) if imports else ''

class NumberCollector(ast.NodeVisitor):
    """Visitor to collect all numbers in the AST for batch processing"""

    def __init__(self):
        self.numbers = []
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
            return
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Track when entering/exiting async functions with @skip_obf"""
        if self._has_skip_obf_decorator(node):
            self.skip_obf_depth += 1
            self.generic_visit(node)
            self.skip_obf_depth -= 1
            return
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Track when entering/exiting classes with @skip_obf"""
        if self._has_skip_obf_decorator(node):
            self.skip_obf_depth += 1
            self.generic_visit(node)
            self.skip_obf_depth -= 1
            return
        self.generic_visit(node)

    def visit_Constant(self, node):
        """Collect integer constants"""
        if self.skip_obf_depth == 0:
            if isinstance(node.value, int) and not isinstance(node.value, bool):
                self.numbers.append(node.value)
        self.generic_visit(node)

    def visit_Num(self, node):
        """Collect numeric literals (older Python versions)"""
        if self.skip_obf_depth == 0:
            if isinstance(node.n, int):
                self.numbers.append(node.n)
        self.generic_visit(node)