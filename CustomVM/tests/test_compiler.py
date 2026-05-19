"""Comprehensive tests for the Python→CVM bytecode compiler.

These tests compile Python source code into CVM bytecode via VMBuilder,
load the built .cvm file through BytecodeLoader, and execute it on the
VirtualMachine — exactly the same pipeline as the CLI tools.
"""

import ast
import io
import os
import sys
import tempfile
import textwrap

import pytest

from customvm import VMBuilder, BytecodeLoader, VirtualMachine
from customvm.compiler import PythonCompiler


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

def compile_and_execute(source):
    """Compile Python source, build .cvm, load and execute on the VM.

    Returns (stack_top, captured_stdout) where stack_top is whatever the
    VM leaves on top of the stack after HALT, and captured_stdout is the
    text printed via syscall 1/2/3.
    """
    builder = VMBuilder()
    compiler = PythonCompiler(builder)
    compiler.compile(source)

    # Write to a temp .cvm file
    with tempfile.NamedTemporaryFile(suffix='.cvm', delete=False) as tmp:
        tmp_path = tmp.name

    try:
        builder.build(tmp_path)

        # Load and execute
        loader = BytecodeLoader()
        code, opcode_set, crypto, const_pool, integrity_hash, func_pool, string_pool = (
            loader.load(tmp_path)
        )

        vm = VirtualMachine()
        vm.load_bytecode(
            code, opcode_set, crypto, const_pool, integrity_hash, func_pool, string_pool
        )

        # Capture stdout during execution
        captured = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            result = vm.execute()
        finally:
            sys.stdout = old_stdout

        return result, captured.getvalue()
    finally:
        os.unlink(tmp_path)


def check(source, expected=None, expected_stdout=None):
    """Assert compiled code produces the expected result / stdout."""
    result, stdout = compile_and_execute(textwrap.dedent(source))
    if expected is not None:
        assert result == expected, (
            f"Expected result {expected!r}, got {result!r}\n"
            f"Source:\n{source}"
        )
    if expected_stdout is not None:
        assert stdout == expected_stdout, (
            f"Expected stdout {expected_stdout!r}, got {stdout!r}\n"
            f"Source:\n{source}"
        )


# ---------------------------------------------------------------------------
# Constants & basic expressions
# ---------------------------------------------------------------------------

class TestConstants:
    @pytest.mark.timeout(10)
    def test_int_constant(self):
        check("x = 42\nprint(x)", expected_stdout="42\n")

    @pytest.mark.timeout(10)
    def test_bool_constant(self):
        check("x = True\nprint(x)", expected_stdout="1\n")

    @pytest.mark.timeout(10)
    def test_multiple_constants(self):
        check("""
            a = 10
            b = 20
            c = a + b
            print(c)
        """, expected_stdout="30\n")


# ---------------------------------------------------------------------------
# Arithmetic expressions
# ---------------------------------------------------------------------------

class TestArithmetic:
    @pytest.mark.timeout(10)
    def test_add(self):
        check("print(3 + 4)", expected_stdout="7\n")

    @pytest.mark.timeout(10)
    def test_sub(self):
        check("print(10 - 3)", expected_stdout="7\n")

    @pytest.mark.timeout(10)
    def test_mul(self):
        check("print(6 * 7)", expected_stdout="42\n")
    @pytest.mark.timeout(10)
    def test_div(self):
        check("print(15 // 4)", expected_stdout="3\n")
    @pytest.mark.timeout(10)
    def test_mod(self):
        check("print(17 % 5)", expected_stdout="2\n")
    @pytest.mark.timeout(10)
    def test_compound_arithmetic(self):
        check("""
            x = 2 + 3 * 4
            print(x)
        """, expected_stdout="14\n")
    @pytest.mark.timeout(10)
    def test_unary_minus(self):
        check("""
            x = -5
            y = -x
            print(y)
        """, expected_stdout="5\n")
    @pytest.mark.timeout(10)
    def test_unary_plus(self):
        check("""
            x = +42
            print(x)
        """, expected_stdout="42\n")


