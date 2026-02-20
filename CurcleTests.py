import random
import math
from Curcle import monte_carlo_area

def exact_circle_area(R):
    return math.pi * R * R

def run_tests():
    random.seed(42)
    
    print("Тест 1: базовый случай (R=1, центр (5,5))")
    areas = [monte_carlo_area(10, 10, 1, 5, 5, 10000) for _ in range(10)]
    mean = sum(areas) / 10
    var = sum((x - mean) ** 2 for x in areas) / 10
    expected = exact_circle_area(1)
    print(f"Среднее: {mean:.4f}, ожидание: {expected:.4f}")
    print(f"Дисперсия: {var:.6f}\n")
    
    print("Тест 2: круг целиком внутри")
    area = monte_carlo_area(10, 10, 3, 5, 5, 50000)
    expected = exact_circle_area(3)
    print(f"Оценка: {area:.4f}, ожидание: {expected:.4f}")
    print(f"Погрешность: {abs(area - expected):.4f}\n")
    
    print("Тест 3: нулевой радиус")
    area = monte_carlo_area(10, 10, 0, 5, 5, 10000)
    print(f"Оценка: {area:.4f}, ожидание: 0\n")
    
    print("Тест 4: круг вне прямоугольника")
    area = monte_carlo_area(10, 10, 1, 20, 20, 10000)
    print(f"Оценка: {area:.6f}, ожидание: 0\n")

if __name__ == "__main__":
    run_tests()