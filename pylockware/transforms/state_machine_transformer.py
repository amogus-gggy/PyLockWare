"""
State Machine Transformer for PyLockWare
Transforms functions into state machines to obfuscate control flow
Enhanced with async/await support
"""
import ast
import random
import string
from pylockware.core.name_generator import generate_random_name


class StateMachineTransformer(ast.NodeTransformer):
    def __init__(self, name_gen_settings='english', add_junk_states=True):
        self.func_counter = 0
        self.state_var = None
        self.final_state = None
        self.name_gen_settings = name_gen_settings
        self.add_junk_states = add_junk_states
        self.junk_states = []
        self.block_to_state_map = {}
        self.state_to_block_map = {}

    # -----------------------------
    # Utility
    # -----------------------------

    def _rand(self, prefix="_s"):
        if prefix:
            return generate_random_name(prefix + "_", self.name_gen_settings)
        else:
            return generate_random_name("_", self.name_gen_settings)

    def _contains_async(self, node):
        return any(isinstance(n, ast.AsyncFunctionDef) for n in ast.walk(node))

    def _has_await(self, node):
        """Check if node contains await expressions"""
        return any(isinstance(n, ast.Await) for n in ast.walk(node))

    # -----------------------------
    # Junk State Generation
    # -----------------------------

    def _generate_junk_states(self, num_junk_states=3):
        """Generate fake states with junk code that never executes."""
        if not self.add_junk_states:
            return []

        junk_cases = []
        used_states = set(self.block_to_state_map.values())
        if self.final_state:
            used_states.add(self.final_state)

        for i in range(num_junk_states):
            while True:
                junk_state = random.randint(1000, 999999)
                if junk_state not in used_states:
                    used_states.add(junk_state)
                    self.junk_states.append(junk_state)
                    break

            junk_block = self._generate_junk_code_block()

            junk_case = ast.If(
                test=ast.Compare(
                    left=ast.Name(id=self.state_var, ctx=ast.Load()),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(junk_state)],
                ),
                body=junk_block,
                orelse=[]
            )
            junk_cases.append(junk_case)

        return junk_cases

    def _generate_junk_code_block(self):
        """Generate a block of junk code for fake states with opaque predicates."""
        junk_var = self._rand("")

        # Opaque predicates that always evaluate to True
        opaque_true_predicates = [
            ast.Compare(
                left=ast.Name(id='len', ctx=ast.Load()),
                ops=[ast.Is()],
                comparators=[ast.Name(id='len', ctx=ast.Load())]
            ),
            ast.Compare(
                left=ast.BinOp(
                    left=ast.Constant(42),
                    op=ast.Sub(),
                    right=ast.Constant(42)
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(0)]
            ),
            ast.Compare(
                left=ast.BinOp(
                    left=ast.Constant(1337),
                    op=ast.BitOr(),
                    right=ast.Constant(0)
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(1337)]
            ),
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
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='pow', ctx=ast.Load()),
                    args=[ast.Constant(7), ast.Constant(0)],
                    keywords=[]
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(1)]
            ),
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
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='abs', ctx=ast.Load()),
                    args=[ast.UnaryOp(op=ast.USub(), operand=ast.Constant(42))],
                    keywords=[]
                ),
                ops=[ast.Eq()],
                comparators=[ast.Constant(42)]
            ),
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
        ]

        # Opaque predicates that always evaluate to False
        opaque_false_predicates = [
            ast.Compare(
                left=ast.Name(id='len', ctx=ast.Load()),
                ops=[ast.IsNot()],
                comparators=[ast.Name(id='len', ctx=ast.Load())]
            ),
            ast.Compare(
                left=ast.Constant(1),
                ops=[ast.Eq()],
                comparators=[ast.Constant(0)]
            ),
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
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='pow', ctx=ast.Load()),
                    args=[ast.Constant(42), ast.Constant(1)],
                    keywords=[]
                ),
                ops=[ast.NotEq()],
                comparators=[ast.Constant(42)]
            ),
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
            ast.Compare(
                left=ast.Constant("abc"),
                ops=[ast.In()],
                comparators=[ast.Constant("def")]
            ),
            ast.Compare(
                left=ast.Call(
                    func=ast.Name(id='isinstance', ctx=ast.Load()),
                    args=[ast.Constant(42), ast.Name(id='str', ctx=ast.Load())],
                    keywords=[]
                ),
                ops=[ast.Is()],
                comparators=[ast.Constant(True)]
            ),
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
        ]

        junk_statements = [
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
            ast.Assign(
                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                value=ast.BinOp(
                    left=ast.Constant("junk_"),
                    op=ast.Add(),
                    right=ast.Constant("string_" + str(random.randint(0, 999)))
                )
            ),
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
            ast.If(
                test=random.choice(opaque_true_predicates),
                body=[
                    ast.Assign(
                        targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                        value=ast.Constant(random.randint(1000, 9999))
                    )
                ],
                orelse=[]
            ),
            ast.If(
                test=random.choice(opaque_false_predicates),
                body=[
                    ast.Assign(
                        targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                        value=ast.Constant(9999)
                    )
                ],
                orelse=[]
            ),
            ast.If(
                test=random.choice(opaque_true_predicates),
                body=[
                    ast.If(
                        test=random.choice(opaque_false_predicates),
                        body=[
                            ast.Assign(
                                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                                value=ast.Constant(0)
                            )
                        ],
                        orelse=[]
                    )
                ],
                orelse=[]
            ),
            ast.Expr(value=ast.Call(
                func=ast.Name(id='str', ctx=ast.Load()),
                args=[ast.Constant(random.randint(0, 10000))],
                keywords=[]
            )),
            ast.Assign(
                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                value=ast.BoolOp(
                    op=ast.And(),
                    values=[
                        random.choice(opaque_true_predicates),
                        random.choice(opaque_true_predicates)
                    ]
                )
            ),
            ast.Assign(
                targets=[ast.Name(id=junk_var, ctx=ast.Store())],
                value=ast.BoolOp(
                    op=ast.Or(),
                    values=[
                        random.choice(opaque_false_predicates),
                        random.choice(opaque_false_predicates)
                    ]
                )
            ),
        ]
        num_statements = random.randint(3, 6)
        return random.sample(junk_statements, min(num_statements, len(junk_statements)))

    # -----------------------------
    # Core
    # -----------------------------

    def visit_ClassDef(self, node):
        """Process class - obfuscate all methods inside"""
        print(f"[STATE_MACHINE] Processing class: {node.name}")
        new_body = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                new_body.append(self.visit(item))
            elif isinstance(item, ast.ClassDef):
                new_body.append(self.visit(item))
            else:
                new_body.append(self.generic_visit(item))
        node.body = new_body
        return node

    def visit_AsyncFunctionDef(self, node):
        """Transform async functions into async state machines with proper await support."""
        self.func_counter += 1
        old_state = self.state_var
        old_block_to_state_map = self.block_to_state_map
        old_state_to_block_map = self.state_to_block_map
        old_final_state = self.final_state
        
        self.state_var = self._rand("")
        ret_var = self._rand("")

        is_generator = any(isinstance(n, (ast.Yield, ast.YieldFrom)) for n in ast.walk(node))
        has_await = self._has_await(node)

        # NEVER transform async generators - they must keep yield
        if is_generator:
            print(f"[STATE_MACHINE] Skipping async generator function: {node.name}")
            self.state_var = old_state
            self.block_to_state_map = old_block_to_state_map
            self.state_to_block_map = old_state_to_block_map
            self.final_state = old_final_state
            return self.generic_visit(node)

        # Hoist global/nonlocal declarations - they must appear before any use
        hoisted_stmts = [s for s in node.body if isinstance(s, (ast.Global, ast.Nonlocal))]
        body_without_hoisted = [s for s in node.body if not isinstance(s, (ast.Global, ast.Nonlocal))]

        # Split body into blocks (without global/nonlocal)
        blocks = self._split_into_blocks(body_without_hoisted)

        # Check if we can expand a single loop body
        expanded_blocks, loop_stmt = self._expand_single_loop_body(blocks)
        is_expanded_loop = loop_stmt is not None

        if is_expanded_loop:
            print(f"[STATE_MACHINE] Async function '{node.name}': expanding single loop body ({len(loop_stmt.body)} statements) into {len(expanded_blocks)} blocks")
            blocks = expanded_blocks

        print(f"[STATE_MACHINE] Async function '{node.name}': {len(node.body)} statements, split into {len(blocks)} blocks")

        if len(blocks) <= 1 and not is_generator:
            print(f"[STATE_MACHINE] Skipping async function '{node.name}': only {len(blocks)} block(s) and not a generator")
            self.state_var = old_state
            return self.generic_visit(node)

        # Generate random state values for each block
        unique_states = set()
        state_values = []

        for i in range(len(blocks)):
            while True:
                rand_state = random.randint(1000, 999999)
                if rand_state not in unique_states:
                    unique_states.add(rand_state)
                    state_values.append(rand_state)
                    break

        self.block_to_state_map = dict(zip(range(len(blocks)), state_values))
        self.state_to_block_map = dict(zip(state_values, range(len(blocks))))

        print(f"[STATE_MACHINE] Async function '{node.name}': state values: {state_values}")
        while True:
            final_rand_state = random.randint(1000, 999999)
            if final_rand_state not in unique_states:
                self.final_state = final_rand_state
                break

        # -----------------------------
        # Generate async state machine
        # -----------------------------

        new_body = []

        # Hoist global/nonlocal declarations first
        new_body.extend(hoisted_stmts)

        # __state = initial state (first block)
        initial_state = self.block_to_state_map[0]
        new_body.append(
            ast.Assign(
                targets=[ast.Name(id=self.state_var, ctx=ast.Store())],
                value=ast.Constant(initial_state),
            )
        )

        # __ret = None
        if not is_generator:
            new_body.append(
                ast.Assign(
                    targets=[ast.Name(id=ret_var, ctx=ast.Store())],
                    value=ast.Constant(None),
                )
            )

        cases = []

        # Generate branches for each block with random states
        block_indices = list(range(len(blocks)))
        random.shuffle(block_indices)

        for idx in block_indices:
            state = self.block_to_state_map[idx]
            block = blocks[idx]
            case_body = self._process_block(block, idx, len(blocks), ret_var, is_generator, state, is_expanded_loop, is_async=True)

            cases.append(
                ast.If(
                    test=ast.Compare(
                        left=ast.Name(id=self.state_var, ctx=ast.Load()),
                        ops=[ast.Eq()],
                        comparators=[ast.Constant(state)],
                    ),
                    body=case_body,
                    orelse=[],
                )
            )

        # Add junk states for obfuscation
        if self.add_junk_states:
            junk_cases = self._generate_junk_states(num_junk_states=random.randint(2, 5))
            cases.extend(junk_cases)
            print(f"[STATE_MACHINE] Async function '{node.name}': added {len(junk_cases)} junk states")

        print(f"[STATE_MACHINE] Async function '{node.name}': IF statements order shuffled: {block_indices}")

        # Use regular while loop - await expressions inside will work fine
        if is_expanded_loop:
            loop = ast.While(
                test=ast.Constant(value=True),
                body=cases,
                orelse=[],
            )
        else:
            loop = ast.While(
                test=ast.Compare(
                    left=ast.Name(id=self.state_var, ctx=ast.Load()),
                    ops=[ast.NotEq()],
                    comparators=[ast.Constant(self.final_state)],
                ),
                body=cases,
                orelse=[],
            )

        new_body.append(loop)

        # return
        if not is_expanded_loop:
            if is_generator:
                new_body.append(ast.Return(value=None))
            else:
                new_body.append(ast.Return(value=ast.Name(id=ret_var, ctx=ast.Load())))

        node.body = new_body
        self.state_var = old_state
        self.block_to_state_map = old_block_to_state_map
        self.state_to_block_map = old_state_to_block_map
        self.final_state = old_final_state
        return node

    def visit_FunctionDef(self, node):
        # Check for @skip_obf decorator
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'skip_obf':
                print(f"[STATE_MACHINE] Skipping function (has @skip_obf): {node.name}")
                return self.generic_visit(node)
            elif isinstance(decorator, ast.Attribute) and decorator.attr == 'skip_obf':
                print(f"[STATE_MACHINE] Skipping function (has @skip_obf): {node.name}")
                return self.generic_visit(node)
        
        # Skip functions that contain async - they're handled by visit_AsyncFunctionDef
        if self._contains_async(node):
            print(f"[STATE_MACHINE] Skipping function (contains async): {node.name}")
            return self.generic_visit(node)

        # Minimum size check
        if len(node.body) < 1:
            print(f"[STATE_MACHINE] Skipping function (empty body): {node.name}")
            return self.generic_visit(node)

        self.func_counter += 1
        old_state = self.state_var
        old_block_to_state_map = self.block_to_state_map
        old_state_to_block_map = self.state_to_block_map
        old_final_state = self.final_state
        self.state_var = self._rand("")
        ret_var = self._rand("")

        is_generator = any(isinstance(n, (ast.Yield, ast.YieldFrom)) for n in ast.walk(node))

        # Hoist global/nonlocal declarations - they must appear before any use
        hoisted_stmts = [s for s in node.body if isinstance(s, (ast.Global, ast.Nonlocal))]
        body_without_hoisted = [s for s in node.body if not isinstance(s, (ast.Global, ast.Nonlocal))]

        # Split body into blocks (without global/nonlocal)
        blocks = self._split_into_blocks(body_without_hoisted)

        # Check if we can expand a single loop body
        expanded_blocks, loop_stmt = self._expand_single_loop_body(blocks)
        is_expanded_loop = loop_stmt is not None

        if is_expanded_loop:
            print(f"[STATE_MACHINE] Function '{node.name}': expanding single loop body ({len(loop_stmt.body)} statements) into {len(expanded_blocks)} blocks")
            blocks = expanded_blocks

        print(f"[STATE_MACHINE] Function '{node.name}': {len(node.body)} statements, split into {len(blocks)} blocks")

        if len(blocks) <= 1 and not is_generator:
            print(f"[STATE_MACHINE] Skipping function '{node.name}': only {len(blocks)} block(s) and not a generator")
            self.state_var = old_state
            return self.generic_visit(node)

        # Generate random state values for each block
        unique_states = set()
        state_values = []

        for i in range(len(blocks)):
            while True:
                rand_state = random.randint(1000, 999999)
                if rand_state not in unique_states:
                    unique_states.add(rand_state)
                    state_values.append(rand_state)
                    break

        self.block_to_state_map = dict(zip(range(len(blocks)), state_values))
        self.state_to_block_map = dict(zip(state_values, range(len(blocks))))

        print(f"[STATE_MACHINE] Function '{node.name}': state values: {state_values}")
        while True:
            final_rand_state = random.randint(1000, 999999)
            if final_rand_state not in unique_states:
                self.final_state = final_rand_state
                break

        # -----------------------------
        # Generate state machine
        # -----------------------------

        new_body = []

        # Hoist global/nonlocal declarations first
        new_body.extend(hoisted_stmts)

        # __state = initial state (first block)
        initial_state = self.block_to_state_map[0]
        new_body.append(
            ast.Assign(
                targets=[ast.Name(id=self.state_var, ctx=ast.Store())],
                value=ast.Constant(initial_state),
            )
        )

        # __ret = None
        if not is_generator:
            new_body.append(
                ast.Assign(
                    targets=[ast.Name(id=ret_var, ctx=ast.Store())],
                    value=ast.Constant(None),
                )
            )

        cases = []

        # Generate branches for each block with random states
        block_indices = list(range(len(blocks)))
        random.shuffle(block_indices)

        for idx in block_indices:
            state = self.block_to_state_map[idx]
            block = blocks[idx]
            case_body = self._process_block(block, idx, len(blocks), ret_var, is_generator, state, is_expanded_loop)

            cases.append(
                ast.If(
                    test=ast.Compare(
                        left=ast.Name(id=self.state_var, ctx=ast.Load()),
                        ops=[ast.Eq()],
                        comparators=[ast.Constant(state)],
                    ),
                    body=case_body,
                    orelse=[],
                )
            )

        # Add junk states for obfuscation
        if self.add_junk_states:
            junk_cases = self._generate_junk_states(num_junk_states=random.randint(2, 5))
            cases.extend(junk_cases)
            print(f"[STATE_MACHINE] Function '{node.name}': added {len(junk_cases)} junk states")

        print(f"[STATE_MACHINE] Function '{node.name}': IF statements order shuffled: {block_indices}")

        # while state != FINAL (or while True for expanded loop)
        if is_expanded_loop:
            loop = ast.While(
                test=ast.Constant(value=True),
                body=cases,
                orelse=[],
            )
        else:
            loop = ast.While(
                test=ast.Compare(
                    left=ast.Name(id=self.state_var, ctx=ast.Load()),
                    ops=[ast.NotEq()],
                    comparators=[ast.Constant(self.final_state)],
                ),
                body=cases,
                orelse=[],
            )

        new_body.append(loop)

        # return (only for non-expanded loops)
        if is_expanded_loop:
            pass
        elif is_generator:
            new_body.append(ast.Return(value=None))
        else:
            new_body.append(ast.Return(value=ast.Name(id=ret_var, ctx=ast.Load())))

        node.body = new_body
        self.state_var = old_state
        self.block_to_state_map = old_block_to_state_map
        self.state_to_block_map = old_state_to_block_map
        self.final_state = old_final_state
        return node

    def _split_into_blocks(self, body):
        """Aggressive splitting into blocks"""
        blocks = []
        current_block = []

        for stmt in body:
            if isinstance(stmt, (ast.For, ast.While, ast.Try, ast.With, ast.Match,
                                 ast.If, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if current_block:
                    blocks.append(current_block)
                    current_block = []
                blocks.append([stmt])
            elif isinstance(stmt, ast.Return):
                if current_block:
                    blocks.append(current_block)
                    current_block = []
                blocks.append([stmt])
            elif len(current_block) >= 2:
                blocks.append(current_block)
                current_block = [stmt]
            else:
                current_block.append(stmt)

        if current_block:
            blocks.append(current_block)

        return blocks

    def _expand_single_loop_body(self, blocks):
        """
        If function consists of only one loop, expand its body
        for state machine transformation
        """
        if len(blocks) == 1:
            stmt = blocks[0][0]
            if isinstance(stmt, (ast.While, ast.For)) and len(stmt.body) > 1:
                expanded_blocks = self._split_into_blocks(stmt.body)
                print(f"[STATE_MACHINE] Expanded loop body into {len(expanded_blocks)} blocks")
                return expanded_blocks, stmt
        return blocks, None

    def _process_block(self, block, idx, total_blocks, ret_var, is_generator, state=None, is_expanded_loop=False, is_async=False):
        """Process a block with support for async/await"""
        case_body = []

        for stmt in block:
            if isinstance(stmt, ast.Return):
                # NEVER use yield for async functions - it turns them into async generators!
                # Always use ret_var assignment for async functions
                if is_generator and not is_async:
                    if stmt.value:
                        case_body.append(ast.Expr(value=ast.Yield(value=stmt.value)))
                    case_body.append(ast.Return(value=None))
                else:
                    case_body.append(
                        ast.Assign(
                            targets=[ast.Name(id=ret_var, ctx=ast.Store())],
                            value=stmt.value if stmt.value else ast.Constant(None),
                        )
                    )
                    if is_expanded_loop:
                        first_state = self.block_to_state_map[0]
                        case_body.append(
                            ast.Assign(
                                targets=[ast.Name(id=self.state_var, ctx=ast.Store())],
                                value=ast.Constant(first_state),
                            )
                        )
                    else:
                        case_body.append(
                            ast.Assign(
                                targets=[ast.Name(id=self.state_var, ctx=ast.Store())],
                                value=ast.Constant(self.final_state),
                            )
                        )

            elif isinstance(stmt, (ast.For, ast.While)):
                case_body.extend(self._process_loop(stmt, idx, total_blocks, is_expanded_loop))

            elif isinstance(stmt, ast.AsyncFor):
                case_body.extend(self._process_async_for(stmt, idx, total_blocks, is_expanded_loop))

            elif isinstance(stmt, ast.AsyncWith):
                case_body.extend(self._process_async_with(stmt, idx, total_blocks, is_expanded_loop))

            elif isinstance(stmt, ast.Try):
                case_body.extend(self._process_try(stmt, idx, total_blocks, is_expanded_loop))

            elif isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                case_body.append(self.visit(stmt))

            else:
                case_body.append(stmt)

        # transition to next state (only if no other transitions in the body)
        has_explicit_transition = any(
            isinstance(s, ast.Assign) and
            isinstance(s.targets[0], ast.Name) and
            s.targets[0].id == self.state_var
            for s in case_body
        )

        if not has_explicit_transition:
            # Find the next block index
            next_block_idx = idx + 1
            if next_block_idx < total_blocks and next_block_idx in self.block_to_state_map:
                # Get the state value for the next block
                next_state = self.block_to_state_map[next_block_idx]
                case_body.append(
                    ast.Assign(
                        targets=[ast.Name(id=self.state_var, ctx=ast.Store())],
                        value=ast.Constant(next_state),
                    )
                )
            else:
                # No next block or not in state map - go to final state or loop back
                if is_expanded_loop:
                    first_state = self.block_to_state_map.get(0, self.final_state)
                    case_body.append(
                        ast.Assign(
                            targets=[ast.Name(id=self.state_var, ctx=ast.Store())],
                            value=ast.Constant(first_state),
                        )
                    )
                else:
                    case_body.append(
                        ast.Assign(
                            targets=[ast.Name(id=self.state_var, ctx=ast.Store())],
                            value=ast.Constant(self.final_state),
                        )
                    )

        return case_body

    def _process_loop(self, loop_node, current_idx, total_blocks, is_expanded_loop=False):
        """Process loop"""
        body = [loop_node]
        next_idx = current_idx + 1
        if next_idx < total_blocks:
            next_state = self.block_to_state_map[next_idx]
            state_value = ast.Constant(next_state)
        elif is_expanded_loop:
            first_state = self.block_to_state_map[0]
            state_value = ast.Constant(first_state)
        else:
            state_value = ast.Constant(self.final_state)

        body.append(
            ast.Assign(
                targets=[ast.Name(id=self.state_var, ctx=ast.Store())],
                value=state_value,
            )
        )
        return body

    def _process_async_for(self, async_for_node, current_idx, total_blocks, is_expanded_loop=False):
        """Process async for loop"""
        body = [async_for_node]
        next_idx = current_idx + 1
        if next_idx < total_blocks:
            next_state = self.block_to_state_map[next_idx]
            state_value = ast.Constant(next_state)
        elif is_expanded_loop:
            first_state = self.block_to_state_map[0]
            state_value = ast.Constant(first_state)
        else:
            state_value = ast.Constant(self.final_state)

        body.append(
            ast.Assign(
                targets=[ast.Name(id=self.state_var, ctx=ast.Store())],
                value=state_value,
            )
        )
        return body

    def _process_async_with(self, async_with_node, current_idx, total_blocks, is_expanded_loop=False):
        """Process async with statement"""
        body = [async_with_node]
        next_idx = current_idx + 1
        if next_idx < total_blocks:
            next_state = self.block_to_state_map[next_idx]
            state_value = ast.Constant(next_state)
        elif is_expanded_loop:
            first_state = self.block_to_state_map[0]
            state_value = ast.Constant(first_state)
        else:
            state_value = ast.Constant(self.final_state)

        body.append(
            ast.Assign(
                targets=[ast.Name(id=self.state_var, ctx=ast.Store())],
                value=state_value,
            )
        )
        return body

    def _process_try(self, try_node, current_idx, total_blocks, is_expanded_loop=False):
        """Process try-except"""
        next_idx = current_idx + 1
        body = [try_node]
        if next_idx < total_blocks:
            next_state = self.block_to_state_map[next_idx]
            state_value = ast.Constant(next_state)
        elif is_expanded_loop:
            first_state = self.block_to_state_map[0]
            state_value = ast.Constant(first_state)
        else:
            state_value = ast.Constant(self.final_state)

        body.append(
            ast.Assign(
                targets=[ast.Name(id=self.state_var, ctx=ast.Store())],
                value=state_value,
            )
        )
        return body

    def apply_transformation(self, code):
        """Apply state machine transformation to Python code."""
        try:
            print(f"[STATE_MACHINE] Starting transformation...")
            tree = ast.parse(code)
            transformed_tree = self.visit(tree)
            ast.fix_missing_locations(transformed_tree)
            result = ast.unparse(transformed_tree)
            print(f"[STATE_MACHINE] Transformation complete. Code changed: {result != code}")
            return result
        except Exception as e:
            print(f"State machine transformation failed: {e}")
            import traceback
            traceback.print_exc()
            return code