# ---------------------------------------------------------------------------
# Comparison operators
# ---------------------------------------------------------------------------

class TestComparisons:
    @pytest.mark.timeout(10)
    def test_eq_true(self):
        check("""
            x = (10 == 10)
            print(x)
        """, expected_stdout="1\n")
    @pytest.mark.timeout(10)
    def test_eq_false(self):
        check("""
            x = (10 == 20)
            print(x)
        """, expected_stdout="0\n")
    @pytest.mark.timeout(10)
    def test_neq_true(self):
        check("""
            x = (10 != 20)
            print(x)
        """, expected_stdout="1\n")
    @pytest.mark.timeout(10)
    def test_lt_true(self):
        check("""
            x = (5 < 10)
            print(x)
        """, expected_stdout="1\n")
    @pytest.mark.timeout(10)
    def test_lt_false(self):
        check("""
            x = (10 < 5)
            print(x)
        """, expected_stdout="0\n")
    @pytest.mark.timeout(10)
    def test_gt_true(self):
        check("""
            x = (10 > 5)
            print(x)
        """, expected_stdout="1\n")
    @pytest.mark.timeout(10)
    def test_le_true(self):
        check("""
            x = (5 <= 5)
            print(x)
        """, expected_stdout="1\n")
    @pytest.mark.timeout(10)
    def test_ge_true(self):
        check("""
            x = (10 >= 5)
            print(x)
        """, expected_stdout="1\n")
    @pytest.mark.timeout(10)
    def test_ge_false(self):
        check("""
            x = (4 >= 5)
            print(x)
        """, expected_stdout="0\n")


# ---------------------------------------------------------------------------
# Boolean operators
# ---------------------------------------------------------------------------

class TestBooleanOps:
    @pytest.mark.timeout(10)
    def test_and_both_true(self):
        check("""
            x = (1 and 2)
            print(x)
        """, expected_stdout="2\n")
    @pytest.mark.timeout(10)
    def test_and_first_false(self):
        check("""
            x = (0 and 2)
            print(x)
        """, expected_stdout="0\n")
    @pytest.mark.timeout(10)
    def test_and_chain(self):
        check("""
            x = (1 and 2 and 3)
            print(x)
        """, expected_stdout="3\n")
    @pytest.mark.timeout(10)
    def test_or_first_true(self):
        check("""
            x = (1 or 2)
            print(x)
        """, expected_stdout="1\n")
    @pytest.mark.timeout(10)
    def test_or_both_false(self):
        check("""
            x = (0 or 0)
            print(x)
        """, expected_stdout="0\n")
    @pytest.mark.timeout(10)
    def test_or_second_becomes_result(self):
        check("""
            x = (0 or 42)
            print(x)
        """, expected_stdout="42\n")
    @pytest.mark.timeout(10)
    def test_or_chain_all_false(self):
        check("""
            x = (0 or 0 or 99)
            print(x)
        """, expected_stdout="99\n")
    @pytest.mark.timeout(10)
    def test_not_true(self):
        check("""
            x = not 0
            print(x)
        """, expected_stdout="1\n")
    @pytest.mark.timeout(10)
    def test_not_false(self):
        check("""
            x = not 42
            print(x)
        """, expected_stdout="0\n")


# ---------------------------------------------------------------------------
# Bitwise operators
# ---------------------------------------------------------------------------

class TestBitwise:
    @pytest.mark.timeout(10)
    def test_bit_and(self):
        check("print(12 & 5)", expected_stdout="4\n")   # 1100 & 0101 = 0100
    @pytest.mark.timeout(10)
    def test_bit_or(self):
        check("print(12 | 5)", expected_stdout="13\n")   # 1100 | 0101 = 1101
    @pytest.mark.timeout(10)
    def test_bit_xor(self):
        check("print(12 ^ 5)", expected_stdout="9\n")    # 1100 ^ 0101 = 1001
    @pytest.mark.timeout(10)
    def test_not(self):
        check("""
            x = ~0
            print(x)
        """, expected_stdout="4294967295\n")
    @pytest.mark.timeout(10)
    def test_shift_left(self):
        check("print(3 << 2)", expected_stdout="12\n")
    @pytest.mark.timeout(10)
    def test_shift_right(self):
        check("print(16 >> 2)", expected_stdout="4\n")


