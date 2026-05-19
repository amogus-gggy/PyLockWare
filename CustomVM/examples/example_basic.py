from customvm import VMBuilder, BytecodeLoader, VirtualMachine

builder = VMBuilder()

builder.push_imm(10)
builder.push_imm(20)
builder.add()
builder.push_imm(1)
builder.syscall()
builder.halt()

builder.build('hello.cvm')

loader = BytecodeLoader()
code, opcode_set, crypto, const_pool, integrity_hash = loader.load('hello.cvm')

vm = VirtualMachine()
vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
result = vm.execute()
