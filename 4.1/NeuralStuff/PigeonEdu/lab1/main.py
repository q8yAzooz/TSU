# main.py - Основной файл для запуска симуляции
import numpy as np
import matplotlib.pyplot as plt
from citymap import load_map, visualize_map
from environment import DeliveryEnvironment
from experiments import ExperimentRunner, AnimationCreator

def main():
    print("=" * 70)
    print("СИМУЛЯЦИЯ ДОСТАВКИ ГРУЗОВ В ГОРОДСКОЙ СРЕДЕ")
    print("=" * 70)
    
    # Загружаем карту
    city_map = load_map('cmap.txt')
    print(f"\n✓ Карта загружена. Размер: {city_map.shape[0]} x {city_map.shape[1]}")
    
    # Визуализируем карту
    print("\n✓ Отображение карты города...")
    visualize_map(city_map)
    
    # Запускаем эксперименты
    print("\n" + "=" * 70)
    print("ЗАПУСК ЭКСПЕРИМЕНТОВ")
    print("=" * 70)
    
    runner = ExperimentRunner(city_map)
    
    # Различные вероятности появления ТС
    probabilities = [0.0, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.1]
    
    print("\nПроводим серию экспериментов...")
    results = runner.test_spawn_probabilities(probabilities, episodes_per_prob=50)
    
    # Вывод результатов
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТЫ ЭКСПЕРИМЕНТОВ")
    print("=" * 70)
    print(f"{'P(ТС)':<10} {'Ср. шаги':<12} {'Успех (%)':<12} {'Аварии (%)':<12}")
    print("-" * 46)
    
    for i, p in enumerate(probabilities):
        print(f"{p:<10.3f} {results['avg_steps'][i]:<12.1f} "
              f"{results['success_rate'][i]*100:<12.1f} "
              f"{results['crash_rate'][i]*100:<12.1f}")
    
    # Графики
    print("\n✓ Построение графиков...")
    runner.plot_results(results)
    
    # Создание анимации
    print("\n✓ Создание анимации движения...")
    anim_creator = AnimationCreator(city_map)
    
    # Демонстрация при средней загрузке
    env = DeliveryEnvironment(city_map, vehicle_spawn_probability=0.03)
    animation = anim_creator.animate_episode(env, max_steps=200)
    
    # Сохраняем анимацию
    animation.save('city_delivery.gif', writer='pillow', fps=5)
    print("  Анимация сохранена как 'city_delivery.gif'")
    
    # Дополнительный анализ
    print("\n" + "=" * 70)
    print("ДОПОЛНИТЕЛЬНЫЙ АНАЛИЗ")
    print("=" * 70)
    
    # Анализ влияния стартовой позиции
    print("\nВлияние стартовой позиции на успешность:")
    
    env = DeliveryEnvironment(city_map, vehicle_spawn_probability=0.03)
    start_positions = list(zip(*np.where(city_map == 2)))
    
    for i, start_pos in enumerate(start_positions):
        successes = 0
        for _ in range(20):
            result = env.run_episode(agent_start_idx=i)
            if result['success']:
                successes += 1
        print(f"  Старт {i+1} {start_pos}: успех {successes/20*100:.1f}%")
    
    print("\n" + "=" * 70)
    print("ЭКСПЕРИМЕНТ ЗАВЕРШЕН УСПЕШНО")
    print("=" * 70)

if __name__ == "__main__":
    main()