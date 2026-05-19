"""
Quick test for virtualization
"""
from pylockware import virtualize, external

@virtualize
def add_numbers(x, y):
    """Simple function to test virtualization"""
    result = x + y
    return result

@virtualize
def multiply_and_add(a, b, c):
    """More complex function"""
    temp = a * b
    result = temp + c
    return result

@external
def main():
    """Main function - not virtualized"""
    print("Testing virtualization...")
    
    # Test 1
    result1 = add_numbers(10, 20)
    print(f"add_numbers(10, 20) = {result1}")
    
    # Test 2
    result2 = multiply_and_add(5, 6, 10)
    print(f"multiply_and_add(5, 6, 10) = {result2}")
    
    print("Tests completed!")

if __name__ == "__main__":
    main()
