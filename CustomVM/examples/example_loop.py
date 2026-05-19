from customvm import VMBuilder, BytecodeLoader, VirtualMachine

builder = VMBuilder()

builder.push_imm(1)
builder.pop_reg(0)

builder.add_label('loop_start')
builder.push_reg(0)
builder.push_imm(1)
builder.syscall()

builder.push_reg(0)
builder.push_imm(1)
builder.add()
builder.pop_reg(0)

builder.push_reg(0)
builder.push_imm(11)
builder.cmp()
builder.jnz('loop_start')

builder.halt()

builder.build('loop.cvm')

loader = BytecodeLoader()
code, opcode_set, crypto, const_pool, integrity_hash = loader.load('loop.cvm')

vm = VirtualMachine()
vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
vm.execute()
