"""
Example: CustomVM Virtualization
Demonstrates the use of @virtualize decorator for maximum code protection
"""

from pylockware import virtualize, external, skip_obf


@virtualize
def calculate_license_key(user_id: int, product_code: int) -> int:
    """
    This function will be converted to CustomVM bytecode.
    The logic is completely hidden from reverse engineering.
    """
    # Secret algorithm
    secret = 0x1337BEEF
    step1 = (user_id ^ product_code) & 0xFFFFFFFF
    step2 = (step1 * 31337) & 0xFFFFFFFF
    step3 = (step2 ^ secret) & 0xFFFFFFFF
    result = (step3 % 1000000) + 100000
    return result


@virtualize
def validate_license(user_id: int, product_code: int, provided_key: int) -> bool:
    """
    Virtualized license validation.
    Even if someone decompiles the code, they won't see this logic.
    """
    expected_key = calculate_license_key(user_id, product_code)
    return expected_key == provided_key


@external
def check_license(user_id: int, product_code: int, license_key: int) -> str:
    """
    Public API function - not virtualized but obfuscated.
    """
    if validate_license(user_id, product_code, license_key):
        return "License valid!"
    else:
        return "Invalid license!"


@skip_obf
def demo():
    """
    Demo function - not obfuscated for debugging.
    """
    print("=" * 60)
    print("CustomVM Virtualization Demo")
    print("=" * 60)
    
    # Test case 1
    user_id = 12345
    product_code = 999
    
    print(f"\nGenerating license for User ID: {user_id}, Product: {product_code}")
    license_key = calculate_license_key(user_id, product_code)
    print(f"License Key: {license_key}")
    
    # Test case 2: Valid license
    print(f"\nValidating license...")
    result = check_license(user_id, product_code, license_key)
    print(f"Result: {result}")
    
    # Test case 3: Invalid license
    print(f"\nTrying invalid license...")
    result = check_license(user_id, product_code, 999999)
    print(f"Result: {result}")
    
    print("\n" + "=" * 60)
    print("Note: The calculate_license_key and validate_license")
    print("functions are converted to CustomVM bytecode.")
    print("Their logic is completely hidden!")
    print("=" * 60)


def main():
    """Entry point"""
    demo()


if __name__ == "__main__":
    main()
