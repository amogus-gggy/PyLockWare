from customvm import VMBuilder, BytecodeLoader, VirtualMachine

builder = VMBuilder()

builder.push_imm(100)
builder.push_imm(0)
builder.store_mem()

builder.push_imm(200)
builder.push_imm(4)
builder.store_mem()

builder.push_imm(0)
builder.load_mem()
builder.push_imm(4)
builder.load_mem()
builder.add()

builder.push_imm(1)
builder.syscall()

builder.halt()

builder.build('memory.cvm')

loader = BytecodeLoader()
code, opcode_set, crypto, const_pool, integrity_hash = loader.load('memory.cvm')

vm = VirtualMachine()
vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
vm.execute()
