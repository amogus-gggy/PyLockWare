# Реализованные возможности работы со строками

## Обзор

В CustomVM добавлена полная поддержка строковых операций, включая:

## Основные возможности

### 1. Строковые литералы
```python
s = "Hello"
name = "World"
```

### 2. Конкатенация строк
```python
# Оператор +
result = "Hello" + " " + "World"  # "Hello World"

# Augmented assignment
text = "Start"
text += " End"  # "Start End"
```

### 3. Длина строки
```python
s = "Hello"
length = len(s)  # 5
```

### 4. Индексация
```python
word = "Hello"

# Константный индекс
print(word[0])  # H
print(word[4])  # o

# Переменный индекс
i = 2
print(word[i])  # l
```

### 5. Срезы (Slicing)
```python
text = "Hello World"

# Полный срез
print(text[:])      # Hello World

# С начала до индекса
print(text[:5])     # Hello

# От индекса до конца
print(text[6:])     # World

# Диапазон
print(text[0:5])    # Hello

# С переменными индексами
start = 2
end = 7
print(text[start:end])  # llo W
```

### 6. Сравнение строк
```python
s1 = "abc"
s2 = "xyz"

# Равенство
print(s1 == "abc")  # 1 (true)
print(s1 != s2)     # 1 (true)

# Лексикографическое сравнение
print(s1 < s2)      # 1 (true)
print(s1 > s2)      # 0 (false)
print(s1 <= "abc")  # 1 (true)
print(s1 >= "zzz")  # 0 (false)
```

### 7. Строки в булевом контексте
```python
# Непустая строка = true
text = "nonempty"
if text:
    print(1)  # выполнится

# Пустая строка = false
empty = ""
if empty:
    print(0)
else:
    print(1)  # выполнится
```

### 8. Строки в циклах
```python
word = "Loop"
i = 0
while i < len(word):
    print(word[i])
    i += 1

# Построение строки в цикле
result = ""
j = 0
while j < 3:
    result += "x"
    j += 1
print(result)  # xxx
```

## Технические детали

### Новые опкоды

- `INST_STR_LOAD (0x3A)` - Загрузка строки из string pool
- `INST_STR_CMP (0x3B)` - Сравнение строк (устанавливает флаги z/n/c)
- `INST_STR_CONCAT (0x3C)` - Конкатенация строк
- `INST_STR_LEN (0x3D)` - Получение длины строки
- `INST_STR_GET (0x3E)` - Получение символа по индексу
- `INST_STR_SLICE (0x3F)` - Срез строки

### Изменения в компиляторе

1. **Отслеживание строковых переменных** - компилятор отслеживает какие переменные содержат строки для правильной генерации операций
2. **Автоматический выбор операций** - `+` автоматически компилируется в `STR_CONCAT` для строк и `ADD` для чисел
3. **Поддержка срезов** - полная поддержка синтаксиса `s[start:end]` с опциональными границами

### Изменения в VM

1. **Смешанный стек** - стек теперь может содержать как числа, так и строки
2. **String pool** - строковые литералы хранятся в отдельном пуле и загружаются по индексу
3. **Автоматическое преобразование типов** - при сравнении строк с числами строки преобразуются в булевы значения (пустая = 0, непустая = 1)

### Изменения в loader

1. **Секция 0x05** - новая секция для хранения string pool
2. **Правильная индексация блоков** - исправлена индексация блоков шифрования для корректной работы с несколькими секциями

## Примеры использования

См. файл `examples/example_strings.py` для полного примера использования всех строковых возможностей.

## Тесты

Добавлено 8 новых тестов в `tests/test_compiler.py`:
- `test_string_literal` - строковые литералы
- `test_string_concatenation` - конкатенация
- `test_string_length` - длина строки
- `test_string_indexing` - индексация
- `test_string_slicing` - срезы
- `test_string_comparison` - сравнение
- `test_string_in_condition` - строки в условиях
- `test_string_augmented_assignment` - augmented assignment

Все 79 тестов проходят успешно.
