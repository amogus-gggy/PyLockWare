"""
Junk Code Transformer for PyLockWare
Generates fake if/elif branches with opaque predicates and complex conditions.
Now with anti-dump string poisoning and maximum visual annoyance.
"""
import ast
import random
from pylockware.core.name_generator import generate_random_name

import random
import string


def generate_random_strings(count, min_len=1, max_len=10):
    """
    Generates a list of random strings with lengths between min_len and max_len.

    Args:
        count (int): Number of strings to generate.
        min_len (int): Minimum length of each string.
        max_len (int): Maximum length of each string.

    Returns:
        list: A list of randomly generated strings.
    """
    # Define the pool of characters (letters and digits)
    characters = string.ascii_letters + string.digits

    random_strings = []
    for _ in range(count):
        # Generate a random length for the current string
        length = random.randint(min_len, max_len)

        # Generate the string by joining random choices
        random_string = ''.join(random.choice(characters) for _ in range(length))
        random_strings.append(random_string)

    return random_strings




class JunkCodeTransformer(ast.NodeTransformer):
    """
    Transforms code by adding fake if/elif branches, try/except blocks,
    dead loops, nested dead code, and ANTI-DUMP strings.
    These constructs are side‑effect free and never alter program logic.
    """


    ANTI_DUMP_STRINGS = generate_random_strings(500, min_len=3, max_len=64)

    def __init__(self, name_gen_settings='english', junk_density=0.8, opaque_complexity='high'):
        self.name_gen_settings = name_gen_settings
        self.junk_density = junk_density
        self.opaque_complexity = opaque_complexity
        self.var_counter = 0

    def _rand_name(self, prefix=""):
        return generate_random_name(prefix, self.name_gen_settings)

    def _anti_dump_string(self):
        return random.choice(self.ANTI_DUMP_STRINGS)

    def _anti_dump_constant(self):
        return ast.Constant(value=self._anti_dump_string())

    # ------------------------------------------------------------------
    # Opaque predicates (always True)
    # ------------------------------------------------------------------
    def _generate_opaque_true(self):
        complexity = self.opaque_complexity

        low = [
            ast.Compare(
                left=ast.BinOp(left=ast.Constant(42), op=ast.Sub(), right=ast.Constant(42)),
                ops=[ast.Eq()], comparators=[ast.Constant(0)]
            ),
            ast.Compare(
                left=ast.BinOp(left=ast.Constant(1337), op=ast.BitOr(), right=ast.Constant(0)),
                ops=[ast.Eq()], comparators=[ast.Constant(1337)]
            ),
            ast.Compare(
                left=ast.Call(func=ast.Name(id='type', ctx=ast.Load()),
                              args=[ast.Constant(1)], keywords=[]),
                ops=[ast.Is()], comparators=[ast.Name(id='int', ctx=ast.Load())]
            ),
            ast.Compare(
                left=ast.Call(func=ast.Name(id='callable', ctx=ast.Load()),
                              args=[ast.Name(id='print', ctx=ast.Load())], keywords=[]),
                ops=[ast.Is()], comparators=[ast.Constant(True)]
            ),
            ast.Compare(
                left=ast.Call(func=ast.Name(id='len', ctx=ast.Load()),
                              args=[ast.Constant("")], keywords=[]),
                ops=[ast.Eq()], comparators=[ast.Constant(0)]
            ),
        ]

        medium = [
            ast.Compare(
                left=ast.BinOp(
                    left=ast.BinOp(left=ast.Constant(100), op=ast.Mult(), right=ast.Constant(2)),
                    op=ast.FloorDiv(), right=ast.Constant(2)),
                ops=[ast.Eq()], comparators=[ast.Constant(100)]
            ),
            ast.Compare(
                left=ast.BinOp(left=ast.Constant(0xDEADBEEF), op=ast.BitAnd(), right=ast.Constant(0xDEADBEEF)),
                ops=[ast.Eq()], comparators=[ast.Constant(0xDEADBEEF)]
            ),
            ast.Compare(
                left=ast.UnaryOp(op=ast.Invert(),
                                 operand=ast.BinOp(
                                     left=ast.UnaryOp(op=ast.USub(), operand=ast.Constant(42)),
                                     op=ast.Sub(), right=ast.Constant(1))),
                ops=[ast.Eq()], comparators=[ast.Constant(42)]
            ),
            ast.Compare(
                left=ast.Call(func=ast.Name(id='str', ctx=ast.Load()),
                              args=[ast.Call(func=ast.Name(id='int', ctx=ast.Load()),
                                             args=[ast.Constant("123")], keywords=[])],
                              keywords=[]),
                ops=[ast.Eq()], comparators=[ast.Constant("123")]
            ),
            ast.Compare(
                left=ast.BinOp(
                    left=ast.Set(elts=[ast.Constant(1), ast.Constant(2)]),
                    op=ast.BitOr(),
                    right=ast.Set(elts=[ast.Constant(3)])),
                ops=[ast.Eq()],
                comparators=[ast.Set(elts=[ast.Constant(1), ast.Constant(2), ast.Constant(3)])]
            ),
            ast.Compare(
                left=ast.Call(func=ast.Name(id='any', ctx=ast.Load()),
                              args=[ast.List(elts=[ast.Constant(True), ast.Constant(False)],
                                            ctx=ast.Load())],
                              keywords=[]),
                ops=[ast.Is()], comparators=[ast.Constant(True)]
            ),
            ast.Compare(
                left=ast.Call(func=ast.Name(id='isinstance', ctx=ast.Load()),
                              args=[ast.Constant(0), ast.Name(id='int', ctx=ast.Load())],
                              keywords=[]),
                ops=[ast.Is()], comparators=[ast.Constant(True)]
            ),
        ]

        high = [
            ast.Compare(
                left=ast.Call(func=ast.Name(id='sum', ctx=ast.Load()),
                              args=[ast.GeneratorExp(
                                  elt=ast.Name(id='i', ctx=ast.Load()),
                                  generators=[ast.comprehension(
                                      target=ast.Name(id='i', ctx=ast.Store()),
                                      iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()),
                                                    args=[ast.Constant(5)], keywords=[]),
                                      ifs=[], is_async=0)])],
                              keywords=[]),
                ops=[ast.Eq()], comparators=[ast.Constant(10)]
            ),
            ast.Compare(
                left=ast.Call(func=ast.Name(id='all', ctx=ast.Load()),
                              args=[ast.GeneratorExp(
                                  elt=ast.Compare(left=ast.Name(id='i', ctx=ast.Load()),
                                                 ops=[ast.Lt()],
                                                 comparators=[ast.Constant(10)]),
                                  generators=[ast.comprehension(
                                      target=ast.Name(id='i', ctx=ast.Store()),
                                      iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()),
                                                    args=[ast.Constant(3)], keywords=[]),
                                      ifs=[], is_async=0)])],
                              keywords=[]),
                ops=[ast.Is()], comparators=[ast.Constant(True)]
            ),
            ast.Compare(
                left=ast.Call(func=ast.Name(id='len', ctx=ast.Load()),
                              args=[ast.SetComp(
                                  elt=ast.Name(id='x', ctx=ast.Load()),
                                  generators=[ast.comprehension(
                                      target=ast.Name(id='x', ctx=ast.Store()),
                                      iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()),
                                                    args=[ast.Constant(3)], keywords=[]),
                                      ifs=[], is_async=0)])],
                              keywords=[]),
                ops=[ast.Eq()], comparators=[ast.Constant(3)]
            ),
            ast.Compare(
                left=ast.Call(
                    func=ast.Lambda(
                        args=ast.arguments(posonlyargs=[], args=[ast.arg(arg='x')],
                                           kwonlyargs=[], kw_defaults=[], defaults=[]),
                        body=ast.Compare(left=ast.Name(id='x', ctx=ast.Load()),
                                        ops=[ast.Eq()],
                                        comparators=[ast.Name(id='x', ctx=ast.Load())])),
                    args=[ast.Constant(42)], keywords=[]),
                ops=[ast.Is()], comparators=[ast.Constant(True)]
            ),
            ast.Compare(
                left=ast.Subscript(
                    value=ast.DictComp(
                        key=ast.Name(id='k', ctx=ast.Load()),
                        value=ast.BinOp(left=ast.Name(id='k', ctx=ast.Load()),
                                       op=ast.Pow(), right=ast.Constant(2)),
                        generators=[ast.comprehension(
                            target=ast.Name(id='k', ctx=ast.Store()),
                            iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()),
                                          args=[ast.Constant(3)], keywords=[]),
                            ifs=[], is_async=0)]),
                    slice=ast.Constant(2), ctx=ast.Load()),
                ops=[ast.Eq()], comparators=[ast.Constant(4)]
            ),
            ast.Compare(
                left=ast.Constant('__name__'),
                ops=[ast.In()],
                comparators=[ast.Call(func=ast.Name(id='dir', ctx=ast.Load()),
                                      args=[], keywords=[])]
            ),
        ]

        if complexity == 'low':
            pool = low
        elif complexity == 'medium':
            pool = low + medium
        else:
            pool = low + medium + high

        return random.choice(pool)

    # ------------------------------------------------------------------
    # Opaque predicates (always False)
    # ------------------------------------------------------------------
    def _generate_opaque_false(self):
        complexity = self.opaque_complexity

        low = [
            ast.Compare(left=ast.Constant(1), ops=[ast.Eq()], comparators=[ast.Constant(0)]),
            ast.Compare(
                left=ast.Call(func=ast.Name(id='callable', ctx=ast.Load()),
                              args=[ast.Constant(1)], keywords=[]),
                ops=[ast.Is()], comparators=[ast.Constant(True)]
            ),
            ast.Compare(
                left=ast.Call(func=ast.Name(id='bool', ctx=ast.Load()),
                              args=[ast.Constant(0)], keywords=[]),
                ops=[ast.Is()], comparators=[ast.Constant(True)]
            ),
        ]

        medium = [
            ast.Compare(
                left=ast.BinOp(
                    left=ast.BinOp(left=ast.Constant(100), op=ast.Mult(), right=ast.Constant(2)),
                    op=ast.FloorDiv(), right=ast.Constant(2)),
                ops=[ast.NotEq()], comparators=[ast.Constant(100)]
            ),
            ast.Compare(left=ast.Constant(42), ops=[ast.In()],
                        comparators=[ast.List(elts=[], ctx=ast.Load())]),
            ast.Compare(
                left=ast.Call(func=ast.Name(id='type', ctx=ast.Load()),
                              args=[ast.Constant(42)], keywords=[]),
                ops=[ast.Is()], comparators=[ast.Name(id='str', ctx=ast.Load())]
            ),
            ast.Compare(
                left=ast.Call(func=ast.Name(id='any', ctx=ast.Load()),
                              args=[ast.List(elts=[ast.Constant(False), ast.Constant(False)],
                                            ctx=ast.Load())],
                              keywords=[]),
                ops=[ast.Is()], comparators=[ast.Constant(True)]
            ),
            ast.Compare(
                left=ast.Call(func=ast.Name(id='isinstance', ctx=ast.Load()),
                              args=[ast.Constant(42), ast.Name(id='str', ctx=ast.Load())],
                              keywords=[]),
                ops=[ast.Is()], comparators=[ast.Constant(True)]
            ),
        ]

        high = [
            ast.Compare(
                left=ast.Call(func=ast.Name(id='sum', ctx=ast.Load()),
                              args=[ast.GeneratorExp(
                                  elt=ast.Name(id='i', ctx=ast.Load()),
                                  generators=[ast.comprehension(
                                      target=ast.Name(id='i', ctx=ast.Store()),
                                      iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()),
                                                    args=[ast.Constant(5)], keywords=[]),
                                      ifs=[], is_async=0)])],
                              keywords=[]),
                ops=[ast.NotEq()], comparators=[ast.Constant(10)]
            ),
            ast.Compare(
                left=ast.Call(func=ast.Name(id='all', ctx=ast.Load()),
                              args=[ast.GeneratorExp(
                                  elt=ast.Compare(left=ast.Name(id='i', ctx=ast.Load()),
                                                 ops=[ast.Gt()],
                                                 comparators=[ast.Constant(10)]),
                                  generators=[ast.comprehension(
                                      target=ast.Name(id='i', ctx=ast.Store()),
                                      iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()),
                                                    args=[ast.Constant(3)], keywords=[]),
                                      ifs=[], is_async=0)])],
                              keywords=[]),
                ops=[ast.Is()], comparators=[ast.Constant(True)]
            ),
            ast.Compare(
                left=ast.Call(func=ast.Name(id='len', ctx=ast.Load()),
                              args=[ast.SetComp(
                                  elt=ast.Name(id='x', ctx=ast.Load()),
                                  generators=[ast.comprehension(
                                      target=ast.Name(id='x', ctx=ast.Store()),
                                      iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()),
                                                    args=[ast.Constant(3)], keywords=[]),
                                                    ifs=[], is_async=0)])],
                              keywords=[]),
                ops=[ast.NotEq()], comparators=[ast.Constant(3)]
            ),
            ast.Compare(
                left=ast.Call(
                    func=ast.Lambda(
                        args=ast.arguments(posonlyargs=[], args=[ast.arg(arg='x')],
                                           kwonlyargs=[], kw_defaults=[], defaults=[]),
                        body=ast.Compare(left=ast.Name(id='x', ctx=ast.Load()),
                                        ops=[ast.NotEq()],
                                        comparators=[ast.Name(id='x', ctx=ast.Load())])),
                    args=[ast.Constant(42)], keywords=[]),
                ops=[ast.Is()], comparators=[ast.Constant(True)]
            ),
            ast.Compare(
                left=ast.Call(
                    func=ast.Attribute(value=ast.DictComp(
                        key=ast.Name(id='k', ctx=ast.Load()),
                        value=ast.BinOp(left=ast.Name(id='k', ctx=ast.Load()),
                                       op=ast.Pow(), right=ast.Constant(2)),
                        generators=[ast.comprehension(
                            target=ast.Name(id='k', ctx=ast.Store()),
                            iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()),
                                          args=[ast.Constant(3)], keywords=[]),
                                          ifs=[], is_async=0)]),
                                       attr='get', ctx=ast.Load()),
                    args=[ast.Constant(99), ast.Constant(0)], keywords=[]),
                ops=[ast.NotEq()], comparators=[ast.Constant(0)]
            ),
            ast.Compare(left=ast.Constant("py"), ops=[ast.In()],
                        comparators=[ast.Constant("lockware")]),
        ]

        if complexity == 'low':
            pool = low
        elif complexity == 'medium':
            pool = low + medium
        else:
            pool = low + medium + high

        return random.choice(pool)

    # ------------------------------------------------------------------
    # Complex boolean combinations
    # ------------------------------------------------------------------
    def _generate_complex_condition(self):
        num_predicates = random.randint(2, 5)
        predicates = []

        for _ in range(num_predicates):
            if random.random() < 0.5:
                predicates.append(self._generate_opaque_true())
            else:
                predicates.append(self._generate_opaque_false())

        result = predicates[0]
        for pred in predicates[1:]:
            if random.random() < 0.5:
                result = ast.BoolOp(op=ast.And(), values=[result, pred])
            else:
                result = ast.BoolOp(op=ast.Or(), values=[result, pred])
        return result

    # ------------------------------------------------------------------
    # Junk statements (harmless, side‑effect free) with anti-dump strings
    # ------------------------------------------------------------------
    def _generate_junk_statement(self):
        junk_var = self._rand_name()
        kind = random.choice([
            'assign', 'list_comp', 'dict_comp', 'expr', 'anti_dump_assign',
            'anti_dump_list', 'anti_dump_dict', 'anti_dump_expr', 'anti_dump_tuple',
            'anti_dump_join', 'anti_dump_format', 'nested_ternary_fake',
        ])

        if kind == 'assign':
            return ast.Assign(
                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                value=ast.BinOp(
                    left=ast.BinOp(left=ast.Constant(random.randint(1, 100)),
                                   op=ast.Mult(),
                                   right=ast.Constant(random.randint(1, 100))),
                    op=ast.Add(),
                    right=ast.Constant(random.randint(1, 100))
                )
            )

        elif kind == 'list_comp':
            return ast.Assign(
                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                value=ast.ListComp(
                    elt=ast.Constant(random.randint(0, 10)),
                    generators=[ast.comprehension(
                        target=ast.Name(id='_', ctx=ast.Store()),
                        iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()),
                                      args=[ast.Constant(random.randint(1, 5))], keywords=[]),
                        ifs=[], is_async=0
                    )]
                )
            )

        elif kind == 'dict_comp':
            return ast.Assign(
                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                value=ast.DictComp(
                    key=ast.Name(id='x', ctx=ast.Load()),
                    value=ast.BinOp(left=ast.Name(id='x', ctx=ast.Load()),
                                   op=ast.Mult(), right=ast.Constant(2)),
                    generators=[ast.comprehension(
                        target=ast.Name(id='x', ctx=ast.Store()),
                        iter=ast.Call(func=ast.Name(id='range', ctx=ast.Load()),
                                      args=[ast.Constant(random.randint(1, 5))], keywords=[]),
                        ifs=[], is_async=0
                    )]
                )
            )

        elif kind == 'expr':
            return ast.Expr(value=ast.Call(
                func=ast.Name(id='str', ctx=ast.Load()),
                args=[ast.Constant(random.randint(0, 10000))], keywords=[]
            ))

        elif kind == 'anti_dump_assign':
            return ast.Assign(
                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                value=self._anti_dump_constant()
            )

        elif kind == 'anti_dump_list':
            return ast.Assign(
                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                value=ast.List(
                    elts=[self._anti_dump_constant() for _ in range(random.randint(2, 5))],
                    ctx=ast.Load()
                )
            )

        elif kind == 'anti_dump_dict':
            n = random.randint(2, 4)
            return ast.Assign(
                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                value=ast.Dict(
                    keys=[self._anti_dump_constant() for _ in range(n)],
                    values=[self._anti_dump_constant() for _ in range(n)]
                )
            )

        elif kind == 'anti_dump_expr':
            return ast.Expr(value=ast.Call(
                func=ast.Name(id='str', ctx=ast.Load()),
                args=[self._anti_dump_constant()], keywords=[]
            ))

        elif kind == 'anti_dump_tuple':
            return ast.Assign(
                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                value=ast.Tuple(
                    elts=[self._anti_dump_constant() for _ in range(random.randint(2, 4))],
                    ctx=ast.Load()
                )
            )

        elif kind == 'anti_dump_join':
            return ast.Assign(
                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=self._anti_dump_constant(),
                        attr='join', ctx=ast.Load()
                    ),
                    args=[ast.List(
                        elts=[self._anti_dump_constant() for _ in range(random.randint(2, 4))],
                        ctx=ast.Load()
                    )],
                    keywords=[]
                )
            )

        elif kind == 'anti_dump_format':
            n = random.randint(2, 4)
            fmt = ":".join(["{}"] * n)
            return ast.Assign(
                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                value=ast.Call(
                    func=ast.Attribute(
                        value=ast.Constant(value=fmt),
                        attr='format', ctx=ast.Load()
                    ),
                    args=[self._anti_dump_constant() for _ in range(n)],
                    keywords=[]
                )
            )

        elif kind == 'nested_ternary_fake':
            return ast.Assign(
                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                value=ast.IfExp(
                    test=self._generate_opaque_true(),
                    body=self._anti_dump_constant(),
                    orelse=self._anti_dump_constant()
                )
            )

        return ast.Pass()

    def _generate_junk_block(self, num_statements=5):
        """Generate a block of junk statements. Safe even when num_statements < 2."""
        lo = 1
        hi = max(lo, num_statements)
        return [self._generate_junk_statement() for _ in range(random.randint(lo, hi))]

    # ------------------------------------------------------------------
    # Deeply nested junk for maximum visual annoyance
    # ------------------------------------------------------------------
    def _generate_nested_if_chain(self, depth=0, max_depth=4):
        if depth >= max_depth:
            return self._generate_junk_block(random.randint(2, 4))

        body = self._generate_junk_block(random.randint(2, 4))

        nested = ast.If(
            test=self._generate_complex_condition() if random.random() < 0.7 else self._generate_opaque_true(),
            body=self._generate_nested_if_chain(depth + 1, max_depth),
            orelse=[]
        )
        body.append(nested)

        elif_branch = ast.If(
            test=self._generate_opaque_false(),
            body=self._generate_junk_block(random.randint(2, 4)),
            orelse=[]
        )

        main_if = ast.If(
            test=self._generate_complex_condition() if random.random() < 0.6 else self._generate_opaque_true(),
            body=body,
            orelse=[elif_branch]
        )
        return [main_if]

    def _generate_nested_try_except(self):
        inner_body = self._generate_junk_block(3)
        inner_body.append(
            ast.Assign(
                targets=[ast.Name(id=self._rand_name(), ctx=ast.Store())],
                value=ast.BinOp(left=ast.Constant(1), op=ast.Div(), right=ast.Constant(0))
            )
        )

        inner_handler = ast.ExceptHandler(
            type=ast.Name(id='ZeroDivisionError', ctx=ast.Load()),
            name=None,
            body=self._generate_junk_block(2)
        )

        inner_try = ast.Try(
            body=inner_body,
            handlers=[inner_handler],
            orelse=[],
            finalbody=[ast.Pass()]
        )

        outer_body = [inner_try] + self._generate_junk_block(2)
        outer_handler = ast.ExceptHandler(
            type=ast.Name(id='Exception', ctx=ast.Load()),
            name=self._rand_name(),
            body=self._generate_junk_block(2)
        )

        outer_try = ast.Try(
            body=outer_body,
            handlers=[outer_handler],
            orelse=self._generate_junk_block(2),
            finalbody=[ast.Pass(), ast.Pass()]
        )
        return [outer_try]

    def _generate_fake_with_block(self):
        """Fake with block: open(fake_secret, 'r') inside try/except Exception."""
        with_body = self._generate_junk_block(2)
        with_body.append(
            ast.Raise(
                exc=ast.Call(
                    func=ast.Name(id='RuntimeError', ctx=ast.Load()),
                    args=[self._anti_dump_constant()], keywords=[]
                )
            )
        )

        # Catch everything open() might raise (FileNotFoundError, PermissionError, etc.)
        # as well as the RuntimeError we raise inside the body.
        handler = ast.ExceptHandler(
            type=ast.Name(id='Exception', ctx=ast.Load()),
            name=None,
            body=self._generate_junk_block(2)
        )

        try_node = ast.Try(
            body=[
                ast.With(
                    items=[
                        ast.withitem(
                            context_expr=ast.Call(
                                func=ast.Name(id='open', ctx=ast.Load()),
                                args=[
                                    self._anti_dump_constant(),   # filename: fake secret
                                    ast.Constant(value='r')       # mode: valid read mode
                                ],
                                keywords=[]
                            ),
                            optional_vars=ast.Name(id=self._rand_name(), ctx=ast.Store())
                        )
                    ],
                    body=with_body,
                    type_comment=None
                )
            ],
            handlers=[handler],
            orelse=[],
            finalbody=[]
        )
        return [try_node]

    def _generate_fake_assert_block(self):
        asserts = []
        for _ in range(random.randint(2, 4)):
            asserts.append(
                ast.Assert(
                    test=self._generate_opaque_true(),
                    msg=self._anti_dump_constant()
                )
            )
        return asserts

    def _generate_fake_docstring(self):
        parts = [self._anti_dump_string() for _ in range(random.randint(3, 6))]
        content = " | ".join(parts)
        return ast.Expr(value=ast.Constant(value=content))

    # ------------------------------------------------------------------
    # Junk compound statements (if, try, for, while, with, assert)
    # ------------------------------------------------------------------
    def _generate_junk_compound(self):
        choice = random.choices(
            ['if', 'try', 'for', 'while', 'nested_if', 'nested_try', 'with', 'assert'],
            weights=[25, 20, 15, 10, 15, 10, 3, 2],
            k=1
        )[0]

        if choice == 'if':
            if random.random() < 0.4:
                main_if = ast.If(
                    test=self._generate_complex_condition() if random.random() < 0.7 else self._generate_opaque_true(),
                    body=self._generate_junk_block(),
                    orelse=[]
                )
                if random.random() < 0.5:
                    elif_branch = ast.If(
                        test=self._generate_opaque_false(),
                        body=self._generate_junk_block(),
                        orelse=[]
                    )
                    main_if.orelse = [elif_branch]
                return main_if
            else:
                return ast.If(
                    test=self._generate_opaque_true() if random.random() < 0.6 else self._generate_complex_condition(),
                    body=self._generate_junk_block(),
                    orelse=[]
                )

        elif choice == 'try':
            body = self._generate_junk_block()
            exc_type = random.choice([
                ast.Name(id='ZeroDivisionError', ctx=ast.Load()),
                ast.Name(id='IndexError', ctx=ast.Load()),
                ast.Name(id='TypeError', ctx=ast.Load()),
            ])
            junk_var = self._rand_name()

            exc_name = exc_type.id if isinstance(exc_type, ast.Name) else ''
            if exc_name == 'ZeroDivisionError':
                trigger_val = ast.BinOp(left=ast.Constant(1), op=ast.Div(), right=ast.Constant(0))
            elif exc_name == 'IndexError':
                trigger_val = ast.Subscript(value=ast.List(elts=[], ctx=ast.Load()),
                                           slice=ast.Constant(0), ctx=ast.Load())
            elif exc_name == 'TypeError':
                trigger_val = ast.BinOp(left=ast.Constant(1), op=ast.Add(), right=ast.Constant("string"))
            else:
                trigger_val = ast.BinOp(left=ast.Constant(1), op=ast.Div(), right=ast.Constant(0))

            trigger = ast.Assign(
                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                value=trigger_val
            )
            body.append(trigger)

            handler = ast.ExceptHandler(
                type=exc_type,
                name=None,
                body=self._generate_junk_block()
            )
            try_node = ast.Try(
                body=body,
                handlers=[handler],
                orelse=[],
                finalbody=[]
            )
            if random.random() < 0.3:
                try_node.orelse = self._generate_junk_block()
            if random.random() < 0.2:
                try_node.finalbody = [ast.Pass()]
            return try_node

        elif choice == 'for':
            junk_var = self._rand_name()
            if random.random() < 0.5:
                iter_node = ast.List(elts=[], ctx=ast.Load())
            else:
                n = random.randint(1, 3)
                iter_node = ast.Call(func=ast.Name(id='range', ctx=ast.Load()),
                                     args=[ast.Constant(n)], keywords=[])
            for_node = ast.For(
                target=ast.Name(id=junk_var, ctx=ast.Store()),
                iter=iter_node,
                body=self._generate_junk_block(),
                orelse=[],
                type_comment=None
            )
            return for_node

        elif choice == 'while':
            cond = random.choice([
                ast.Constant(False),
                ast.Compare(left=ast.Constant(1), ops=[ast.Eq()], comparators=[ast.Constant(0)]),
                ast.Name(id='False', ctx=ast.Load()),
                ast.Constant(0),
                ast.UnaryOp(op=ast.Not(), operand=ast.Constant(True)),
            ])
            while_node = ast.While(
                test=cond,
                body=self._generate_junk_block(),
                orelse=[]
            )
            return while_node

        elif choice == 'nested_if':
            return self._generate_nested_if_chain()[0]

        elif choice == 'nested_try':
            return self._generate_nested_try_except()[0]

        elif choice == 'with':
            return self._generate_fake_with_block()[0]

        elif choice == 'assert':
            asserts = self._generate_fake_assert_block()
            return ast.If(
                test=self._generate_opaque_true(),
                body=asserts,
                orelse=[]
            )

        return ast.Pass()

    # ------------------------------------------------------------------
    # AST visitors
    # ------------------------------------------------------------------
    def _insert_junk_around_statements(self, body):
        new_body = []
        for stmt in body:
            if random.random() < 0.6:
                new_body.append(self._generate_junk_compound())
            new_body.append(stmt)
            if random.random() < 0.4:
                new_body.append(self._generate_junk_compound())
            if random.random() < 0.15:
                new_body.append(self._generate_fake_docstring())
        if random.random() < 0.5:
            new_body.append(self._generate_junk_compound())
        if random.random() < 0.2:
            new_body.append(self._generate_fake_docstring())
        return new_body

    def visit_FunctionDef(self, node):
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'skip_obf':
                return self.generic_visit(node)
            elif isinstance(decorator, ast.Attribute) and decorator.attr == 'skip_obf':
                return self.generic_visit(node)

        if random.random() > self.junk_density:
            return self.generic_visit(node)

        if not (node.body and isinstance(node.body[0], ast.Expr) and
                isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str)):
            node.body.insert(0, self._generate_fake_docstring())

        node.body = self._insert_junk_around_statements(node.body)
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        if random.random() > self.junk_density:
            return self.generic_visit(node)

        if not (node.body and isinstance(node.body[0], ast.Expr) and
                isinstance(node.body[0].value, ast.Constant) and isinstance(node.body[0].value.value, str)):
            node.body.insert(0, self._generate_fake_docstring())

        node.body = self._insert_junk_around_statements(node.body)
        return self.generic_visit(node)

    def visit_ClassDef(self, node):
        new_body = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                new_body.append(self.visit(item))
            elif isinstance(item, ast.ClassDef):
                new_body.append(self.visit(item))
            else:
                new_body.append(self.generic_visit(item))
        node.body = new_body
        return node

    def visit_Module(self, node):
        new_body = []
        for _ in range(random.randint(2, 5)):
            new_body.append(self._generate_junk_statement())
            new_body.append(self._generate_junk_compound())

        for stmt in node.body:
            new_body.append(stmt)
            if random.random() < 0.3:
                new_body.append(self._generate_junk_compound())
            if random.random() < 0.1:
                new_body.append(self._generate_fake_docstring())

        for _ in range(random.randint(1, 3)):
            new_body.append(self._generate_junk_compound())

        node.body = new_body
        return self.generic_visit(node)

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------
    def apply_transformation(self, code):
        try:
            tree = ast.parse(code)
            transformed_tree = self.visit(tree)
            ast.fix_missing_locations(transformed_tree)
            result = ast.unparse(transformed_tree)
            return result
        except Exception:
            return code