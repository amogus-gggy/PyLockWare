"""
Virtualization Module
Converts @virtualize decorated functions to CustomVM bytecode
"""

import ast
import os
import sys
import hashlib
import secrets
import shutil
from pathlib import Path
from typing import Dict, List, Tuple

# Add vendor CustomVM to path
customvm_path = Path(__file__).parent.parent / "vendor"
if str(customvm_path) not in sys.path:
    sys.path.insert(0, str(customvm_path))

from customvm import VMBuilder
from customvm.compiler import PythonCompiler

from pylockware.core.module_base import ModuleBase


class VirtualizationModule(ModuleBase):
    """
    Module for virtualizing functions marked with @virtualize decorator.
    
    Process:
    1. Find all @virtualize decorated functions
    2. Compile each function to CVM bytecode
    3. Embed CustomVM runtime in output (no external dependencies!)
    4. Replace function with vmentry() call
    5. Embed CVM bytecode in output
    """
    
    def __init__(self, config: dict):
        super().__init__(config)
        self.virtualized_functions: Dict[str, str] = {}  # func_name -> cvm_file
        self.vm_runtime_id = secrets.token_hex(8)  # Unique ID for this build
        
    def validate_config(self) -> bool:
        """Validate module configuration"""
        return True
    
    def process(self, project_path: str, output_path: str) -> bool:
        """
        Process all Python files and virtualize @virtualize functions.
        
        Args:
            project_path: Source project directory
            output_path: Output directory for obfuscated code
            
        Returns:
            True if successful
        """
        print("[Virtualization] Starting function virtualization...")
        
        # Create VM assets directory in output
        vm_assets_dir = Path(output_path) / "__vm_assets__"
        vm_assets_dir.mkdir(exist_ok=True)
        
        # Process all Python files
        for root, dirs, files in os.walk(output_path):
            # Skip __vm_assets__ directory
            if '__vm_assets__' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    self._process_file(file_path, vm_assets_dir)
        
        # Generate VM runtime and embed CustomVM
        if self.virtualized_functions:
            self._embed_customvm(vm_assets_dir)
            self._generate_vm_runtime(vm_assets_dir)
            print(f"[Virtualization] Virtualized {len(self.virtualized_functions)} functions")
        else:
            print("[Virtualization] No @virtualize functions found")
        
        return True
    
    def _embed_customvm(self, vm_assets_dir: Path):
        """
        Embed CustomVM code directly into the build.
        No external dependencies required!
        """
        print("[Virtualization] Embedding CustomVM runtime...")
        
        # Source CustomVM directory (from vendor)
        customvm_src = Path(__file__).parent.parent / "vendor" / "customvm"
        
        if not customvm_src.exists():
            print(f"[Virtualization] ERROR: CustomVM not found at {customvm_src}")
            return
        
        # Target directory
        customvm_target = vm_assets_dir / "customvm"
        customvm_target.mkdir(exist_ok=True)
        
        # Copy essential CustomVM files
        essential_files = [
            '__init__.py',
            'vm.py',
            'opcodes.py',
            'crypto.py',
            'loader.py',
            'builder.py',  # Needed for BytecodeLoader
        ]
        
        for filename in essential_files:
            src_file = customvm_src / filename
            dst_file = customvm_target / filename
            
            if src_file.exists():
                shutil.copy2(src_file, dst_file)
                print(f"[Virtualization]   Embedded: {filename}")
            else:
                print(f"[Virtualization]   WARNING: {filename} not found")
    
    def _process_file(self, file_path: Path, vm_assets_dir: Path):
        """Process a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            tree = ast.parse(source)
            transformer = VirtualizationTransformer(file_path.stem, vm_assets_dir, self.vm_runtime_id)
            new_tree = transformer.visit(tree)
            
            if transformer.modified:
                # Add VM runtime import at the top
                import_node = ast.ImportFrom(
                    module='__vm_assets__._vm_runtime',
                    names=[ast.alias(name='vmentry', asname=None)],
                    level=0
                )
                new_tree.body.insert(0, import_node)
                
                # Write modified file
                new_source = ast.unparse(new_tree)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_source)
                
                # Track virtualized functions
                self.virtualized_functions.update(transformer.virtualized_functions)
                
        except Exception as e:
            print(f"[Virtualization] Error processing {file_path}: {e}")
    
    def _generate_vm_runtime(self, vm_assets_dir: Path):
        """Generate unique VM runtime for this build"""
        runtime_code = f'''"""
