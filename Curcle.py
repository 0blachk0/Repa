import random
import math

def monte_carlo_area(A, B, R, X0, Y0, N):
    if X0 - R < 0 or X0 + R > A or Y0 - R < 0 or Y0 + R > B:
        raise ValueError("Круг не полностью помещается в прямоугольнике")
   
    inside = 0
    for _ in range(N):
        x = random.uniform(0, A)
        y = random.uniform(0, B)
        if (x - X0) ** 2 + (y - Y0) ** 2 <= R ** 2:
            inside += 1
    return (inside / N) * (A * B)

try:
    A = float(input("Введите ширину прямоугольника A: "))
    B = float(input("Введите высоту прямоугольника B: "))
    R = float(input("Введите радиус круга R: "))
    X0 = float(input("Введите координату X центра круга: "))
    Y0 = float(input("Введите координату Y центра круга: "))
    N = int(input("Введите количество точек N: "))
    runs = int(input("Введите количество запусков: "))
    
    results = [monte_carlo_area(A, B, R, X0, Y0, N) for i in range(runs)]
    
    mean = sum(results) / runs
    variance = sum((x - mean) ** 2 for x in results) / (runs-1)
    print("Площади:", [round(s, 4) for s in results])
    print("Матожидание:", round(mean, 4))
    print("Дисперсия:", round(variance, 6))
    
except ValueError as e:
    print("Ошибка:", e)

