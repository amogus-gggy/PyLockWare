from customvm import VMBuilder, BytecodeLoader, VirtualMachine

builder = VMBuilder()

builder.push_imm(15)
builder.push_imm(7)
builder.and_op()
builder.push_imm(1)
builder.syscall()

builder.push_imm(12)
builder.push_imm(10)
builder.or_op()
builder.push_imm(1)
builder.syscall()

builder.push_imm(15)
builder.push_imm(10)
builder.xor_op()
builder.push_imm(1)
builder.syscall()

builder.push_imm(5)
builder.not_op()
builder.push_imm(1)
builder.syscall()

builder.push_imm(8)
builder.push_imm(2)
builder.shl()
builder.push_imm(1)
builder.syscall()

builder.push_imm(32)
builder.push_imm(2)
builder.shr()
builder.push_imm(1)
builder.syscall()

builder.halt()

builder.build('bitwise.cvm')

loader = BytecodeLoader()
code, opcode_set, crypto, const_pool, integrity_hash = loader.load('bitwise.cvm')

vm = VirtualMachine()
vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
vm.execute()
