import random
import math
from Triangle import point_in_polygon, monte_carlo_polygon_area

def polygon_area_exact(vertices):
    "шнурок"
    n = len(vertices)
    area = 0
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) / 2

def run_tests():
    random.seed(42)
    
    print("Тест 1: квадрат")
    square = [(2, 2), (8, 2), (8, 8), (2, 8)]
    areas = [monte_carlo_polygon_area(10, 10, square, 10000) for _ in range(10)]
    mean = sum(areas) / 10
    var = sum((x - mean) ** 2 for x in areas) / 9
    expected = polygon_area_exact(square)
    print(f"Среднее: {mean:.3f}, ожидание: {expected:.3f}")
    print(f"Дисперсия: {var:.5f}\n")
    
    print("Тест 2: треугольник")
    triangle = [(2, 2), (8, 2), (5, 8)]
    area = monte_carlo_polygon_area(10, 10, triangle, 50000)
    expected = polygon_area_exact(triangle)
    print(f"Оценка: {area:.3f}, ожидание: {expected:.3f}")
    print(f"Погрешность: {abs(area - expected):.3f}\n")
    
    print("Тест 3: пятиугольник (звезда/выпуклый)")
    pentagon = [(3, 2), (7, 2), (9, 5), (5, 8), (1, 5)]
    area = monte_carlo_polygon_area(10, 10, pentagon, 50000)
    expected = polygon_area_exact(pentagon)
    print(f"Оценка: {area:.3f}, ожидание: {expected:.3f}")
    print(f"Погрешность: {abs(area - expected):.3f}\n")
    
    print("Тест 4: вогнутый многоугольник")
    concave = [(2, 2), (8, 2), (5, 5), (8, 8), (2, 8)]
    area = monte_carlo_polygon_area(10, 10, concave, 50000)
    expected = polygon_area_exact(concave)
    print(f"Оценка: {area:.3f}, ожидание: {expected:.3f}")
    print(f"Погрешность: {abs(area - expected):.3f}\n")
    
    print("Тест 5: точка внутри/снаружи")
    square = [(0, 0), (4, 0), (4, 4), (0, 4)]
    print(f"Точка (2,2) внутри: {point_in_polygon(2, 2, square)}")
    print(f"Точка (5,2) снаружи: {point_in_polygon(5, 2, square)}")
    print(f"Точка (2,4) на границе: {point_in_polygon(2, 4, square)}")
    print(f"Точка (0,0) в вершине: {point_in_polygon(0, 0, square)}\n")
    
    print("Тест 6: сложная фигура (буква C)")
    c_shape = [(1, 1), (3, 1), (3, 2), (2, 2), (2, 3), (3, 3), (3, 4), (1, 4)]
    area = monte_carlo_polygon_area(5, 5, c_shape, 50000)
    expected = polygon_area_exact(c_shape)
    print(f"Оценка: {area:.3f}, ожидание: {expected:.3f}")
    print(f"Погрешность: {abs(area - expected):.3f}\n")
    
    print("Тест 7: проверка на вырожденном многоугольнике (линия)")
    line = [(1, 1), (3, 1), (3, 1), (1, 1)]
    try:
        area = monte_carlo_polygon_area(5, 5, line, 10000)
        print(f"Оценка: {area:.6f}")
    except Exception as e:
        print(f"Ожидаемая ошибка: {e}\n")

if __name__ == "__main__":
    run_tests()