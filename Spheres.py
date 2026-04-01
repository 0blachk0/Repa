
import numpy as np
import matplotlib.pyplot as plt

def isotropic_direction():
    phi = 2 * np.pi * np.random.random()
    theta = np.arccos(2 * np.random.random() - 1)
    
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    
    return np.array([x, y, z])

def ray_sphere_intersection(origin, direction, sphere_center, sphere_radius):
    oc = origin - sphere_center
    
    a = np.dot(direction, direction)
    b = 2 * np.dot(oc, direction)
    c = np.dot(oc, oc) - sphere_radius**2
    
    discriminant = b**2 - 4*a*c
    if discriminant < 0:
        return False
    
    sqrt_disc = np.sqrt(discriminant)
    t1 = (-b - sqrt_disc) / (2*a)
    t2 = (-b + sqrt_disc) / (2*a)
    
    if t1 > 0 or t2 > 0:
        return True
    return False

def simulate_hit_fraction(L, R, N):
    source = np.array([0, 0, 0])
    sphere_center = np.array([L, 0, 0])
    
    hits = 0
    for _ in range(N):
        direction = isotropic_direction()
        if ray_sphere_intersection(source, direction, sphere_center, R):
            hits += 1
    
    return hits / N

if __name__ == "__main__":
    print("Моделирование пересечения луча со сферой")
    
    R = float(input("Введите радиус сферы R: "))
    N_particles = int(input("Введите количество частиц в одном измерении: "))
    N_measurements = int(input("Введите количество измерений: "))
    
    L_values = []
    fractions = []
    
    print("\nВведите расстояния L для каждого измерения:")
    for i in range(N_measurements):
        L = float(input(f"L{i+1} = "))
        L_values.append(L)
        fraction = simulate_hit_fraction(L, R, N_particles)
        fractions.append(fraction)
        print(f"  N/N0 = {fraction:.6f}")
    
    plt.figure(figsize=(10, 6))
    plt.plot(L_values, fractions, 'bo', markersize=8, label='N/N0')
    plt.xlabel('Расстояние L от источника до центра сферы')
    plt.ylabel('Доля попавших частиц N/N0')
    plt.title(f'Зависимость доли попавших частиц от расстояния\n(R={R}, {N_particles} частиц на точку)')
    plt.grid(True, alpha=0.3)
    
    L_min = min(L_values)
    L_max = max(L_values)
    L_theory = np.linspace(L_min, L_max, 200)
    theory = 0.5 * (1 - np.sqrt(1 - (R/L_theory)**2))
    plt.plot(L_theory, theory, 'r--', label='Теория', alpha=0.7)
    
    plt.legend()
    plt.tight_layout()
    plt.show()
    
    print(f"\nМаксимальная доля: {max(fractions):.6f}")
    print(f"Минимальная доля: {min(fractions):.6f}")


    