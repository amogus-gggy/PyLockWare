"""
Boolean Expression Obfuscation Module for PyLockWare
Obfuscates True/False/bool operations with bitwise-heavy combined expressions.
"""
import ast
import random
from pylockware.core.name_generator import generate_random_name


def _bconst(v):
    return ast.Constant(v)


def _bname(n):
    return ast.Name(id=n, ctx=ast.Load())


def _binop(l, op, r):
    return ast.BinOp(left=l, op=op, right=r)


def _cmp(l, op, r):
    return ast.Compare(left=l, ops=[op], comparators=[r])


def _unary(op, operand):
    return ast.UnaryOp(op=op, operand=operand)


def _call(name, *args):
    return ast.Call(func=_bname(name), args=list(args), keywords=[])


def _bool(node):
    return _call('bool', node)


class BooleanObfuscator(ast.NodeTransformer):
    """
    AST transformer that obfuscates boolean expressions using bitwise operations.
    Every obfuscation point applies a combination of 2 independent transforms.
    """

    def __init__(self, name_gen_settings='english'):
        self.name_gen_settings = name_gen_settings
        self.obf_count = 0
        self.helper_func_name = generate_random_name("_", name_gen_settings)
        self.call_depth = 0
        self.helper_injected = False
        self.assign_depth = 0

    # ------------------------------------------------------------------
    # Primitive True/False building blocks (bitwise only, no not-chains)
    # ------------------------------------------------------------------

    def _true_atoms(self):
        """Return pool of simple bitwise True atoms (used in combinations)."""
        a = random.randint(1, 0xFFFF)
        b = random.randint(1, 0xFFFF)
        k = random.randint(1, 7)
        return [
            # (a ^ a) == 0
            _cmp(_binop(_bconst(a), ast.BitXor(), _bconst(a)), ast.Eq(), _bconst(0)),
            # (a & a) == a
            _cmp(_binop(_bconst(a), ast.BitAnd(), _bconst(a)), ast.Eq(), _bconst(a)),
            # (a | 0) == a
            _cmp(_binop(_bconst(a), ast.BitOr(), _bconst(0)), ast.Eq(), _bconst(a)),
            # ~(~a) == a
            _cmp(_unary(ast.Invert(), _unary(ast.Invert(), _bconst(a))), ast.Eq(), _bconst(a)),
            # (a << k) >> k == a
            _cmp(
                _binop(_binop(_bconst(a), ast.LShift(), _bconst(k)), ast.RShift(), _bconst(k)),
                ast.Eq(), _bconst(a)
            ),
            # ((a ^ b) ^ b) == a
            _cmp(
                _binop(_binop(_bconst(a), ast.BitXor(), _bconst(b)), ast.BitXor(), _bconst(b)),
                ast.Eq(), _bconst(a)
            ),
            # (a & ~0) == a  (~0 == -1)
            _cmp(_binop(_bconst(a), ast.BitAnd(), _unary(ast.Invert(), _bconst(0))), ast.Eq(), _bconst(a)),
            # bool(a & a)
            _bool(_binop(_bconst(a), ast.BitAnd(), _bconst(a))),
            # ~(-1) == 0
            _cmp(_unary(ast.Invert(), _bconst(-1)), ast.Eq(), _bconst(0)),
            # (1 << k) >> k == 1
            _cmp(
                _binop(_binop(_bconst(1), ast.LShift(), _bconst(k)), ast.RShift(), _bconst(k)),
                ast.Eq(), _bconst(1)
            ),
        ]

    def _false_atoms(self):
        """Return pool of simple bitwise False atoms."""
        a = random.randint(2, 0xFFFF)
        b = random.randint(1, 0xFFFF)
        k = random.randint(1, 7)
        return [
            # (~a & a) != 0  → always 0, so False
            _cmp(_binop(_unary(ast.Invert(), _bconst(a)), ast.BitAnd(), _bconst(a)), ast.NotEq(), _bconst(0)),
            # (a & 0) != 0
            _cmp(_binop(_bconst(a), ast.BitAnd(), _bconst(0)), ast.NotEq(), _bconst(0)),
            # (a ^ a) != 0
            _cmp(_binop(_bconst(a), ast.BitXor(), _bconst(a)), ast.NotEq(), _bconst(0)),
            # ((a ^ b) ^ b) != a
            _cmp(
                _binop(_binop(_bconst(a), ast.BitXor(), _bconst(b)), ast.BitXor(), _bconst(b)),
                ast.NotEq(), _bconst(a)
            ),
            # (a << k) == a  (k >= 1 so always False)
            _cmp(_binop(_bconst(a), ast.LShift(), _bconst(k)), ast.Eq(), _bconst(a)),
            # ~(~0) != 0  → ~(~0)=0, False
            _cmp(_unary(ast.Invert(), _unary(ast.Invert(), _bconst(0))), ast.NotEq(), _bconst(0)),
            # bool(a & 0)  is True
            _cmp(_bool(_binop(_bconst(a), ast.BitAnd(), _bconst(0))), ast.Is(), _bconst(True)),
            # ~(~a) != a
            _cmp(_unary(ast.Invert(), _unary(ast.Invert(), _bconst(a))), ast.NotEq(), _bconst(a)),
        ]

    # ------------------------------------------------------------------
    # Combined True/False generators (atoms joined with `and`/`or`)
    # ------------------------------------------------------------------

    def _generate_true_expr(self):
        """
        Combine 2 independent True atoms with `and`.
        Result is always True, looks complex.
        """
        atoms = self._true_atoms()
        a1, a2 = random.sample(atoms, 2)
        return ast.BoolOp(op=ast.And(), values=[a1, a2])

    def _generate_false_expr(self):
        """
        Combine 2 independent False atoms with `or`.
        Result is always False, looks complex.
        """
        atoms = self._false_atoms()
        a1, a2 = random.sample(atoms, 2)
        return ast.BoolOp(op=ast.Or(), values=[a1, a2])

    # ------------------------------------------------------------------
    # Chain combinator — applies exactly 2 different transforms to node
    # ------------------------------------------------------------------

    # Single-step transforms that preserve boolean semantics:
    #   each returns (transformed_node)
    # They are designed to be composable.

    def _t_xor0(self, node):
        """bool(bool(x) ^ 0) — bitwise XOR identity."""
        return _bool(_binop(_bool(node), ast.BitXor(), _bconst(0)))

    def _t_or0(self, node):
        """bool(bool(x) | 0) — bitwise OR identity."""
        return _bool(_binop(_bool(node), ast.BitOr(), _bconst(0)))

    def _t_and_neg1(self, node):
        """bool(bool(x) & ~0) — bitwise AND identity (~0 = -1)."""
        return _bool(_binop(_bool(node), ast.BitAnd(), _unary(ast.Invert(), _bconst(0))))

    def _t_and_true(self, node):
        """x and (true_expr) — append True via and."""
        return ast.BoolOp(op=ast.And(), values=[node, self._generate_true_expr()])

    def _t_or_false(self, node):
        """x or (false_expr) — append False via or."""
        return ast.BoolOp(op=ast.Or(), values=[node, self._generate_false_expr()])

    def _t_cmp_is_true(self, node):
        """bool(x) is True — explicit is-comparison."""
        return _cmp(_bool(node), ast.Is(), _bconst(True))

    def _t_shift_round(self, node):
        """bool((bool(x) << 3) >> 3) — shift round-trip."""
        k = random.randint(1, 5)
        inner = _binop(_binop(_bool(node), ast.LShift(), _bconst(k)), ast.RShift(), _bconst(k))
        return _bool(inner)

    def _t_xor_flip_back(self, node):
        """bool(bool(x) ^ 0xFF ^ 0xFF) — XOR cancel."""
        mask = random.randint(1, 0xFF)
        inner = _binop(_binop(_bool(node), ast.BitXor(), _bconst(mask)), ast.BitXor(), _bconst(mask))
        return _bool(inner)

    def _chain_obf(self, node):
        """
        Apply exactly 2 distinct transforms chosen at random.
        Guarantees no repeated transform in the chain.
        """
        pool = [
            self._t_xor0,
            self._t_or0,
            self._t_and_neg1,
            self._t_and_true,
            self._t_or_false,
            self._t_cmp_is_true,
            self._t_shift_round,
            self._t_xor_flip_back,
        ]
        t1, t2 = random.sample(pool, 2)
        return t2(t1(node))

    # ------------------------------------------------------------------
    # Visitors
    # ------------------------------------------------------------------

    def visit_Constant(self, node):
        if self.call_depth > 0 or self.assign_depth > 0:
            return node
        if node.value is True:
            self.obf_count += 1
            return self._generate_true_expr()
        elif node.value is False:
            self.obf_count += 1
            return self._generate_false_expr()
        return node

    def visit_NameConstant(self, node):
        if node.value is True:
            self.obf_count += 1
            return self._generate_true_expr()
        elif node.value is False:
            self.obf_count += 1
            return self._generate_false_expr()
        return node

    def visit_Assign(self, node):
        self.assign_depth += 1
        node.value = self.visit(node.value)
        self.assign_depth -= 1
        node.targets = [self.visit(t) for t in node.targets]
        return node

    def visit_UnaryOp(self, node):
        """Obfuscate 'not x' with combined bitwise transforms — no not-chains."""
        if isinstance(node.op, ast.Not):
            self.obf_count += 1
            operand = self.generic_visit(node.operand)
            # Core not-equivalents (bitwise only, no not-spam):
            #   bool(bool(x) ^ 1)     — XOR flips the bit
            #   (bool(x) ^ 1) == 1    — XOR then compare
            #   bool(~bool(x) & 1)    — invert then mask LSB
            transform = random.choice(['xor1', 'xor1_cmp', 'invert_lsb'])

            if transform == 'xor1':
                core = _bool(_binop(_bool(operand), ast.BitXor(), _bconst(1)))
            elif transform == 'xor1_cmp':
                core = _cmp(_binop(_bool(operand), ast.BitXor(), _bconst(1)), ast.Eq(), _bconst(1))
            else:  # invert_lsb
                # ~bool(x) & 1  picks the flipped LSB (0 or 1)
                core = _bool(_binop(_unary(ast.Invert(), _bool(operand)), ast.BitAnd(), _bconst(1)))

            # Then wrap in one additional bitwise identity to add noise
            wrapper = random.choice([self._t_xor0, self._t_or0, self._t_and_neg1])
            return wrapper(core)

        return self.generic_visit(node)

    def visit_BoolOp(self, node):
        """Obfuscate and/or by combining demorgan + bitwise noise."""
        node = self.generic_visit(node)

        transform = random.choice(['identity', 'demorgan', 'distribute', 'nested'])

        if isinstance(node.op, ast.And):
            if transform == 'identity':
                # (a and b)  →  chain_obf(a and b and true_expr)
                self.obf_count += 1
                node.values.append(self._generate_true_expr())
                return self._chain_obf(node)
            elif transform == 'demorgan':
                # not (not a or not b)
                self.obf_count += 1
                negated = [
                    _bconst(not v.value) if isinstance(v, ast.Constant) and v.value in (True, False)
                    else _unary(ast.Not(), v)
                    for v in node.values
                ]
                core = _unary(ast.Not(), ast.BoolOp(op=ast.Or(), values=negated))
                return self._t_xor0(core)
            elif transform == 'distribute':
                self.obf_count += 1
                node.values = [
                    ast.BoolOp(op=ast.And(), values=[v, self._generate_true_expr()])
                    for v in node.values
                ]
            else:  # nested
                if len(node.values) >= 2:
                    self.obf_count += 1
                    last = node.values[-1]
                    node.values[-1] = ast.IfExp(
                        test=last,
                        body=self._generate_true_expr(),
                        orelse=self._generate_false_expr()
                    )

        elif isinstance(node.op, ast.Or):
            if transform == 'identity':
                self.obf_count += 1
                node.values.append(self._generate_false_expr())
                return self._chain_obf(node)
            elif transform == 'demorgan':
                # not (not a and not b)
                self.obf_count += 1
                negated = [
                    _bconst(not v.value) if isinstance(v, ast.Constant) and v.value in (True, False)
                    else _unary(ast.Not(), v)
                    for v in node.values
                ]
                core = _unary(ast.Not(), ast.BoolOp(op=ast.And(), values=negated))
                return self._t_xor0(core)
            elif transform == 'distribute':
                self.obf_count += 1
                node.values = [
                    ast.BoolOp(op=ast.Or(), values=[v, self._generate_false_expr()])
                    for v in node.values
                ]
            else:  # nested
                if len(node.values) >= 2:
                    self.obf_count += 1
                    last = node.values[-1]
                    node.values[-1] = ast.IfExp(
                        test=last,
                        body=self._generate_true_expr(),
                        orelse=self._generate_false_expr()
                    )

        return node

    def visit_Compare(self, node):
        """Wrap comparison result in a 2-step bitwise chain."""
        node = self.generic_visit(node)

        if random.random() < 0.65:
            self.obf_count += 1
            return self._chain_obf(node)

        return node

    def visit_Call(self, node):
        self.call_depth += 1
        node.func = self.visit(node.func)
        self.call_depth -= 1
        return node

    def visit_List(self, node):
        return node

    def visit_Tuple(self, node):
        return node

    def visit_Dict(self, node):
        return node

    def visit_If(self, node):
        if self.call_depth > 0:
            return self.generic_visit(node)

        node.test = self.visit(node.test)
        self.obf_count += 1
        node.test = self._chain_obf(node.test)
        node.body = [self.visit(s) for s in node.body]
        node.orelse = [self.visit(s) for s in node.orelse]
        return node

    def visit_While(self, node):
        node.test = self.visit(node.test)
        self.obf_count += 1
        node.test = self._chain_obf(node.test)
        node.body = [self.visit(s) for s in node.body]
        node.orelse = [self.visit(s) for s in node.orelse]
        return node

    def visit_IfExp(self, node):
        node.test = self.visit(node.test)
        if random.random() < 0.5:
            self.obf_count += 1
            node.test = self._chain_obf(node.test)
        node.body = self.visit(node.body)
        node.orelse = self.visit(node.orelse)
        return node

    def visit_Assert(self, node):
        node.test = self.visit(node.test)
        if random.random() < 0.4:
            self.obf_count += 1
            node.test = ast.BoolOp(
                op=ast.And(),
                values=[node.test, self._generate_true_expr()]
            )
        return node

    def apply_obfuscation(self, code: str) -> str:
        try:
            tree = ast.parse(code)
            obfuscated_tree = self.visit(tree)
            ast.fix_missing_locations(obfuscated_tree)
            return ast.unparse(obfuscated_tree)
        except Exception as e:
            print(f"Boolean obfuscation failed: {e}")
            return code

    def reset(self):
        self.obf_count = 0
        self.call_depth = 0
        self.assign_depth = 0


def obfuscate_booleans(code: str, name_gen_settings: str = 'english') -> str:
    obfuscator = BooleanObfuscator(name_gen_settings)
    return obfuscator.apply_obfuscation(code)