# ---------------------------------------------------------------------------
# Augmented assignments
# ---------------------------------------------------------------------------

class TestAugAssign:
    @pytest.mark.timeout(10)
    def test_add(self):
        check("""
            x = 5
            x += 3
            print(x)
        """, expected_stdout="8\n")
    @pytest.mark.timeout(10)
    def test_sub(self):
        check("""
            x = 10
            x -= 4
            print(x)
        """, expected_stdout="6\n")
    @pytest.mark.timeout(10)
    def test_mul(self):
        check("""
            x = 6
            x *= 7
            print(x)
        """, expected_stdout="42\n")
    @pytest.mark.timeout(10)
    def test_div(self):
        check("""
            x = 15
            x //= 4
            print(x)
        """, expected_stdout="3\n")
    @pytest.mark.timeout(10)
    def test_mod(self):
        check("""
            x = 17
            x %= 5
            print(x)
        """, expected_stdout="2\n")
    @pytest.mark.timeout(10)
    def test_bit_and(self):
        check("""
            x = 12
            x &= 5
            print(x)
        """, expected_stdout="4\n")
    @pytest.mark.timeout(10)
    def test_bit_or(self):
        check("""
            x = 12
            x |= 5
            print(x)
        """, expected_stdout="13\n")


# Note: the VM represents all values as unsigned 32-bit integers.
# Negative constants like -1 are stored as 0xFFFFFFFF = 4294967295.
# We use the signed sentinel names in the test source code, but the
# expected output reflects the unsigned VM representation.

# ---------------------------------------------------------------------------
# If / elif / else
# ---------------------------------------------------------------------------

class TestIf:
    @pytest.mark.timeout(10)
    def test_if_true(self):
        check("""
            if 1:
                print(10)
            else:
                print(20)
        """, expected_stdout="10\n")
    @pytest.mark.timeout(10)
    def test_if_false(self):
        check("""
            if 0:
                print(10)
            else:
                print(20)
        """, expected_stdout="20\n")
    @pytest.mark.timeout(10)
    def test_if_no_else(self):
        check("""
            x = 5
            if x > 3:
                print(1)
            print(2)
        """, expected_stdout="1\n2\n")
    @pytest.mark.timeout(10)
    def test_if_elif_else(self):
        check("""
            x = 5
            if x == 0:
                print(0)
            elif x == 5:
                print(5)
            elif x == 10:
                print(10)
            else:
                print(-1)
        """, expected_stdout="5\n")
    @pytest.mark.timeout(10)
    def test_if_elif_falls_to_else(self):
        check("""
            x = 99
            if x == 0:
                print(0)
            elif x == 5:
                print(5)
            else:
                print(-1)
        """, expected_stdout="4294967295\n")


# ---------------------------------------------------------------------------
# While loops
# ---------------------------------------------------------------------------

class TestWhile:
    @pytest.mark.timeout(10)
    def test_simple_count(self):
        check("""
            i = 0
            while i < 5:
                print(i)
                i += 1
        """, expected_stdout="0\n1\n2\n3\n4\n")
    @pytest.mark.timeout(10)
    def test_while_false_immediately(self):
        check("""
            x = 0
            while x:
                print(99)
            print(1)
        """, expected_stdout="1\n")
    @pytest.mark.timeout(10)
    def test_while_sum(self):
        check("""
            i = 1
            total = 0
            while i <= 10:
                total += i
                i += 1
            print(total)
        """, expected_stdout="55\n")


# ---------------------------------------------------------------------------
# For loops (over range)
# ---------------------------------------------------------------------------

