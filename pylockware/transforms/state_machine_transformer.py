"""
State Machine Transformer for PyLockWare
Transforms functions into state machines to obfuscate control flow.
State comparisons and assignments are obfuscated with bitwise operations.
"""
import ast
import random
from pylockware.core.name_generator import generate_random_name


# ---------------------------------------------------------------------------
# AST helpers
# ---------------------------------------------------------------------------

def _c(v):
    return ast.Constant(v)


def _n(name):
    return ast.Name(id=name, ctx=ast.Load())


def _ns(name):
    return ast.Name(id=name, ctx=ast.Store())


def _binop(l, op, r):
    return ast.BinOp(left=l, op=op, right=r)


def _cmp(l, op, r):
    return ast.Compare(left=l, ops=[op], comparators=[r])


def _unary(op, operand):
    return ast.UnaryOp(op=op, operand=operand)


def _assign(target_name, value):
    return ast.Assign(targets=[_ns(target_name)], value=value)


def _call(name, *args):
    return ast.Call(func=_n(name), args=list(args), keywords=[])


# ---------------------------------------------------------------------------
# Bitwise opaque predicate pools (always True / always False, bitwise only)
# ---------------------------------------------------------------------------

def _bitwise_true_predicates():
    a = random.randint(1, 0xFFFF)
    b = random.randint(1, 0xFFFF)
    k = random.randint(1, 7)
    mask = random.randint(1, 0xFFFFFF)
    return [
        # (a ^ a) == 0
        _cmp(_binop(_c(a), ast.BitXor(), _c(a)), ast.Eq(), _c(0)),
        # (a & a) == a
        _cmp(_binop(_c(a), ast.BitAnd(), _c(a)), ast.Eq(), _c(a)),
        # ~(~a) == a
        _cmp(_unary(ast.Invert(), _unary(ast.Invert(), _c(a))), ast.Eq(), _c(a)),
        # (a << k) >> k == a
        _cmp(
            _binop(_binop(_c(a), ast.LShift(), _c(k)), ast.RShift(), _c(k)),
            ast.Eq(), _c(a)
        ),
        # ((a ^ b) ^ b) == a
        _cmp(
            _binop(_binop(_c(a), ast.BitXor(), _c(b)), ast.BitXor(), _c(b)),
            ast.Eq(), _c(a)
        ),
        # (a & ~0) == a   (~0 == -1)
        _cmp(_binop(_c(a), ast.BitAnd(), _unary(ast.Invert(), _c(0))), ast.Eq(), _c(a)),
        # (mask | ~mask) == -1
        _cmp(
            _binop(_c(mask), ast.BitOr(), _unary(ast.Invert(), _c(mask))),
            ast.Eq(), _c(-1)
        ),
        # bool(a & a)  is  True
        _cmp(_call('bool', _binop(_c(a), ast.BitAnd(), _c(a))), ast.Is(), _c(True)),
        # ~(-1) == 0
        _cmp(_unary(ast.Invert(), _c(-1)), ast.Eq(), _c(0)),
    ]


def _bitwise_false_predicates():
    a = random.randint(2, 0xFFFF)
    b = random.randint(1, 0xFFFF)
    k = random.randint(1, 7)
    return [
        # (~a & a) != 0  → always 0, so False
        _cmp(_binop(_unary(ast.Invert(), _c(a)), ast.BitAnd(), _c(a)), ast.NotEq(), _c(0)),
        # (a & 0) != 0
        _cmp(_binop(_c(a), ast.BitAnd(), _c(0)), ast.NotEq(), _c(0)),
        # (a ^ a) != 0
        _cmp(_binop(_c(a), ast.BitXor(), _c(a)), ast.NotEq(), _c(0)),
        # (a << k) == a   (k>=1)
        _cmp(_binop(_c(a), ast.LShift(), _c(k)), ast.Eq(), _c(a)),
        # ~(~0) != 0  → 0 != 0 → False
        _cmp(_unary(ast.Invert(), _unary(ast.Invert(), _c(0))), ast.NotEq(), _c(0)),
        # ((a ^ b) ^ b) != a  → always equal, so False
        _cmp(
            _binop(_binop(_c(a), ast.BitXor(), _c(b)), ast.BitXor(), _c(b)),
            ast.NotEq(), _c(a)
        ),
        # ~(~a) != a  → always equal
        _cmp(_unary(ast.Invert(), _unary(ast.Invert(), _c(a))), ast.NotEq(), _c(a)),
        # bool(a & 0)  is True  → False
        _cmp(_call('bool', _binop(_c(a), ast.BitAnd(), _c(0))), ast.Is(), _c(True)),
    ]


