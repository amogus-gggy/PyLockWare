"""
Junk Code Transformer for PyLockWare
Generates fake if/elif branches with opaque predicates and complex conditions
"""
import ast
import random
from pylockware.core.name_generator import generate_random_name


class JunkCodeTransformer(ast.NodeTransformer):
    """
    Transforms code by adding fake if/elif branches, try/except blocks,
    dead loops and other dead code with opaque predicates.
    These constructs are side‑effect free and never alter program logic.
    """

    def __init__(self, name_gen_settings='english', junk_density=0.5, opaque_complexity='high'):
        """
        Initialize the transformer.

        Args:
            name_gen_settings: Settings for generating random variable names
            junk_density: Probability of adding junk code to each function (0.0 to 1.0)
            opaque_complexity: 'low', 'medium', or 'high' complexity for opaque predicates
        """
        self.name_gen_settings = name_gen_settings
        self.junk_density = junk_density
        self.opaque_complexity = opaque_complexity
        self.var_counter = 0

    def _rand_name(self, prefix=""):
        """Generate a random variable name."""
        return generate_random_name(prefix, self.name_gen_settings)

    # ----------------------------------------------------------------------
    # Opaque predicates (always True)
    # ----------------------------------------------------------------------
    def _generate_opaque_true(self):
        """
        Generate an opaque predicate that always evaluates to True.
        Uses mathematical identities, type checks, functional tricks, etc.
        """
        complexity = self.opaque_complexity

        # ---- low complexity ----
        low = [
            # identity / bit ops
            ast.Compare(
                left=ast.BinOp(left=ast.Constant(42), op=ast.Sub(), right=ast.Constant(42)),
                ops=[ast.Eq()], comparators=[ast.Constant(0)]
            ),
            ast.Compare(
                left=ast.BinOp(left=ast.Constant(1337), op=ast.BitOr(), right=ast.Constant(0)),
                ops=[ast.Eq()], comparators=[ast.Constant(1337)]
            ),
            # simple type checks
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
            # len of empty container
            ast.Compare(
                left=ast.Call(func=ast.Name(id='len', ctx=ast.Load()),
                              args=[ast.Constant("")], keywords=[]),
                ops=[ast.Eq()], comparators=[ast.Constant(0)]
            ),
        ]

        # ---- medium complexity ----
        medium = [
            # math: (x*2)//2 == x
            ast.Compare(
                left=ast.BinOp(
                    left=ast.BinOp(left=ast.Constant(100), op=ast.Mult(), right=ast.Constant(2)),
                    op=ast.FloorDiv(), right=ast.Constant(2)),
                ops=[ast.Eq()], comparators=[ast.Constant(100)]
            ),
            # bit identity: x & x == x
            ast.Compare(
                left=ast.BinOp(left=ast.Constant(0xDEADBEEF), op=ast.BitAnd(), right=ast.Constant(0xDEADBEEF)),
                ops=[ast.Eq()], comparators=[ast.Constant(0xDEADBEEF)]
            ),
            # ~(-x-1) == x
            ast.Compare(
                left=ast.UnaryOp(op=ast.Invert(),
                                 operand=ast.BinOp(
                                     left=ast.UnaryOp(op=ast.USub(), operand=ast.Constant(42)),
                                     op=ast.Sub(), right=ast.Constant(1))),
                ops=[ast.Eq()], comparators=[ast.Constant(42)]
            ),
            # str(int("123")) == "123"
            ast.Compare(
                left=ast.Call(func=ast.Name(id='str', ctx=ast.Load()),
                              args=[ast.Call(func=ast.Name(id='int', ctx=ast.Load()),
                                             args=[ast.Constant("123")], keywords=[])],
                              keywords=[]),
                ops=[ast.Eq()], comparators=[ast.Constant("123")]
            ),
            # set operation: {1,2} | {3} == {1,2,3}
            ast.Compare(
                left=ast.BinOp(
                    left=ast.Set(elts=[ast.Constant(1), ast.Constant(2)]),
                    op=ast.BitOr(),
                    right=ast.Set(elts=[ast.Constant(3)])),
                ops=[ast.Eq()],
                comparators=[ast.Set(elts=[ast.Constant(1), ast.Constant(2), ast.Constant(3)])]
            ),
            # any([True, False]) == True
            ast.Compare(
                left=ast.Call(func=ast.Name(id='any', ctx=ast.Load()),
                              args=[ast.List(elts=[ast.Constant(True), ast.Constant(False)],
                                            ctx=ast.Load())],
                              keywords=[]),
                ops=[ast.Is()], comparators=[ast.Constant(True)]
            ),
            # isinstance(0, int)
            ast.Compare(
                left=ast.Call(func=ast.Name(id='isinstance', ctx=ast.Load()),
                              args=[ast.Constant(0), ast.Name(id='int', ctx=ast.Load())],
                              keywords=[]),
                ops=[ast.Is()], comparators=[ast.Constant(True)]
            ),
        ]

        # ---- high complexity (includes generator expressions) ----
        high = [
            # generator sum: sum(i for i in range(5)) == 10
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
            # all(i < 10 for i in range(3)) == True
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
            # set comprehension: len({x for x in range(3)}) == 3
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
            # lambda identity: (lambda x: x == x)(42) -> True
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
            # dict comprehension: {k: k**2 for k in range(3)}[2] == 4
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
            # globals(): '__name__' in dir() -> always true in a module
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

    # ----------------------------------------------------------------------
    # Opaque predicates (always False)
    # ----------------------------------------------------------------------
    def _generate_opaque_false(self):
        """
        Generate an opaque predicate that always evaluates to False.
        Uses contradictions, type mismatches, impossible math etc.
        """
        complexity = self.opaque_complexity

        low = [
            # 1 == 0
            ast.Compare(left=ast.Constant(1), ops=[ast.Eq()], comparators=[ast.Constant(0)]),
            # callable(1) -> False
            ast.Compare(
                left=ast.Call(func=ast.Name(id='callable', ctx=ast.Load()),
                              args=[ast.Constant(1)], keywords=[]),
                ops=[ast.Is()], comparators=[ast.Constant(True)]
            ),
            # bool(0) is True -> False
            ast.Compare(
                left=ast.Call(func=ast.Name(id='bool', ctx=ast.Load()),
                              args=[ast.Constant(0)], keywords=[]),
                ops=[ast.Is()], comparators=[ast.Constant(True)]
            ),
        ]

        medium = [
            # (100*2)//2 != 100  (always false)
            ast.Compare(
                left=ast.BinOp(
                    left=ast.BinOp(left=ast.Constant(100), op=ast.Mult(), right=ast.Constant(2)),
                    op=ast.FloorDiv(), right=ast.Constant(2)),
                ops=[ast.NotEq()], comparators=[ast.Constant(100)]
            ),
            # 42 in [] -> False
            ast.Compare(left=ast.Constant(42), ops=[ast.In()],
                        comparators=[ast.List(elts=[], ctx=ast.Load())]),
            # type(42) == str -> False
            ast.Compare(
                left=ast.Call(func=ast.Name(id='type', ctx=ast.Load()),
                              args=[ast.Constant(42)], keywords=[]),
                ops=[ast.Is()], comparators=[ast.Name(id='str', ctx=ast.Load())]
            ),
            # any([False, False]) -> False
            ast.Compare(
                left=ast.Call(func=ast.Name(id='any', ctx=ast.Load()),
                              args=[ast.List(elts=[ast.Constant(False), ast.Constant(False)],
                                            ctx=ast.Load())],
                              keywords=[]),
                ops=[ast.Is()], comparators=[ast.Constant(True)]
            ),
            # isinstance(42, str) -> False
            ast.Compare(
                left=ast.Call(func=ast.Name(id='isinstance', ctx=ast.Load()),
                              args=[ast.Constant(42), ast.Name(id='str', ctx=ast.Load())],
                              keywords=[]),
                ops=[ast.Is()], comparators=[ast.Constant(True)]
            ),
        ]

        high = [
            # generator: sum(i for i in range(5)) != 10  (always false)
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
            # all(i > 10 for i in range(3)) -> False (0 > 10 is false)
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
            # len({x for x in range(3)}) != 3
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
            # lambda contradiction: (lambda x: x != x)(42) -> False
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
            # dict comprehension: {k: k**2 for k in range(3)}.get(99, 0) != 0
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
            # "py" in "lockware" -> False (case-sensitive)
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

    # ----------------------------------------------------------------------
    # Complex boolean combinations
    # ----------------------------------------------------------------------
    def _generate_complex_condition(self):
        """Generate a complex boolean combination of opaque predicates."""
        num_predicates = random.randint(2, 4)
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

    # ----------------------------------------------------------------------
    # Junk statements (harmless, side‑effect free)
    # ----------------------------------------------------------------------
    def _generate_junk_statement(self):
        """Generate a single junk statement that does nothing meaningful."""
        junk_var = self._rand_name()
        kind = random.choice(['assign', 'list_comp', 'dict_comp', 'expr'])
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
        else:  # expr (no-op)
            return ast.Expr(value=ast.Call(
                func=ast.Name(id='str', ctx=ast.Load()),
                args=[ast.Constant(random.randint(0, 10000))], keywords=[]
            ))

    def _generate_junk_block(self, num_statements=3):
        """Generate a block of junk statements."""
        return [self._generate_junk_statement() for _ in range(random.randint(2, num_statements))]

    # ----------------------------------------------------------------------
    # Junk compound statements (if, try, for, while)
    # ----------------------------------------------------------------------
    def _generate_junk_compound(self):
        """Return a random junk compound statement (harmless)."""
        choice = random.choices(
            ['if', 'try', 'for', 'while'],
            weights=[40, 30, 20, 10],
            k=1
        )[0]

        if choice == 'if':
            # Fake if-elif chain
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
            # try-except(-else-finally) that always catches the exception it generates
            body = self._generate_junk_block()
            exc_type = random.choice([
                ast.Name(id='ZeroDivisionError', ctx=ast.Load()),
                ast.Name(id='IndexError', ctx=ast.Load()),
                ast.Name(id='TypeError', ctx=ast.Load()),
            ])
            junk_var = self._rand_name()

            # Build a statement that raises exactly the chosen exception
            exc_name = exc_type.id if isinstance(exc_type, ast.Name) else ''
            if exc_name == 'ZeroDivisionError':
                trigger_val = ast.BinOp(left=ast.Constant(1), op=ast.Div(), right=ast.Constant(0))
            elif exc_name == 'IndexError':
                trigger_val = ast.Subscript(value=ast.List(elts=[], ctx=ast.Load()),
                                           slice=ast.Constant(0), ctx=ast.Load())
            elif exc_name == 'TypeError':
                # e.g., 1 + "string" or len(42)
                trigger_val = ast.BinOp(left=ast.Constant(1), op=ast.Add(), right=ast.Constant("string"))
            else:
                trigger_val = ast.BinOp(left=ast.Constant(1), op=ast.Div(), right=ast.Constant(0))  # fallback

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
                try_node.finalbody = [ast.Pass()]  # finally can be pass
            return try_node

        elif choice == 'for':
            # for loop with a dummy iterator (often zero iterations)
            junk_var = self._rand_name()
            # 50% chance: empty iterator (safe), 50% chance: small range
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

        else:  # 'while'
            # while False / while 0  (never executed)
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

    # ----------------------------------------------------------------------
    # AST visitors
    # ----------------------------------------------------------------------
    def _insert_junk_around_statements(self, body):
        """Insert junk compound statements around existing statements in a body list."""
        new_body = []
        for stmt in body:
            # sometimes prepend a junk compound
            if random.random() < 0.5:
                new_body.append(self._generate_junk_compound())
            # original statement
            new_body.append(stmt)
            # sometimes append a junk compound
            if random.random() < 0.3:
                new_body.append(self._generate_junk_compound())
        # occasionally add a final junk compound
        if random.random() < 0.4:
            new_body.append(self._generate_junk_compound())
        return new_body

    def visit_FunctionDef(self, node):
        """Add junk code to function definitions."""
        # Check for @skip_obf decorator
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'skip_obf':
                return self.generic_visit(node)
            elif isinstance(decorator, ast.Attribute) and decorator.attr == 'skip_obf':
                return self.generic_visit(node)

        if random.random() > self.junk_density:
            return self.generic_visit(node)

        node.body = self._insert_junk_around_statements(node.body)
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Add junk code to async function definitions (same logic)."""
        if random.random() > self.junk_density:
            return self.generic_visit(node)

        node.body = self._insert_junk_around_statements(node.body)
        return self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Process class definitions - apply junk code to methods."""
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

    # ----------------------------------------------------------------------
    # Entry point
    # ----------------------------------------------------------------------
    def apply_transformation(self, code):
        """
        Apply junk code transformation to Python code.

        Args:
            code: Python source code as string

        Returns:
            Transformed code with junk constructs
        """
        try:
            tree = ast.parse(code)
            transformed_tree = self.visit(tree)
            ast.fix_missing_locations(transformed_tree)
            result = ast.unparse(transformed_tree)
            return result
        except Exception:
            # If anything fails, return the original code unchanged
            return code