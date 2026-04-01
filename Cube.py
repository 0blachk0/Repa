
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool
import time

NA = 6.022e23
M_NA = 22.99
M_I = 126.90
Z_NA = 11
Z_I = 53
MC2 = 0.511

def isotropic_direction():
    phi = 2 * np.pi * np.random.random()
    theta = np.arccos(2 * np.random.random() - 1)
    return np.array([np.sin(theta) * np.cos(phi),
                     np.sin(theta) * np.sin(phi),
                     np.cos(theta)])

def ray_cylinder_intersection(origin, direction, R, d):
    x0, y0, z0 = origin
    l, m, n = direction
    
    a = l*l + m*m
    if a > 0:
        b = 2*(x0*l + y0*m)
        c = x0*x0 + y0*y0 - R*R
        disc = b*b - 4*a*c
        
        if disc >= 0:
            t1 = (-b - np.sqrt(disc)) / (2*a)
            t2 = (-b + np.sqrt(disc)) / (2*a)
            
            for t in sorted([t1, t2]):
                if t > 0:
                    z = z0 + n*t
                    if -d <= z <= d:
                        return origin + t * direction
    
    if n != 0:
        t = (d - z0) / n
        if t > 0:
            x = x0 + l*t
            y = y0 + m*t
            if x*x + y*y <= R*R:
                return origin + t * direction
        
        t = (-d - z0) / n
        if t > 0:
            x = x0 + l*t
            y = y0 + m*t
            if x*x + y*y <= R*R:
                return origin + t * direction
    
    return None

def flateABCD(P1, P2, P3):
    v1 = P2 - P1
    v2 = P3 - P1
    normal = np.cross(v1, v2)
    norm = np.linalg.norm(normal)
    if norm > 0:
        A, B, C = normal / norm
    else:
        A, B, C = normal
    D = -np.dot([A, B, C], P1)
    return np.array([A, B, C, D])

def sigma_photo(E, Z):
    sigma0 = 6.651e-25
    return sigma0 * 4 * np.sqrt(2) * (Z**5) / (137**4) * (MC2 / E)**(7/2)

def sigma_compton(E, Z):
    sigma0 = 6.651e-25
    gamma = E / MC2
    term1 = (1 - 2*(gamma+1)/gamma**2) * np.log(2*gamma + 1)
    term2 = 0.5 + 4/gamma - 1/(2*(2*gamma+1)**2)
    return sigma0 * (3*Z / (8*gamma)) * (term1 + term2)

def macro_cross_section(E):
    rho = 3.67
    M_NaI = M_NA + M_I
    n_mol = rho * NA / M_NaI
    n_Na = n_mol
    n_I = n_mol
    
    sigma_Na_ph = sigma_photo(E, Z_NA)
    sigma_Na_c = sigma_compton(E, Z_NA)
    sigma_I_ph = sigma_photo(E, Z_I)
    sigma_I_c = sigma_compton(E, Z_I)
    
    Sigma_ph = n_Na * sigma_Na_ph + n_I * sigma_I_ph
    Sigma_c = n_Na * sigma_Na_c + n_I * sigma_I_c
    
    return Sigma_ph, Sigma_c, Sigma_ph + Sigma_c

def free_path(Sigma):
    if Sigma <= 0:
        return float('inf')
    return -np.log(np.random.random()) / Sigma

def compton_energy_loss(energy, theta):
    return energy / (1 + energy / MC2 * (1 - np.cos(theta)))

def simulate_photon(source_pos, R, d, E0):
    direction = isotropic_direction()
    point = ray_cylinder_intersection(source_pos, direction, R, d)
    
    if point is None:
        return 0
    
    pos = point
    energy = E0
    
    while energy > 0:
        Sigma_ph, Sigma_c, Sigma_total = macro_cross_section(energy)
        
        l = free_path(Sigma_total)
        pos = pos + l * direction
        
        if abs(pos[2]) > d:
            break
        if pos[0]**2 + pos[1]**2 > R**2:
            break
        
        p_photo = Sigma_ph / Sigma_total
        if np.random.random() < p_photo:
            return energy
        else:
            cos_theta = 2 * np.random.random() - 1
            theta = np.arccos(cos_theta)
            E_scattered = compton_energy_loss(energy, theta)
            energy_deposit = energy - E_scattered
            energy = E_scattered
    
    return 0

def process_batch(args):
    batch_size, source_pos, R, d, E0 = args
    energies = []
    for _ in range(batch_size):
        E_dep = simulate_photon(source_pos, R, d, E0)
        energies.append(E_dep)
    return energies

