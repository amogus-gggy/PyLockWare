from customvm import VMBuilder, BytecodeLoader, VirtualMachine

builder = VMBuilder()

builder.push_imm(72)
builder.push_imm(2)
builder.syscall()

builder.push_imm(101)
builder.push_imm(2)
builder.syscall()

builder.push_imm(108)
builder.push_imm(2)
builder.syscall()

builder.push_imm(108)
builder.push_imm(2)
builder.syscall()

builder.push_imm(111)
builder.push_imm(2)
builder.syscall()

builder.push_imm(32)
builder.push_imm(2)
builder.syscall()

builder.push_imm(87)
builder.push_imm(2)
builder.syscall()

builder.push_imm(111)
builder.push_imm(2)
builder.syscall()

builder.push_imm(114)
builder.push_imm(2)
builder.syscall()

builder.push_imm(108)
builder.push_imm(2)
builder.syscall()

builder.push_imm(100)
builder.push_imm(2)
builder.syscall()

builder.halt()

builder.build('hello_world.cvm')

loader = BytecodeLoader()
code, opcode_set, crypto, const_pool, integrity_hash = loader.load('hello_world.cvm')

vm = VirtualMachine()
vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
vm.execute()
