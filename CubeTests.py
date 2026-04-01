import numpy as np
import matplotlib.pyplot as plt
from Cube import ray, flateABCD, cross, inside, create_cube, compute_face_planes, simulate_cube_hits

def test_special_positions(D, N):
    """
    Unit тесты для специальных положений источника
    """
    print("\n" + "="*70)
    print("UNIT ТЕСТЫ ДЛЯ ПРОВЕРКИ ПОПАДАНИЙ В КУБ")
    print("="*70)
    
    # Центр куба в начале координат
    cube_center = np.array([0, 0, 0])
    
    # Создаём куб для тестов
    vertices, faces = create_cube(D, cube_center)
    planes = compute_face_planes(faces)
    
    print(f"\nПараметры тестов:")
    print(f"  Длина грани куба D = {D}")
    print(f"  Центр куба: ({cube_center[0]}, {cube_center[1]}, {cube_center[2]})")
    print(f"  Количество частиц: {N}")
    
    # Тест 1: Источник в центре куба
    source1 = np.array([0, 0, 0])
    prob1 = simulate_cube_hits(source1, cube_center, D, N)
    expected1 = 1.0  # Все частицы должны остаться внутри
    print(f"\nТест 1: Источник в центре куба")
    print(f"  Положение: ({source1[0]}, {source1[1]}, {source1[2]})")
    print(f"  Вероятность: {prob1:.6f}")
    print(f"  Ожидание: {expected1:.6f}")
    print(f"  Результат: {'ПРОЙДЕН' if abs(prob1 - expected1) < 0.1 else 'НЕ ПРОЙДЕН'}")
    
    # Тест 2: Источник над центром верхней грани (снаружи)
    source2 = np.array([0, 0, D/2 + 0.5])
    prob2 = simulate_cube_hits(source2, cube_center, D, N)
    print(f"\nТест 2: Источник над центром верхней грани")
    print(f"  Положение: ({source2[0]}, {source2[1]}, {source2[2]})")
    print(f"  Вероятность: {prob2:.6f}")
    print(f"  Ожидание: > 0 (часть частиц попадает)")
    print(f"  Результат: {'ПРОЙДЕН' if prob2 > 0 else 'НЕ ПРОЙДЕН'}")
    
    # Тест 3: Источник на оси X на расстоянии L
    L = D * 2
    source3 = np.array([L, 0, 0])
    prob3 = simulate_cube_hits(source3, cube_center, D, N)
    print(f"\nТест 3: Источник на оси X, L={L}")
    print(f"  Положение: ({source3[0]}, {source3[1]}, {source3[2]})")
    print(f"  Вероятность: {prob3:.6f}")
    print(f"  Ожидание: > 0 (должна быть меньше, чем в тесте 2)")
    print(f"  Результат: {'ПРОЙДЕН' if prob3 > 0 else 'НЕ ПРОЙДЕН'}")
    
    # Тест 4: Источник на середине ребра (снаружи)
    source4 = np.array([D/2, D/2, D/2 + 0.5])
    prob4 = simulate_cube_hits(source4, cube_center, D, N)
    print(f"\nТест 4: Источник над серединой ребра")
    print(f"  Положение: ({source4[0]}, {source4[1]}, {source4[2]})")
    print(f"  Вероятность: {prob4:.6f}")
    print(f"  Ожидание: > 0")
    print(f"  Результат: {'ПРОЙДЕН' if prob4 > 0 else 'НЕ ПРОЙДЕН'}")
    
    # Тест 5: Источник над вершиной
    source5 = np.array([D/2 + 0.5, D/2 + 0.5, D/2 + 0.5])
    prob5 = simulate_cube_hits(source5, cube_center, D, N)
    print(f"\nТест 5: Источник над вершиной")
    print(f"  Положение: ({source5[0]}, {source5[1]}, {source5[2]})")
    print(f"  Вероятность: {prob5:.6f}")
    print(f"  Ожидание: > 0")
    print(f"  Результат: {'ПРОЙДЕН' if prob5 > 0 else 'НЕ ПРОЙДЕН'}")
    
    # Тест 6: Проверка функции inside на границе
    print(f"\nТест 6: Проверка функции inside на границе")
    
    # Берем первую грань (нижнюю, z = -D/2)
    test_face = faces[0]
    
    # Точка внутри грани
    point_inside = np.array([0, 0, -D/2])
    inside_result = inside(test_face, point_inside)
    print(f"  Точка внутри грани (0,0,-D/2): {inside_result}")
    
    # Точка на ребре грани
    point_edge = np.array([-D/2, -D/2, -D/2])
    edge_result = inside(test_face, point_edge)
    print(f"  Точка на ребре (-D/2,-D/2,-D/2): {edge_result}")
    
    # Точка вне грани
    point_outside = np.array([D, 0, -D/2])
    outside_result = inside(test_face, point_outside)
    print(f"  Точка вне грани (D,0,-D/2): {outside_result}")
    
    print(f"\nТест 6: {'ПРОЙДЕН' if inside_result and edge_result and not outside_result else 'НЕ ПРОЙДЕН'}")
    
    # Тест 7: Проверка функции cross
    print(f"\nТест 7: Проверка функции cross")
    
    direction = np.array([1, 0, 0])
    source = np.array([-2, 0, 0])
    plane = flateABCD(np.array([0, -1, -1]), np.array([0, 1, -1]), np.array([0, 1, 1]))
    
    intersection = cross(direction, source, plane)
    print(f"  Пересечение луча с плоскостью x=0: {intersection}")
    print(f"  Ожидание: точка (0,0,0)")
    
    test_passed = intersection is not None and abs(intersection[0]) < 1e-6 and abs(intersection[1]) < 1e-6 and abs(intersection[2]) < 1e-6
    print(f"  Результат: {'ПРОЙДЕН' if test_passed else 'НЕ ПРОЙДЕН'}")
    
    # Итоги
    print("\n" + "="*70)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("="*70)
    print("Все тесты завершены. Визуальная проверка результатов выше.")

