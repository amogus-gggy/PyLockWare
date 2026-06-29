"""
Expression Virtualization for PyLockWare (Ultra-Optimized & Hardened).
Compiles Python expressions to custom bytecode and executes them in a high-performance VM.
"""
import ast
import base64
import struct
import uuid
import random
import zlib

def _rand_name():
    return "h" + uuid.uuid4().hex[:8]

def _gen_vm_runtime():
    op_names = [
        'LOAD_VAR', 'LOAD_CONST', 'ADD', 'SUB', 'MUL', 'DIV',
        'FLOORDIV', 'MOD', 'POW', 'BIT_AND', 'BIT_OR', 'BIT_XOR', 'LSHIFT', 'RSHIFT',
        'CALL_0', 'CALL_1', 'CALL_2', 'CALL_3', 'CALL_N',
        'RETURN', 'COMPARE_GT', 'COMPARE_LT', 'COMPARE_GTE', 'COMPARE_LTE',
        'COMPARE_EQ', 'COMPARE_NEQ', 'NEGATE', 'NOT_', 'BOOL_AND', 'BOOL_OR',
        'GET_SUBSCRIPT'
    ]

    opcodes = {}
    used = set()
    for name in op_names:
        while True:
            val = random.randint(0, 255)
            if val not in used:
                used.add(val)
                opcodes[name] = val
                break

    xor_key = [random.randint(1, 254) for _ in range(random.randint(8, 16))]
    xor_key_str = str(xor_key)

    vmentry_name = _rand_name()
    cache_name = _rand_name()

    h_keys = ['stack', 'pc', 'op', 'args', 'consts', 'code', 'data', 'b64_str', 'checksum', 'actual_checksum']
    h_names = {k: _rand_name() for k in h_keys}
    hv = h_names
    def _h(name): return hv[name]

    # FIX: Explicit indentation levels
    indent1 = "    "      # 4 spaces (inside function)
    indent2 = "        "  # 8 spaces (inside while)
    indent3 = "            " # 12 spaces (inside if/elif)

    vm_loop_lines = [
        f"{indent1}{_h('stack')} = []",
        f"{indent1}{_h('pc')} = 0",
        f"{indent1}while {_h('pc')} < len({_h('code')}):",
        f"{indent2}{_h('op')} = {_h('code')}[{_h('pc')}]; {_h('pc')} += 1",
    ]

    shuffled_ops = list(op_names)
    random.shuffle(shuffled_ops)

    first = True
    for op_name in shuffled_ops:
        cond = "if" if first else "elif"
        first = False
        vm_loop_lines.append(f"{indent2}{cond} {_h('op')} == {opcodes[op_name]}:")

        if op_name == 'LOAD_VAR':
            vm_loop_lines.append(f"{indent3}{_h('stack')}.append({_h('args')}[{_h('code')}[{_h('pc')}]]); {_h('pc')} += 1")
        elif op_name == 'LOAD_CONST':
            vm_loop_lines.append(f"{indent3}{_h('stack')}.append({_h('consts')}[{_h('code')}[{_h('pc')}]]); {_h('pc')} += 1")
        elif op_name == 'ADD':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a + _b)")
        elif op_name == 'SUB':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a - _b)")
        elif op_name == 'MUL':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a * _b)")
        elif op_name == 'DIV':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a / _b)")
        elif op_name == 'FLOORDIV':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a // _b)")
        elif op_name == 'MOD':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a % _b)")
        elif op_name == 'POW':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a ** _b)")
        elif op_name == 'BIT_AND':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a & _b)")
        elif op_name == 'BIT_OR':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a | _b)")
        elif op_name == 'BIT_XOR':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a ^ _b)")
        elif op_name == 'LSHIFT':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a << _b)")
        elif op_name == 'RSHIFT':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a >> _b)")
        elif op_name == 'CALL_0':
            vm_loop_lines.append(f"{indent3}{_h('stack')}.append({_h('stack')}.pop()())")
        elif op_name == 'CALL_1':
            vm_loop_lines.append(f"{indent3}_a = {_h('stack')}.pop(); _f = {_h('stack')}.pop(); {_h('stack')}.append(_f(_a))")
        elif op_name == 'CALL_2':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); _f = {_h('stack')}.pop(); {_h('stack')}.append(_f(_a, _b))")
        elif op_name == 'CALL_3':
            vm_loop_lines.append(f"{indent3}_c = {_h('stack')}.pop(); _b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); _f = {_h('stack')}.pop(); {_h('stack')}.append(_f(_a, _b, _c))")
        elif op_name == 'CALL_N':
            vm_loop_lines.extend([
                f"{indent3}_num = {_h('code')}[{_h('pc')}]; {_h('pc')} += 1",
                f"{indent3}_args = [{_h('stack')}.pop() for _ in range(_num)][::-1]",
                f"{indent3}_f = {_h('stack')}.pop()",
                f"{indent3}{_h('stack')}.append(_f(*_args))"
            ])
        elif op_name == 'RETURN':
            vm_loop_lines.append(f"{indent3}return {_h('stack')}.pop()")
        elif op_name == 'COMPARE_GT':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a > _b)")
        elif op_name == 'COMPARE_LT':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a < _b)")
        elif op_name == 'COMPARE_GTE':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a >= _b)")
        elif op_name == 'COMPARE_LTE':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a <= _b)")
        elif op_name == 'COMPARE_EQ':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a == _b)")
        elif op_name == 'COMPARE_NEQ':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a != _b)")
        elif op_name == 'NEGATE':
            vm_loop_lines.append(f"{indent3}{_h('stack')}.append(-{_h('stack')}.pop())")
        elif op_name == 'NOT_':
            vm_loop_lines.append(f"{indent3}{_h('stack')}.append(not {_h('stack')}.pop())")
        elif op_name == 'BOOL_AND':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a and _b)")
        elif op_name == 'BOOL_OR':
            vm_loop_lines.append(f"{indent3}_b = {_h('stack')}.pop(); _a = {_h('stack')}.pop(); {_h('stack')}.append(_a or _b)")
        elif op_name == 'GET_SUBSCRIPT':
            vm_loop_lines.append(f"{indent3}_idx = {_h('stack')}.pop(); _obj = {_h('stack')}.pop(); {_h('stack')}.append(_obj[_idx])")

    for _ in range(random.randint(10, 25)):
        dummy_op = random.randint(0, 255)
        while dummy_op in opcodes.values():
            dummy_op = random.randint(0, 255)
        vm_loop_lines.append(f"{indent2}elif {_h('op')} == {dummy_op}:")
        vm_loop_lines.append(f"{indent3}pass")

    vm_loop_str = "\n".join(vm_loop_lines)

    vmentry_code = f"""\
import base64 as _b64
import struct as _struct
import zlib as _zlib

{cache_name} = {{}}
_XOR_KEY = {xor_key_str}

def {vmentry_name}({_h('b64_str')}, *{_h('args')}):
    if {_h('b64_str')} not in {cache_name}:
        {_h('data')} = _b64.b64decode({_h('b64_str')})
        _key_len = len(_XOR_KEY)
        {_h('data')} = bytes([b ^ _XOR_KEY[i % _key_len] for i, b in enumerate({_h('data')})])
        
        {_h('checksum')} = _struct.unpack('<I', {_h('data')}[:4])[0]
        {_h('actual_checksum')} = _zlib.crc32({_h('data')}[4:]) & 0xFFFFFFFF
        if {_h('checksum')} != {_h('actual_checksum')}:
            raise RuntimeError("Integrity check failed")
        {_h('data')} = {_h('data')}[4:]
        
        offset = 0
        num_consts = _struct.unpack('<H', {_h('data')}[offset:offset+2])[0]; offset += 2
        {_h('consts')} = []
        for _ in range(num_consts):
            ctype = {_h('data')}[offset]; offset += 1
            clen = _struct.unpack('<H', {_h('data')}[offset:offset+2])[0]; offset += 2
            cdata = {_h('data')}[offset:offset+clen]; offset += clen
            if ctype == 0: {_h('consts')}.append(_struct.unpack('<i', cdata)[0])
            elif ctype == 1: {_h('consts')}.append(_struct.unpack('<d', cdata)[0])
            elif ctype == 2: {_h('consts')}.append(cdata.decode('utf-8'))
            elif ctype == 3: {_h('consts')}.append(bool(cdata[0]))
            elif ctype == 4: {_h('consts')}.append(None)
            
        {_h('code')} = {_h('data')}[offset:]
        {cache_name}[{_h('b64_str')}] = ({_h('consts')}, {_h('code')})
        
    {_h('consts')}, {_h('code')} = {cache_name}[{_h('b64_str')}]
    
{vm_loop_str}
"""
    return vmentry_code, opcodes, vmentry_name, xor_key

