# experiments.py - Исправленная версия
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
from environment import DeliveryEnvironment

def load_map(filename):
    """Правильная загрузка карты из файла"""
    try:
        with open(filename, 'r') as f:
            # Читаем все строки и преобразуем каждую в список чисел
            map_data = []
            for line in f:
                line = line.strip()
                if line:  # Пропускаем пустые строки
                    # Преобразуем каждый символ в int
                    row = [int(char) for char in line]
                    map_data.append(row)
            
            # Преобразуем в numpy array
            map_array = np.array(map_data)
            print(f"Карта загружена. Размер: {map_array.shape}")
            print(f"Уникальные значения: {np.unique(map_array)}")
            return map_array
    except FileNotFoundError:
        print(f"Ошибка: Файл {filename} не найден!")
        return None
    except Exception as e:
        print(f"Ошибка при загрузке карты: {e}")
        return None

def visualize_map(map_data, title="Карта города"):
    """Визуализация карты с правильным отображением"""
    if map_data is None:
        print("Нет данных для визуализации")
        return None, None
    
    # Создаем фигуру
    fig, ax = plt.subplots(figsize=(14, 14))
    
    # Создаем цветовую карту
    cmap = ListedColormap(['white', 'black', 'green', 'yellow', 'red'])
    
    # Отображаем карту
    im = ax.imshow(map_data, cmap=cmap, interpolation='nearest', vmin=0, vmax=4)
    
    # Добавляем сетку для лучшей видимости
    ax.grid(True, which='both', color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
    ax.set_xticks(np.arange(-0.5, map_data.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, map_data.shape[0], 1), minor=True)
    
    # Добавляем легенду
    legend_elements = [
        plt.Rectangle((0,0),1,1, facecolor='white', label='0 - Дорога'),
        plt.Rectangle((0,0),1,1, facecolor='black', label='1 - Стена'),
        plt.Rectangle((0,0),1,1, facecolor='green', label='2 - Старт агента'),
        plt.Rectangle((0,0),1,1, facecolor='yellow', label='3 - Место появления ТС'),
        plt.Rectangle((0,0),1,1, facecolor='red', label='4 - Цель доставки')
    ]
    ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.2, 1))
    
    plt.title(title)
    plt.tight_layout()
    plt.show()
    
    return fig, ax

