import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import chisquare

def main():
    values = np.array([1, 2, 3, 4, 5])
    probs = np.array([0.1, 0.5, 0.1, 0.1, 0.2])
    theoretical_mean = np.dot(values, probs)
    theoretical_var = np.dot(values**2, probs) - theoretical_mean**2
    
    Ns = [10, 100, 1000, 10000]
    alpha = 0.05
    colors = ['#1f77b4', '#ff7f0e'] 

    for N in Ns:
        samples = np.random.choice(values, size=N, p=probs)
        freq = np.array([np.sum(samples == v) for v in values])
        emp_probs = freq / N

        sample_mean = np.mean(samples)
        sample_var = np.var(samples, ddof=1)
        chi2, p_val = chisquare(freq, f_exp=probs*N)
        hypothesis_result = "ОТВЕРГАЕТСЯ" if p_val < alpha else "НЕ ОТВЕРГАЕТСЯ"

        plt.figure(figsize=(10, 5))
        x = np.arange(len(values))
        width = 0.35

        bars1 = plt.bar(x - width/2, emp_probs, width, 
                       label='Эмпирические', color=colors[0], alpha=0.7)
        bars2 = plt.bar(x + width/2, probs, width, 
                       label='Теоретические', color=colors[1], alpha=0.7)

        plt.title(f'Сравнение вероятностей (N={N})')
        plt.xlabel('Значения')
        plt.ylabel('Вероятность')
        plt.xticks(x, values)
        plt.legend()
        plt.ylim(0, 0.6)

        for bar1, bar2 in zip(bars1, bars2):
            height1 = bar1.get_height()
            height2 = bar2.get_height()
            plt.text(bar1.get_x() + bar1.get_width()/2, height1 + 0.01,
                    f'{height1:.2f}', ha='center')
            plt.text(bar2.get_x() + bar2.get_width()/2, height2 + 0.01,
                    f'{height2:.2f}', ha='center')
        
        plt.tight_layout()
        plt.show()

        print(f"\n{'='*50}\nN = {N}:")
        print(f"Выборочное среднее: {sample_mean:.4f} (теор.: {theoretical_mean:.4f})")
        print(f"Выборочная дисперсия: {sample_var:.4f} (теор.: {theoretical_var:.4f})")
        print(f"Хи-квадрат: {chi2:.4f}, p-значение: {p_val:.4f}")
        print(f"Гипотеза: {hypothesis_result} (α={alpha})")

if __name__ == "__main__":
    main()