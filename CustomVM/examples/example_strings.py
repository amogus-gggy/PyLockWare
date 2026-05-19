# Пример работы со строками в CustomVM

# Строковые литералы
greeting = "Hello"
name = "World"
print(greeting)
print(name)

# Конкатенация строк
message = greeting + ", " + name + "!"
print(message)

# Длина строки
print(len(greeting))
print(len(message))

# Индексация строк (константный индекс)
print(greeting[0])  # H
print(greeting[4])  # o

# Индексация строк (переменный индекс)
i = 1
print(greeting[i])  # e

# Срезы строк
text = "Hello World"
print(text[:5])      # Hello
print(text[6:])      # World
print(text[0:5])     # Hello
print(text[:])       # Hello World

# Сравнение строк
s1 = "abc"
s2 = "xyz"
print(s1 == "abc")   # 1 (true)
print(s1 != s2)      # 1 (true)
print(s1 < s2)       # 1 (true, лексикографическое сравнение)

# Строки в условиях
nonempty = "text"
empty = ""

if nonempty:
    print(1)  # выполнится
else:
    print(0)

if empty:
    print(0)
else:
    print(1)  # выполнится

# Augmented assignment со строками
result = "Start"
result += " Middle"
result += " End"
print(result)  # Start Middle End

# Строки в циклах
word = "Loop"
i = 0
while i < len(word):
    print(word[i])
    i += 1

# Построение строки в цикле
output = ""
j = 0
while j < 3:
    output += "x"
    j += 1
print(output)  # xxx

print(9999)  # маркер завершения