def encrypt_and_encode(data, xor_key):
    checksum = zlib.crc32(data) & 0xFFFFFFFF
    payload = struct.pack('<I', checksum) + data

    key_len = len(xor_key)
    enc = bytes([b ^ xor_key[i % key_len] for i, b in enumerate(payload)])
    return base64.b64encode(enc).decode('ascii')

_VM_RUNTIME_CODE, _OPCODES, _VM_ENTRY_NAME, _VM_XOR_KEY = _gen_vm_runtime()
VM_RUNTIME_CODE = _VM_RUNTIME_CODE

class ExprCompiler(ast.NodeVisitor):
    def __init__(self, opcodes):
        self.opcodes = opcodes
        self.code = bytearray()
        self.consts = []
        self.deps = {}

    def generic_visit(self, node):
        raise ValueError(f"Unsupported node type: {type(node).__name__}")

    def add_const(self, value):
        try:
            if value not in self.consts:
                self.consts.append(value)
            return self.consts.index(value)
        except TypeError:
            self.consts.append(value)
            return len(self.consts) - 1

    def add_dep(self, node):
        key = ast.unparse(node)
        if key not in self.deps:
            self.deps[key] = (len(self.deps), node)
        return self.deps[key][0]

    def visit_Expression(self, node):
        self.visit(node.body)

    def visit_Name(self, node):
        idx = self.add_dep(node)
        self.code.append(self.opcodes['LOAD_VAR'])
        self.code.append(idx)

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name):
            idx = self.add_dep(node)
            self.code.append(self.opcodes['LOAD_VAR'])
            self.code.append(idx)
        else:
            raise ValueError("Complex attributes not supported")

    def visit_Constant(self, node):
        idx = self.add_const(node.value)
        self.code.append(self.opcodes['LOAD_CONST'])
        self.code.append(idx)

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        if isinstance(node.op, ast.Add): self.code.append(self.opcodes['ADD'])
        elif isinstance(node.op, ast.Sub): self.code.append(self.opcodes['SUB'])
        elif isinstance(node.op, ast.Mult): self.code.append(self.opcodes['MUL'])
        elif isinstance(node.op, ast.Div): self.code.append(self.opcodes['DIV'])
        elif isinstance(node.op, ast.FloorDiv): self.code.append(self.opcodes['FLOORDIV'])
        elif isinstance(node.op, ast.Mod): self.code.append(self.opcodes['MOD'])
        elif isinstance(node.op, ast.Pow): self.code.append(self.opcodes['POW'])
        elif isinstance(node.op, ast.BitAnd): self.code.append(self.opcodes['BIT_AND'])
        elif isinstance(node.op, ast.BitOr): self.code.append(self.opcodes['BIT_OR'])
        elif isinstance(node.op, ast.BitXor): self.code.append(self.opcodes['BIT_XOR'])
        elif isinstance(node.op, ast.LShift): self.code.append(self.opcodes['LSHIFT'])
        elif isinstance(node.op, ast.RShift): self.code.append(self.opcodes['RSHIFT'])
        else: raise ValueError(f"Unsupported BinOp: {type(node.op).__name__}")

    def visit_Call(self, node):
        self.visit(node.func)
        for arg in node.args:
            self.visit(arg)

        num_args = len(node.args)
        if num_args == 0: self.code.append(self.opcodes['CALL_0'])
        elif num_args == 1: self.code.append(self.opcodes['CALL_1'])
        elif num_args == 2: self.code.append(self.opcodes['CALL_2'])
        elif num_args == 3: self.code.append(self.opcodes['CALL_3'])
        else:
            self.code.append(self.opcodes['CALL_N'])
            self.code.append(num_args)

    def visit_UnaryOp(self, node):
        self.visit(node.operand)
        if isinstance(node.op, ast.USub):
            self.code.append(self.opcodes['NEGATE'])
        elif isinstance(node.op, ast.UAdd):
            pass
        elif isinstance(node.op, ast.Not):
            self.code.append(self.opcodes['NOT_'])
        elif isinstance(node.op, ast.Invert):
            self.visit(ast.Constant(value=-1))
            self.code.append(self.opcodes['BIT_XOR'])
        else: raise ValueError(f"Unsupported UnaryOp: {type(node.op).__name__}")

    def visit_Compare(self, node):
        self.visit(node.left)
        for op, comp in zip(node.ops, node.comparators):
            self.visit(comp)
            if isinstance(op, ast.Gt): self.code.append(self.opcodes['COMPARE_GT'])
            elif isinstance(op, ast.Lt): self.code.append(self.opcodes['COMPARE_LT'])
            elif isinstance(op, ast.GtE): self.code.append(self.opcodes['COMPARE_GTE'])
            elif isinstance(op, ast.LtE): self.code.append(self.opcodes['COMPARE_LTE'])
            elif isinstance(op, ast.Eq): self.code.append(self.opcodes['COMPARE_EQ'])
            elif isinstance(op, ast.NotEq): self.code.append(self.opcodes['COMPARE_NEQ'])
            else: raise ValueError(f"Unsupported Compare: {type(op).__name__}")

    def visit_BoolOp(self, node):
        for val in node.values:
            self.visit(val)
        for _ in range(len(node.values) - 1):
            if isinstance(node.op, ast.And): self.code.append(self.opcodes['BOOL_AND'])
            elif isinstance(node.op, ast.Or): self.code.append(self.opcodes['BOOL_OR'])

    def visit_Subscript(self, node):
        self.visit(node.value)
        self.visit(node.slice)
        self.code.append(self.opcodes['GET_SUBSCRIPT'])

    def compile_node(self, node):
        self.visit(node)
        self.code.append(self.opcodes['RETURN'])
        return self.serialize()

    def serialize(self):
        b = bytearray()
        b.extend(struct.pack('<H', len(self.consts)))
        for c in self.consts:
            if isinstance(c, int) and not isinstance(c, bool):
                b.append(0); b.extend(struct.pack('<H', 4)); b.extend(struct.pack('<i', c))
            elif isinstance(c, float):
                b.append(1); b.extend(struct.pack('<H', 8)); b.extend(struct.pack('<d', c))
            elif isinstance(c, str):
                b.append(2)
                enc = c.encode('utf-8')
                b.extend(struct.pack('<H', len(enc))); b.extend(enc)
            elif isinstance(c, bool):
                b.append(3); b.extend(struct.pack('<H', 1)); b.append(int(c))
            elif c is None:
                b.append(4); b.extend(struct.pack('<H', 0))

        b.extend(self.code)
        return bytes(b)

