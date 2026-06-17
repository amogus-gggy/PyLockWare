"""
Advanced call / name indirection obfuscation (chained lookup tables).

Obfuscation layers
──────────────────
1. Every user-defined name lookup/call is wrapped in _resolve(key).

2. _resolve chains through three independent tables + an optional
   extra hop through TX (~45 % of chains):

       entry_key → T1 → (TX?) → T2 → T3 → _decode → original name

3. T3 payload uses one of four encoding schemes per entry (x/b/r/h).

4. Each name gets 2–5 independent alias chains; alias chosen per call site.

5. ~100 junk entries injected into all tables, then shuffled.

6. Key strings passed to _resolve are randomly split into fragments at AST level.

7. Decoy runtime symbols add noise for reverse-engineering.
"""
import ast
import base64
import os
import random
from typing import Dict, List, Optional, Set, Tuple


def _ct_xor(s: str, key: int) -> List[int]:
    return [ord(c) ^ ((key + i * 13 + i * i) % 256) for i, c in enumerate(s)]


def _ct_b64(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


def _ct_hex(s: str) -> str:
    return s.encode().hex()


class ChainedTableMapper:
    ENC_XOR = 'x'
    ENC_B64 = 'b'
    ENC_REV = 'r'
    ENC_HEX = 'h'

    def __init__(self, seed: Optional[bytes] = None):
        raw = seed or os.urandom(16)
        self.rng = random.Random(int.from_bytes(raw[:8], 'big'))
        self._ctr = 0
        self.name_aliases: Dict[str, List[str]] = {}
        self.T1: Dict[str, str] = {}
        self.TX: Dict[str, str] = {}
        self.T2: Dict[str, str] = {}
        self.T3: Dict[str, Tuple] = {}
        self._tx_set: Set[str] = set()

    def _uid(self, tag: str) -> str:
        self._ctr += 1
        noise = self.rng.randint(0, 0xFFFF)
        return f"{tag}{self._ctr:04x}{noise:04x}"

    def _encode(self, name: str) -> Tuple:
        s = self.rng.choice([self.ENC_XOR, self.ENC_B64, self.ENC_REV, self.ENC_HEX])
        if s == self.ENC_XOR:
            k = self.rng.randint(1, 253)
            return (s, _ct_xor(name, k), k)
        if s == self.ENC_B64:
            return (s, _ct_b64(name), None)
        if s == self.ENC_REV:
            return (s, _ct_b64(name[::-1]), None)
        return (s, _ct_hex(name), None)

    def _add_chain(self, name: str) -> str:
        ek = self._uid("e")
        dk = self._uid("d")
        sk = self._uid("s")
        self.T1[ek] = dk
        if self.rng.random() < 0.45:
            rk = self._uid("r")
            self.TX[dk] = rk
            self._tx_set.add(dk)
            self.T2[rk] = sk
        else:
            self.T2[dk] = sk
        self.T3[sk] = self._encode(name)
        return ek

    def register(self, name: str, n: Optional[int] = None) -> None:
        if name in self.name_aliases:
            return
        count = n if n is not None else self.rng.randint(2, 5)
        self.name_aliases[name] = [self._add_chain(name) for _ in range(count)]

    def get_key(self, name: str) -> str:
        if name not in self.name_aliases:
            self.register(name)
        return self.rng.choice(self.name_aliases[name])

    def inject_junk(self, n: int = 100) -> None:
        for _ in range(n):
            fake = f"__z{self.rng.randint(0, 0xFFFFFF):06x}"
            self.register(fake, n=self.rng.randint(1, 3))

    def _shuffled(self, d: dict) -> dict:
        items = list(d.items())
        self.rng.shuffle(items)
        return dict(items)

    def generate_runtime(self) -> str:
        t1 = self._shuffled(self.T1)
        tx = self._shuffled(self.TX)
        t2 = self._shuffled(self.T2)
        t3 = self._shuffled(self.T3)
        txset_repr = repr(set(self._tx_set))

        def kv(d: dict) -> str:
            rows = [f"    {k!r}: {v!r}" for k, v in d.items()]
            return "{\n" + ",\n".join(rows) + "\n}"

        t1s = kv(t1)
        txs = kv(tx)
        t2s = kv(t2)
        t3s = ("{\n" +
               ",\n".join(f"    {k!r}: ({enc!r}, {pay!r}, {aux!r})"
                          for k, (enc, pay, aux) in t3.items()) +
               "\n}")

        return f"""\
import base64 as _b64
import builtins as _builtins
import inspect as _inspect

_T1 = {t1s}

_TX = {txs}

_T2 = {t2s}

_T3 = {t3s}

_TXK = {txset_repr}

def _decode(enc, pay, aux):
    if enc == 'x':
        return ''.join(chr(b ^ ((aux + i * 13 + i * i) % 256))
                       for i, b in enumerate(pay))
    if enc == 'b':
        return _b64.b64decode(pay).decode()
    if enc == 'r':
        return _b64.b64decode(pay).decode()[::-1]
    return bytes.fromhex(pay).decode()

def _resolve(__k):
    d = _T1[__k]
    if d in _TXK:
        d = _TX[d]
    return _decode(*_T3[_T2[d]])

def _call(__k, *args, **kwargs):
    name = _resolve(__k)
    _fr = _inspect.currentframe().f_back
    _f = None
    while _fr is not None:
        _f = _fr.f_locals.get(name)
        if _f is not None:
            break
        _f = _fr.f_globals.get(name)
        if _f is not None:
            break
        _fr = _fr.f_back
    if _f is None:
        _f = getattr(_builtins, name, None)
    if _f is None:
        raise NameError(f"{{name!r}} not found")
    return _f(*args, **kwargs)

def _method_call(__obj, __k, *args, **kwargs):
    return getattr(__obj, _resolve(__k))(*args, **kwargs)

def _get_attr(__obj, __k):
    return getattr(__obj, _resolve(__k))

def _set_attr(__obj, __k, __val):
    setattr(__obj, _resolve(__k), __val)

def _get_item(__obj, __k):
    return __obj[__k]

def _set_item(__obj, __k, __val):
    __obj[__k] = __val

_T1b     = {{v: k for k, v in _T1.items()}}
_T3b     = {{k: v for k, v in _T3.items() if hash(k) & 1}}
_SHADOW  = dict(_T2)
_T2b     = {{v: k for k, v in _T2.items()}}
_TXb     = {{v: k for k, v in _TX.items()}}

def _resolve2(__k):
    import hashlib as _hl
    _h = _hl.md5(__k.encode()).hexdigest()
    _seg = _T1.get(_h[:8], _T2.get(_h[8:16], __k))
    try:
        return _b64.b64decode(_seg + '==').decode()
    except Exception:
        return _seg

def _resolve3(__k):
    _r = _T1b.get(__k, __k)
    _s = _T2b.get(_r, _r)
    return _s[::-1] if _s else __k

def _call2(__k, *args, **kwargs):
    return _resolve2(__k)

def _get_attr2(__obj, __k):
    return getattr(__obj, _resolve2(__k))

def _method_call2(__obj, __k, *args, **kwargs):
    return getattr(__obj, _resolve3(__k))(*args, **kwargs)
"""


class AdvancedObfuscator(ast.NodeTransformer):
    BUILTINS: Set[str] = {
        'True', 'False', 'None',
        'Exception', 'BaseException', 'StopIteration', 'GeneratorExit',
        'RuntimeError', 'ValueError', 'TypeError', 'KeyError', 'IndexError',
        'AttributeError', 'NameError', 'OSError', 'IOError', 'NotImplementedError',
        'int', 'str', 'float', 'complex', 'bool', 'bytes', 'bytearray',
        'list', 'dict', 'tuple', 'set', 'frozenset', 'memoryview',
        'len', 'range', 'enumerate', 'zip', 'map', 'filter', 'sorted',
        'reversed', 'sum', 'min', 'max', 'any', 'all', 'next', 'iter',
        'isinstance', 'issubclass', 'hasattr', 'getattr', 'setattr', 'delattr',
        'super', 'object', 'type', 'print', 'input', 'open', 'id', 'hash',
        'repr', 'abs', 'round', 'pow', 'divmod', 'chr', 'ord', 'hex', 'oct',
        'bin', 'callable', 'format', 'vars', 'dir', 'locals', 'globals',
        'eval', 'exec', 'compile', 'breakpoint', 'staticmethod', 'classmethod',
        'property', 'slice', 'NotImplemented', 'Ellipsis',
        '__import__', '__name__', '__file__', '__doc__', '__package__',
        '__class__', '__builtins__', '__cached__', '__loader__', '__spec__',
        '__all__', '__slots__', '__dict__', '__init_subclass__',
        '_call', '_method_call', '_get_attr', '_set_attr',
        '_get_item', '_set_item', '_resolve', '_decode',
        '_T1', '_TX', '_T2', '_T3', '_TXK',
        '_T1b', '_T3b', '_SHADOW', '_T2b', '_TXb',
        '_resolve2', '_resolve3', '_call2', '_get_attr2', '_method_call2',
        '_b64', '_builtins', '_inspect',
    }

    def __init__(self, seed: Optional[bytes] = None):
        self.mapper = ChainedTableMapper(seed=seed)
        self.rng = self.mapper.rng
        self.defined_names: Set[str] = set()
        self.imported_names: Set[str] = set()
        self.global_names: Set[str] = set()
        self.nonlocal_names: Set[str] = set()

    def _is_special(self, name: str) -> bool:
        return (name in self.BUILTINS
                or name in self.global_names
                or name in self.nonlocal_names
                or (name.startswith('__') and name.endswith('__')))

    def _resolve_key(self, name: str) -> ast.expr:
        key = self.mapper.get_key(name)
        return self._fragment(key)

    def _fragment(self, key: str) -> ast.expr:
        if len(key) < 8 or self.rng.random() < 0.30:
            return ast.Constant(value=key)
        n_splits = self.rng.randint(1, min(2, len(key) // 4))
        positions = sorted(
            self.rng.sample(range(2, len(key) - 1), n_splits)
        )
        boundaries = [0] + positions + [len(key)]
        parts = [key[boundaries[i]:boundaries[i + 1]]
                 for i in range(len(boundaries) - 1)]
        node: ast.expr = ast.Constant(value=parts[0])
        for p in parts[1:]:
            node = ast.BinOp(left=node, op=ast.Add(), right=ast.Constant(value=p))
        return node

    def _visit_keywords(self, keywords: list) -> list:
        return [ast.keyword(arg=kw.arg, value=self.visit(kw.value))
                for kw in keywords]

    def visit_FunctionDef(self, node):
        self.defined_names.add(node.name)
        node.decorator_list = [self.visit(d) for d in node.decorator_list]
        for arg in (node.args.args + node.args.posonlyargs + node.args.kwonlyargs):
            if arg.annotation:
                arg.annotation = self.visit(arg.annotation)
        node.args.defaults = [self.visit(d) for d in node.args.defaults]
        node.args.kw_defaults = [self.visit(d) if d else None
                                  for d in node.args.kw_defaults]
        if node.returns:
            node.returns = self.visit(node.returns)
        node.body = [self.visit(s) for s in node.body]
        return node

    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):
        self.defined_names.add(node.name)
        node.decorator_list = [self.visit(d) for d in node.decorator_list]
        node.bases = [self.visit(b) for b in node.bases]
        node.keywords = self._visit_keywords(node.keywords)
        node.body = [self.visit(s) for s in node.body]
        return node

    def visit_Lambda(self, node):
        node.args.defaults = [self.visit(d) for d in node.args.defaults]
        node.args.kw_defaults = [self.visit(d) if d else None
                                 for d in node.args.kw_defaults]
        node.body = self.visit(node.body)
        return node

    def visit_Import(self, node):
        for alias in node.names:
            self.imported_names.add(alias.asname or alias.name.split('.')[0])
        return node

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.imported_names.add(alias.asname or alias.name)
        return node

    def visit_Global(self, node):
        self.global_names.update(node.names)
        return node

    def visit_Nonlocal(self, node):
        self.nonlocal_names.update(node.names)
        return node

    def visit_Call(self, node):
        original_func = node.func
        v_args = [self.visit(a) for a in node.args]
        v_kws = self._visit_keywords(node.keywords)

        if isinstance(original_func, ast.Name):
            name = original_func.id
            if self._is_special(name):
                node.args, node.keywords = v_args, v_kws
                return node
            return ast.Call(
                func=ast.Name(id='_call', ctx=ast.Load()),
                args=[self._resolve_key(name)] + v_args,
                keywords=v_kws,
            )

        if isinstance(original_func, ast.Attribute):
            attr = original_func.attr
            obj = self.visit(original_func.value)
            if attr.startswith('__') and attr.endswith('__'):
                node.func = ast.Attribute(value=obj, attr=attr, ctx=ast.Load())
                node.args = v_args
                node.keywords = v_kws
                return node
            return ast.Call(
                func=ast.Name(id='_method_call', ctx=ast.Load()),
                args=[obj, self._resolve_key(attr)] + v_args,
                keywords=v_kws,
            )

        node.func = self.visit(original_func)
        node.args = v_args
        node.keywords = v_kws
        return node

    def visit_Attribute(self, node):
        node.value = self.visit(node.value)
        if isinstance(node.ctx, ast.Store):
            return node
        if isinstance(node.ctx, ast.Load):
            if node.attr.startswith('__') and node.attr.endswith('__'):
                return node
            return ast.Call(
                func=ast.Name(id='_get_attr', ctx=ast.Load()),
                args=[node.value, self._resolve_key(node.attr)],
                keywords=[],
            )
        return node

    def visit_Subscript(self, node):
        node.value = self.visit(node.value)
        node.slice = self.visit(node.slice)
        if isinstance(node.ctx, ast.Store):
            return node
        if isinstance(node.ctx, ast.Load):
            # Don't obfuscate slices (e.g., x[:8], x[1:5]) - only simple subscripts
            if isinstance(node.slice, ast.Slice):
                return node
            return ast.Call(
                func=ast.Name(id='_get_item', ctx=ast.Load()),
                args=[node.value, node.slice],
                keywords=[],
            )
        return node

    def visit_Assign(self, node):
        new_value = self.visit(node.value)
        if len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Attribute):
                obj = self.visit(target.value)
                return ast.Expr(value=ast.Call(
                    func=ast.Name(id='_set_attr', ctx=ast.Load()),
                    args=[obj, self._resolve_key(target.attr), new_value],
                    keywords=[],
                ))
            if isinstance(target, ast.Subscript):
                # Don't obfuscate slice assignments (e.g., x[:8] = value)
                if isinstance(target.slice, ast.Slice):
                    return ast.Assign(targets=[node.targets[0]], value=new_value)
                obj = self.visit(target.value)
                idx = self.visit(target.slice)
                return ast.Expr(value=ast.Call(
                    func=ast.Name(id='_set_item', ctx=ast.Load()),
                    args=[obj, idx, new_value],
                    keywords=[],
                ))
        new_targets = [self.visit(t) for t in node.targets]
        return ast.Assign(targets=new_targets, value=new_value)

    def visit_AnnAssign(self, node):
        new_value = self.visit(node.value) if node.value else None
        if node.value:
            if isinstance(node.target, ast.Attribute):
                obj = self.visit(node.target.value)
                return ast.Expr(value=ast.Call(
                    func=ast.Name(id='_set_attr', ctx=ast.Load()),
                    args=[obj, self._resolve_key(node.target.attr), new_value],
                    keywords=[],
                ))
            if isinstance(node.target, ast.Subscript):
                # Don't obfuscate slice assignments
                if isinstance(node.target.slice, ast.Slice):
                    return ast.AnnAssign(
                        target=node.target,
                        annotation=self.visit(node.annotation) if node.annotation else None,
                        value=new_value,
                        simple=node.simple,
                    )
                obj = self.visit(node.target.value)
                idx = self.visit(node.target.slice)
                return ast.Expr(value=ast.Call(
                    func=ast.Name(id='_set_item', ctx=ast.Load()),
                    args=[obj, idx, new_value],
                    keywords=[],
                ))
        return ast.AnnAssign(
            target=node.target,
            annotation=self.visit(node.annotation) if node.annotation else None,
            value=new_value,
            simple=node.simple,
        )

    def visit_AugAssign(self, node):
        new_value = self.visit(node.value)
        if isinstance(node.target, ast.Attribute):
            obj = self.visit(node.target.value)
            key = self._resolve_key(node.target.attr)
            current = ast.Call(
                func=ast.Name(id='_get_attr', ctx=ast.Load()),
                args=[obj, key], keywords=[])
            computed = ast.BinOp(left=current, op=node.op, right=new_value)
            return ast.Expr(value=ast.Call(
                func=ast.Name(id='_set_attr', ctx=ast.Load()),
                args=[obj, key, computed], keywords=[],
            ))
        if isinstance(node.target, ast.Subscript):
            # Don't obfuscate slice augmented assignments (e.g., x[:8] += 1)
            if isinstance(node.target.slice, ast.Slice):
                node.value = new_value
                return node
            obj = self.visit(node.target.value)
            idx = self.visit(node.target.slice)
            current = ast.Call(
                func=ast.Name(id='_get_item', ctx=ast.Load()),
                args=[obj, idx], keywords=[])
            computed = ast.BinOp(left=current, op=node.op, right=new_value)
            return ast.Expr(value=ast.Call(
                func=ast.Name(id='_set_item', ctx=ast.Load()),
                args=[obj, idx, computed], keywords=[],
            ))
        node.value = new_value
        return node

    def _visit_generators(self, generators):
        for gen in generators:
            gen.iter = self.visit(gen.iter)
            gen.ifs = [self.visit(c) for c in gen.ifs]

    def visit_ListComp(self, node):
        self._visit_generators(node.generators)
        node.elt = self.visit(node.elt)
        return node

    def visit_SetComp(self, node):
        self._visit_generators(node.generators)
        node.elt = self.visit(node.elt)
        return node

    def visit_GeneratorExp(self, node):
        self._visit_generators(node.generators)
        node.elt = self.visit(node.elt)
        return node

    def visit_DictComp(self, node):
        self._visit_generators(node.generators)
        node.key = self.visit(node.key)
        node.value = self.visit(node.value)
        return node

    def visit_JoinedStr(self, node):
        for v in node.values:
            if isinstance(v, ast.FormattedValue):
                v.value = self.visit(v.value)
                if v.format_spec:
                    v.format_spec = self.visit(v.format_spec)
        return node

    def visit_If(self, node):
        node.test = self.visit(node.test)
        node.body = [self.visit(s) for s in node.body]
        node.orelse = [self.visit(s) for s in node.orelse]
        return node

    def visit_While(self, node):
        node.test = self.visit(node.test)
        node.body = [self.visit(s) for s in node.body]
        node.orelse = [self.visit(s) for s in node.orelse]
        return node

    def visit_For(self, node):
        node.iter = self.visit(node.iter)
        node.body = [self.visit(s) for s in node.body]
        node.orelse = [self.visit(s) for s in node.orelse]
        return node

    def visit_AsyncFor(self, node):
        return self.visit_For(node)

    def visit_With(self, node):
        for item in node.items:
            item.context_expr = self.visit(item.context_expr)
            if item.optional_vars:
                item.optional_vars = self.visit(item.optional_vars)
        node.body = [self.visit(s) for s in node.body]
        return node

    def visit_AsyncWith(self, node):
        return self.visit_With(node)

    def visit_Try(self, node):
        node.body = [self.visit(s) for s in node.body]
        for handler in node.handlers:
            if handler.type:
                handler.type = self.visit(handler.type)
            handler.body = [self.visit(s) for s in handler.body]
        node.orelse = [self.visit(s) for s in node.orelse]
        node.finalbody = [self.visit(s) for s in node.finalbody]
        return node

    def visit_Return(self, node):
        if node.value:
            node.value = self.visit(node.value)
        return node

    def visit_Yield(self, node):
        if node.value:
            node.value = self.visit(node.value)
        return node

    def visit_YieldFrom(self, node):
        node.value = self.visit(node.value)
        return node

    def visit_Await(self, node):
        node.value = self.visit(node.value)
        return node

    def visit_IfExp(self, node):
        node.test = self.visit(node.test)
        node.body = self.visit(node.body)
        node.orelse = self.visit(node.orelse)
        return node

    def visit_BoolOp(self, node):
        node.values = [self.visit(v) for v in node.values]
        return node

    def visit_BinOp(self, node):
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)
        return node

    def visit_UnaryOp(self, node):
        node.operand = self.visit(node.operand)
        return node

    def visit_Compare(self, node):
        node.left = self.visit(node.left)
        node.comparators = [self.visit(c) for c in node.comparators]
        return node

    def visit_Delete(self, node):
        node.targets = [self.visit(t) for t in node.targets]
        return node

    def visit_Raise(self, node):
        if node.exc:
            node.exc = self.visit(node.exc)
        if node.cause:
            node.cause = self.visit(node.cause)
        return node

    def visit_Assert(self, node):
        node.test = self.visit(node.test)
        if node.msg:
            node.msg = self.visit(node.msg)
        return node

    def visit_Starred(self, node):
        node.value = self.visit(node.value)
        return node

    def visit_NamedExpr(self, node):
        node.value = self.visit(node.value)
        return node


def obfuscate_source(
    source: str,
    junk_entries: int = 100,
    seed: Optional[bytes] = None,
) -> str:
    """Parse source, apply chained-table call obfuscation, return unparsed code."""
    tree = ast.parse(source)
    obfuscator = AdvancedObfuscator(seed=seed)
    obfuscator.mapper.inject_junk(junk_entries)
    new_tree = obfuscator.visit(tree)
    ast.fix_missing_locations(new_tree)
    runtime_src = obfuscator.mapper.generate_runtime()
    runtime_tree = ast.parse(runtime_src)
    new_tree.body = runtime_tree.body + new_tree.body
    return ast.unparse(new_tree)