class ExperimentRunner:
    def __init__(self, map_data):
        self.map_data = map_data
        self.spawn_positions = list(zip(*np.where(map_data == 3)))
        self.goal_positions = list(zip(*np.where(map_data == 4)))
        self.start_positions = list(zip(*np.where(map_data == 2)))
        
        print(f"Найдено стартовых позиций: {len(self.start_positions)}")
        print(f"Найдено мест появления ТС: {len(self.spawn_positions)}")
        print(f"Найдено целей: {len(self.goal_positions)}")
        
    def test_spawn_probabilities(self, probabilities, episodes_per_prob=30):
        """Тестирование различных вероятностей появления ТС"""
        results = {
            'probabilities': probabilities,
            'avg_steps': [],
            'success_rate': [],
            'crash_rate': [],
            'std_steps': []
        }
        
        for prob in probabilities:
            print(f"\nТестирование вероятности {prob:.3f}...")
            env = DeliveryEnvironment(self.map_data, vehicle_spawn_probability=prob)
            
            steps_list = []
            successes = 0
            crashes = 0
            
            for episode in range(episodes_per_prob):
                # Чередуем стартовые позиции
                if self.start_positions:
                    start_idx = episode % len(self.start_positions)
                else:
                    start_idx = 0
                    
                result = env.run_episode(agent_start_idx=start_idx, max_steps=500)
                
                steps_list.append(result['steps'])
                if result['success']:
                    successes += 1
                if result['crashed']:
                    crashes += 1
                
                # Прогресс
                if (episode + 1) % 10 == 0:
                    print(f"  Прогресс: {episode + 1}/{episodes_per_prob}")
            
            results['avg_steps'].append(np.mean(steps_list))
            results['std_steps'].append(np.std(steps_list))
            results['success_rate'].append(successes / episodes_per_prob)
            results['crash_rate'].append(crashes / episodes_per_prob)
            
            print(f"  Среднее шагов: {results['avg_steps'][-1]:.1f} ± {results['std_steps'][-1]:.1f}")
            print(f"  Успех: {results['success_rate'][-1]*100:.1f}%, Аварии: {results['crash_rate'][-1]*100:.1f}%")
        
        return results
    
    def plot_results(self, results):
        """Построение графиков результатов"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. График среднего количества шагов с погрешностью
        ax1.errorbar(results['probabilities'], results['avg_steps'], 
                    yerr=results['std_steps'], fmt='b-o', linewidth=2, 
                    markersize=8, capsize=5, capthick=2)
        ax1.set_xlabel('Вероятность появления ТС')
        ax1.set_ylabel('Среднее количество шагов')
        ax1.set_title('Зависимость времени доставки от загруженности')
        ax1.grid(True, alpha=0.3)
        ax1.set_xlim(-0.005, max(results['probabilities']) + 0.005)
        
        # 2. График успешности и аварий
        ax2.plot(results['probabilities'], results['success_rate'], 'g-o', 
                linewidth=2, markersize=8, label='Успешные доставки')
        ax2.plot(results['probabilities'], results['crash_rate'], 'r-o', 
                linewidth=2, markersize=8, label='Аварии')
        ax2.set_xlabel('Вероятность появления ТС')
        ax2.set_ylabel('Вероятность')
        ax2.set_title('Влияние загруженности на исход доставки')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(-0.005, max(results['probabilities']) + 0.005)
        ax2.set_ylim(-0.05, 1.05)
        
        # 3. Гистограмма распределения шагов для разных вероятностей
        for i, prob in enumerate(results['probabilities'][::2]):  # Каждая вторая вероятность
            ax3.bar(i, results['avg_steps'][i*2], label=f'p={prob:.3f}')
        ax3.set_xlabel('Вероятность ТС')
        ax3.set_ylabel('Среднее количество шагов')
        ax3.set_title('Сравнение времени доставки')
        ax3.set_xticks(range(len(results['probabilities'][::2])))
        ax3.set_xticklabels([f'{p:.3f}' for p in results['probabilities'][::2]])
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Диаграмма рассеяния успех/авария
        ax4.scatter(results['success_rate'], results['crash_rate'], 
                   c=results['probabilities'], cmap='viridis', s=100)
        ax4.set_xlabel('Вероятность успеха')
        ax4.set_ylabel('Вероятность аварии')
        ax4.set_title('Соотношение успехов и аварий')
        ax4.grid(True, alpha=0.3)
        
        # Добавляем colorbar для вероятностей
        cbar = plt.colorbar(ax4.collections[0], ax=ax4)
        cbar.set_label('Вероятность появления ТС')
        
        plt.suptitle('Анализ эффективности доставки в зависимости от загруженности дорог', 
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.show()
        
        return fig

class AnimationCreator:
    def __init__(self, map_data):
        self.map_data = map_data
        self.height, self.width = map_data.shape
        
        # Создаем цветовую карту для визуализации
        self.colors = ['white', 'black', 'green', 'yellow', 'red', 'blue', 'orange']
        self.cmap = ListedColormap(self.colors)
        
    def create_frame(self, env_state):
        """Создание одного кадра анимации"""
        frame = self.map_data.copy()
        
        # Отмечаем агента
        if env_state['agent_position']:
            ax, ay = env_state['agent_position']
            if 0 <= ax < frame.shape[0] and 0 <= ay < frame.shape[1]:
                frame[ax, ay] = 5  # Синий для агента
        
        # Отмечаем транспортные средства
        for v_pos in env_state['vehicle_positions']:
            vx, vy = v_pos
            if 0 <= vx < frame.shape[0] and 0 <= vy < frame.shape[1]:
                if frame[vx, vy] not in [5]:  # Не затираем агента
                    frame[vx, vy] = 6  # Оранжевый для ТС
        
        return frame
    
    def animate_episode(self, env, max_steps=200):
        """Создание анимации эпизода"""
        env.reset()
        frames = []
        step_data = []
        
        for step in range(max_steps):
            state, done = env.step()
            frames.append(self.create_frame(state))
            
            # Сохраняем данные
            agent_pos = state['agent_position']
            vehicle_positions = list(state['vehicle_positions']) if state['vehicle_positions'] else []
            step_data.append((agent_pos, vehicle_positions))
            
            if done:
                break
        
        if not frames:
            print("Нет кадров для анимации")
            return None
        
        # Создание анимации
        fig, ax = plt.subplots(figsize=(14, 14))
        
        def update(frame_num):
            ax.clear()
            
            # Отображаем текущий кадр
            im = ax.imshow(frames[frame_num], cmap=self.cmap, interpolation='nearest',
                          vmin=0, vmax=6)
            
            # Добавляем сетку
            ax.grid(True, which='both', color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
            ax.set_xticks(np.arange(-0.5, self.width, 1), minor=True)
            ax.set_yticks(np.arange(-0.5, self.height, 1), minor=True)
            
            # Получаем данные
            agent_pos, vehicle_positions = step_data[frame_num]
            
            # Заголовок
            ax.set_title(f'Шаг {frame_num + 1} из {len(frames)}', fontsize=14)
            
            # Статус
            status_text = f"Позиция агента: {agent_pos}\nАктивных ТС: {len(vehicle_positions)}"
            
            if frame_num == len(frames) - 1:
                if env.agent and env.agent.reached_goal:
                    status_text += "\n✓ ДОСТАВКА ВЫПОЛНЕНА!"
                    ax.text(0.5, 0.1, '✓ УСПЕХ', transform=ax.transAxes,
                           fontsize=20, color='green', ha='center',
                           bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8))
                elif env.agent and env.agent.crashed:
                    status_text += "\n✗ АВАРИЯ!"
                    ax.text(0.5, 0.1, '✗ АВАРИЯ', transform=ax.transAxes,
                           fontsize=20, color='red', ha='center',
                           bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.8))
            
            ax.text(0.02, 0.98, status_text, transform=ax.transAxes,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
                   verticalalignment='top', fontsize=11,
                   fontfamily='monospace')
            
            return [im]
        
        ani = animation.FuncAnimation(fig, update, frames=len(frames), 
                                     interval=300, blit=True, repeat=True)
        
        plt.tight_layout()
        return ani

# Основная часть
if __name__ == "__main__":
    print("=" * 70)
    print("МОДЕЛИРОВАНИЕ ДОСТАВКИ ГРУЗОВ В ГОРОДСКОЙ СРЕДЕ")
    print("=" * 70)
    
    # Загружаем карту
    city_map = load_map('cmap.txt')
    
    if city_map is None:
        print("Не удалось загрузить карту. Программа завершена.")
        exit()
    
    # Визуализируем карту
    print("\n" + "=" * 70)
    print("ВИЗУАЛИЗАЦИЯ КАРТЫ")
    print("=" * 70)
    visualize_map(city_map)
    
    # Создаем исполнителя экспериментов
    runner = ExperimentRunner(city_map)
    
    # Тестируем различные вероятности появления ТС
    probabilities = [0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.1, 0.12, 0.15]
    
    print("\n" + "=" * 70)
    print("ЗАПУСК ЭКСПЕРИМЕНТОВ")
    print("=" * 70)
    print(f"Количество эпизодов на вероятность: 30")
    print(f"Максимальное число шагов: 500")
    
    results = runner.test_spawn_probabilities(probabilities, episodes_per_prob=30)
    
    # Строим графики
    print("\n" + "=" * 70)
    print("ПОСТРОЕНИЕ ГРАФИКОВ")
    print("=" * 70)
    runner.plot_results(results)
    
    # Создаем анимацию
    print("\n" + "=" * 70)
    print("СОЗДАНИЕ АНИМАЦИИ")
    print("=" * 70)
    anim_creator = AnimationCreator(city_map)
    env_demo = DeliveryEnvironment(city_map, vehicle_spawn_probability=0.03)
    animation = anim_creator.animate_episode(env_demo, max_steps=200)
    
    if animation:
        try:
            print("Сохранение анимации...")
            animation.save('city_delivery.gif', writer='pillow', fps=5, dpi=100)
            print("✓ Анимация сохранена как 'city_delivery.gif'")
        except Exception as e:
            print(f"✗ Не удалось сохранить анимацию: {e}")
            print("Отображение анимации на экране...")
            plt.show()
    
    print("\n" + "=" * 70)
    print("ЭКСПЕРИМЕНТ ЗАВЕРШЕН УСПЕШНО")
    print("=" * 70)