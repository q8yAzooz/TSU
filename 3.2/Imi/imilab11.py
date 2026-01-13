import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm, chi2
import random
import math

class NormalRVGenerator:
    @staticmethod
    def box_muller(size):
        samples = []
        for _ in range((size + 1) // 2):
            u1 = random.random()
            u2 = random.random()
            while u1 == 0:
                u1 = random.random()
            
            z0 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
            z1 = math.sqrt(-2 * math.log(u1)) * math.sin(2 * math.pi * u2)
            samples.extend([z0, z1])
        
        return np.array(samples[:size])

class NormalRVSimulation:
    def __init__(self):
        self.N_options = [10, 100, 1000, 10000]
        self.bins = 16
        self.min = -4
        self.max = 4

    def generate_standard_normal(self, size):
        return NormalRVGenerator.box_muller(size)

    def run_simulation(self, N, alpha=0.05):
        samples = self.generate_standard_normal(N)
        sample_mean = np.mean(samples)
        sample_variance = np.var(samples, ddof=1)

        abs_error_mean = abs(sample_mean - 0)  
        rel_error_variance = abs(sample_variance - 1) / 1 

        frequencies, bin_edges = np.histogram(samples, bins=self.bins, range=(self.min, self.max))
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

        expected = N * (norm.cdf(bin_edges[1:]) - norm.cdf(bin_edges[:-1]))
        chi_square = np.sum((frequencies - expected)**2 / expected)

        df = self.bins - 1
        critical_value = chi2.ppf(1 - alpha, df)
        p_value = 1 - chi2.cdf(chi_square, df)
        hypothesis = "НЕ отвергается" if chi_square <= critical_value else "ОТВЕРГАЕТСЯ"

        plt.bar(bin_centers, frequencies, width=(self.max - self.min)/self.bins, alpha=0.7, label='Эмпирическое')
        x = np.linspace(self.min, self.max, 1000)
        plt.plot(x, N * norm.pdf(x) * (self.max - self.min)/self.bins, 'r-', label='Теоретическое')
        plt.title(f'Гистограмма (N={N})')
        plt.xlabel('Значение')
        plt.ylabel('Частота')
        plt.legend()
        plt.show()

        return {
            'sample_mean': sample_mean,
            'abs_error_mean': abs_error_mean,
            'sample_variance': sample_variance,
            'rel_error_variance': rel_error_variance,
            'chi_square': chi_square,
            'critical_value': critical_value,
            'p_value': p_value,
            'hypothesis': hypothesis
        }

sim = NormalRVSimulation()
results = sim.run_simulation(10000)

print(f"[Результаты для N=10000]")
print(f"Выборочное среднее: {results['sample_mean']:.4f}")
print(f"Абсолютная ошибка среднего: {results['abs_error_mean']:.4f}")
print(f"Выборочная дисперсия: {results['sample_variance']:.4f}")
print(f"Относительная ошибка дисперсии: {results['rel_error_variance']:.4f}")
print(f"Хи-квадрат: {results['chi_square']:.2f}")
print(f"Критическое значение (α=0.05): {results['critical_value']:.2f}")
print(f"p-значение: {results['p_value']:.4f}")
print(f"Гипотеза о нормальности: {results['hypothesis']}")