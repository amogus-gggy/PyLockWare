import sys
import os
import subprocess
from customvm import VMBuilder

def create_standalone_executable(cvm_file, output_name=None):
    if not os.path.exists(cvm_file):
        print(f"Error: CVM file '{cvm_file}' not found")
        return False
    
    if output_name is None:
        base = os.path.splitext(os.path.basename(cvm_file))[0]
        output_name = base
    
    runner_script = f"{output_name}_runner.py"
    
    with open(cvm_file, 'rb') as f:
        cvm_data = f.read()
    
    import base64
    encoded_cvm = base64.b64encode(cvm_data).decode('ascii')
    
    runner_code = f'''import base64
import tempfile
import os
from customvm import BytecodeLoader, VirtualMachine

EMBEDDED_CVM = base64.b64decode(b'{encoded_cvm}')

def main():
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
    
    with open(runner_script, 'w', encoding='utf-8') as f:
        f.write(runner_code)
    
    print(f"Created runner script: {runner_script}")
    
    try:
        print("Building standalone executable with PyInstaller...")
        cmd = [
            'pyinstaller',
            '--onefile',
            '--noconsole',
            '--name', output_name,
            runner_script
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Success! Executable created: dist/{output_name}.exe")
            os.remove(runner_script)
            return True
        else:
            print(f"PyInstaller error: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("PyInstaller not found. Install with: pip install pyinstaller")
        print(f"Standalone runner script saved as: {runner_script}")
        return False

def main():
    if len(sys.argv) < 2:
        print("CustomVM Standalone Builder - Create standalone executables")
        print()
        print("Usage: cvmstandalone <file.cvm> [output_name]")
        print()
        print("Example:")
        print("  cvmstandalone program.cvm")
        print("  cvmstandalone program.cvm myapp")
        print()
        print("Requires: pip install pyinstaller")
        sys.exit(1)
    
    cvm_file = sys.argv[1]
    output_name = sys.argv[2] if len(sys.argv) >= 3 else None
    
    create_standalone_executable(cvm_file, output_name)

if __name__ == '__main__':
    main()
