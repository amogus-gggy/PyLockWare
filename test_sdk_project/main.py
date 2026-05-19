"""
PyLockWare Protected Application
"""

from pylockware import external, skip_obf


@external
def public_api(message: str) -> str:
    """
    Public API function - name will be preserved.
    Use @external for functions that need to be called from outside.
    """
    return process_message(message)


def process_message(message: str) -> str:
    """
    Internal function - will be obfuscated.
    This function will have full obfuscation applied.
    """
    return message.upper()


@skip_obf
def debug_info():
    """
    Debug function - will not be obfuscated.
    Use @skip_obf only during development, remove in production.
    """
    print("[DEBUG] Application is running")
    print("[DEBUG] This function is not obfuscated for easier debugging")


def main():
    """Main entry point"""
    print("=" * 60)
    print("PyLockWare Protected Application")
    print("=" * 60)
    
    # Call public API
    result = public_api("hello world")
    print(f"Result: {result}")
    
    # Debug info (remove in production)
    debug_info()
    
    print("=" * 60)
    print("Application completed successfully!")


if __name__ == "__main__":
    main()
