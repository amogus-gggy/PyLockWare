import sys
import os
import glob
from customvm import VMBuilder

def convert_directory(input_dir, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(input_dir, 'cvm_output')
    
    os.makedirs(output_dir, exist_ok=True)
    
    py_files = glob.glob(os.path.join(input_dir, '*.py'))
    
    if not py_files:
        print(f"No Python files found in {input_dir}")
        return
    
    print(f"Found {len(py_files)} Python files")
    print(f"Output directory: {output_dir}")
    print()
    
    converted = 0
    failed = 0
    
    for py_file in py_files:
        basename = os.path.basename(py_file)
        name_without_ext = os.path.splitext(basename)[0]
        output_file = os.path.join(output_dir, f"{name_without_ext}.cvm")
        
        print(f"Converting: {basename}...", end=' ')
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            builder = VMBuilder()
            exec_globals = {'builder': builder}
            exec(source_code, exec_globals)
            builder.build(output_file)
            
            file_size = os.path.getsize(output_file)
            print(f"OK ({file_size} bytes)")
            converted += 1
            
        except Exception as e:
            print(f"FAILED ({e})")
            failed += 1
    
    print()
    print(f"Conversion complete: {converted} succeeded, {failed} failed")
    print(f"Output files saved to: {output_dir}")

def main():
    if len(sys.argv) < 2:
        print("CustomVM Batch Converter - Convert multiple Python files to CVM")
        print()
        print("Usage: cvmbatch <input_directory> [output_directory]")
        print()
        print("Example:")
        print("  cvmbatch ./scripts")
        print("  cvmbatch ./scripts ./protected")
        sys.exit(1)
    
    input_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) >= 3 else None
    
    if not os.path.isdir(input_dir):
        print(f"Error: '{input_dir}' is not a directory")
        sys.exit(1)
    
    convert_directory(input_dir, output_dir)

if __name__ == '__main__':
    main()