def run_distance_dependence(D, N, N_points=20):
    """
    Исследование зависимости вероятности попадания от расстояния
    """
    print("\n" + "="*70)
    print("ИССЛЕДОВАНИЕ ЗАВИСИМОСТИ ОТ РАССТОЯНИЯ")
    print("="*70)
    
    cube_center = np.array([0, 0, 0])
    distances = np.linspace(D/2 + 0.5, 5*D, N_points)
    probabilities = []
    
    print(f"\nМоделирование для {N_points} точек, {N} частиц на точку...")
    
    for i, L in enumerate(distances):
        source = np.array([L, 0, 0])
        prob = simulate_cube_hits(source, cube_center, D, N)
        probabilities.append(prob)
        print(f"  {i+1}/{N_points}: L = {L:.2f} -> P = {prob:.6f}")
    
    return distances, probabilities

if __name__ == "__main__":
    np.random.seed(42)  # Для воспроизводимости
    
    print("ТЕСТОВАЯ ПРОГРАММА ДЛЯ МОДЕЛИРОВАНИЯ ПОПАДАНИЙ В КУБ")
    print("="*70)
    
    # Ввод параметров
    D = float(input("Введите длину грани куба D: "))
    N_particles = int(input("Введите количество частиц для тестов: "))
    
    # Запуск unit тестов
    test_special_positions(D, N_particles)
    
    # Исследование зависимости от расстояния
    distances, probabilities = run_distance_dependence(D, N_particles//2, N_points=15)
    
    
    L_fixed = D * 3
    positions = [
        (L_fixed, 0, 0, 'ось X'),
        (0, L_fixed, 0, 'ось Y'),
        (0, 0, L_fixed, 'ось Z'),
        (L_fixed/np.sqrt(3), L_fixed/np.sqrt(3), L_fixed/np.sqrt(3), 'диагональ')
    ]
    
    probs_directions = []
    for x, y, z, name in positions:
        source = np.array([x, y, z])
        prob = simulate_cube_hits(source, [0,0,0], D, N_particles//2)
        probs_directions.append(prob)
        print(f"  {name}: P = {prob:.6f}")
