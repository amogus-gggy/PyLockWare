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
        self.string_protected = False
        self.name_gen_settings = name_gen_settings

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

    def visit_Str(self, node):
        """Handle string literals in older Python versions."""

        return self._protect_string(node)

    def visit_Constant(self, node):
        """Handle string constants in newer Python versions."""

        if isinstance(node.value, str):
            return self._protect_string(node)

        return node

    def visit_JoinedStr(self, node):
        """Handle f-strings - convert to helper function calls for better protection."""

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
        self.string_protected = True
        self.string_counter += 1

        # Encode with base64 and zlib

        encoded = base64.b64encode(
            zlib.compress(original_string.encode("utf-8"))
        ).decode("utf-8")

        # Return a Call node to the decode function
        return ast.Call(
            func=ast.Name(id=self.decode_func_name, ctx=ast.Load()),
            args=[ast.Constant(value=encoded)],
            keywords=[],
        )

    def reset(self):
        """Reset the state for processing a new file."""
        self.string_counter = 0
        self.string_protected = False

    def apply_protection(self, code):
        """Apply string protection to Python code."""

        try:
            # Parse the code

            tree = ast.parse(code)

            # Transform the tree
            protected_tree = self.visit(tree)

            # Add string decoding helper at the beginning

            if self.string_protected:
                # Create the decoder function with random names
                decoder_code = f"""import base64
import zlib

def {self.decode_func_name}(encoded_str):
    return zlib.decompress(base64.b64decode(encoded_str.encode('utf-8'))).decode('utf-8')

# Advanced f-string protection helpers
def {self.fstring_func_name}(*args):
    \"\"\"Helper function for protected f-strings.\"\"\"
    return "".join(map(str, args))

"""
                # Parse the decoder code

                decoder_tree = ast.parse(decoder_code)

                # Combine the decoder tree with the protected tree

                decoder_tree.body.extend(protected_tree.body)

                protected_tree = decoder_tree

            # Convert back to code

            protected_code = ast.unparse(protected_tree)

            return protected_code

        except Exception as e:
            print(f"String protection failed: {e}")

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
                f"Protected strings in {file_path}"
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
