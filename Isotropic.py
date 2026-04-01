import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def isotropic_direction_cartesian():
    while True:
        x = np.random.uniform(-1, 1)
        y = np.random.uniform(-1, 1)
        z = np.random.uniform(-1, 1)
        
        length = np.sqrt(x**2 + y**2 + z**2)
        
        if length > 0 and length <= 1:
            return np.array([x/length, y/length, z/length])

def isotropic_direction_spherical():
    phi = 2 * np.pi * np.random.random()
    theta = np.arccos(2 * np.random.random() - 1)
    
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    
    return np.array([x, y, z])

def simulate_isotropic_source(N, R, method_func):
    points = []
    for _ in range(N):
        dir_vec = method_func()
        point = dir_vec * R
        points.append(point)
    return np.array(points)

def plot_3d_isotropic(points, R, title):
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
               c='blue', alpha=0.6, s=2, label='Частицы')
    
    ax.scatter(0, 0, 0, c='red', s=100, marker='o', label='Источник')
    
    u = np.linspace(0, 2 * np.pi, 30)
    v = np.linspace(0, np.pi, 30)
    x = R * np.outer(np.cos(u), np.sin(v))
    y = R * np.outer(np.sin(u), np.sin(v))
    z = R * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_surface(x, y, z, color='gray', alpha=0.1)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title(title)
    ax.legend()
    
    ax.set_xlim([-R*1.1, R*1.1])
    ax.set_ylim([-R*1.1, R*1.1])
    ax.set_zlim([-R*1.1, R*1.1])
    
    plt.show()

if __name__ == "__main__":
    N = int(input("Введите количество частиц: "))
    R = float(input("Введите радиус сферы: "))
    
    print("Генерация методом сферических координат...")
    points_spherical = simulate_isotropic_source(N, R, isotropic_direction_spherical)
    
    print("Генерация декартовым методом (куб + отбрасывание)...")
    points_cartesian = simulate_isotropic_source(N, R, isotropic_direction_cartesian)
    
    plot_3d_isotropic(points_spherical, R, 
                      f'Сферические координаты, {N} частиц, R={R}')
    
    plot_3d_isotropic(points_cartesian, R, 
                      f'Декартовы (куб+отбрасывание), {N} частиц, R={R}')
    


    
    