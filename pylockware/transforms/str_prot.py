import ast
import base64
import zlib
import random
import string
from pylockware.core.name_generator import generate_random_name

class StringProtectionTransformer(ast.NodeTransformer):
    """AST transformer to protect string literals using base64 and zlib."""

    def __init__(self, name_gen_settings='english'):
        self.string_counter = 0
        self.protected_strings = {}
        self.name_gen_settings = name_gen_settings
        
        # Track if we're inside a @skip_obf function/class
        self.skip_obf_depth = 0

        # Generate completely random names for helper functions
        self.decode_func_name = self._generate_random_name()
        self.fstring_func_name = self._generate_random_name()
        self.format_func_name = self._generate_random_name()
        self.protected_str_prefix = self._generate_random_name()
    
    def _generate_random_name(self, prefix=None):
        """Generate a random name. If prefix is provided, use it; otherwise generate completely random name."""
        if prefix:
            return generate_random_name(f"_{prefix}_", self.name_gen_settings)
        else:
            # Generate completely random name without recognizable pattern
            return generate_random_name("_", self.name_gen_settings)
    
    def _has_skip_obf_decorator(self, node):
        """Check if node has @skip_obf decorator"""
        if not hasattr(node, 'decorator_list'):
            return False
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == 'skip_obf':
                return True
            elif isinstance(decorator, ast.Attribute) and decorator.attr == 'skip_obf':
                return True
        return False
    
    def visit_FunctionDef(self, node):
        """Track when entering/exiting functions with @skip_obf"""
        if self._has_skip_obf_decorator(node):
            self.skip_obf_depth += 1
            self.generic_visit(node)
            self.skip_obf_depth -= 1
            return node
        return self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node):
        """Track when entering/exiting async functions with @skip_obf"""
        if self._has_skip_obf_decorator(node):
            self.skip_obf_depth += 1
            self.generic_visit(node)
            self.skip_obf_depth -= 1
            return node
        return self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Track when entering/exiting classes with @skip_obf"""
        if self._has_skip_obf_decorator(node):
            self.skip_obf_depth += 1
            self.generic_visit(node)
            self.skip_obf_depth -= 1
            return node
        return self.generic_visit(node)

    def visit_Str(self, node):
        """Handle string literals in older Python versions."""
        if self.skip_obf_depth > 0:
            return node
        return self._protect_string(node)

    def visit_Constant(self, node):
        """Handle string constants in newer Python versions."""
        if self.skip_obf_depth > 0:
            return node
        
        if isinstance(node.value, str):
            return self._protect_string(node)

        return node

    def visit_JoinedStr(self, node):
        """Handle f-strings - convert to helper function calls for better protection."""
        if self.skip_obf_depth > 0:
            return node

        # Collect all values from the f-string

        args = []

        for value in node.values:
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                # Protect string literals in f-strings

                protected = self._protect_string(value)

                args.append(protected)

            elif isinstance(value, ast.FormattedValue):
                # Handle formatted values

                if isinstance(value.value, ast.Constant) and isinstance(
                        value.value.value, str
                ):
                    # Protect the string literal inside the formatted value

                    protected_literal = self._protect_string(value.value)

                    value.value = protected_literal

                args.append(value.value)

            else:
                # Keep expressions as-is

                args.append(value)

        # Always convert f-strings to helper function call for better protection

        if len(args) > 0:
            # Create a call to the randomly named helper function

            return ast.Call(
                func=ast.Name(id=self.fstring_func_name, ctx=ast.Load()),
                args=args,
                keywords=[],
            )

        else:
            # Empty f-string, return empty string

            return ast.Constant(value="")

    def visit_Call(self, node):
        """Handle function calls, especially print() with string arguments."""

        # Check if this is a print call

        if isinstance(node.func, ast.Name) and node.func.id == "print":
            # Protect string arguments in print calls

            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    protected_arg = self._protect_string(arg)

                    # Replace the argument with the protected version

                    node.args[node.args.index(arg)] = protected_arg

                elif isinstance(arg, ast.JoinedStr):
                    # Handle f-strings in print calls

                    protected_fstring = self.visit_JoinedStr(arg)

                    node.args[node.args.index(arg)] = protected_fstring

        # Continue visiting other nodes

        return self.generic_visit(node)

    def visit_FormattedValue(self, node):
        """Handle individual formatted values in f-strings."""

        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            # Protect string literals in formatted values

            protected = self._protect_string(node.value)

            node.value = protected

        return self.generic_visit(node)

    def _protect_string(self, node):
        """Protect a string node by encoding it."""

        original_string = node.value if hasattr(node, "value") else node.s

        # Skip empty strings only

        if len(original_string) == 0:
            return node

        # Skip strings that look like they might be code or imports (be more selective)

        suspicious_patterns = [
            "import ",
            "def ",
            "class ",
            "from ",
            "return ",
            "yield ",
            "raise ",
            "assert ",
        ]

        if any(
                original_string.strip().startswith(pattern)
                for pattern in suspicious_patterns
        ):
            return node

        # Skip format strings that contain braces AND format specifiers (be more specific)

        if (
                "{" in original_string
                and "}" in original_string
                and any(
            spec in original_string for spec in ["%s", "%d", "%f", "{:", "format"]
        )
        ):
            return node

        # Protect the string

        # Generate a completely random variable name instead of using counter
        var_name = self._generate_random_name()

        # Encode with base64 and zlib

        encoded = base64.b64encode(
            zlib.compress(original_string.encode("utf-8"))
        ).decode("utf-8")

        self.protected_strings[var_name] = encoded

        # Return a Name node that will be replaced later

        return ast.Name(id=var_name, ctx=ast.Load())

    def apply_protection(self, code):
        """Apply string protection to Python code."""

        try:
            # Parse the code

            tree = ast.parse(code)

            # Transform the tree

            # Use the same name generator settings as the current instance
            transformer = StringProtectionTransformer(name_gen_settings=getattr(self, 'name_gen_settings', 'english'))

            protected_tree = transformer.visit(tree)

            # Add string decoding helper at the beginning

            if transformer.protected_strings:
                # Define the protected string prefix as a global variable
                protected_prefix_var = f"PROTECTED_STR_PREFIX_{transformer.protected_str_prefix[1:]}"
                
                # Create the decoder function with random names
                decoder_code = f"""import base64
