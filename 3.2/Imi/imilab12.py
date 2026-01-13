import tkinter as tk
from tkinter import messagebox
import random
import math
import time

class Form1(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Погодная симуляция")
        self.geometry("400x350")
        self.resizable(False, False)
        
        self.rand = random.Random()
        self.leaving_rates = [0.4, 0.8, 0.5]
        self.transitions = [
            [(1, 0.75), (2, 0.25)],
            [(0, 0.5), (2, 0.5)],
            [(0, 0.2), (1, 0.8)]
        ]
        self.state_names = ["Ясно", "Облачно", "Пасмурно"]
        self.colors = ["#87CEEB", "#D3D3D3", "#A9A9A9"]
        
        self.panelWeather = tk.Label(self, height=5, width=50, relief="sunken")
        self.panelWeather.pack(pady=10)
        
        self.lblWeather = tk.Label(self, font=("Arial", 14))
        self.lblWeather.pack()
        
        self.lblTime = tk.Label(self, font=("Arial", 12))
        self.lblTime.pack(pady=5)
        
        frame_probs = tk.Frame(self)
        frame_probs.pack(pady=10)
        
        self.lblP1 = tk.Label(frame_probs, font=("Arial", 10), anchor="w")
        self.lblP1.pack(fill="x")
        self.lblP2 = tk.Label(frame_probs, font=("Arial", 10), anchor="w")
        self.lblP2.pack(fill="x")
        self.lblP3 = tk.Label(frame_probs, font=("Arial", 10), anchor="w")
        self.lblP3.pack(fill="x")
        
        self.btnControl = tk.Button(self, text="Старт", width=10, command=self.btnControl_Click)
        self.btnControl.pack(pady=15)
        
        self.isRunning = False
        self.reset_simulation()

    def reset_simulation(self):
        self.current_state = 0
        self.current_time = 0.0
        self.last_update_time = 0.0
        self.durations = [0.0, 0.0, 0.0]
        self.next_transition_time = -math.log(self.rand.random()) / self.leaving_rates[self.current_state]
        
        self.lblWeather.config(text=self.state_names[self.current_state])
        self.lblTime.config(text="0 дней")
        self.lblP1.config(text="P(Ясно): 0.0000")
        self.lblP2.config(text="P(Облачно): 0.0000")
        self.lblP3.config(text="P(Пасмурно): 0.0000")
        self.panelWeather.config(bg=self.colors[self.current_state])
        self.btnControl.config(text="Старт")

    def btnControl_Click(self):
        if not self.isRunning:
            if self.btnControl.cget("text") == "Старт":
                self.reset_simulation()
            self.isRunning = True
            self.btnControl.config(text="Пауза")
            self.timer_tick()
        else:
            self.isRunning = False
            self.btnControl.config(text="Продолжить")

    def timer_tick(self):
        if not self.isRunning:
            return
            
        dt = 0.2  
        self.current_time += dt
        
        while self.next_transition_time <= self.current_time:
            self.durations[self.current_state] += self.next_transition_time - self.last_update_time
            self.last_update_time = self.next_transition_time
            
            r = self.rand.random()
            cum_prob = 0.0
            for state, prob in self.transitions[self.current_state]:
                cum_prob += prob
                if r < cum_prob:
                    self.current_state = state
                    break
            
            rate = self.leaving_rates[self.current_state]
            self.next_transition_time += -math.log(self.rand.random()) / rate
        
        self.durations[self.current_state] += self.current_time - self.last_update_time
        self.last_update_time = self.current_time
        
        self.lblWeather.config(text=self.state_names[self.current_state])
        self.lblTime.config(text=f"{int(self.current_time)} дней")
        self.panelWeather.config(bg=self.colors[self.current_state])
        
        if self.current_time > 0:
            total_time = self.current_time
            self.lblP1.config(text=f"P(Ясно): {self.durations[0] / total_time:.4f}")
            self.lblP2.config(text=f"P(Облачно): {self.durations[1] / total_time:.4f}")
            self.lblP3.config(text=f"P(Пасмурно): {self.durations[2] / total_time:.4f}")
        
        if self.current_time >= 50:
            self.isRunning = False
            self.btnControl.config(text="Старт")
            total_time = self.current_time
            messagebox.showinfo(
                "Симуляция завершена",
                f"Итоговое P(Ясно): {self.durations[0]/total_time:.4f}\n"
                f"Итоговое P(Облачно): {self.durations[1]/total_time:.4f}\n"
                f"Итоговое P(Пасмурно): {self.durations[2]/total_time:.4f}"
            )
        else:
            self.after(100, self.timer_tick)

if __name__ == "__main__":
    app = Form1()
    app.mainloop()