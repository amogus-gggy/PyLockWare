from customvm import VMBuilder, BytecodeLoader, VirtualMachine

builder = VMBuilder()

idx1 = builder.add_const(100)
idx2 = builder.add_const(200)
idx3 = builder.add_const(300)

builder.load_const(idx1)
builder.load_const(idx2)
builder.add()
builder.load_const(idx3)
builder.add()

builder.push_imm(1)
builder.syscall()

builder.halt()

builder.build('constants.cvm')

loader = BytecodeLoader()
code, opcode_set, crypto, const_pool, integrity_hash = loader.load('constants.cvm')

vm = VirtualMachine()
vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
vm.execute()
