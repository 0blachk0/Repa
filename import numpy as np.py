import numpy as np
import matplotlib.pyplot as plt

mc2 = 0.511
E0 = 0.662
gamma = E0 / mc2

# Массив углов от 0 до 180 градусов
angles_deg = np.linspace(0, 180, 500)
# Переводим в радианы для косинуса
angles_rad = np.radians(angles_deg)

# Считаем потерянную энергию (Eloss) по формуле из вашей программы
E_prime = E0 / (1 + gamma * (1 - np.cos(angles_rad)))
E_loss = E0 - E_prime

# Строим график
plt.figure(figsize=(8, 5))
plt.plot(angles_deg, E_loss, 'k-', linewidth=2)
plt.axhline(y=0.477, color='r', linestyle='--', label='Комптоновский край (Максимум)')

plt.title('Зависимость потерянной энергии от угла рассеяния (для 0.662 МэВ)')
plt.xlabel('Угол рассеяния $\\theta$ (градусы)')
plt.ylabel('Потерянная энергия $E_{loss}$ (МэВ)')
plt.grid(True, alpha=0.5)
plt.xlim(0, 180)
plt.ylim(0, 0.5)
plt.legend()
plt.show()