_CALLOBF_NAMES = frozenset({
    '_call', '_resolve', '_decode', '_method_call', '_get_attr',
    '_set_attr', '_get_item', '_set_item', '_resolve2', '_resolve3',
    '_call2', '_get_attr2', '_method_call2',
})

_UNSUPPORTED_TYPES = (
    ast.List, ast.Dict, ast.Set, ast.Tuple, ast.IfExp,
    ast.Starred, ast.Slice, ast.Lambda,
    ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp,
    ast.Yield, ast.YieldFrom, ast.Await,
)

_CONST_TYPES = (int, float, str, bool, type(None))

class VMVirtualizer(ast.NodeTransformer):
    def __init__(self, opcodes=None, xor_key=None, vmentry_name=None):
        self.opcodes = opcodes or _OPCODES
        self.xor_key = xor_key or _VM_XOR_KEY
        self.vmentry_name = vmentry_name or _VM_ENTRY_NAME
        self._target_depth = 0

    def _is_supported(self, node):
        for sub in ast.walk(node):
            if isinstance(sub, _UNSUPPORTED_TYPES):
                return False
            if isinstance(sub, ast.Call):
                if not isinstance(sub.func, (ast.Name, ast.Attribute)):
                    return False
                if sub.keywords:
                    return False
                for arg in sub.args:
                    if isinstance(arg, ast.Starred):
                        return False
            elif isinstance(sub, ast.BinOp):
                if not isinstance(sub.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow, ast.BitAnd, ast.BitOr, ast.BitXor, ast.LShift, ast.RShift)):
                    return False
            elif isinstance(sub, ast.UnaryOp):
                if not isinstance(sub.op, (ast.UAdd, ast.USub, ast.Not, ast.Invert)):
                    return False
            elif isinstance(sub, ast.Compare):
                for op in sub.ops:
                    if not isinstance(op, (ast.Gt, ast.Lt, ast.GtE, ast.LtE, ast.Eq, ast.NotEq)):
                        return False
            elif isinstance(sub, ast.BoolOp):
                if not isinstance(sub.op, (ast.And, ast.Or)):
                    return False
            elif isinstance(sub, ast.Constant):
                if not isinstance(sub.value, _CONST_TYPES):
                    return False
            elif isinstance(sub, ast.Attribute):
                if not isinstance(sub.value, ast.Name):
                    return False
        return True

    def _try_compile(self, node):
        if self._target_depth > 0: return None
        if not self._is_supported(node): return None

        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                if isinstance(sub.func, ast.Name) and sub.func.id == 'super' and not sub.args:
                    return None

        try:
            compiler = ExprCompiler(self.opcodes)
            compiler.visit(ast.Expression(body=node))
            compiler.code.append(self.opcodes['RETURN'])
            bytecode = compiler.serialize()
            b64_str = encrypt_and_encode(bytecode, self.xor_key)

            deps_list = sorted(compiler.deps.items(), key=lambda x: x[1][0])
            dep_nodes = [item[1][1] for item in deps_list]

            return b64_str, dep_nodes
        except Exception:
            return None

    def _transform(self, node):
        result = self._try_compile(node)
        if result is None: return node

        b64_str, dep_nodes = result

        args = [ast.Constant(value=b64_str)] + dep_nodes
        new_node = ast.Call(
            func=ast.Name(id=self.vmentry_name, ctx=ast.Load()),
            args=args,
            keywords=[],
        )
        return ast.copy_location(new_node, node)

    def visit_For(self, node):
        self._target_depth += 1
        node.iter = self.visit(node.iter)
        self._target_depth -= 1
        node.body = [self.visit(s) for s in node.body]
        node.orelse = [self.visit(s) for s in node.orelse]
        return node

    def visit_While(self, node):
        self._target_depth += 1
        node.test = self.visit(node.test)
        self._target_depth -= 1
        node.body = [self.visit(s) for s in node.body]
        node.orelse = [self.visit(s) for s in node.orelse]
        return node

    def visit_With(self, node):
        self._target_depth += 1
        for item in node.items:
            item.context_expr = self.visit(item.context_expr)
        self._target_depth -= 1
        for item in node.items:
            if item.optional_vars:
                item.optional_vars = self.visit(item.optional_vars)
        node.body = [self.visit(s) for s in node.body]
        return node

    def visit_Assign(self, node):
        self._target_depth += 1
        new_targets = [self.visit(t) for t in node.targets]
        self._target_depth -= 1
        new_value = self.visit(node.value)
        return ast.Assign(targets=new_targets, value=new_value)

    def visit_AugAssign(self, node):
        self._target_depth += 1
        target = self.visit(node.target)
        self._target_depth -= 1
        new_value = self.visit(node.value)
        return ast.AugAssign(target=target, op=node.op, value=new_value)

    def visit_AnnAssign(self, node):
        self._target_depth += 1
        target = self.visit(node.target)
        self._target_depth -= 1
        new_value = self.visit(node.value) if node.value else None
        return ast.AnnAssign(target=target, annotation=node.annotation, value=new_value, simple=node.simple)

    def visit_Delete(self, node):
        self._target_depth += 1
        new_targets = [self.visit(t) for t in node.targets]
        self._target_depth -= 1
        return ast.Delete(targets=new_targets)

    def visit_NamedExpr(self, node):
        self._target_depth += 1
        target = self.visit(node.target)
        self._target_depth -= 1
        new_value = self.visit(node.value)
        return ast.NamedExpr(target=target, value=new_value)

    def visit_ListComp(self, node): return node
    def visit_SetComp(self, node): return node
    def visit_GeneratorExp(self, node): return node
    def visit_DictComp(self, node): return node

    def visit_FunctionDef(self, node):
        if node.name in _CALLOBF_NAMES: return node
        node.decorator_list = [self.visit(d) for d in node.decorator_list]
        for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
            if arg.annotation: arg.annotation = self.visit(arg.annotation)
        node.args.defaults = [self.visit(d) for d in node.args.defaults]
        node.args.kw_defaults = [self.visit(d) if d else None for d in node.args.kw_defaults]
        if node.returns: node.returns = self.visit(node.returns)
        node.body = [self.visit(s) for s in node.body]
        return node

    def visit_AsyncFunctionDef(self, node):
        return self.visit_FunctionDef(node)

    def visit_BinOp(self, node):
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)
        return self._transform(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == self.vmentry_name: return node
        node.func = self.visit(node.func)
        node.args = [self.visit(a) for a in node.args]
        return self._transform(node)

    def visit_UnaryOp(self, node):
        node.operand = self.visit(node.operand)
        return self._transform(node)

    def visit_Compare(self, node):
        node.left = self.visit(node.left)
        node.comparators = [self.visit(c) for c in node.comparators]
        return self._transform(node)

    def visit_BoolOp(self, node):
        node.values = [self.visit(v) for v in node.values]
        return self._transform(node)

    def visit_Subscript(self, node):
        node.value = self.visit(node.value)
        node.slice = self.visit(node.slice)
        return self._transform(node)

def virtualize_code(source):
    tree = ast.parse(source)
    transformer = VMVirtualizer()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    return ast.unparse(new_tree)

def build_virtualized_module(source):
    return VM_RUNTIME_CODE + "\n" + virtualize_code(source)

def self_test():
    """Самотестирование VM для гарантии корректности генерации кода."""
    print("=== Running VM Self-Test ===")
    import math

    tests = [
        ("2 + 2", {}, 4),
        ("(10 - 3) * 2.5", {}, 17.5),
        ("x + y * z", {"x": 10, "y": 5, "z": 2}, 20),
        ("math.sin(0) + 1", {"math": math}, 1.0),
        ("a > b and c < d", {"a": 10, "b": 5, "c": 2, "d": 8}, True),
        ("not (x == y)", {"x": 1, "y": 2}, True),
        ("arr[1] + 5", {"arr": [10, 20, 30]}, 25),
        ("pow(2, 3) + 1", {"pow": pow}, 9),
        ("(15 % 4) // 2", {}, 1),
        ("(x << 2) | (y >> 1)", {"x": 3, "y": 4}, 14),
        ("a ^ b", {"a": 0b1010, "b": 0b1100}, 0b0110),
        ("~x", {"x": 5}, -6),
        ("pow(2, 3, 5)", {"pow": pow}, 3),
    ]

    namespace = {}
    exec(VM_RUNTIME_CODE, namespace)
    vmentry = namespace[_VM_ENTRY_NAME]

    all_passed = True
    for expr, vars_dict, expected in tests:
        tree = ast.parse(expr, mode='eval')
        compiler = ExprCompiler(_OPCODES)
        compiler.visit(tree)
        compiler.code.append(_OPCODES['RETURN'])
        bytecode = compiler.serialize()
        b64_str = encrypt_and_encode(bytecode, _VM_XOR_KEY)

        deps_list = sorted(compiler.deps.items(), key=lambda x: x[1][0])
        dep_nodes = [item[1][1] for item in deps_list]
        dep_names = [ast.unparse(n) for n in dep_nodes]

        args = [b64_str]
        for name in dep_names:
            val = eval(name, vars_dict)
            args.append(val)

        try:
            result = vmentry(*args)
            if isinstance(expected, float) and abs(result - expected) < 1e-9:
                result = expected

            if result == expected:
                print(f"[PASS] {expr} = {result}")
            else:
                print(f"[FAIL] {expr} | Expected: {expected}, Got: {result}")
                all_passed = False
        except Exception as e:
            print(f"[ERROR] {expr} | Exception: {e}")
            all_passed = False

    if all_passed:
        print("All self-tests passed!")
    else:
        print("Some self-tests failed.")
        raise RuntimeError("VM Self-Test Failed")

if __name__ == "__main__":
    self_test()