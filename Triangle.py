import random

def point_in_polygon(px, py, vertices):
    n = len(vertices)
    inside = False
    
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        
        if ((y1 > py) != (y2 > py)):
            x_intersect = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
            if x_intersect > px:
                inside = not inside
    
    return inside

def monte_carlo_polygon_area(A, B, vertices, N):
    inside = 0
    for _ in range(N):
        x = random.uniform(0, A)
        y = random.uniform(0, B)
        if point_in_polygon(x, y, vertices):
            inside += 1
    return (inside / N) * (A * B)

A = float(input("Введите ширину прямоугольника A: "))
B = float(input("Введите высоту прямоугольника B: "))

n = int(input("Введите количество вершин многоугольника: "))
if n < 3:
    print("Ошибка: многоугольник должен иметь хотя бы 3 вершины")
    exit()

vertices = []
print("Введите координаты вершин (x y) в порядке обхода:")
for i in range(n):
    try:
        x, y = map(float, input(f"Вершина {i+1}: ").split())
        if x < 0 or x > A or y < 0 or y > B:
            print(f"Вершина ({x}, {y}) вне прямоугольника")
            exit()
        vertices.append((x, y))
    except:
        print("Ошибка ввода. Введите два числа через пробел.")
        exit()

N = int(input("Введите количество случайных точек N: "))
runs = int(input("Введите количество запусков: "))

random.seed()
results = []

for run in range(runs):
    area = monte_carlo_polygon_area(A, B, vertices, N)
    results.append(area)
    print(f"Запуск {run+1}: {area:.3f}")

mean = sum(results) / runs
variance = sum((x - mean) ** 2 for x in results) / (runs - 1)

print("Оценки площади:", [round(s, 3) for s in results])
print("Матожидание:", round(mean, 4))
print("Дисперсия:", round(variance, 6))
print("Стандартное отклонение:", round(variance ** 0.5, 4))