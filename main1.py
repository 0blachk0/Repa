import numpy as np
import matplotlib.pyplot as plt
from gradient import GradientDescent
import unittest
import sys


def main():

    gd = GradientDescent()
    x0 = 5.0 
    num_steps = 100
    lr = 0.01
    threshold = 1e-6

    print("Поиск минимума функции y(x) = x^3 * exp(ln^2(x))")
    print(f"Начальная точка: {x0}")
    print(f"Количество шагов: {num_steps}")
    print(f"Learning rate: {lr}")
    print(f"Порог остановки: {threshold}\n")

    points = gd.get_min_with_gd(x0, num_steps, lr, threshold)

    analytical_min, min_value = gd.find_analytical_minimum()

    print(f"Найденный градиентный спуск: x = {points[-1]:.6f}, y = {gd.y(points[-1]):.6f}")
    print(f"Численно найденный минимум: x = {analytical_min:.6f}, y = {min_value:.6f}")
    print(f"Количество шагов: {len(points)}")
    plot_results(gd, points, analytical_min, min_value)
    demo_derivative(gd, points[-1])


def plot_results(gd, points, analytical_min, min_value):
    x_plot = np.linspace(0.1, 6, 1000)
    y_plot = gd.y(x_plot)

    y_points = [gd.y(x) for x in points]

    plt.figure(figsize=(12, 8))

    plt.plot(x_plot, y_plot, 'b-', linewidth=2, label='y(x) = x³ * exp(ln²(x))')

    plt.plot(points, y_points, 'ro-', markersize=4, linewidth=1,
             label='Точки градиентного спуска')

    plt.plot(points[0], y_points[0], 'go', markersize=8,
             label=f'Начальная точка ({points[0]:.2f}, {y_points[0]:.2f})')

    plt.plot(points[-1], y_points[-1], 'mo', markersize=8,
             label=f'Конечная точка ({points[-1]:.2f}, {y_points[-1]:.2f})')

    # Аналитический минимум
    plt.plot(analytical_min, min_value, 'k*', markersize=12,
             label=f'Численный минимум ({analytical_min:.2f}, {min_value:.2f})')

    plt.xlabel('x')
    plt.ylabel('y(x)')
    plt.title('Градиентный спуск для функции y(x) = x³ * exp(ln²(x))')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


def demo_derivative(gd, x_point):
    derivative = gd.dy(x_point)
    print(f"\nДемонстрация производной:")
    print(f"y'({x_point:.4f}) = {derivative:.6f}")

    # Численная проверка производной
    h = 1e-7
    numerical_derivative = (gd.y(x_point + h) - gd.y(x_point)) / h
    print(f"Численная производная: {numerical_derivative:.6f}")
    print(f"Разница: {abs(derivative - numerical_derivative):.2e}")


class TestGradientDescent(unittest.TestCase):

    def setUp(self):
        self.gd = GradientDescent()
    
    def test_dy_function(self):
        "Тест вычисляемсоти производной"
        x = 2.0
        h = 1e-7

        analytical = self.gd.dy(x)
        numerical = (self.gd.y(x + h) - self.gd.y(x)) / h
        self.assertAlmostEqual(analytical, numerical, places=4)

    def test_y_function(self):
        "Тест вычисляемости функции y(x)"
        result = self.gd.y(1.0)
        expected = 1.0  # y(1) = 1^3 * exp(ln^2(1)) = 1 * exp(0) = 1
        self.assertAlmostEqual(result, expected, places=6)

    def test_gradient_descent_convergence(self):
        "Тест сходимость"
        points = self.gd.get_min_with_gd(
            x0=2.0,
            num_steps=100,
            lr=0.001,
            threshold=1e-6
        )

        self.assertGreater(len(points), 1)
        self.assertLessEqual(len(points), 101)

        self.assertTrue(np.isfinite(points[-1]), f"Последняя точка {points[-1]} не конечна")
        self.assertGreater(points[-1], 0, f"Последняя точка {points[-1]} не положительная")

        for i, point in enumerate(points):
            self.assertTrue(np.isfinite(point), f"Точка {i} не конечна: {point}")
            self.assertGreater(point, 0, f"Точка {i} не положительная: {point}")

    def test_gradient_descent_with_negative_protection(self):
        "Тест отрицательных значений"
        points = self.gd.get_min_with_gd(
            x0=0.1,
            num_steps=1000,
            lr=0.0001,
            threshold=1e-8
        )

        for i, point in enumerate(points):
            self.assertTrue(np.isfinite(point), f"Точка {i} не конечна: {point}")
            self.assertGreater(point, 0, f"Точка {i} не положительная: {point}")

        self.assertGreater(len(points), 1)
        self.assertLessEqual(len(points), 1001)

    def test_gradient_descent_various_conditions(self):
        "Тест градиентного спуска с различными начальными условиями"
        test_cases = [
            (1.5, 0.001),
            (0.5, 0.0005),
            (3.0, 0.001),
        ]

        for x0, lr in test_cases:
            with self.subTest(x0=x0, lr=lr):
                points = self.gd.get_min_with_gd(x0=x0, lr=lr, num_steps=200)

                self.assertGreater(len(points), 1)
                self.assertTrue(np.isfinite(points[-1]))
                self.assertGreater(points[-1], 0)
def run_tests():

    print("Запуск тестов")
    print("=" * 50)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestGradientDescent)

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("=" * 50)
    print(f"Тестов пройдено: {result.testsRun}")
    return result.wasSuccessful()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        run_tests()
    else:
        main()