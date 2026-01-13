import math
import random

class PoissonGenerator:
    @staticmethod
    def get_poisson(lambda_):
        if lambda_ < 30:
            L = math.exp(-lambda_)
            k = 0
            p = 1.0
            while p > L:
                k += 1
                p *= random.random()
            return k - 1
        else:
            while True:
                u1 = random.random()
                u2 = random.random()
                while u1 <= 0:
                    u1 = random.random()
                z0 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
                sample = lambda_ + z0 * math.sqrt(lambda_)
                if sample >= 0:
                    return int(round(sample))

def simulate_matches():
    lambda_A = 50
    lambda_B = 49
    num_games = 1000  

    wins_A = 0
    wins_B = 0
    ties = 0

    for _ in range(num_games):
        points_A = PoissonGenerator.get_poisson(lambda_A)
        points_B = PoissonGenerator.get_poisson(lambda_B)

        if points_A > points_B:
            wins_A += 1
        elif points_B > points_A:
            wins_B += 1
        else:
            ties += 1

    print(f"Результаты {num_games} матчей:")
    print(f"Победы A: {wins_A} ({wins_A/num_games*100:.1f}%)")
    print(f"Победы B: {wins_B} ({wins_B/num_games*100:.1f}%)")
    print(f"Ничьи: {ties} ({ties/num_games*100:.1f}%)")

simulate_matches()