def _rand_true():
    return random.choice(_bitwise_true_predicates())


def _rand_false():
    return random.choice(_bitwise_false_predicates())


# ---------------------------------------------------------------------------
# Obfuscated state comparison / assignment builders
# ---------------------------------------------------------------------------

def _make_state_cmp(state_var, state_val):
    """
    Generate obfuscated comparison `state_var == state_val`.
    Picks one of several bitwise-equivalent forms, then adds an opaque AND.
    """
    mask = random.randint(1, 0xFFFF)
    k = random.randint(1, 6)

    style = random.randint(0, 4)
    if style == 0:
        # (state ^ mask) == (state_val ^ mask)
        core = _cmp(
            _binop(_n(state_var), ast.BitXor(), _c(mask)),
            ast.Eq(),
            _c(state_val ^ mask)
        )
    elif style == 1:
        # (state - state_val) == 0
        core = _cmp(
            _binop(_n(state_var), ast.Sub(), _c(state_val)),
            ast.Eq(), _c(0)
        )
    elif style == 2:
        # (state | 0) == state_val
        core = _cmp(_binop(_n(state_var), ast.BitOr(), _c(0)), ast.Eq(), _c(state_val))
    elif style == 3:
        # (state & ~0) == state_val
        core = _cmp(
            _binop(_n(state_var), ast.BitAnd(), _unary(ast.Invert(), _c(0))),
            ast.Eq(), _c(state_val)
        )
    else:
        # bool(state ^ state_val) == False  (XOR == 0 when equal)
        core = _cmp(
            _call('bool', _binop(_n(state_var), ast.BitXor(), _c(state_val))),
            ast.Eq(), _c(False)
        )

    # Combine with a True opaque predicate via `and`
    return ast.BoolOp(op=ast.And(), values=[core, _rand_true()])


def _make_state_neq_cmp(state_var, state_val):
    """
    Generate obfuscated comparison `state_var != state_val` for while-loop.
    """
    mask = random.randint(1, 0xFFFF)
    style = random.randint(0, 3)

    if style == 0:
        # (state ^ mask) != (state_val ^ mask)
        return _cmp(
            _binop(_n(state_var), ast.BitXor(), _c(mask)),
            ast.NotEq(),
            _c(state_val ^ mask)
        )
    elif style == 1:
        # (state - state_val) != 0
        return _cmp(
            _binop(_n(state_var), ast.Sub(), _c(state_val)),
            ast.NotEq(), _c(0)
        )
    elif style == 2:
        # bool(state ^ state_val)  (truthy when not equal)
        return _call('bool', _binop(_n(state_var), ast.BitXor(), _c(state_val)))
    else:
        # (state | 0) != state_val
        return _cmp(_binop(_n(state_var), ast.BitOr(), _c(0)), ast.NotEq(), _c(state_val))


