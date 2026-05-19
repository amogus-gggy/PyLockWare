

# ---- Арифметика ----
a = 10
b = 3
result = a + b * 2 - 5  # 10 + 6 - 5 = 11
print(result)

# ---- Сравнения ----
print(a == 10)   # 1 (true)
print(a != 5)    # 1 (true)
print(a < 5)     # 0 (false)
print(a >= 10)   # 1 (true)

# ---- Булевы операторы ----
x = 1
y = 0
print(x and y)   # 0
print(x or y)    # 1
print(not x)     # 0
print(not y)     # 1

# ---- Битовые операции ----
print(12 & 5)    # 4
print(12 | 5)    # 13
print(12 ^ 5)    # 9
print(3 << 2)    # 12
print(16 >> 2)   # 4

# ---- Augmented assignment ----
n = 10
n += 5
print(n)         # 15
n -= 3
print(n)         # 12
n *= 2
print(n)         # 24
n //= 5
print(n)         # 4
n |= 8
print(n)         # 12

# ---- If / elif / else ----
val = 7
if val < 0:
    print(999)
elif val < 5:
    print(111)
elif val < 10:
    print(222)   # ← выполнится это
else:
    print(333)

# ---- While ----
i = 0
sum_while = 0
while i <= 10:
    sum_while += i
    i += 1
print(sum_while)  # 55

# ---- For по range ----
# range(stop)
for i in range(5):
    print(i)      # 0 1 2 3 4

# range(start, stop)
for i in range(10, 15):
    print(i)      # 10 11 12 13 14

# range(start, stop, step)
for i in range(0, 10, 3):
    print(i)      # 0 3 6 9

# обратный шаг
for i in range(5, 2, -1):
    print(i)      # 5 4 3

# ---- Break / Continue ----
for i in range(10):
    if i == 7:
        break
    if i % 2 == 0:
        continue
    print(i)      # 1 3 5

# ---- Вложенные циклы ----
result = 0
for i in range(3):
    for j in range(4):
        result += 1
print(result)     # 12

# ---- Факториал через while ----
num = 6
fact = 1
while num > 1:
    fact *= num
    num -= 1
print(fact)       # 720

# ---- Степень двойки через for ----
power = 1
for _ in range(10):
    power *= 2
print(power)      # 1024

# ---- Сумма чётных чисел в диапазоне ----
total = 0
for i in range(1, 21):
    if i % 2 == 0:
        total += i
print(total)      # 110

# ---- Строки ----
# Строковые литералы
greeting = "Hello"
name = "World"
print(greeting)   # Hello
print(name)       # World

# Конкатенация строк
message = greeting + ", " + name + "!"
print(message)    # Hello, World!

# Длина строки
print(len(greeting))  # 5
print(len(message))   # 13

# Индексация строк
print(greeting[0])    # H
print(greeting[4])    # o
idx = 1
print(greeting[idx])  # e

# Срезы строк
text = "Hello World"
print(text[:5])       # Hello
print(text[6:])       # World
print(text[0:5])      # Hello
print(text[:])        # Hello World

# Сравнение строк
s1 = "abc"
s2 = "xyz"
print(s1 == "abc")    # 1 (true)
print(s1 != s2)       # 1 (true)
print(s1 < s2)        # 1 (true)

# Строки в условиях
nonempty = "text"
empty = ""
if nonempty:
    print(1)          # 1 (выполнится)
else:
    print(0)

if empty:
    print(0)
else:
    print(1)          # 1 (выполнится)

# Augmented assignment со строками
result_str = "Start"
result_str += " Middle"
result_str += " End"
print(result_str)     # Start Middle End

# Строки в циклах
word = "Loop"
k = 0
while k < len(word):
    print(word[k])    # L o o p
    k += 1

# Построение строки в цикле
output = ""
m = 0
while m < 3:
    output += "x"
    m += 1
print(output)         # xxx

print(9999)       # маркер конца
