from customvm import VMBuilder, BytecodeLoader, VirtualMachine

builder = VMBuilder()

builder.add_label('factorial')
builder.push_reg(0)
builder.push_imm(1)
builder.cmp()
builder.jle('base_case')

builder.push_reg(0)
builder.push_reg(0)
builder.push_imm(1)
builder.sub()
builder.pop_reg(0)
builder.call('factorial')
builder.mul()
builder.ret()

builder.add_label('base_case')
builder.push_imm(1)
builder.ret()

builder.push_imm(5)
builder.pop_reg(0)
builder.call('factorial')
builder.push_imm(1)
builder.syscall()
builder.halt()

builder.build('factorial.cvm')

loader = BytecodeLoader()
code, opcode_set, crypto, const_pool, integrity_hash = loader.load('factorial.cvm')

vm = VirtualMachine()
vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
vm.execute()
