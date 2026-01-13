import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random

class Form1(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Симуляция валютных курсов")
        self.geometry("800x600")
        
        # Параметры модели
        self.mu_euro = 0.005
        self.mu_dollar = 0.008
        self.sigma = 0.1
        self.rand = random.Random()
        self.time_step = 0.1
        self.update_interval = 100  # миллисекунды
        
        # Начальные цены
        self.euro_price = 91.0
        self.dollar_price = 80.0
        self.time_points = [0]
        self.euro_prices = [self.euro_price]
        self.dollar_prices = [self.dollar_price]
        
        # Создание виджетов
        self.create_widgets()
        
        # Настройка графика
        self.setup_chart()
        
        self.is_running = False

    def create_widgets(self):
        # Фрейм для управления
        control_frame = tk.Frame(self)
        control_frame.pack(pady=10, fill=tk.X)
        
        # Метки и поля ввода
        tk.Label(control_frame, text="Начальная цена евро:").grid(row=0, column=0, padx=5)
        self.txt_euro_price = tk.Entry(control_frame, width=10)
        self.txt_euro_price.insert(0, "91.0")
        self.txt_euro_price.grid(row=0, column=1, padx=5)
        
        tk.Label(control_frame, text="Начальная цена доллара:").grid(row=0, column=2, padx=5)
        self.txt_dollar_price = tk.Entry(control_frame, width=10)
        self.txt_dollar_price.insert(0, "80.0")
        self.txt_dollar_price.grid(row=0, column=3, padx=5)
        
        # Кнопка управления
        self.btn_start_stop = tk.Button(control_frame, text="Старт", width=10, command=self.btn_start_stop_click)
        self.btn_start_stop.grid(row=0, column=4, padx=10)
        
        # Метки для отображения текущих цен
        price_frame = tk.Frame(self)
        price_frame.pack(pady=10, fill=tk.X)
        
        self.lbl_euro = tk.Label(price_frame, text="Текущий курс евро: 91.0000", font=("Arial", 10))
        self.lbl_euro.pack(side=tk.LEFT, padx=20)
        
        self.lbl_dollar = tk.Label(price_frame, text="Текущий курс доллара: 80.0000", font=("Arial", 10))
        self.lbl_dollar.pack(side=tk.LEFT, padx=20)
        
        self.chart_frame = tk.Frame(self)
        self.chart_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    def setup_chart(self):
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.ax.set_xlabel("Время (с)")
        self.ax.set_ylabel("Цена")
        self.ax.grid(True)
        
        self.euro_line, = self.ax.plot(self.time_points, self.euro_prices, 'g-', label="Евро")
        self.dollar_line, = self.ax.plot(self.time_points, self.dollar_prices, 'r-', label="Доллар")
        
        self.ax.legend()
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def btn_start_stop_click(self):
        if self.is_running:
            self.is_running = False
            self.btn_start_stop.config(text="Старт")
        else:
            try:
                self.euro_price = float(self.txt_euro_price.get())
                self.dollar_price = float(self.txt_dollar_price.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Пожалуйста, введите корректные начальные цены.")
                return
            
            self.time_points = [0]
            self.euro_prices = [self.euro_price]
            self.dollar_prices = [self.dollar_price]
            
            self.update_chart()
            
            self.is_running = True
            self.btn_start_stop.config(text="Стоп")
            self.simulate_step()

    def box_muller(self):
        # Генерация одного стандартного нормального значения методом Бокса-Мюллера
        u1 = self.rand.random()
        u2 = self.rand.random()
        z = np.sqrt(-2 * np.log(u1)) * np.cos(2 * np.pi * u2)
        return z

    def simulate_step(self):
        if not self.is_running:
            return
        
        zeta_euro = self.box_muller()
        zeta_dollar = self.box_muller()
        
        dt = self.time_step
        self.euro_price += (self.mu_euro * self.euro_price * dt + 
                           self.sigma * self.euro_price * np.sqrt(dt) * zeta_euro)
        
        self.dollar_price += (self.mu_dollar * self.dollar_price * dt + 
                            self.sigma * self.dollar_price * np.sqrt(dt) * zeta_dollar) 
        
        new_time = self.time_points[-1] + dt
        self.time_points.append(new_time)
        self.euro_prices.append(self.euro_price)
        self.dollar_prices.append(self.dollar_price)
        
        self.lbl_euro.config(text=f"Текущий курс евро: {self.euro_price:.4f}")
        self.lbl_dollar.config(text=f"Текущий курс доллара: {self.dollar_price:.4f}")
        
        self.update_chart()
        
        self.after(self.update_interval, self.simulate_step)

    def update_chart(self):
        self.euro_line.set_data(self.time_points, self.euro_prices)
        self.dollar_line.set_data(self.time_points, self.dollar_prices)
        
        self.ax.relim()
        self.ax.autoscale_view()
        
        self.canvas.draw()

if __name__ == "__main__":
    app = Form1()
    app.mainloop()