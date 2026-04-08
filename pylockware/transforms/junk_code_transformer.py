"""
Junk Code Transformer for PyLockWare
Generates fake if/elif branches with opaque predicates and complex conditions
"""
import ast
import random
from pylockware.core.name_generator import generate_random_name


class JunkCodeTransformer(ast.NodeTransformer):
    """
    Transforms code by adding fake if/elif branches with opaque predicates.
    These are complex conditions that always evaluate to True or False but are hard to analyze.
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
    
    def _generate_opaque_true(self):
        """
        Generate an opaque predicate that always evaluates to True.
        Uses mathematical identities and bit manipulation tricks.
        """
        complexity = self.opaque_complexity
        
        # Low complexity - simple mathematical identities
        low_predicates = [
            # x == x is always true
            ast.Compare(
                left=ast.Name(id='len', ctx=ast.Load()),
                ops=[ast.Is()],
                comparators=[ast.Name(id='len', ctx=ast.Load())]
            ),
            # x - x == 0
            ast.Compare(
                left=ast.BinOp(
                    left=ast.Constant(42),
                    op=ast.Sub(),
                    right=ast.Constant(42)
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(0)]
            ),
            # x | 0 == x
            ast.Compare(
                left=ast.BinOp(
                    left=ast.Constant(1337),
                    op=ast.BitOr(),
                    right=ast.Constant(0)
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(1337)]
            ),
            # len("") == 0
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='len', ctx=ast.Load()),
                    args=[ast.Constant("")],
                    keywords=[]
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(0)]
            ),
            # bool(1) is True
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='bool', ctx=ast.Load()),
                    args=[ast.Constant(1)],
                    keywords=[]
                ),
                ops=[ast.Is()],
                comparators=[ast.Constant(True)]
            ),
        ]
        
        # Medium complexity - more complex mathematical identities
        medium_predicates = [
            # (x * 2) / 2 == x for even numbers
            ast.Compare(
                left=ast.BinOp(
                    left=ast.BinOp(
                        left=ast.Constant(100),
                        op=ast.Mult(),
                        right=ast.Constant(2)
                    ),
                    op=ast.FloorDiv(),
                    right=ast.Constant(2)
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(100)]
            ),
            # x & x == x
            ast.Compare(
                left=ast.BinOp(
                    left=ast.Constant(0xDEADBEEF),
                    op=ast.BitAnd(),
                    right=ast.Constant(0xDEADBEEF)
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(0xDEADBEEF)]
            ),
            # ~(-x-1) == x
            ast.Compare(
                left=ast.UnaryOp(
                    op=ast.Invert(),
                    operand=ast.BinOp(
                        left=ast.UnaryOp(op=ast.USub(), operand=ast.Constant(42)),
                        op=ast.Sub(),
                        right=ast.Constant(1)
                    )
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(42)]
            ),
            # str(int("123")) == "123"
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='str', ctx=ast.Load()),
                    args=[ast.Call(
                        func=ast.Name(id='int', ctx=ast.Load()),
                        args=[ast.Constant("123")],
                        keywords=[]
                    )],
                    keywords=[]
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant("123")]
            ),
            # list("abc") == ["a", "b", "c"]
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='list', ctx=ast.Load()),
                    args=[ast.Constant("abc")],
                    keywords=[]
                ),
                ops=[ast.Eq()],
                comparators=[ast.List(
                    elts=[ast.Constant("a"), ast.Constant("b"), ast.Constant("c")],
                    ctx=ast.Load()
                )]
            ),
        ]
        
        # High complexity - very complex opaque predicates
        high_predicates = [
            # pow(x, 0) == 1 for any x != 0
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='pow', ctx=ast.Load()),
                    args=[ast.Constant(7), ast.Constant(0)],
                    keywords=[]
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(1)]
            ),
            # (x ^ y) ^ y == x
            ast.Compare(
                left=ast.BinOp(
                    left=ast.BinOp(
                        left=ast.Constant(0x12345678),
                        op=ast.BitXor(),
                        right=ast.Constant(0xABCDEF00)
                    ),
                    op=ast.BitXor(),
                    right=ast.Constant(0xABCDEF00)
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(0x12345678)]
            ),
            # chr(ord('A')) == 'A'
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='chr', ctx=ast.Load()),
                    args=[ast.Call(
                        func=ast.Name(id='ord', ctx=ast.Load()),
                        args=[ast.Constant("A")],
                        keywords=[]
                    )],
                    keywords=[]
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant("A")]
            ),
            # sum([1,2,3]) == 6
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='sum', ctx=ast.Load()),
                    args=[ast.List(
                        elts=[ast.Constant(1), ast.Constant(2), ast.Constant(3)],
                        ctx=ast.Load()
                    )],
                    keywords=[]
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(6)]
            ),
            # all([True, True, True]) == True
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='all', ctx=ast.Load()),
                    args=[ast.List(
                        elts=[ast.Constant(True), ast.Constant(True), ast.Constant(True)],
                        ctx=ast.Load()
                    )],
                    keywords=[]
                ),
                ops=[ast.Is()],
                comparators=[ast.Constant(True)]
            ),
            # any([False, False, True]) == True
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='any', ctx=ast.Load()),
                    args=[ast.List(
                        elts=[ast.Constant(False), ast.Constant(False), ast.Constant(True)],
                        ctx=ast.Load()
                    )],
                    keywords=[]
                ),
                ops=[ast.Is()],
                comparators=[ast.Constant(True)]
            ),
            # min(5, max(10, 5)) == 5
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='min', ctx=ast.Load()),
                    args=[
                        ast.Constant(5),
                        ast.Call(
                            func=ast.Name(id='max', ctx=ast.Load()),
                            args=[ast.Constant(10), ast.Constant(5)],
                            keywords=[]
                        )
                    ],
                    keywords=[]
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(5)]
            ),
            # abs(-42) == 42
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='abs', ctx=ast.Load()),
                    args=[ast.UnaryOp(op=ast.USub(), operand=ast.Constant(42))],
                    keywords=[]
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(42)]
            ),
        ]
        
        if complexity == 'low':
            return random.choice(low_predicates)
        elif complexity == 'medium':
            return random.choice(low_predicates + medium_predicates)
        else:  # high
            return random.choice(low_predicates + medium_predicates + high_predicates)
    
    def _generate_opaque_false(self):
        """
        Generate an opaque predicate that always evaluates to False.
        Uses negations and contradictions.
        """
        complexity = self.opaque_complexity
        
        # Low complexity
        low_predicates = [
            # x != x is always false
            ast.Compare(
                left=ast.Name(id='len', ctx=ast.Load()),
                ops=[ast.IsNot()],
                comparators=[ast.Name(id='len', ctx=ast.Load())]
            ),
            # 1 == 0
            ast.Compare(
                left=ast.Constant(1),
                ops=[ast.Eq()],
                comparators=[ast.Constant(0)]
            ),
            # len("") != 0
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='len', ctx=ast.Load()),
                    args=[ast.Constant("")],
                    keywords=[]
                ),
                ops=[ast.NotEq()],
                comparators=[ast.Constant(0)]
            ),
            # bool(0) is True
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='bool', ctx=ast.Load()),
                    args=[ast.Constant(0)],
                    keywords=[]
                ),
                ops=[ast.Is()],
                comparators=[ast.Constant(True)]
            ),
        ]
        
        # Medium complexity
        medium_predicates = [
            # (x * 2) / 2 != x
            ast.Compare(
                left=ast.BinOp(
                    left=ast.BinOp(
                        left=ast.Constant(100),
                        op=ast.Mult(),
                        right=ast.Constant(2)
                    ),
                    op=ast.FloorDiv(),
                    right=ast.Constant(2)
                ),
                ops=[ast.NotEq()],
                comparators=[ast.Constant(100)]
            ),
            # x & (x+1) == 0 (only true for specific x)
            ast.Compare(
                left=ast.BinOp(
                    left=ast.Constant(100),
                    op=ast.BitAnd(),
                    right=ast.BinOp(
                        left=ast.Constant(100),
                        op=ast.Add(),
                        right=ast.Constant(1)
                    )
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(0)]
            ),
            # str(int("abc")) raises error, but str(123) != "456"
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='str', ctx=ast.Load()),
                    args=[ast.Call(
                        func=ast.Name(id='int', ctx=ast.Load()),
                        args=[ast.Constant(123)],
                        keywords=[]
                    )],
                    keywords=[]
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant("456")]
            ),
        ]
        
        # High complexity
        high_predicates = [
            # pow(x, 1) != x (always false)
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='pow', ctx=ast.Load()),
                    args=[ast.Constant(42), ast.Constant(1)],
                    keywords=[]
                ),
                ops=[ast.NotEq()],
                comparators=[ast.Constant(42)]
            ),
            # (x ^ y) ^ x != y
            ast.Compare(
                left=ast.BinOp(
                    left=ast.BinOp(
                        left=ast.Constant(0x12345678),
                        op=ast.BitXor(),
                        right=ast.Constant(0xABCDEF00)
                    ),
                    op=ast.BitXor(),
                    right=ast.Constant(0x12345678)
                ),
                ops=[ast.NotEq()],
                comparators=[ast.Constant(0xABCDEF00)]
            ),
            # sum([1,2,3]) != 6
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='sum', ctx=ast.Load()),
                    args=[ast.List(
                        elts=[ast.Constant(1), ast.Constant(2), ast.Constant(3)],
                        ctx=ast.Load()
                    )],
                    keywords=[]
                ),
                ops=[ast.NotEq()],
                comparators=[ast.Constant(6)]
            ),
            # all([True, False, True]) == True
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='all', ctx=ast.Load()),
                    args=[ast.List(
                        elts=[ast.Constant(True), ast.Constant(False), ast.Constant(True)],
                        ctx=ast.Load()
                    )],
                    keywords=[]
                ),
                ops=[ast.Is()],
                comparators=[ast.Constant(True)]
            ),
            # len([1,2,3]) == 5
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='len', ctx=ast.Load()),
                    args=[ast.List(
                        elts=[ast.Constant(1), ast.Constant(2), ast.Constant(3)],
                        ctx=ast.Load()
                    )],
                    keywords=[]
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(5)]
            ),
            # "abc" in "def"
            ast.Compare(
                left=ast.Constant("abc"),
                ops=[ast.In()],
                comparators=[ast.Constant("def")]
            ),
            # isinstance(42, str)
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='isinstance', ctx=ast.Load()),
                    args=[ast.Constant(42), ast.Name(id='str', ctx=ast.Load())],
                    keywords=[]
                ),
                ops=[ast.Is()],
                comparators=[ast.Constant(True)]
            ),
        ]
        
        if complexity == 'low':
            return random.choice(low_predicates)
        elif complexity == 'medium':
            return random.choice(low_predicates + medium_predicates)
        else:  # high
            return random.choice(low_predicates + medium_predicates + high_predicates)
    
    def _generate_complex_condition(self):
        """Generate a complex boolean combination of opaque predicates."""
        # Randomly combine multiple opaque predicates with AND/OR
        num_predicates = random.randint(2, 4)
        predicates = []
        
        for _ in range(num_predicates):
            if random.random() < 0.5:
                predicates.append(self._generate_opaque_true())
            else:
                predicates.append(self._generate_opaque_false())
        
        # Combine with boolean operators
        result = predicates[0]
        for pred in predicates[1:]:
            if random.random() < 0.5:
                result = ast.BoolOp(
                    op=ast.And(),
                    values=[result, pred]
                )
            else:
                result = ast.BoolOp(
                    op=ast.Or(),
                    values=[result, pred]
                )
        
        return result
    
    def _generate_junk_statement(self):
        """Generate a junk statement that does nothing meaningful."""
        junk_var = self._rand_name()
        junk_statements = [
            # Fake assignments with complex expressions
            ast.Assign(
                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                value=ast.BinOp(
                    left=ast.BinOp(
                        left=ast.Constant(random.randint(1, 100)),
                        op=ast.Mult(),
                        right=ast.Constant(random.randint(1, 100))
                    ),
                    op=ast.Add(),
                    right=ast.Constant(random.randint(1, 100))
                )
            ),
            # String operations
            ast.Assign(
                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                value=ast.BinOp(
                    left=ast.Constant("junk_"),
                    op=ast.Add(),
                    right=ast.Constant("string_" + str(random.randint(0, 999)))
                )
            ),
            # List operations
            ast.Assign(
                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                value=ast.ListComp(
                    elt=ast.Constant(random.randint(0, 10)),
                    generators=[ast.comprehension(
                        target=ast.Name(id='_', ctx=ast.Store()),
                        iter=ast.Call(
                            func=ast.Name(id='range', ctx=ast.Load()),
                            args=[ast.Constant(random.randint(1, 5))],
                            keywords=[]
                        ),
                        ifs=[],
                        is_async=0
                    )]
                )
            ),
            # Expression statements (no-op)
            ast.Expr(value=ast.Call(
                func=ast.Name(id='str', ctx=ast.Load()),
                args=[ast.Constant(random.randint(0, 10000))],
                keywords=[]
            )),
            # Dict comprehension
            ast.Assign(
                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                value=ast.DictComp(
                    key=ast.Name(id='x', ctx=ast.Load()),
                    value=ast.BinOp(
                        left=ast.Name(id='x', ctx=ast.Load()),
                        op=ast.Mult(),
                        right=ast.Constant(2)
                    ),
                    generators=[ast.comprehension(
                        target=ast.Name(id='x', ctx=ast.Store()),
                        iter=ast.Call(
                            func=ast.Name(id='range', ctx=ast.Load()),
                            args=[ast.Constant(random.randint(1, 5))],
                            keywords=[]
                        ),
                        ifs=[],
                        is_async=0
                    )]
                )
            ),
        ]
        return random.choice(junk_statements)
    
    def _generate_junk_block(self, num_statements=3):
        """Generate a block of junk statements."""
        return [self._generate_junk_statement() for _ in range(random.randint(2, num_statements))]
    
    def _generate_fake_if_branch(self, is_true_branch=True, use_complex=True):
        """
        Generate a fake if/elif branch with opaque predicates.
        
        Args:
            is_true_branch: If True, the condition always evaluates to True, else False
            use_complex: If True, use complex boolean combinations
        """
        if use_complex and random.random() < 0.7:
            test = self._generate_complex_condition()
        elif is_true_branch:
            test = self._generate_opaque_true()
        else:
            test = self._generate_opaque_false()
        
        junk_block = self._generate_junk_block()
        
        return ast.If(
            test=test,
            body=junk_block,
            orelse=[]
        )
    
    def visit_FunctionDef(self, node):
        """Add junk code to function definitions."""
        # Randomly decide whether to add junk to this function
        if random.random() > self.junk_density:
            return self.generic_visit(node)

        print(f"[JUNK_CODE] Adding junk code to function: {node.name}")

        new_body = []

        for stmt in node.body:
            # Add fake if branches before the statement
            if random.random() < 0.5:  # 50% chance
                fake_branch = self._generate_fake_if_branch(is_true_branch=True)
                new_body.append(fake_branch)

            # Add elif chain sometimes
            if random.random() < 0.3:  # 30% chance
                elif_branch = self._generate_fake_if_branch(is_true_branch=False)
                # Create if-elif chain
                main_if = self._generate_fake_if_branch(is_true_branch=True)
                main_if.orelse = [elif_branch]
                new_body.append(main_if)

            # Add the original statement
            new_body.append(stmt)

            # Add fake if branches after the statement
            if random.random() < 0.3:  # 30% chance
                fake_branch = self._generate_fake_if_branch(is_true_branch=False)
                new_body.append(fake_branch)

        # Sometimes add junk at the end
        if random.random() < 0.4:
            new_body.append(self._generate_fake_if_branch(is_true_branch=True))

        node.body = new_body
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Add junk code to async function definitions with async-compatible junk."""
        # Randomly decide whether to add junk to this function
        if random.random() > self.junk_density:
            return self.generic_visit(node)

        print(f"[JUNK_CODE] Adding junk code to async function: {node.name}")

        new_body = []

        for stmt in node.body:
            # Add fake if branches before the statement
            if random.random() < 0.5:  # 50% chance
                fake_branch = self._generate_fake_if_branch(is_true_branch=True)
                new_body.append(fake_branch)

            # Add elif chain sometimes
            if random.random() < 0.3:  # 30% chance
                elif_branch = self._generate_fake_if_branch(is_true_branch=False)
                # Create if-elif chain
                main_if = self._generate_fake_if_branch(is_true_branch=True)
                main_if.orelse = [elif_branch]
                new_body.append(main_if)

            # Add the original statement
            new_body.append(stmt)

            # Add fake if branches after the statement
            if random.random() < 0.3:  # 30% chance
                fake_branch = self._generate_fake_if_branch(is_true_branch=False)
                new_body.append(fake_branch)

        # Sometimes add junk at the end
        if random.random() < 0.4:
            new_body.append(self._generate_fake_if_branch(is_true_branch=True))

        node.body = new_body
        return self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Process class definitions - apply junk code to methods."""
        print(f"[JUNK_CODE] Processing class: {node.name}")
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
    
    def apply_transformation(self, code):
        """
        Apply junk code transformation to Python code.
        
        Args:
            code: Python source code as string
            
        Returns:
            Transformed code with junk if/elif branches
        """
        try:
            print(f"[JUNK_CODE] Starting transformation...")
            tree = ast.parse(code)
            transformed_tree = self.visit(tree)
            ast.fix_missing_locations(transformed_tree)
            result = ast.unparse(transformed_tree)
            print(f"[JUNK_CODE] Transformation complete. Code changed: {result != code}")
            return result
        except Exception as e:
            print(f"Junk code transformation failed: {e}")
            return code
