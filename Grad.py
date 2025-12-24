import numpy as np


class GradientDescent:

    def y(self, x):
        x = np.clip(x, 1e-10, 1e10)
        return x ** 3 * np.exp(np.log(x) ** 2)

    def dy(self, x):
        x = np.clip(x, 1e-10, 1e10)

        log_x = np.log(x)
        log_x_squared = log_x ** 2

        max_exp_arg = 100
        safe_log_x_squared = np.minimum(log_x_squared, max_exp_arg)
        return x ** 2 * np.exp(np.log(x) ** 2) * (3 + 2 * np.log(x))

    def get_min_with_gd(self, x0, num_steps=1000, lr=0.001, threshold=1e-6):
        
        current_x = np.clip(x0, 1e-10, 1e10)
        points = [current_x]

        for step in range(num_steps):
            try:
                gradient = self.dy(current_x)

                max_gradient = 1e10
                gradient = np.clip(gradient, -max_gradient, max_gradient)

                new_x = current_x - lr * gradient

                new_x = np.clip(new_x, 1e-10, 1e10)

                if not np.isfinite(new_x) or not np.isfinite(current_x):
                    break

                if abs(new_x - current_x) < threshold:
                    points.append(new_x)
                    break

                points.append(new_x)
                current_x = new_x

            except (FloatingPointError, ValueError):
                break

        return points

    def find_analytical_minimum(self, search_range=(0.1, 10), num_points=10000):
        x_values = np.linspace(search_range[0], search_range[1], num_points)
        y_values = self.y(x_values)

        min_index = np.argmin(y_values)
        x_min = x_values[min_index]
        y_min = y_values[min_index]

        return x_min, y_min