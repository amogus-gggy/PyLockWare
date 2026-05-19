import sys
import os
from customvm import BytecodeLoader, VirtualMachine

def main():
    if len(sys.argv) < 2:
        print("CustomVM Runner - Execute CVM bytecode files")
        print()
        print("Usage: cvmrun <file.cvm>")
        print()
        print("Example:")
        print("  cvmrun program.cvm")
        sys.exit(1)
    
    cvm_file = sys.argv[1]
    
    if not os.path.exists(cvm_file):
        print(f"Error: File '{cvm_file}' not found")
        sys.exit(1)
    
    try:
        loader = BytecodeLoader()
        code, opcode_set, crypto, const_pool, integrity_hash, func_pool, string_pool = loader.load(cvm_file)

        vm = VirtualMachine()
        vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash, func_pool, string_pool)
        
        result = vm.execute()
        
        if result is not None:
            print(f"\nExecution completed. Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
