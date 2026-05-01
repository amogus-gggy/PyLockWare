"""
Демонстрация обфускации различных типов констант
"""

def demo_integers():
    """Демонстрация обфускации целых чисел"""
    zero = 0
    one = 1
    negative = -42
    positive = 123
    
    print(f"Целые числа: {zero}, {one}, {negative}, {positive}")
    return zero, one, negative, positive


def demo_floats():
    """Демонстрация обфускации вещественных чисел"""
    pi = 3.14159
    negative_float = -2.5
    zero_float = 0.0
    scientific = 1.23e-4
    
    print(f"Вещественные числа: {pi}, {negative_float}, {zero_float}, {scientific}")
    return pi, negative_float, zero_float, scientific


def demo_booleans():
    """Демонстрация булевых значений (не обфусцируются)"""
    true_val = True
    false_val = False
    
    print(f"Булевы значения: {true_val}, {false_val}")
    return true_val, false_val


def demo_complex():
    """Демонстрация комплексных чисел (не обфусцируются)"""
    c1 = 3 + 4j
    c2 = -1 - 1j
    
    print(f"Комплексные числа: {c1}, {c2}")
    return c1, c2


def main():
    print("=== Демонстрация обфускации констант ===")
    
    integers = demo_integers()
    floats = demo_floats()
    booleans = demo_booleans()
    complex_nums = demo_complex()
    
    print("\n=== Результаты ===")
    print(f"Целые: {integers}")
    print(f"Вещественные: {floats}")
    print(f"Булевы: {booleans}")
    print(f"Комплексные: {complex_nums}")


if __name__ == "__main__":
    main()