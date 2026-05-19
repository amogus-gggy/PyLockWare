import sys
import os
from customvm import VMBuilder, BytecodeLoader, VirtualMachine
from customvm.compiler import PythonCompiler

def main():
    if len(sys.argv) < 2:
        print("CustomVM Builder - Build Python scripts to CVM bytecode")
        print()
        print("Usage: cvmbuild <input.py> [output.cvm]")
        print()
        print("Example:")
        print("  cvmbuild script.py")
        print("  cvmbuild script.py protected.cvm")
        sys.exit(1)

    input_file = sys.argv[1]

    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        base = os.path.splitext(input_file)[0]
        output_file = f"{base}.cvm"

    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        sys.exit(1)

    print(f"Building: {input_file} -> {output_file}")

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()

        builder = VMBuilder()
        compiler = PythonCompiler(builder)
        compiler.compile(source_code)
        builder.build(output_file)

        file_size = os.path.getsize(output_file)
        print(f"Success! Built {output_file} ({file_size} bytes)")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