class TestFor:
    @pytest.mark.timeout(10)
    def test_range_one_arg(self):
        check("""
            for i in range(5):
                print(i)
        """, expected_stdout="0\n1\n2\n3\n4\n")
    @pytest.mark.timeout(10)
    def test_range_two_args(self):
        check("""
            for i in range(5, 10):
                print(i)
        """, expected_stdout="5\n6\n7\n8\n9\n")
    @pytest.mark.timeout(10)
    def test_range_three_args_positive_step(self):
        check("""
            for i in range(0, 10, 3):
                print(i)
        """, expected_stdout="0\n3\n6\n9\n")
    @pytest.mark.timeout(10)
    def test_range_negative_step(self):
        check("""
            for i in range(10, 5, -1):
                print(i)
        """, expected_stdout="10\n9\n8\n7\n6\n")
    @pytest.mark.timeout(10)
    def test_for_sum(self):
        check("""
            total = 0
            for i in range(1, 101):
                total += i
            print(total)
        """, expected_stdout="5050\n")


# ---------------------------------------------------------------------------
# Nested loops
# ---------------------------------------------------------------------------

class TestNestedLoops:
    @pytest.mark.timeout(10)
    def test_nested_for(self):
        check("""
            result = 0
            for i in range(3):
                for j in range(3):
                    result += 1
            print(result)
        """, expected_stdout="9\n")
    @pytest.mark.timeout(10)
    def test_for_inside_while(self):
        check("""
            i = 0
            total = 0
            while i < 3:
                for j in range(2):
                    total += 1
                i += 1
            print(total)
        """, expected_stdout="6\n")


# ---------------------------------------------------------------------------
# Break / Continue
# ---------------------------------------------------------------------------

class TestBreakContinue:
    @pytest.mark.timeout(10)
    def test_break_while(self):
        check("""
            i = 0
            while i < 10:
                if i == 5:
                    break
                print(i)
                i += 1
        """, expected_stdout="0\n1\n2\n3\n4\n")
    @pytest.mark.timeout(10)
    def test_continue_while(self):
        check("""
            i = 0
            while i < 5:
                i += 1
                if i == 3:
                    continue
                print(i)
        """, expected_stdout="1\n2\n4\n5\n")
    @pytest.mark.timeout(10)
    def test_break_for(self):
        check("""
            for i in range(10):
                if i == 4:
                    break
                print(i)
        """, expected_stdout="0\n1\n2\n3\n")


# ---------------------------------------------------------------------------
# Complex programs
# ---------------------------------------------------------------------------

class TestComplexPrograms:
    @pytest.mark.timeout(10)
    def test_fizzbuzz(self):
        # Negative sentinels printed as unsigned 32-bit:
        #   -1 → 4294967295,  -2 → 4294967294,  -3 → 4294967293
        check("""
            i = 1
            while i <= 15:
                if i % 15 == 0:
                    print(-1)
                elif i % 3 == 0:
                    print(-2)
                elif i % 5 == 0:
                    print(-3)
                else:
                    print(i)
                i += 1
        """, expected_stdout=(
            "1\n2\n4294967294\n4\n4294967293\n4294967294\n7\n8\n"
            "4294967294\n4294967293\n11\n4294967294\n13\n14\n4294967295\n"
        ))
    @pytest.mark.timeout(10)
    def test_power_of_two(self):
        check("""
            n = 1
            for i in range(10):
                n *= 2
            print(n)
        """, expected_stdout="1024\n")
    @pytest.mark.timeout(10)
    def test_factorial(self):
        check("""
            n = 5
            result = 1
            while n > 1:
                result *= n
                n -= 1
            print(result)
        """, expected_stdout="120\n")


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    @pytest.mark.timeout(10)
    def test_empty_range(self):
        check("""
            for i in range(0):
                print(99)
            print(42)
        """, expected_stdout="42\n")
    @pytest.mark.timeout(10)
    def test_single_iteration(self):
        check("""
            for i in range(1):
                print(i)
        """, expected_stdout="0\n")
    @pytest.mark.timeout(10)
    def test_nested_if_in_loop(self):
        check("""
            total = 0
            for i in range(10):
                if i % 2 == 0:
                    total += i
            print(total)
        """, expected_stdout="20\n")


