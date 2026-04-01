
import math
import random
import numpy as np
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count

NA = 6.022e23  # Число Авогадро
mc2 = 0.511  # Энергия покоя электрона в МэВ
Z_Na = 11
Z_I = 53
A_Na = 22.99  # г/моль
A_I = 126.9  # г/моль
rho_NaI = 3.67  # г/см³
M_NaI = 149.89  # г/моль

# Расчет атомной плотности для Na и I в кристалле NaI
n_molecules = (rho_NaI / M_NaI) * NA  # молекул/см³
N_Na = n_molecules  # атомов Na/см³
N_I = n_molecules  # атомов I/см³

# Параметры спектра
E_min = 0.05
E_max = 1.0
num_channels = 1024
Cch = (E_max - E_min) / num_channels  # цена канала

def ray():
    """ изотропное направление, возвращает (l, m, n)"""
    theta = random.uniform(0, math.pi)
    phi = random.uniform(0, 2 * math.pi)
    l = math.sin(theta) * math.cos(phi)
    m = math.sin(theta) * math.sin(phi)
    n = math.cos(theta)
    return l, m, n


def flateABCD(P1, P2, P3):
    """
    коэффициенты плоскости по трем точкам
    """
    x1, y1, z1 = P1
    x2, y2, z2 = P2
    x3, y3, z3 = P3

    A = (y2 - y1) * (z3 - z1) - (z2 - z1) * (y3 - y1)
    B = (z2 - z1) * (x3 - x1) - (x2 - x1) * (z3 - z1)
    C = (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)
    D = - (A * x1 + B * y1 + C * z1)
    return A, B, C, D


def crossFlat(RAY, Ps_local, F):
    """
    Определяет точку пересечения луча и плоскости
    Возвращает t и точку пересечения (x, y, z) или None, если t < 0
    """
    l, m, n = RAY
    x0, y0, z0 = Ps_local
    A, B, C, D = F

    denominator = A * l + B * m + C * n
    if abs(denominator) < 1e-12:  # Луч параллелен плоскости
        return None, None

    t = - (A * x0 + B * y0 + C * z0 + D) / denominator

    if t < 0:  #  позади источника
        return None, None

    x = x0 + l * t
    y = y0 + m * t
    z = z0 + n * t
    return t, (x, y, z)


def insideFlat(R_cyl, P_cross):
    """
    Проверяет, что точка пересечения лежит в пределах торца цилиндра
    """
    x, y, z = P_cross
    # Расстояние от оси цилиндра (оси Z)
    r = math.sqrt(x ** 2 + y ** 2)
    return r <= R_cyl


def crossCil(RAY, R_cyl):
    """
    Определяет пересечение луча с бесконечным цилиндром x^2 + y^2 = R^2
    Возвращает минимальное положительное t и точку пересечения (x, y, z)
    """
    l, m, n = RAY
    x0, y0, z0 = Ps  # используем глобальные координаты источника

    a = l ** 2 + m ** 2
    if a < 1e-12:  # Луч // оси Z
        return None, None

    b = 2 * (x0 * l + y0 * m)
    c = x0 ** 2 + y0 ** 2 - R_cyl ** 2

    D_val = b ** 2 - 4 * a * c

    if D_val < 0:
        return None, None

    t1 = (-b - math.sqrt(D_val)) / (2 * a)
    t2 = (-b + math.sqrt(D_val)) / (2 * a)

    # наименьшее положительное t
    t_min = None
    for t in [t1, t2]:
        if t > 1e-12:  #и не слишком маленькое
            if t_min is None or t < t_min:
                t_min = t

    if t_min is None:
        return None, None

    x = x0 + l * t_min
    y = y0 + m * t_min
    z = z0 + n * t_min
    return t_min, (x, y, z)


def insideCil(d_half, P):
    """
    Проверяет, что точка P находится внутри цилиндра
    """
    x, y, z = P

    if abs(z) > d_half:
        return False

    if math.sqrt(x ** 2 + y ** 2) > R:
        return False
    return True


def inObj(P):
    """
    Проверяет, что точка взаимодействия внутри цилиндра
    (обертка для insideCil с глобальными параметрами)
    """
    return insideCil(d, P)


# Физические функции
def sigmaPh(E, Z):
    """
    Микроскопическое сечение фотоэффекта на K-оболочке
    """
    if E <= 0:
        return 0
    # 6.651e-25 - классический радиус электрона
    return 6.651e-25 * 4 * math.sqrt(2) * (Z ** 5) / (137 ** 4) * (mc2 / E) ** (7 / 2)


