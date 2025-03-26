import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

# Константы
g = 9.81  # ускорение свободного падения, м/с^2
rho = 1.225  # плотность воздуха, кг/м^3
C_d = 0.47  # коэффициент лобового сопротивления для сферы
A = 0.0001  # площадь поперечного сечения, м^2 (для маленького шарика)

# Функция для расчета ускорения с учетом сопротивления воздуха
def acceleration(v, m):
    return -g - (0.5 * rho * C_d * A * v**2) / m

# Функция для моделирования полета
def simulate_flight(dt, initial_height, initial_speed, angle, m):
    # Начальные условия
    v = initial_speed  # начальная скорость, м/с
    angle_rad = np.radians(angle)  # угол запуска в радианах
    vx = v * np.cos(angle_rad)
    vy = v * np.sin(angle_rad)
    x, y = 0.0, initial_height  # начальная высота

    # Массивы для хранения результатов
    x_list, y_list = [x], [y]

    # Моделирование
    while y >= 0:
        v = np.sqrt(vx**2 + vy**2)
        ax = - (0.5 * rho * C_d * A * v * vx) / m  # ускорение по x
        ay = acceleration(v, m)  # ускорение по y

        vx += ax * dt
        vy += ay * dt

        x += vx * dt
        y += vy * dt

        x_list.append(x)
        y_list.append(y)

    return x_list, y_list

# Функция для обновления графика и таблицы
def update_graph():
    dt = float(entry_dt.get())  # Получаем шаг времени из поля ввода
    initial_height = float(entry_height.get())  # Получаем начальную высоту
    initial_speed = float(entry_speed.get())  # Получаем начальную скорость
    angle = float(entry_angle.get())  # Получаем угол запуска
    m = float(entry_mass.get())  # Получаем массу

    x_list, y_list = simulate_flight(dt, initial_height, initial_speed, angle, m)  # Моделируем полет

    # Очищаем предыдущий график
    ax.clear()
    ax.plot(x_list, y_list, label=f"Шаг по времени = {dt} с")
    ax.set_xlabel("Расстояние (м)")
    ax.set_ylabel("Высота (м)")
    ax.set_title("Траектория полета")
    ax.legend()
    ax.grid(True)

    # Находим максимальное значение из X и Y
    max_x = max(x_list)
    max_y = max(y_list)
    max_limit = max(max_x, max_y)  # Берем наибольшее значение

    # Устанавливаем одинаковые пределы для обеих осей
    ax.set_xlim(0, max_limit)
    ax.set_ylim(0, max_limit)

    canvas.draw()

    # Добавляем запись в таблицу
    max_height = max(y_list)
    distance = x_list[-1]
    speed_end = np.sqrt((x_list[-1] - x_list[-2])**2 + (y_list[-1] - y_list[-2])**2) / dt

    table.insert("", "end", values=(dt, f"{distance:.2f} м", f"{max_height:.2f} м", f"{speed_end:.2f} м/с"))
    
# Создаем главное окно
root = tk.Tk()
root.title("Симулятор траектории полета")

# Поле для ввода шага времени
label_dt = tk.Label(root, text="Шаг по времени (с):")
label_dt.grid(row=0, column=0, padx=5, pady=5)
entry_dt = tk.Entry(root)
entry_dt.grid(row=0, column=1, padx=5, pady=5)
entry_dt.insert(0, "0.01")  # Уменьшенный шаг времени

# Поле для ввода начальной высоты
label_height = tk.Label(root, text="Изначальная высота (м):")
label_height.grid(row=1, column=0, padx=5, pady=5)
entry_height = tk.Entry(root)
entry_height.grid(row=1, column=1, padx=5, pady=5)
entry_height.insert(0, "0.0")  # Значение по умолчанию

# Поле для ввода начальной скорости
label_speed = tk.Label(root, text="Изначальная скорость (м/с):")
label_speed.grid(row=2, column=0, padx=5, pady=5)
entry_speed = tk.Entry(root)
entry_speed.grid(row=2, column=1, padx=5, pady=5)
entry_speed.insert(0, "100.0")  # Значение по умолчанию

# Поле для ввода угла запуска
label_angle = tk.Label(root, text="Угол (градусы):")
label_angle.grid(row=3, column=0, padx=5, pady=5)
entry_angle = tk.Entry(root)
entry_angle.grid(row=3, column=1, padx=5, pady=5)
entry_angle.insert(0, "30.0")  # Значение по умолчанию

# Поле для ввода массы
label_mass = tk.Label(root, text="Масса (кг):")
label_mass.grid(row=4, column=0, padx=5, pady=5)
entry_mass = tk.Entry(root)
entry_mass.grid(row=4, column=1, padx=5, pady=5)
entry_mass.insert(0, "0.001")  # Значение по умолчанию

# Кнопка для запуска моделирования
button_run = tk.Button(root, text="Запустить", command=update_graph)
button_run.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

# Создаем график
fig, ax = plt.subplots()
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=6, column=0, columnspan=2, padx=5, pady=5)

# Создаем таблицу для вывода результатов
columns = ("Шаг по времени", "Расстояние", "Максимальная высота", "Скорость в конечной точке")
table = ttk.Treeview(root, columns=columns, show="headings")
for col in columns:
    table.heading(col, text=col)
table.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

# Запуск основного цикла
root.mainloop()