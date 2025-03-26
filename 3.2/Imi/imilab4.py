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
width = 50  # Ширина сетки
height = 50  # Высота сетки

# Инициализация сетки
grid = np.random.choice([0, 1], size=(height, width), p=[0.8, 0.2])  # Случайное начальное состояние

# Функция для обновления состояния клеточного автомата
def update_automaton():
    global grid, is_running

    while is_running:
        new_grid = grid.copy()

        # Применяем правила игры "Жизнь"
        for i in range(height):
            for j in range(width):
                # Считаем количество живых соседей
                neighbors = (
                    grid[i - 1, j - 1] + grid[i - 1, j] + grid[i - 1, (j + 1) % width] +
                    grid[i, j - 1] + grid[i, (j + 1) % width] +
                    grid[(i + 1) % height, j - 1] + grid[(i + 1) % height, j] + grid[(i + 1) % height, (j + 1) % width]
                )

                # Правила игры "Жизнь"
                if grid[i, j] == 1:
                    if neighbors < 2 or neighbors > 3:
                        new_grid[i, j] = 0  # Клетка умирает
                else:
                    if neighbors == 3:
                        new_grid[i, j] = 1  # Клетка оживает

        grid = new_grid
        time.sleep(0.1)  # Задержка для визуализации

        # Обновляем график
        ax.clear()
        ax.imshow(grid, cmap="binary", interpolation="none")
        canvas.draw()

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
    grid = np.random.choice([0, 1], size=(height, width), p=[0.8, 0.2])  # Случайное начальное состояние
    ax.clear()
    ax.imshow(grid, cmap="binary", interpolation="none")
    canvas.draw()

# Создаем главное окно
root = tk.Tk()
root.title("Игра \"Жизнь\"")

# Кнопки для управления
button_start = tk.Button(root, text="Start", command=start_simulation)
button_start.grid(row=0, column=0, padx=5, pady=5)

button_stop = tk.Button(root, text="Stop", command=stop_simulation)
button_stop.grid(row=0, column=1, padx=5, pady=5)

button_reset = tk.Button(root, text="Reset", command=reset_simulation)
button_reset.grid(row=0, column=2, padx=5, pady=5)

# Создаем график
fig, ax = plt.subplots(figsize=(8, 8))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=1, column=0, columnspan=3, padx=5, pady=5)

# Отображаем начальное состояние
ax.imshow(grid, cmap="binary", interpolation="none")
ax.set_title("Игра \"Жизнь\"")
ax.axis("off")

# Запуск основного цикла
root.mainloop()