def sigmaK(E, Z):
    """
    Микроскопическое сечение комптон-эффекта
    """
    if E <= 0:
        return 0
    gamma = E / mc2
    if gamma <= 0:
        return 0

    #  со слайда
    term1 = 1 - (2 * (gamma + 1) / gamma ** 2) * math.log(2 * gamma + 1)
    term2 = 1 / 2 + 4 / gamma - 1 / (2 * (2 * gamma + 1) ** 2)

    return 6.651e-25 * (3 * Z) / (8 * gamma) * (term1 + term2)


def Sigma(sigmaPh_values, sigmaK_values):
    """
    Вычисляет макроскопические сечения для всех атомов
    sigmaPh_values, sigmaK_values - списки для Na и I
    Возвращает (Sigma_ph_total, Sigma_k_total, Sigma_total)
    """
    # Фотоэффект: Σ = (5/4) * N * σ
    Sigma_ph_Na = (5 / 4) * N_Na * sigmaPh_values[0]  # sigmaPh для Na
    Sigma_ph_I = (5 / 4) * N_I * sigmaPh_values[1]  # sigmaPh для I
    Sigma_ph_total = Sigma_ph_Na + Sigma_ph_I

    # Комптон: Σ = N_A * (Z/A) * σ_K
    # для каждого атома
    Sigma_k_Na = NA * (Z_Na / A_Na) * sigmaK_values[0] * 1e-24
    Sigma_k_I = NA * (Z_I / A_I) * sigmaK_values[1]
    Sigma_k_total = Sigma_k_Na + Sigma_k_I

    Sigma_total = Sigma_ph_total + Sigma_k_total

    return Sigma_ph_total, Sigma_k_total, Sigma_total


def Length(Sigma_total):
    """
    Разыгрывает среднюю длину свободного пробега
    """
    if Sigma_total <= 0:
        return float('inf')
    return - (1.0 / Sigma_total) * math.log(random.random())


def Interaction(P_cross, l, m, n, L):
    """
    Вычисляет координату взаимодействия
    """
    x, y, z = P_cross
    x_int = x + l * L
    y_int = y + m * L
    z_int = z + n * L
    return (x_int, y_int, z_int)


def cost(l, m, n, ll, mm, nn):
    """
    Вычисляет косинус угла между двумя единичными векторами
    """
    return l * ll + m * mm + n * nn


def Eloss(cos_theta, E):
    """
    Определяет потерянную энергию при комптоновском рассеянии
    Формула комптон-эффекта: E' = E / (1 + γ(1-cosθ))
    Потерянная энергия: ΔE = E - E'
    """
    gamma = E / mc2
    # Энергия после рассеяния
    E_prime = E / (1 + gamma * (1 - cos_theta))
    return E - E_prime


def Lottery(Sigma_ph, Sigma_k, Sigma_total):
    """
    Разыгрывает тип взаимодействия на основе сечений
    Возвращает 'ph' для фотоэффекта, 'k' для комптона
    """
    if Sigma_total <= 0:
        return None

    rand = random.random()
    p_ph = Sigma_ph / Sigma_total

    if rand < p_ph:
        return 'ph'
    else:
        return 'k'

# === ФУНКЦИИ ДЛЯ МНОГОПОТОЧНОСТИ ===

def init_worker(R_val, d_val, Ps_val, F_top_val, F_bottom_val):
    """Инициализирует глобальные переменные внутри каждого ядра"""
    global R, d, Ps, F_top, F_bottom
    R = R_val
    d = d_val
    Ps = Ps_val
    F_top = F_top_val
    F_bottom = F_bottom_val


