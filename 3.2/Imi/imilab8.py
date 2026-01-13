import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

class StochasticApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Моделирование событий")

        self.events = []  
        self.probabilities = []

        self.setup_ui()

    def setup_ui(self):
        self.tree = ttk.Treeview(self.root, columns=("Event", "Probability"), show="headings")
        self.tree.heading("Event", text="Событие")
        self.tree.heading("Probability", text="Вероятность")
        self.tree.pack(padx=10, pady=10)

        self.add_initial_rows()

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="Добавить", command=self.add_row).grid(row=0, column=0, padx=2)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_row).grid(row=0, column=1, padx=2)

        ttk.Label(self.root, text="Количество испытаний (N):").pack()
        self.entry_n = ttk.Entry(self.root)
        self.entry_n.pack()

        ttk.Button(self.root, text="Старт", command=self.run_simulation).pack(pady=10)

        self.figure = plt.Figure(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.ax = self.figure.add_subplot(111)
        self.canvas.get_tk_widget().pack()

    def add_initial_rows(self):
        self.tree.insert("", "end", values=("Событие 1", 0.2))
        self.tree.insert("", "end", values=("Событие 2", 0.3))
        self.tree.insert("", "end", values=("Событие 3", 0.5))

    def add_row(self):
        self.tree.insert("", "end", values=("Новое событие", 0.0))

    def delete_row(self):
        selected = self.tree.selection()
        if selected:
            self.tree.delete(selected[0])

    def run_simulation(self):
        self.events.clear()
        self.probabilities.clear()
        
        for child in self.tree.get_children():
            values = self.tree.item(child)['values']
            if len(values) >= 2:
                try:
                    event = str(values[0])
                    prob = float(values[1])
                    self.events.append(event)
                    self.probabilities.append(prob)
                except ValueError:
                    messagebox.showerror("Ошибка", "Некорректное значение вероятности")
                    return

        total = sum(self.probabilities)
        if abs(total - 1.0) > 1e-6:
            messagebox.showerror("Ошибка", f"Сумма вероятностей: {total:.2f} ≠ 1")
            return

        try:
            N = int(self.entry_n.get())
            if N <= 0:
                raise ValueError
        except:
            messagebox.showerror("Ошибка", "N должно быть положительным целым числом")
            return

        freq = {event: 0 for event in self.events}
        for _ in range(N):
            r = random.random()
            cumulative = 0.0
            for i, p in enumerate(self.probabilities):
                cumulative += p
                if r < cumulative:
                    freq[self.events[i]] += 1
                    break

        self.ax.clear()
        events = list(freq.keys())
        empirical = [count/N for count in freq.values()]
        theoretical = self.probabilities

        width = 0.35
        x = range(len(events))
        self.ax.bar([xi - width/2 for xi in x], empirical, width, label='Эмпирические')
        self.ax.bar([xi + width/2 for xi in x], theoretical, width, label='Теоретические')
        
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(events)
        self.ax.legend()
        self.ax.set_ylim(0, 1.0)
        self.canvas.draw()

root = tk.Tk()
app = StochasticApp(root)
root.mainloop()