import sys
import os
import base64
import tempfile
from customvm import VMBuilder, BytecodeLoader, VirtualMachine

def encrypt_and_create_standalone(input_file):
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found")
        return False
    
    print(f"[*] Reading: {input_file}")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    print("[*] Building VM bytecode...")
    builder = VMBuilder()
    
    try:
        exec_globals = {'builder': builder}
        exec(source_code, exec_globals)
    except Exception as e:
        print(f"Error executing builder script: {e}")
        return False
    
    temp_cvm = f"{input_file}.tmp.cvm"
    builder.build(temp_cvm)
    print(f"[+] Bytecode built: {os.path.getsize(temp_cvm)} bytes")
    
    with open(temp_cvm, 'rb') as f:
        cvm_data = f.read()
    
    os.remove(temp_cvm)
    
    encoded_cvm = base64.b64encode(cvm_data).decode('ascii')
    
    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name}_vm.py"
    
    standalone_code = f'''import base64
import tempfile
import os

EMBEDDED_CVM = base64.b64decode(b'{encoded_cvm}')

def main():
    try:
        from customvm import BytecodeLoader, VirtualMachine
    except ImportError:
        print("Error: customvm not installed. Run: pip install customvm")
        return
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.cvm') as f:
        f.write(EMBEDDED_CVM)
        temp_path = f.name
    
    try:
        loader = BytecodeLoader()
        code, opcode_set, crypto, const_pool, integrity_hash, func_pool, string_pool = loader.load(temp_path)

        vm = VirtualMachine()
        vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash, func_pool, string_pool)

        result = vm.execute()

        if result is not None:
            print(f"Result: {{result}}")
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == '__main__':
    main()
'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(standalone_code)
    
    print(f"[+] Created standalone file: {output_file}")
    print(f"[+] File size: {os.path.getsize(output_file)} bytes")
    print(f"\n[*] Testing execution...")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.cvm') as f:
            f.write(cvm_data)
            temp_path = f.name
        
        loader = BytecodeLoader()
        code, opcode_set, crypto, const_pool, integrity_hash = loader.load(temp_path)
        
        vm = VirtualMachine()
        vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash)
        
        print("[*] Executing VM...")
        result = vm.execute()
        
        os.unlink(temp_path)
        
        print(f"\n[+] Test successful!")
        print(f"[+] You can now run: python {output_file}")
        return True
        
    except Exception as e:
        print(f"Error during test: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("CustomVM Encryptor - Create Standalone VM Files")
        print()
        print("Usage: python vm_encryptor.py <input_file.py>")
        print()
        print("Example:")
        print("  python vm_encryptor.py my_script.py")
        print()
        print("Output:")
        print("  Creates: my_script_vm.py (standalone executable)")
        print()
        print("The input file should use VMBuilder API:")
        print("  builder.push_imm(100)")
        print("  builder.halt()")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    print("=" * 60)
    print("CustomVM Encryptor")
    print("=" * 60)
    
    if encrypt_and_create_standalone(input_file):
        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("FAILED!")
        print("=" * 60)
        sys.exit(1)

if __name__ == '__main__':
    main()