def simulate_event(_):
    """Вся логика расчета одной частицы (перенесена из цикла)"""
    local_spectrum_updates = []
    
    # Начальная энергия для Cs-137
    E = 0.662  # МэВ

    # начальное направление
    l, m, n = ray()

    # Текущая точка старта (источник)
    current_point = Ps

    # пересечение с верхним торцом
    t_top, P_top = crossFlat((l, m, n), current_point, F_top)
    hit_top = False
    if t_top is not None and insideFlat(R, P_top):
        hit_top = True
        t_entry = t_top
        P_entry = P_top

    # пересечение с нижним торцом
    t_bottom, P_bottom = crossFlat((l, m, n), current_point, F_bottom)
    hit_bottom = False
    if t_bottom is not None and insideFlat(R, P_bottom):
        hit_bottom = True
        if not hit_top or t_bottom < t_entry:
            t_entry = t_bottom
            P_entry = P_bottom

    # пересечение с цилиндром
    t_cyl, P_cyl = crossCil((l, m, n), R)
    hit_cyl = False
    if t_cyl is not None and insideCil(d, P_cyl):
        hit_cyl = True
        # Проверяем, что это ближайшее пересечение
        if (not hit_top and not hit_bottom) or (hit_top and t_cyl < t_entry) or (hit_bottom and t_cyl < t_entry):
            t_entry = t_cyl
            P_entry = P_cyl

    if not (hit_top or hit_bottom or hit_cyl):
        return local_spectrum_updates

    # детектор в точке P_entry
    current_point = P_entry

    # фотон внутри детектора
    while E > 0:
        # сечения для текущей энергии
        sigma_ph_Na = sigmaPh(E, Z_Na)
        sigma_ph_I = sigmaPh(E, Z_I)
        sigma_k_Na = sigmaK(E, Z_Na)
        sigma_k_I = sigmaK(E, Z_I)

        Sigma_ph, Sigma_k, Sigma_total = Sigma([sigma_ph_Na, sigma_ph_I], [sigma_k_Na, sigma_k_I])

        if Sigma_total <= 0:
            break

        # свободного пробега
        L = Length(Sigma_total)

        #  точка взаимодействия
        P_int = Interaction(current_point, l, m, n, L)

        # взаимодействие внутри детектора?
        if not inObj(P_int):
            break

        interaction_type = Lottery(Sigma_ph, Sigma_k, Sigma_total)

        if interaction_type == 'ph':
            # Фотоэффект - вся энергия поглощена
            channel = int(round(E / Cch))
            if 0 <= channel < num_channels:
                local_spectrum_updates.append(channel)
            break

        elif interaction_type == 'k':
            # Комптон-эффект
            # новое направление
            l_new, m_new, n_new = ray()

            # косинус угла между старым и новым направлением
            cos_theta = cost(l, m, n, l_new, m_new, n_new)

            # потерянная энергия
            dE = Eloss(cos_theta, E)

            # Регистрируем её
            if dE > 0:
                channel = int(round(dE / Cch))
                if 0 <= channel < num_channels:
                    local_spectrum_updates.append(channel)

            # Обновляем энергию фотона
            E = E - dE

            # Обновляем направление
            l, m, n = l_new, m_new, n_new

            # Обновляем текущую точку
            current_point = P_int
            
    return local_spectrum_updates


# === ГЛАВНЫЙ БЛОК ПРОГРАММЫ ===

if __name__ == '__main__':
    # Ввод параметров детектора и источника
    print("Введите параметры детектора :")
    R_input = float(input("Радиус цилиндра R (см): "))
    D_input = float(input("Высота цилиндра D (см): "))
    d_input = D_input / 2

    print("\nВведите координаты источника:")
    XO = float(input("XO (см): "))
    YO = float(input("YO (см): "))
    ZO = float(input("ZO (см): "))

    N_events = int(input("\nКоличество  событий: "))
    
    # Запрос количества ядер
    max_cores = cpu_count()
    cores = int(input(f"Количество ядер для расчёта (доступно {max_cores}): "))
    
    spectrum = [0] * num_channels

    # Подготовка глобальных переменных (передаем их в воркеры)
    Ps_val = (XO, YO, ZO)
    P1_top = (0, 0, d_input); P2_top = (R_input, 0, d_input); P3_top = (0, R_input, d_input)
    F_top_val = flateABCD(P1_top, P2_top, P3_top)

    P1_bottom = (0, 0, -d_input); P2_bottom = (R_input, 0, -d_input); P3_bottom = (0, R_input, -d_input)
    F_bottom_val = flateABCD(P1_bottom, P2_bottom, P3_bottom)

    print("\nМоделирование началось...")
    
    # Запуск многопроцессорности
    with Pool(processes=cores, initializer=init_worker, initargs=(R_input, d_input, Ps_val, F_top_val, F_bottom_val)) as pool:
        # map возвращает результаты (обновления каналов) для каждой частицы
        results = pool.imap_unordered(simulate_event, range(N_events), chunksize=1000)
        
        for i, channel_updates in enumerate(results):
            if (i + 1) % 10000 == 0:
                print(f"Обработано {i + 1} событий из {N_events}")
            # Добавляем данные частицы в общий спектр
            for channel in channel_updates:
                spectrum[channel] += 1

    # Построение графика (цвет 'k-' означает чёрный)
    channels = np.arange(num_channels)
    energy_axis = channels * Cch + E_min

    plt.figure(figsize=(12, 6))
    plt.plot(energy_axis, spectrum, 'k-', linewidth=0.5)
    plt.xlabel('Энергия (МэВ)')
    plt.ylabel('Количество отсчетов')
    plt.title(f'Смоделированный спектр Cs-137 (N={N_events} событий)')
    plt.grid(True, alpha=0.3)
    plt.xlim(E_min, E_max)
    plt.show()
