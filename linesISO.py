import numpy as np
import matplotlib.pyplot as plt

def simulate_particles(energies, probabilities, N):

    if abs(sum(probabilities) - 1.0) > 1e-6:
        raise ValueError("Сумма вероятностей должна быть равна 1")
    
    cum_probs = np.cumsum([0] + probabilities)[:-1]
    
    counts = [0, 0, 0]
    
    for _ in range(N):
        G = np.random.random() 
        
        if G < probabilities[0]:
            idx = 0
        elif G < probabilities[0] + probabilities[1]:
            idx = 1
        else:
            idx = 2
        
        counts[idx] += 1
    

    obtained_probs = [c/N for c in counts]

    deviations = [abs(obtained_probs[i] - probabilities[i]) for i in range(3)]
    
    return counts, obtained_probs, deviations

def plot_results(energies, probabilities, counts, obtained_probs, deviations, N):
    """Построение гистограммы и отображение отклонений"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    x = np.arange(3)
    width = 0.6
    
    bars = ax1.bar(x, counts, width, color=['blue', 'green', 'red'], alpha=0.7)
    ax1.set_xlabel('Энергетическая линия')
    ax1.set_ylabel('Количество частиц')
    ax1.set_title(f'Распределение частиц по энергиям (N={N})')
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'E1={energies[0]}', f'E2={energies[1]}', f'E3={energies[2]}'])
    
    for bar, count in zip(bars, counts):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.05 * max(counts),
                f'{count}', ha='center', va='bottom')
    
    ax1.grid(True, alpha=0.3, axis='y')
    
    x2 = np.arange(3)
    width2 = 0.35
    
    bars_given = ax2.bar(x2 - width2/2, probabilities, width2, 
                         label='Заданные', color='blue', alpha=0.5)
    bars_obtained = ax2.bar(x2 + width2/2, obtained_probs, width2, 
                           label='Полученные', color='green', alpha=0.7)
    
    ax2.set_xlabel('Энергетическая линия')
    ax2.set_ylabel('Вероятность')
    ax2.set_title('Сравнение заданных и полученных вероятностей')
    ax2.set_xticks(x2)
    ax2.set_xticklabels([f'E1={energies[0]}', f'E2={energies[1]}', f'E3={energies[2]}'])
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    for i in range(3):
        ax2.text(i + width2/2, obtained_probs[i] + 0.02, 
                f'Δ={deviations[i]:.4f}', 
                ha='center', va='bottom', fontsize=9, rotation=0)
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("Моделирование источника с тремя дискретными энергиями")

    
    E1 = float(input("Введите значение энергии E1: "))
    E2 = float(input("Введите значение энергии E2: "))
    E3 = float(input("Введите значение энергии E3: "))
    energies = [E1, E2, E3]
    
    P1 = float(input("Введите вероятность P1 (для E1): "))
    P2 = float(input("Введите вероятность P2 (для E2): "))
    P3 = float(input("Введите вероятность P3 (для E3): "))
    probabilities = [P1, P2, P3]

    if abs(P1 + P2 + P3 - 1.0) > 1e-6:
        print(f"Ошибка: сумма вероятностей равна {P1+P2+P3}, должна быть 1")
        exit()
    
    N = int(input("Введите количество частиц: "))
    
    # Моделирование
    counts, obtained_probs, deviations = simulate_particles(energies, probabilities, N)
    

 
    print("РЕЗУЛЬТАТЫ МОДЕЛИРОВАНИЯ")
 
    print(f"Всего частиц: {N}")
  
    print(f"{'Линия':<10} {'Энергия':<10} {'P_зад':<10} {'P_получ':<10} {'Отклонение':<10}")
   
    
    for i in range(3):
        print(f"E{i+1:<9} {energies[i]:<10.2f} {probabilities[i]:<10.4f} "
              f"{obtained_probs[i]:<10.4f} {deviations[i]:<10.6f}")
    
    
    print(f"Среднее отклонение: {np.mean(deviations):.6f}")
    print(f"Макс. отклонение: {np.max(deviations):.6f}")

    plot_results(energies, probabilities, counts, obtained_probs, deviations, N)

