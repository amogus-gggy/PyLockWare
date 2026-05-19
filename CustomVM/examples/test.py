a = []
for i in range(100):
    if not (i % 2 == 0) and not (i > 67):
        a.append(i)

print(len(a))