def _make_state_assign(state_var, state_val, initial=False):
    """
    Generate obfuscated state mutation `state_var → state_val`.
    Returns a LIST of statements so callers must use extend().
    Uses augmented assignments and multi-step mutations so the target
    value is never written explicitly in a single plain assignment.

    initial=True: variable is not yet defined, use only write-only forms.
    """
    # Styles that read the variable (require it already exists):
    #   0 (state ^= state ^ K), 1 (state += K - state), 2 (state -= state - K),
    #   3 (state ^= state; state |= K), 4 (state = (state & 0) | K),
    #   5 (state ^= state; ...), 6 (state = (state ^ state) | K)
    # Safe for initial (write-only):
    #   7 = K ^ mask ^ mask, 8 = K | 0, 9 = K & ~0, 10 = (K<<k)>>k
    if initial:
        style = random.randint(7, 10)
    else:
        style = random.randint(0, 6)

    sn = _n(state_var)  # load
    ss = _ns(state_var)  # store

    if style == 0:
        # state ^= state ^ K   →   state = 0 ^ K = K
        return [ast.AugAssign(
            target=ast.Name(id=state_var, ctx=ast.Store()),
            op=ast.BitXor(),
            value=_binop(sn, ast.BitXor(), _c(state_val))
        )]

    elif style == 1:
        # state += K - state   →   state = K
        return [ast.AugAssign(
            target=ast.Name(id=state_var, ctx=ast.Store()),
            op=ast.Add(),
            value=_binop(_c(state_val), ast.Sub(), sn)
        )]

    elif style == 2:
        # state -= state - K   →   state = K
        return [ast.AugAssign(
            target=ast.Name(id=state_var, ctx=ast.Store()),
            op=ast.Sub(),
            value=_binop(sn, ast.Sub(), _c(state_val))
        )]

    elif style == 3:
        # two-step: state ^= state  (→0)  then  state |= K
        return [
            ast.AugAssign(
                target=ast.Name(id=state_var, ctx=ast.Store()),
                op=ast.BitXor(),
                value=sn
            ),
            ast.AugAssign(
                target=ast.Name(id=state_var, ctx=ast.Store()),
                op=ast.BitOr(),
                value=_c(state_val)
            ),
        ]

    elif style == 4:
        # state = (state & 0) | K   — AND clears, OR sets
        return [_assign(state_var,
            _binop(_binop(sn, ast.BitAnd(), _c(0)), ast.BitOr(), _c(state_val))
        )]

    elif style == 5:
        # three-step with mask:
        #   state ^= state          (→ 0)
        #   state ^= (K ^ mask)     (→ K ^ mask)
        #   state ^= mask           (→ K)
        mask = random.randint(1, 0xFFFF)
        sv = ast.Name(id=state_var, ctx=ast.Store())
        return [
            ast.AugAssign(target=ast.Name(id=state_var, ctx=ast.Store()), op=ast.BitXor(), value=sn),
            ast.AugAssign(target=ast.Name(id=state_var, ctx=ast.Store()), op=ast.BitXor(), value=_c(state_val ^ mask)),
            ast.AugAssign(target=ast.Name(id=state_var, ctx=ast.Store()), op=ast.BitXor(), value=_c(mask)),
        ]

    elif style == 6:
        # state = (state ^ state) | K  (inline zero-then-set)
        return [_assign(state_var,
            _binop(_binop(sn, ast.BitXor(), sn), ast.BitOr(), _c(state_val))
        )]

    elif style == 7:
        # state = (K ^ mask) ^ mask
        mask = random.randint(1, 0xFFFF)
        return [_assign(state_var,
            _binop(_binop(_c(state_val), ast.BitXor(), _c(mask)), ast.BitXor(), _c(mask))
        )]

    elif style == 8:
        # state = K | 0
        return [_assign(state_var, _binop(_c(state_val), ast.BitOr(), _c(0)))]

    elif style == 9:
        # state = K & ~0
        return [_assign(state_var,
            _binop(_c(state_val), ast.BitAnd(), _unary(ast.Invert(), _c(0)))
        )]

    else:  # 10
        # state = (K << k) >> k
        k = random.randint(1, 4)
        return [_assign(state_var,
            _binop(_binop(_c(state_val), ast.LShift(), _c(k)), ast.RShift(), _c(k))
        )]


# ---------------------------------------------------------------------------
# Transformer
# ---------------------------------------------------------------------------