# ---------------------------------------------------------------------------
# Error cases — compiler should raise properly
# ---------------------------------------------------------------------------

class TestCompilerErrors:
    @pytest.mark.timeout(10)
    def test_undefined_variable(self):
        with pytest.raises(NameError, match="Undefined variable"):
            compile_and_execute("print(x)")

    @pytest.mark.timeout(10)
    def test_unsupported_construct(self):
        with pytest.raises(NotImplementedError, match="List"):
            compile_and_execute("x = [1, 2, 3]")
    @pytest.mark.timeout(10)
    def test_unsupported_constant(self):
        # Strings are now supported, test with a different unsupported type
        with pytest.raises(NotImplementedError, match="Constant type"):
            compile_and_execute("x = 3.14")  # float not supported


# ---------------------------------------------------------------------------
# String operations tests
# ---------------------------------------------------------------------------

class TestStringOperations:
    @pytest.mark.timeout(10)
    def test_string_literal(self):
        result, stdout = compile_and_execute("""
s = "Hello"
print(s)
""")
        assert "Hello" in stdout

    @pytest.mark.timeout(10)
    def test_string_concatenation(self):
        result, stdout = compile_and_execute("""
s1 = "Hello"
s2 = "World"
s3 = s1 + " " + s2
print(s3)
""")
        assert "Hello World" in stdout

    @pytest.mark.timeout(10)
    def test_string_length(self):
        result, stdout = compile_and_execute("""
s = "Hello"
x = len(s)
print(x)
""")
        assert "5" in stdout

    @pytest.mark.timeout(10)
    def test_string_indexing(self):
        result, stdout = compile_and_execute("""
s = "Hello"
print(s[0])
print(s[1])
i = 2
print(s[i])
""")
        assert "H" in stdout
        assert "e" in stdout
        assert "l" in stdout

    @pytest.mark.timeout(10)
    def test_string_slicing(self):
        result, stdout = compile_and_execute("""
s = "Hello World"
print(s[:5])
print(s[6:])
print(s[0:5])
""")
        assert "Hello" in stdout
        assert "World" in stdout

    @pytest.mark.timeout(10)
    def test_string_comparison(self):
        result, stdout = compile_and_execute("""
s1 = "Hello"
s2 = "World"
print(s1 == "Hello")
print(s1 != "Bye")
print(s1 < s2)
""")
        lines = stdout.strip().split('\n')
        assert lines[0] == "1"  # s1 == "Hello"
        assert lines[1] == "1"  # s1 != "Bye"
        assert lines[2] == "1"  # s1 < s2

    @pytest.mark.timeout(10)
    def test_string_in_condition(self):
        result, stdout = compile_and_execute("""
text = "nonempty"
if text:
    print(1)
else:
    print(0)

empty = ""
if empty:
    print(0)
else:
    print(1)
""")
        lines = stdout.strip().split('\n')
        assert lines[0] == "1"  # nonempty string is truthy
        assert lines[1] == "1"  # empty string is falsy

    @pytest.mark.timeout(10)
    def test_string_augmented_assignment(self):
        result, stdout = compile_and_execute("""
s = "Hello"
s += " World"
print(s)
""")
        assert "Hello World" in stdout


# ---------------------------------------------------------------------------
# Smoke test: original test_simple.py still works
# ---------------------------------------------------------------------------

class TestRegression:
    @pytest.mark.timeout(10)
    def test_original_test_simple(self):
        check("""
            x = 5
            y = x * 2
            print(y)
        """, expected_stdout="10\n")
    @pytest.mark.timeout(10)
    def test_variable_reuse(self):
        check("""
            x = 10
            x = x + 5
            print(x)
        """, expected_stdout="15\n")
