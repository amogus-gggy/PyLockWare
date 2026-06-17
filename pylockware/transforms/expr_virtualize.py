"""
Expression Virtualization for PyLockWare.
Compiles Python expressions to custom bytecode and executes them in a VM.
"""
import ast
import base64
import struct
import uuid
import random
import sys


def _rand_name():
    return "_h_" + uuid.uuid4().hex[:8]


def _gen_opcodes():
    op_names = [
        'LOAD_VAR', 'LOAD_CONST', 'ADD', 'SUB', 'MUL', 'DIV',
        'FLOORDIV', 'MOD', 'CALL', 'RETURN', 'COMPARE_GT', 'COMPARE_LT',
        'COMPARE_GTE', 'COMPARE_LTE', 'COMPARE_EQ', 'COMPARE_NEQ',
        'NEGATE', 'NOT_', 'BOOL_AND', 'BOOL_OR', 'GET_SUBSCRIPT',
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
    return opcodes


def _gen_vm_runtime():
    opcodes = _gen_opcodes()
    handler_keys = [
        'load_var', 'load_const', 'add', 'sub', 'mul', 'div',
        'floordiv', 'mod', 'call', 'return', 'compare_gt', 'compare_lt',
        'compare_gte', 'compare_lte', 'compare_eq', 'compare_neq',
        'negate', 'not_', 'bool_and', 'bool_or', 'get_subscript',
    ]
    h_names = {k: _rand_name() for k in handler_keys}
    h_garbage = _rand_name()

    key = random.randint(1, 254)
    index_key = random.randint(1, 255)

    num_total = 48
    indices = list(range(num_total))
    random.shuffle(indices)

    real_ops = [
        ('LOAD_VAR', h_names['load_var']),
        ('LOAD_CONST', h_names['load_const']),
        ('ADD', h_names['add']),
        ('SUB', h_names['sub']),
        ('MUL', h_names['mul']),
        ('DIV', h_names['div']),
        ('FLOORDIV', h_names['floordiv']),
        ('MOD', h_names['mod']),
        ('CALL', h_names['call']),
        ('RETURN', h_names['return']),
        ('COMPARE_GT', h_names['compare_gt']),
        ('COMPARE_LT', h_names['compare_lt']),
        ('COMPARE_GTE', h_names['compare_gte']),
        ('COMPARE_LTE', h_names['compare_lte']),
        ('COMPARE_EQ', h_names['compare_eq']),
        ('COMPARE_NEQ', h_names['compare_neq']),
        ('NEGATE', h_names['negate']),
        ('NOT_', h_names['not_']),
        ('BOOL_AND', h_names['bool_and']),
        ('BOOL_OR', h_names['bool_or']),
        ('GET_SUBSCRIPT', h_names['get_subscript']),
    ]

    op_to_idx = {}
    func_array = [h_garbage] * num_total

    for op_name, h_name in real_ops:
        idx = indices.pop()
        op_to_idx[op_name] = idx
        func_array[idx] = h_name

    func_array_str = ", ".join(func_array)

    hv = h_names

    def _h(name):
        return hv[name]

    handlers = []

    handlers.append(f"""
def {_h('load_var')}(stack, code, pc, ns, names, consts):
    idx = code[pc]; pc += 1
    name = names[idx]
    if name in ns:
        stack.append(ns[name])
    else:
        _b = __builtins__
        if isinstance(_b, dict):
            stack.append(_b.get(name))
        else:
            stack.append(getattr(_b, name, None))
    return pc
""")

    handlers.append(f"""
def {_h('load_const')}(stack, code, pc, ns, names, consts):
    idx = code[pc]; pc += 1
    stack.append(consts[idx])
    return pc
""")

    handlers.append(f"""
def {_h('add')}(stack, code, pc, ns, names, consts):
    b = stack.pop(); a = stack.pop()
    stack.append(a + b)
    return pc
""")

    handlers.append(f"""
def {_h('sub')}(stack, code, pc, ns, names, consts):
    b = stack.pop(); a = stack.pop()
    stack.append(a - b)
    return pc
""")

    handlers.append(f"""
def {_h('mul')}(stack, code, pc, ns, names, consts):
    b = stack.pop(); a = stack.pop()
    stack.append(a * b)
    return pc
""")

    handlers.append(f"""
def {_h('div')}(stack, code, pc, ns, names, consts):
    b = stack.pop(); a = stack.pop()
    stack.append(a / b)
    return pc
""")

    handlers.append(f"""
def {_h('floordiv')}(stack, code, pc, ns, names, consts):
    b = stack.pop(); a = stack.pop()
    stack.append(a // b)
    return pc
""")

    handlers.append(f"""
def {_h('mod')}(stack, code, pc, ns, names, consts):
    b = stack.pop(); a = stack.pop()
    stack.append(a % b)
    return pc
""")

    handlers.append(f"""
def {_h('call')}(stack, code, pc, ns, names, consts):
    num_args = code[pc]; pc += 1
    args = [stack.pop() for _ in range(num_args)][::-1]
    func = stack.pop()
    stack.append(func(*args))
    return pc
""")

    handlers.append(f"""
def {_h('return')}(stack, code, pc, ns, names, consts):
    raise _VMReturn(stack.pop())
""")

    handlers.append(f"""
def {_h('compare_gt')}(stack, code, pc, ns, names, consts):
    b = stack.pop(); a = stack.pop()
    stack.append(a > b)
    return pc
""")

    handlers.append(f"""
def {_h('compare_lt')}(stack, code, pc, ns, names, consts):
    b = stack.pop(); a = stack.pop()
    stack.append(a < b)
    return pc
""")

    handlers.append(f"""
def {_h('compare_gte')}(stack, code, pc, ns, names, consts):
    b = stack.pop(); a = stack.pop()
    stack.append(a >= b)
    return pc
""")

    handlers.append(f"""
def {_h('compare_lte')}(stack, code, pc, ns, names, consts):
    b = stack.pop(); a = stack.pop()
    stack.append(a <= b)
    return pc
""")

    handlers.append(f"""
def {_h('compare_eq')}(stack, code, pc, ns, names, consts):
    b = stack.pop(); a = stack.pop()
    stack.append(a == b)
    return pc
""")

    handlers.append(f"""
def {_h('compare_neq')}(stack, code, pc, ns, names, consts):
    b = stack.pop(); a = stack.pop()
    stack.append(a != b)
    return pc
""")

    handlers.append(f"""
def {_h('negate')}(stack, code, pc, ns, names, consts):
    a = stack.pop()
    stack.append(-a)
    return pc
""")

    handlers.append(f"""
def {_h('not_')}(stack, code, pc, ns, names, consts):
    a = stack.pop()
    stack.append(not a)
    return pc
""")

    handlers.append(f"""
def {_h('bool_and')}(stack, code, pc, ns, names, consts):
    b = stack.pop(); a = stack.pop()
    stack.append(a and b)
    return pc
""")

    handlers.append(f"""
def {_h('bool_or')}(stack, code, pc, ns, names, consts):
    b = stack.pop(); a = stack.pop()
    stack.append(a or b)
    return pc
""")

    handlers.append(f"""
def {_h('get_subscript')}(stack, code, pc, ns, names, consts):
    idx = stack.pop(); obj = stack.pop()
    stack.append(obj[idx])
    return pc
""")

    handlers.append(f"""
def {h_garbage}(stack, code, pc, ns, names, consts):
    stack.append(None)
    return pc
""")

    handlers_str = "\n".join(handlers)

    vm_code = f"""\
class _VMReturn(Exception):
    def __init__(self, value):
        self.value = value

{handlers_str}

all_funcs = [{func_array_str}]

_VK = {key}
_VIK = {index_key}

import base64 as _b64
import struct as _struct

def _vmentry(b64_str, ns=None):
    if ns is None:
        ns = {{}}
    data = _b64.b64decode(b64_str)
    data = bytes([b ^ _VK for b in data])
    offset = 0
    num_consts = _struct.unpack('<H', data[offset:offset+2])[0]; offset += 2
    consts = []
    for _ in range(num_consts):
        ctype = data[offset]; offset += 1
        clen = _struct.unpack('<H', data[offset:offset+2])[0]; offset += 2
        cdata = data[offset:offset+clen]; offset += clen
        if ctype == 0: consts.append(_struct.unpack('<i', cdata)[0])
        elif ctype == 1: consts.append(_struct.unpack('<d', cdata)[0])
        elif ctype == 2: consts.append(cdata.decode('utf-8'))
        elif ctype == 3: consts.append(bool(cdata[0]))
        elif ctype == 4: consts.append(None)
    num_names = _struct.unpack('<H', data[offset:offset+2])[0]; offset += 2
    names = []
    for _ in range(num_names):
        nlen = data[offset]; offset += 1
        names.append(data[offset:offset+nlen].decode('utf-8')); offset += nlen
    mapping_len = _struct.unpack('<H', data[offset:offset+2])[0]; offset += 2
    encrypted_mapping = data[offset:offset+mapping_len]; offset += mapping_len
    mapping = bytes([b ^ _VIK for b in encrypted_mapping])
    code = data[offset:]
    stack = []
    pc = 0
    try:
        while pc < len(code):
            op = code[pc]; pc += 1
            pc = all_funcs[mapping[op]](stack, code, pc, ns, names, consts)
    except _VMReturn as e:
        return e.value
"""
    return vm_code, opcodes, op_to_idx, key, index_key


def encrypt_and_encode(data, key=0xA5):
    enc = bytes([b ^ key for b in data])
    return base64.b64encode(enc).decode('ascii')


_VM_RUNTIME_CODE, _OPCODES, _OP_TO_IDX, _VM_KEY, _VM_INDEX_KEY = _gen_vm_runtime()
VM_RUNTIME_CODE = _VM_RUNTIME_CODE


class ExprCompiler(ast.NodeVisitor):

    def __init__(self, opcodes, index_key, op_to_idx):
        self.opcodes = opcodes
        self.index_key = index_key
        self.op_to_idx = op_to_idx
        self.code = bytearray()
        self.consts = []
        self.names = []

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

    def add_name(self, name):
        if name not in self.names:
            self.names.append(name)
        return self.names.index(name)

    def visit_Expression(self, node):
        self.visit(node.body)

    def visit_Name(self, node):
        idx = self.add_name(node.id)
        self.code.append(self.opcodes['LOAD_VAR'])
        self.code.append(idx)

    def visit_Constant(self, node):
        idx = self.add_const(node.value)
        self.code.append(self.opcodes['LOAD_CONST'])
        self.code.append(idx)

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        if isinstance(node.op, ast.Add):
            self.code.append(self.opcodes['ADD'])
        elif isinstance(node.op, ast.Sub):
            self.code.append(self.opcodes['SUB'])
        elif isinstance(node.op, ast.Mult):
            self.code.append(self.opcodes['MUL'])
        elif isinstance(node.op, ast.Div):
            self.code.append(self.opcodes['DIV'])
        elif isinstance(node.op, ast.FloorDiv):
            self.code.append(self.opcodes['FLOORDIV'])
        elif isinstance(node.op, ast.Mod):
            self.code.append(self.opcodes['MOD'])

    def visit_Call(self, node):
        self.visit(node.func)
        for arg in node.args:
            self.visit(arg)
        self.code.append(self.opcodes['CALL'])
        self.code.append(len(node.args))

    def visit_UnaryOp(self, node):
        self.visit(node.operand)
        if isinstance(node.op, ast.USub):
            self.visit(ast.Constant(value=-1))
            self.code.append(self.opcodes['MUL'])
        elif isinstance(node.op, ast.UAdd):
            pass

    def visit_Compare(self, node):
        self.visit(node.left)
        for op, comp in zip(node.ops, node.comparators):
            self.visit(comp)
            if isinstance(op, ast.Gt):
                self.code.append(self.opcodes['COMPARE_GT'])
            elif isinstance(op, ast.Lt):
                self.code.append(self.opcodes['COMPARE_LT'])
            elif isinstance(op, ast.GtE):
                self.code.append(self.opcodes['COMPARE_GTE'])
            elif isinstance(op, ast.LtE):
                self.code.append(self.opcodes['COMPARE_LTE'])
            elif isinstance(op, ast.Eq):
                self.code.append(self.opcodes['COMPARE_EQ'])
            elif isinstance(op, ast.NotEq):
                self.code.append(self.opcodes['COMPARE_NEQ'])

    def visit_BoolOp(self, node):
        for val in node.values:
            self.visit(val)
        for _ in range(len(node.values) - 1):
            if isinstance(node.op, ast.And):
                self.code.append(self.opcodes['BOOL_AND'])
            elif isinstance(node.op, ast.Or):
                self.code.append(self.opcodes['BOOL_OR'])

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

        b.extend(struct.pack('<H', len(self.names)))
        for n in self.names:
            enc = n.encode('utf-8')
            b.append(len(enc)); b.extend(enc)

        mapping = bytearray(256)
        for i in range(256):
            mapping[i] = 0 ^ self.index_key

        for op_name in self.opcodes:
            mapping[self.opcodes[op_name]] = self.op_to_idx[op_name] ^ self.index_key

        b.extend(struct.pack('<H', len(mapping)))
        b.extend(mapping)
        b.extend(self.code)
        return bytes(b)


def compile_expr_to_b64(expr_str):
    tree = ast.parse(expr_str, mode='eval')
    compiler = ExprCompiler(_OPCODES, _VM_INDEX_KEY, _OP_TO_IDX)
    compiler.visit(tree)
    compiler.code.append(_OPCODES['RETURN'])
    bytecode = compiler.serialize()
    var_names = list(compiler.names)
    b64_str = encrypt_and_encode(bytecode, _VM_KEY)
    return b64_str, var_names


_CALLOBF_NAMES = frozenset({
    '_call', '_resolve', '_decode', '_method_call', '_get_attr',
    '_set_attr', '_get_item', '_set_item', '_resolve2', '_resolve3',
    '_call2', '_get_attr2', '_method_call2',
})

_UNSUPPORTED_TYPES = (
    ast.List, ast.Dict, ast.Set, ast.Tuple, ast.IfExp,
    ast.Attribute, ast.Starred, ast.Slice, ast.Lambda,
    ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp,
    ast.Yield, ast.YieldFrom, ast.Await,
)

_CONST_TYPES = (int, float, str, bool, type(None))


class VMVirtualizer(ast.NodeTransformer):

    def __init__(self, opcodes=None, index_key=None, op_to_idx=None):
        self.opcodes = opcodes or _OPCODES
        self.index_key = index_key or _VM_INDEX_KEY
        self.op_to_idx = op_to_idx or _OP_TO_IDX
        self._target_depth = 0

    def _is_supported(self, node):
        for sub in ast.walk(node):
            if isinstance(sub, _UNSUPPORTED_TYPES):
                return False
            if isinstance(sub, ast.Call):
                if not isinstance(sub.func, ast.Name):
                    return False
                if sub.keywords:
                    return False
                for arg in sub.args:
                    if isinstance(arg, ast.Starred):
                        return False
                for kw in sub.keywords:
                    if kw.arg is None:
                        return False
            elif isinstance(sub, ast.BinOp):
                if not isinstance(sub.op, (ast.Add, ast.Sub, ast.Mult,
                                           ast.Div, ast.FloorDiv, ast.Mod)):
                    return False
            elif isinstance(sub, ast.UnaryOp):
                if not isinstance(sub.op, (ast.UAdd, ast.USub)):
                    return False
            elif isinstance(sub, ast.Compare):
                for op in sub.ops:
                    if not isinstance(op, (ast.Gt, ast.Lt, ast.GtE, ast.LtE,
                                           ast.Eq, ast.NotEq)):
                        return False
            elif isinstance(sub, ast.BoolOp):
                if not isinstance(sub.op, (ast.And, ast.Or)):
                    return False
            elif isinstance(sub, ast.Constant):
                if not isinstance(sub.value, _CONST_TYPES):
                    return False
        return True

    def _try_compile(self, node):
        if self._target_depth > 0:
            return None
        if not self._is_supported(node):
            return None

        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                if isinstance(sub.func, ast.Name) and sub.func.id == 'super' and not sub.args:
                    return None

        try:
            compiler = ExprCompiler(self.opcodes, self.index_key, self.op_to_idx)
            compiler.visit(ast.Expression(body=node))
            compiler.code.append(self.opcodes['RETURN'])
            bytecode = compiler.serialize()
            b64_str = encrypt_and_encode(bytecode, _VM_KEY)
            var_names = list(compiler.names)
            return b64_str, var_names
        except Exception:
            return None

    def _transform(self, node):
        result = self._try_compile(node)
        if result is None:
            return node

        b64_str, var_names = result

        dict_keys = [ast.Constant(value=k) for k in var_names]
        dict_values = [ast.Name(id=k, ctx=ast.Load()) for k in var_names]
        ns_dict = ast.Dict(keys=dict_keys, values=dict_values)

        new_node = ast.Call(
            func=ast.Name(id='_vmentry', ctx=ast.Load()),
            args=[ast.Constant(value=b64_str), ns_dict],
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
        return ast.AnnAssign(
            target=target, annotation=node.annotation,
            value=new_value, simple=node.simple,
        )

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

    def visit_ListComp(self, node):
        return node

    def visit_SetComp(self, node):
        return node

    def visit_GeneratorExp(self, node):
        return node

    def visit_DictComp(self, node):
        return node

    def visit_FunctionDef(self, node):
        if node.name in _CALLOBF_NAMES:
            return node
        node.decorator_list = [self.visit(d) for d in node.decorator_list]
        for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
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

    def visit_BinOp(self, node):
        node.left = self.visit(node.left)
        node.right = self.visit(node.right)
        return self._transform(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == '_vmentry':
            return node
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