class StateMachineTransformer(ast.NodeTransformer):
    def __init__(self, name_gen_settings='english', add_junk_states=True):
        self.func_counter = 0
        self.state_var = None
        self.final_state = None
        self.name_gen_settings = name_gen_settings
        self.add_junk_states = add_junk_states
        self.junk_states = []

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

        for _ in range(num_junk_states):
            while True:
                junk_state = random.randint(1000, 999999)
                if junk_state not in used_states:
                    used_states.add(junk_state)
                    self.junk_states.append(junk_state)
                    break

            junk_block = self._generate_junk_code_block()

            # Use obfuscated state comparison for junk too
            junk_case = ast.If(
                test=_make_state_cmp(self.state_var, junk_state),
                body=junk_block,
                orelse=[]
            )
            junk_cases.append(junk_case)

        return junk_cases

    def _generate_junk_code_block(self):
        """Generate junk code block with bitwise opaque predicates."""
        junk_var = self._rand("")

        true_preds = _bitwise_true_predicates()
        false_preds = _bitwise_false_predicates()

        junk_statements = [
            # Fake bitwise assignment
            _assign(junk_var, _binop(
                _binop(_c(random.randint(1, 0xFFFF)), ast.BitXor(), _c(random.randint(1, 0xFFFF))),
                ast.BitAnd(), _unary(ast.Invert(), _c(0))
            )),
            # XOR double-cancel assignment
            _assign(junk_var, _binop(
                _binop(_c(random.randint(1, 0xFF)), ast.BitXor(), _c(random.randint(1, 0xFF))),
                ast.BitXor(), _c(random.randint(1, 0xFF))
            )),
            # Shift round-trip
            _assign(junk_var, _binop(
                _binop(_c(random.randint(1, 0xFF)), ast.LShift(), _c(random.randint(1, 5))),
                ast.RShift(), _c(random.randint(1, 5))
            )),
            # if true_pred: fake assign
            ast.If(
                test=random.choice(true_preds),
                body=[_assign(junk_var, _c(random.randint(1000, 9999)))],
                orelse=[]
            ),
            # if false_pred: unreachable
            ast.If(
                test=random.choice(false_preds),
                body=[_assign(junk_var, _c(0xDEAD))],
                orelse=[]
            ),
            # Nested: if true { if false { ... } }
            ast.If(
                test=random.choice(true_preds),
                body=[ast.If(
                    test=random.choice(false_preds),
                    body=[_assign(junk_var, _c(0))],
                    orelse=[]
                )],
                orelse=[]
            ),
            # BoolOp: true_pred and true_pred assignment
            _assign(junk_var, ast.BoolOp(
                op=ast.And(),
                values=[random.choice(true_preds), random.choice(true_preds)]
            )),
            # BoolOp: false_pred or false_pred assignment
            _assign(junk_var, ast.BoolOp(
                op=ast.Or(),
                values=[random.choice(false_preds), random.choice(false_preds)]
            )),
            # str() call dead expr
            ast.Expr(value=_call('str', _c(random.randint(0, 10000)))),
        ]

        num = random.randint(3, 6)
        return random.sample(junk_statements, min(num, len(junk_statements)))

    def _opaque_guard(self):
        """
        Return an If node wrapping a True opaque predicate.
        Used to guard real state bodies with an always-true condition
        that makes static analysis harder.
        """
        # Combine two true predicates with AND for extra noise
        t1, t2 = random.sample(_bitwise_true_predicates(), 2)
        return ast.BoolOp(op=ast.And(), values=[t1, t2])

    # -----------------------------
    # Core
    # -----------------------------

    def visit_ClassDef(self, node):
        new_body = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.ClassDef)):
                new_body.append(self.visit(item))
            else:
                new_body.append(self.generic_visit(item))
        node.body = new_body
        return node

    def visit_FunctionDef(self, node):
        if self._contains_async(node):
            return self.generic_visit(node)

        if len(node.body) < 1:
            return self.generic_visit(node)

        self.func_counter += 1
        old_state = self.state_var
        self.state_var = self._rand("")
        ret_var = self._rand("")

        is_generator = any(isinstance(n, (ast.Yield, ast.YieldFrom)) for n in ast.walk(node))

        blocks = self._split_into_blocks(node.body)
        expanded_blocks, loop_stmt = self._expand_single_loop_body(blocks)
        is_expanded_loop = loop_stmt is not None

        if is_expanded_loop:
            blocks = expanded_blocks

        if len(blocks) <= 1 and not is_generator:
            self.state_var = old_state
            return self.generic_visit(node)

        # Generate unique random state values
        unique_states = set()
        state_values = []
        for _ in range(len(blocks)):
            while True:
                s = random.randint(1000, 999999)
                if s not in unique_states:
                    unique_states.add(s)
                    state_values.append(s)
                    break

        self.block_to_state_map = dict(zip(range(len(blocks)), state_values))
        self.state_to_block_map = dict(zip(state_values, range(len(blocks))))

        while True:
            s = random.randint(1000, 999999)
            if s not in unique_states:
                self.final_state = s
                break

        # Build function body
        new_body = []

        # state = obfuscated(initial_state)
        initial_state = self.block_to_state_map[0]
        new_body.extend(_make_state_assign(self.state_var, initial_state, initial=True))

        if not is_generator:
            new_body.append(_assign(ret_var, _c(None)))

        # Build shuffled if-cases
        cases = []
        block_indices = list(range(len(blocks)))
        random.shuffle(block_indices)

        for idx in block_indices:
            state = self.block_to_state_map[idx]
            block = blocks[idx]
            case_body = self._process_block(
                block, idx, len(blocks), ret_var, is_generator, state, is_expanded_loop
            )

            # Wrap case body in opaque guard ~40% of the time
            # (adds an always-true if around the real body to confuse CFG analysis)
            if random.random() < 0.4 and case_body:
                guarded_body = [ast.If(
                    test=self._opaque_guard(),
                    body=case_body,
                    orelse=[]
                )]
                # Must still do the state transition — move last assign out of guard
                # Only wrap non-transition statements
                trans = [s for s in case_body if self._is_state_assign(s)]
                body_stmts = [s for s in case_body if not self._is_state_assign(s)]
                if body_stmts:
                    guarded_body = [ast.If(
                        test=self._opaque_guard(),
                        body=body_stmts,
                        orelse=[]
                    )] + trans
                    case_body = guarded_body

            cases.append(ast.If(
                test=_make_state_cmp(self.state_var, state),
                body=case_body,
                orelse=[]
            ))

        # Junk states
        if self.add_junk_states:
            junk_cases = self._generate_junk_states(num_junk_states=random.randint(2, 5))
            # Interleave junk cases randomly among real cases
            for jc in junk_cases:
                pos = random.randint(0, len(cases))
                cases.insert(pos, jc)

        # While loop with obfuscated condition
        if is_expanded_loop:
            loop = ast.While(test=_c(True), body=cases, orelse=[])
        else:
            loop = ast.While(
                test=_make_state_neq_cmp(self.state_var, self.final_state),
                body=cases,
                orelse=[]
            )

        new_body.append(loop)

        if not is_expanded_loop:
            if is_generator:
                new_body.append(ast.Return(value=None))
            else:
                new_body.append(ast.Return(value=_n(ret_var)))

        node.body = new_body
        self.state_var = old_state
        return self.generic_visit(node)

    def _is_state_assign(self, stmt):
        """Check if stmt is an assignment to the state variable."""
        return (
            isinstance(stmt, ast.Assign) and
            len(stmt.targets) == 1 and
            isinstance(stmt.targets[0], ast.Name) and
            stmt.targets[0].id == self.state_var
        )

    def _split_into_blocks(self, body):
        blocks = []
        current_block = []

        for stmt in body:
            if isinstance(stmt, (ast.For, ast.While, ast.Try, ast.With, ast.Match,
                                 ast.If, ast.FunctionDef, ast.ClassDef)):
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
        if len(blocks) == 1:
            stmt = blocks[0][0]
            if isinstance(stmt, (ast.While, ast.For)) and len(stmt.body) > 1:
                expanded_blocks = self._split_into_blocks(stmt.body)
                return expanded_blocks, stmt
        return blocks, None

    def _process_block(self, block, idx, total_blocks, ret_var, is_generator, state=None, is_expanded_loop=False):
        case_body = []

        for stmt in block:
            if isinstance(stmt, ast.Return):
                if is_generator:
                    if stmt.value:
                        case_body.append(ast.Expr(value=ast.Yield(value=stmt.value)))
                    case_body.append(ast.Return(value=None))
                else:
                    case_body.append(_assign(ret_var, stmt.value if stmt.value else _c(None)))
                    if is_expanded_loop:
                        case_body.extend(_make_state_assign(self.state_var, self.block_to_state_map[0]))
                    else:
                        case_body.extend(_make_state_assign(self.state_var, self.final_state))

            elif isinstance(stmt, (ast.Yield, ast.YieldFrom)):
                case_body.append(stmt)
                next_idx = idx + 1
                if next_idx < total_blocks:
                    case_body.extend(_make_state_assign(self.state_var, self.block_to_state_map[next_idx]))
                    case_body.append(ast.Return(value=None))

            elif isinstance(stmt, (ast.For, ast.While)):
                case_body.extend(self._process_loop(stmt, idx, total_blocks, is_expanded_loop))

            elif isinstance(stmt, ast.Try):
                case_body.extend(self._process_try(stmt, idx, total_blocks, is_expanded_loop))

            elif isinstance(stmt, (ast.FunctionDef, ast.ClassDef)):
                case_body.append(self.visit(stmt))

            else:
                case_body.append(stmt)

        # Add state transition if not already present
        has_explicit_transition = any(self._is_state_assign(s) for s in case_body)

        if not has_explicit_transition:
            next_idx = idx + 1
            if next_idx < total_blocks:
                next_val = self.block_to_state_map[next_idx]
            elif is_expanded_loop:
                next_val = self.block_to_state_map[0]
            else:
                next_val = self.final_state
            case_body.extend(_make_state_assign(self.state_var, next_val))

        return case_body

    def _process_loop(self, loop_node, current_idx, total_blocks, is_expanded_loop=False):
        body = [loop_node]
        next_idx = current_idx + 1
        if next_idx < total_blocks:
            next_val = self.block_to_state_map[next_idx]
        elif is_expanded_loop:
            next_val = self.block_to_state_map[0]
        else:
            next_val = self.final_state
        body.extend(_make_state_assign(self.state_var, next_val))
        return body

    def _process_try(self, try_node, current_idx, total_blocks, is_expanded_loop=False):
        next_idx = current_idx + 1
        body = [try_node]
        if next_idx < total_blocks:
            next_val = self.block_to_state_map[next_idx]
        elif is_expanded_loop:
            next_val = self.block_to_state_map[0]
        else:
            next_val = self.final_state
        body.extend(_make_state_assign(self.state_var, next_val))
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
            return code
