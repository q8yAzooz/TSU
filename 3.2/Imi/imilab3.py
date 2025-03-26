import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading
import time

# Глобальные переменные для управления потоком
is_running = False

# Параметры клеточного автомата
rule = 228  # Правило клеточного автомата (можно изменить)
width = 100  # Ширина сетки
height = 50  # Высота сетки

# Инициализация сетки
grid = np.zeros((height, width), dtype=int)
grid[0, width // 2] = 1  # Начальное состояние (одна клетка в центре)

# Функция для обновления состояния клеточного автомата
def update_automaton():
    global grid, is_running
    current_row = 0

    while is_running:
        if current_row >= height - 1:
            break  # Остановить, если достигли конца сетки

        # Применяем правило клеточного автомата для следующей строки
        for i in range(1, width - 1):
            left = grid[current_row, i - 1]
            center = grid[current_row, i]
            right = grid[current_row, i + 1]
            pattern = (left, center, right)
            new_state = apply_rule(pattern, rule)
            grid[current_row + 1, i] = new_state

        current_row += 1
        time.sleep(0.1)  # Задержка для визуализации

        # Обновляем график
        ax.clear()
        ax.imshow(grid, cmap="binary", interpolation="none")
        canvas.draw()

# Функция для применения правила клеточного автомата
def apply_rule(pattern, rule):
    # Преобразуем паттерн в индекс (0-7)
    index = int("".join(map(str, pattern)), 2)
    # Возвращаем бит из правила
    return (rule >> index) & 1

# Функция для запуска моделирования
def start_simulation():
    global is_running
    if not is_running:
        is_running = True
        threading.Thread(target=update_automaton, daemon=True).start()

# Функция для остановки моделирования
def stop_simulation():
    global is_running
    is_running = False

# Функция для сброса сетки
def reset_simulation():
    global grid
    grid = np.zeros((height, width), dtype=int)
    grid[0, width // 2] = 1  # Начальное состояние
    ax.clear()
    ax.imshow(grid, cmap="binary", interpolation="none")
    canvas.draw()

# Создаем главное окно
root = tk.Tk()
root.title("Элементарный клеточный автомат")

# Кнопки для управления
button_start = tk.Button(root, text="Start", command=start_simulation)
button_start.grid(row=0, column=0, padx=5, pady=5)

button_stop = tk.Button(root, text="Stop", command=stop_simulation)
button_stop.grid(row=0, column=1, padx=5, pady=5)

button_reset = tk.Button(root, text="Reset", command=reset_simulation)
button_reset.grid(row=0, column=2, padx=5, pady=5)

# Создаем график
fig, ax = plt.subplots(figsize=(8, 4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=1, column=0, columnspan=3, padx=5, pady=5)

# Отображаем начальное состояние
ax.imshow(grid, cmap="binary", interpolation="none")
ax.set_title(f"Элементарный клеточный автомат (Правило {rule})")
ax.axis("off")

# Запуск основного цикла
root.mainloop()