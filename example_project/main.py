import utils
from config.settings import Config

def main():
    """Main entry point for the example application."""
    config = Config()
    print(f"App Name: {config.app_name}")
    print(f"Version: {config.version}")
    
    # Примеры различных булевых выражений для обфускации
    a = 5
    b = 7
    x = True
    y = False
    
    # Простые сравнения в if
    if a > b:
        print(f"{a} is greater than {b}")
    
    if a < b:
        print(f"{a} is less than {b}")
    
    # Булевы литералы
    if True:
        print("This always executes")
    
    if False:
        print("This never executes")
    
    # Отрицание
    if not x:
        print("x is False")
    
    if not y:
        print("y is True (double negation)")
    
    # Логические операторы AND
    if x and y:
        print("Both x and y are True")
    
    if x and not y:
        print("x is True and y is False")
    
    # Логические операторы OR
    if x or y:
        print("At least one of x or y is True")
    
    if y or x:
        print("x or y is True")
    
    # Сложные комбинации
    if (a > 3) and (b < 10):
        print("a > 3 AND b < 10")
    
    if (a < 3) or (b > 5):
        print("a < 3 OR b > 5")
    
    # Вложенные условия
    if a > 0:
        if b > 0:
            print("Both a and b are positive")
    
    # Тернарные выражения
    result = "positive" if a > 0 else "non-positive"
    print(f"a is {result}")
    
    # Сравнения с вычислениями
    if a + b == 12:
        print("a + b equals 12")
    
    if a * b > 30:
        print("a * b is greater than 30")
    
    # Проверка на None
    value = None
    if value is None:
        print("value is None")
    
    if value is not None:
        print("value is not None")
    
    # Проверка на истинность/ложность
    empty_list = []
    non_empty_list = [1, 2, 3]
    
    if empty_list:
        print("empty_list is truthy")
    
    if not empty_list:
        print("empty_list is falsy")
    
    if non_empty_list:
        print("non_empty_list is truthy")
    
    # assert с булевыми выражениями
    assert x == True
    assert y == False
    assert a + b == 12
    
    # while с булевыми условиями
    counter = 0
    while counter < 3 and x:
        print(f"Counter: {counter}")
        counter += 1
    
    # Сложные вложенные булевы выражения
    if ((a > 0 and b > 0) or (a < 0 and b < 0)) and not (a == b):
        print("Complex condition satisfied")
    
    # Цепочка сравнений
    if 0 < a < 10:
        print("a is between 0 and 10")
    
    if a != b:
        print("a is not equal to b")
    
    if a == a:
        print("a equals itself")

    result = utils.calculate_sum(10, 20)
    print(f"Calculation result: {result}")

    print("Hello from packed PyLock application!")

if __name__ == "__main__":
    main()