CustomVM Runtime - Generated for build {self.vm_runtime_id}
DO NOT MODIFY - Auto-generated code
Embedded CustomVM - No external dependencies required
"""

import sys
import os
from pathlib import Path

# Import embedded CustomVM
_vm_path = Path(__file__).parent / "customvm"
if str(_vm_path) not in sys.path:
    sys.path.insert(0, str(_vm_path.parent))

from customvm import BytecodeLoader, VirtualMachine


def vmentry(bytecode_file: str, *args, **kwargs):
    """
    VM entry point for virtualized functions.
    
    Args:
        bytecode_file: Name of the .cvm file (without path)
        *args: Arguments to pass to the virtualized function
        **kwargs: Keyword arguments to pass to the virtualized function
        
    Returns:
        Result from the virtualized function
    """
    # Locate bytecode file
    assets_dir = Path(__file__).parent
    cvm_path = assets_dir / bytecode_file
    
    if not cvm_path.exists():
        raise FileNotFoundError(f"VM bytecode not found: {{bytecode_file}}")
    
    # Load and execute
    try:
        loader = BytecodeLoader()
        # Loader returns 7 values: code, opcode_set, crypto, const_pool, integrity_hash, func_pool, string_pool
        result = loader.load(str(cvm_path))
        
        if len(result) == 7:
            code, opcode_set, crypto, const_pool, integrity_hash, func_pool, string_pool = result
        else:
            # Fallback for older format
            code, opcode_set, crypto, const_pool, integrity_hash = result[:5]
            func_pool = []
            string_pool = []
        
        # Inject arguments into const_pool
        # The compiled code expects arguments at the beginning of const_pool
        if args:
            # Prepend arguments to const_pool (keeping their original types)
            const_pool = list(args) + list(const_pool)
        
        vm = VirtualMachine()
        vm.load_bytecode(code, opcode_set, crypto, const_pool, integrity_hash, func_pool, string_pool)
        
        # Execute the VM
        result = vm.execute()
        
        return result
        
    except Exception as e:
        raise RuntimeError(f"VM execution failed: {{e}}")


# Build ID: {self.vm_runtime_id}
__vm_build_id__ = "{self.vm_runtime_id}"
'''
        
        runtime_file = vm_assets_dir / "_vm_runtime.py"
        with open(runtime_file, 'w', encoding='utf-8') as f:
            f.write(runtime_code)
        
        # Create __init__.py
        init_file = vm_assets_dir / "__init__.py"
        with open(init_file, 'w', encoding='utf-8') as f:
            f.write(f'# VM Assets - Build {self.vm_runtime_id}\n')
        
        print(f"[Virtualization] Generated VM runtime with build ID: {self.vm_runtime_id}")


class VirtualizationTransformer(ast.NodeTransformer):
    """AST transformer to replace @virtualize functions with vmentry calls"""
    
    def __init__(self, module_name: str, vm_assets_dir: Path, build_id: str):
        self.module_name = module_name
        self.vm_assets_dir = vm_assets_dir
        self.build_id = build_id
        self.virtualized_functions: Dict[str, str] = {}
        self.modified = False
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        """Visit function definition and check for @virtualize decorator"""
        # Check if function has @virtualize decorator
        has_virtualize = False
        new_decorators = []
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'virtualize':
                has_virtualize = True
                # Remove @virtualize decorator
            else:
                new_decorators.append(decorator)
        
        if has_virtualize:
            # Compile function to CVM bytecode
            cvm_file = self._virtualize_function(node)
            
            if cvm_file:
                # Replace function with vmentry wrapper
                wrapper = self._create_vmentry_wrapper(node, cvm_file)
                wrapper.decorator_list = new_decorators
                self.modified = True
                return wrapper
        
        # Keep original function
        node.decorator_list = new_decorators
        return self.generic_visit(node)
    
    def _virtualize_function(self, func_node: ast.FunctionDef) -> str:
        """
        Compile function to CVM bytecode.
        
        Returns:
            CVM filename (without path)
        """
        try:
            # Generate unique filename
            func_hash = hashlib.sha256(
                f"{self.module_name}_{func_node.name}_{self.build_id}".encode()
            ).hexdigest()[:12]
            cvm_filename = f"{func_node.name}_{func_hash}.cvm"
            cvm_path = self.vm_assets_dir / cvm_filename
            
            # Extract function parameters
            param_names = [arg.arg for arg in func_node.args.args]
            
            # Create inline version of function body
            # For functions with parameters, we'll load them from const_pool
            
            if len(param_names) == 1:
                # Single parameter function
                # Load parameter from const_pool[0] (injected by vmentry)
                param_name = param_names[0]
                
                # Create wrapper that loads argument from const_pool index 0
                wrapper_source = f"""# Load parameter from const_pool
{param_name} = 0  # Placeholder constant, will be replaced by vmentry
# Function body:
"""
                for stmt in func_node.body:
                    wrapper_source += ast.unparse(stmt) + "\n"
                
            elif len(param_names) == 0:
                # No parameters - just compile body
                wrapper_source = ""
                for stmt in func_node.body:
                    wrapper_source += ast.unparse(stmt) + "\n"
            else:
                # Multiple parameters - load from const_pool[0], const_pool[1], etc.
                wrapper_source = "# Load parameters from const_pool\n"
                for i, param in enumerate(param_names):
                    wrapper_source += f'{param} = {i}  # Placeholder, will be replaced by vmentry\n'
                for stmt in func_node.body:
                    wrapper_source += ast.unparse(stmt) + "\n"
            
            # Create VM builder and compile
            builder = VMBuilder()
            compiler = PythonCompiler(builder)
            
            try:
                # Try to compile the function body
                compiler.compile(wrapper_source)
                builder.build(str(cvm_path))
                
                self.virtualized_functions[func_node.name] = cvm_filename
                print(f"[Virtualization] Compiled {func_node.name} -> {cvm_filename}")
                if param_names:
                    print(f"[Virtualization]   Parameters: {param_names}")
                return cvm_filename
                
            except Exception as e:
                print(f"[Virtualization] Failed to compile {func_node.name}: {e}")
                print(f"[Virtualization] Error: {str(e)}")
                print(f"[Virtualization] CustomVM supports: arithmetic, strings, control flow, string methods")
                print(f"[Virtualization] Function will not be virtualized")
                return None
                
        except Exception as e:
            print(f"[Virtualization] Error virtualizing {func_node.name}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_vmentry_wrapper(self, func_node: ast.FunctionDef, cvm_file: str) -> ast.FunctionDef:
        """
        Create a wrapper function that calls vmentry.
        
        Original:
            @virtualize
            def foo(x, y):
                return x + y
        
        Becomes:
            def foo(x, y):
                return vmentry('foo_abc123.cvm', x, y)
        """
        # Collect all function arguments
        arg_names = []
        
        # Regular arguments
        for arg in func_node.args.args:
            arg_names.append(ast.Name(id=arg.arg, ctx=ast.Load()))
        
        # *args
        if func_node.args.vararg:
            arg_names.append(ast.Starred(
                value=ast.Name(id=func_node.args.vararg.arg, ctx=ast.Load()),
                ctx=ast.Load()
            ))
        
        # **kwargs
        kwargs = []
        if func_node.args.kwarg:
            kwargs.append(ast.keyword(
                arg=None,
                value=ast.Name(id=func_node.args.kwarg.arg, ctx=ast.Load())
            ))
        
        # Create vmentry call with all arguments
        vmentry_call = ast.Call(
            func=ast.Name(id='vmentry', ctx=ast.Load()),
            args=[ast.Constant(value=cvm_file)] + arg_names,  # CVM filename + function args
            keywords=kwargs
        )
        
        # Create return statement
        return_stmt = ast.Return(value=vmentry_call)
        
        # Create new function with same signature
        new_func = ast.FunctionDef(
            name=func_node.name,
            args=func_node.args,
            body=[return_stmt],
            decorator_list=[],
            returns=func_node.returns,
            type_comment=func_node.type_comment,
            lineno=func_node.lineno,
            col_offset=func_node.col_offset
        )
        
        return ast.fix_missing_locations(new_func)
