import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import threading
import time

# Глобальные переменные для управления потоком
is_running = False
time_elapsed = 0

# Функция для генерации случайных данных (имитация курсов валют)
def generate_currency_data():
    return np.random.rand() * 10, np.random.rand() * 10  # Возвращаем два случайных значения

# Функция для обновления графиков и данных
def update_data():
    global is_running, time_elapsed
    while is_running:
        time.sleep(1)  # Обновляем данные каждую секунду
        time_elapsed += 1
        currency1, currency2 = generate_currency_data()

        # Добавляем данные в графики
        x_data.append(time_elapsed)
        y1_data.append(currency1)
        y2_data.append(currency2)

        # Обновляем графики
        ax1.clear()
        ax1.plot(x_data, y1_data, label="Currency 1")
        ax1.set_xlabel(" ")
        ax1.set_ylabel("Значение")
        ax1.set_title("Валюта 1")
        ax1.legend()
        ax1.grid(True)

        ax2.clear()
        ax2.plot(x_data, y2_data, label="Currency 2", color="orange")
        ax2.set_xlabel("Время (с)")
        ax2.set_ylabel("Значение")
        ax2.set_title("Валюта 2")
        ax2.legend()
        ax2.grid(True)

        canvas.draw()

        # Добавляем данные в таблицу
        table.insert("", "end", values=(time_elapsed, f"{currency1:.2f}", f"{currency2:.2f}"))

# Функция для запуска моделирования
def start_simulation():
    global is_running
    if not is_running:
        is_running = True
        threading.Thread(target=update_data, daemon=True).start()

# Функция для остановки моделирования
def stop_simulation():
    global is_running
    is_running = False

# Создаем главное окно
root = tk.Tk()
root.title("Currency Simulation")

# Кнопки для управления
button_start = tk.Button(root, text="Start", command=start_simulation)
button_start.grid(row=0, column=0, padx=5, pady=5)

button_stop = tk.Button(root, text="Stop", command=stop_simulation)
button_stop.grid(row=0, column=1, padx=5, pady=5)

# Создаем графики
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), sharey=True)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=1, column=0, columnspan=2, padx=5, pady=5)

# Данные для графиков
x_data, y1_data, y2_data = [], [], []

# Создаем таблицу для вывода результатов
columns = ("Время (с)", "Валюта 1", "Валюта 2")
table = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    table.heading(col, text=col)
table.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

# Запуск основного цикла
root.mainloop()