def main():
    print("Моделирование работы гамма-детектора (цилиндр)")
    print("="*60)
    
    R = float(input("Введите радиус детектора R (см): "))
    H = float(input("Введите высоту детектора H (см): "))
    Xs = float(input("Введите X источника (см): "))
    Ys = float(input("Введите Y источника (см): "))
    Zs = float(input("Введите Z источника (см): "))
    N_photons = int(input("Введите количество фотонов: "))
    
    source_pos = np.array([Xs, Ys, Zs])
    d = H / 2
    E0 = 0.662
    
    print("\nПоследовательное моделирование...")
    start_time = time.time()
    
    spectrum = np.zeros(1024)
    Emax = 1.0
    Emin = 0.0
    dE = (Emax - Emin) / 1024
    
    for i in range(N_photons):
        if (i+1) % 1000 == 0:
            print(f"  {i+1}/{N_photons}")
        E_dep = simulate_photon(source_pos, R, d, E0)
        if E_dep > 0:
            channel = int(E_dep / dE)
            if channel < 1024:
                spectrum[channel] += 1
    
    seq_time = time.time() - start_time
    print(f"Время: {seq_time:.2f} сек")
    
    plt.figure(figsize=(12, 6))
    energy_axis = np.linspace(Emin, Emax, 1024)
    plt.plot(energy_axis, spectrum, 'b-', linewidth=0.5)
    plt.xlabel('Энергия (МэВ)')
    plt.ylabel('Количество отсчётов')
    plt.title(f'Спектр Cs-137 (NaI, R={R} см, H={H} см, N={N_photons})')
    plt.grid(True, alpha=0.3)
    plt.axvline(x=0.662, color='red', linestyle='--', alpha=0.7, label='Фотопик 0.662 МэВ')
    plt.axvline(x=0.184, color='green', linestyle='--', alpha=0.7, label='Комптоновское плечо')
    plt.legend()
    plt.xlim(0, 0.8)
    plt.tight_layout()
    plt.show()
    
    print("\n" + "="*60)
    print("Параллельное моделирование (задача 9)")
    print("="*60)
    
    n_cores = int(input("\nВведите количество ядер: "))
    batch_size = N_photons // n_cores
    if batch_size == 0:
        batch_size = 1
        n_cores = N_photons
    
    args = [(batch_size, source_pos, R, d, E0) for _ in range(n_cores)]
    
    print(f"Запуск на {n_cores} ядрах...")
    start_time = time.time()
    
    with Pool(processes=n_cores) as pool:
        results = pool.map(process_batch, args)
    
    parallel_time = time.time() - start_time
    
    spectrum_par = np.zeros(1024)
    for energies in results:
        for E_dep in energies:
            if E_dep > 0:
                channel = int(E_dep / dE)
                if channel < 1024:
                    spectrum_par[channel] += 1
    
    print(f"Время: {parallel_time:.2f} сек")
    print(f"Ускорение: {seq_time/parallel_time:.2f}x")
    
    plt.figure(figsize=(12, 6))
    plt.plot(energy_axis, spectrum, 'b-', linewidth=0.5, alpha=0.7, label='Последовательный')
    plt.plot(energy_axis, spectrum_par, 'r-', linewidth=0.5, alpha=0.7, label='Параллельный')
    plt.xlabel('Энергия (МэВ)')
    plt.ylabel('Количество отсчётов')
    plt.title('Сравнение спектров')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.xlim(0, 0.8)
    plt.tight_layout()
    plt.show()
    
    print("\nДругие источники:")
    print("  Co-60: 1.17 и 1.33 МэВ")
    print("  Na-22: 0.511 и 1.27 МэВ")
    print("  Am-241: 0.060 МэВ")
    
    answer = input("\nИзменить энергию? (y/n): ")
    if answer.lower() == 'y':
        new_E = float(input("Новая энергия (МэВ): "))
        spectrum_new = np.zeros(1024)
        for i in range(min(N_photons // 10, 10000)):
            E_dep = simulate_photon(source_pos, R, d, new_E)
            if E_dep > 0:
                channel = int(E_dep / dE)
                if channel < 1024:
                    spectrum_new[channel] += 1
        
        plt.figure(figsize=(12, 6))
        plt.plot(energy_axis, spectrum_new, 'g-', linewidth=0.5)
        plt.xlabel('Энергия (МэВ)')
        plt.ylabel('Количество отсчётов')
        plt.title(f'Спектр E={new_E} МэВ')
        plt.grid(True, alpha=0.3)
        plt.xlim(0, min(1.5, new_E * 1.2))
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    np.random.seed(42)
    main()