import zlib

# Global variable for protected string prefix
{protected_prefix_var} = '{transformer.protected_str_prefix}'

def {transformer.decode_func_name}(encoded_str):
    return zlib.decompress(base64.b64decode(encoded_str.encode('utf-8'))).decode('utf-8')

# Advanced f-string protection helpers
def {transformer.fstring_func_name}(*args):
    \"\"\"Helper function for protected f-strings.\"\"\"
    result = ""
    for arg in args:
        if isinstance(arg, str) and arg.startswith({protected_prefix_var}):
            # This is a protected string, decode it
            var_name = arg
            if var_name in globals():
                result += globals()[var_name]
            else:
                result += arg
        else:
            # This is an expression result
            result += str(arg)
    return result

def {transformer.format_func_name}(template, *args):
    \"\"\"Alternative f-string formatter for complex cases.\"\"\"
    try:
        # Decode template if it's protected
        if isinstance(template, str) and template.startswith({protected_prefix_var}):
            if template in globals():
                template = globals()[template]

        # Simple string formatting
        return template.format(*args)
    except:
        # Fallback to basic concatenation
        result = str(template)
        for arg in args:
            result += str(arg)
        return result
"""

                # Add protected string variables

                for var_name, encoded_value in transformer.protected_strings.items():
                    decoder_code += f"{var_name} = {transformer.decode_func_name}('{encoded_value}')\n"

                # Parse the decoder code

                decoder_tree = ast.parse(decoder_code)

                # Combine the decoder tree with the protected tree

                decoder_tree.body.extend(protected_tree.body)

                protected_tree = decoder_tree

            # Convert back to code

            protected_code = ast.unparse(protected_tree)

            return protected_code

        except Exception as e:

            return code

def protect_strings_in_file(file_path):
    """Protect strings in a Python file."""

    try:
        with open(file_path, encoding="utf-8") as f:
            original_code = f.read()

        protector = StringProtectionTransformer()

        protected_code = protector.apply_protection(original_code)

        if protected_code != original_code:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(protected_code)

            print(
                f"Protected {len(protector.protected_strings)} strings in {file_path}"
            )

            return True

        return False

    except Exception as e:
        print(f"Error protecting strings in {file_path}: {e}")

        return False

def protect_strings_in_directory(directory):
    """Protect strings in all Python files in a directory."""

    from pathlib import Path

    protected_files = 0

    total_strings = 0

    for py_file in Path(directory).rglob("*.py"):
        if protect_strings_in_file(py_file):
            protected_files += 1

            # Count protected strings by reading the file again

            with open(py_file, encoding="utf-8") as f:
                content = f.read()

                total_strings += content.count("_protected_str_")

    print(
        f"Protected strings in {protected_files} files ({total_strings} total strings)"
    )

    return protected_files, total_strings
