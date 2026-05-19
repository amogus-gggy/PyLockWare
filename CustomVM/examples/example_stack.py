from customvm import VMBuilder, BytecodeLoader, VirtualMachine

builder = VMBuilder()

builder.push_imm(10)
builder.push_imm(20)
builder.push_imm(30)

builder.dup()
builder.push_imm(1)
builder.syscall()

builder.swap()
builder.push_imm(1)
builder.syscall()

builder.rot()
builder.push_imm(1)
builder.syscall()

builder.halt()

builder.build('stack_ops.cvm')

loader = BytecodeLoader()
code, opcode_set, crypto, const_pool, integrity_hash = loader.load('stack_ops.cvm')

vm = VirtualMachine()
vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
vm.execute()
