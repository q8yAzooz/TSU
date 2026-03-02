# environment.py - Среда для симуляции
import numpy as np
import random
import matplotlib.pyplot as plt
from collections import deque
from agents import Vehicle, DeliveryAgent

class DeliveryEnvironment:
    def __init__(self, map_data, vehicle_spawn_probability=0.02):
        self.original_map = map_data.copy()
        self.map = map_data.copy()
        self.height, self.width = map_data.shape
        
        # Находим все особые точки
        self.start_positions = list(zip(*np.where(map_data == 2)))
        self.goal_positions = list(zip(*np.where(map_data == 4)))
        self.spawn_positions = list(zip(*np.where(map_data == 3)))
        
        # Параметры
        self.vehicle_spawn_probability = vehicle_spawn_probability
        self.vehicles = []
        self.vehicle_counter = 0
        self.agent = None
        self.episode_steps = 0
        self.episodes_completed = 0
        
        # История для статистики
        self.steps_history = []
        self.success_history = []
        
    def reset(self, agent_start_idx=0):
        """Сброс среды для нового эпизода"""
        self.map = self.original_map.copy()
        self.vehicles = []
        self.vehicle_counter = 0
        
        # Создаем агента на стартовой позиции
        if self.start_positions:
            start_pos = self.start_positions[agent_start_idx % len(self.start_positions)]
            self.agent = DeliveryAgent(start_pos, self.original_map)
        
        self.episode_steps = 0
        return self.get_state()
    
    def get_state(self):
        """Получить текущее состояние среды"""
        state = {
            'agent_position': self.agent.position if self.agent else None,
            'vehicle_positions': [v.position for v in self.vehicles if v.active],
            'map': self.map,
            'steps': self.episode_steps,
            'agent_reached_goal': self.agent.reached_goal if self.agent else False,
            'agent_crashed': self.agent.crashed if self.agent else False
        }
        return state
    
    def spawn_vehicle(self):
        """Попытка создать новое транспортное средство"""
        if random.random() < self.vehicle_spawn_probability and self.spawn_positions:
            spawn_pos = random.choice(self.spawn_positions)
            # Проверяем, не занята ли позиция
            position_free = True
            for v in self.vehicles:
                if v.active and v.position == spawn_pos:
                    position_free = False
                    break
            
            if position_free and self.agent and self.agent.position != spawn_pos:
                vehicle = Vehicle(spawn_pos, self.original_map, self.vehicle_counter)
                self.vehicles.append(vehicle)
                self.vehicle_counter += 1
    
    def move_vehicles(self):
        """Переместить все транспортные средства"""
        for vehicle in self.vehicles:
            if vehicle.active:
                vehicle.move()
    
    def check_collisions(self):
        """Проверить столкновения агента с ТС"""
        if not self.agent:
            return False
        
        agent_pos = self.agent.position
        
        for vehicle in self.vehicles:
            if vehicle.active and vehicle.position == agent_pos:
                self.agent.crashed = True
                return True
        
        return False
    
    def step(self, agent_action=None):
        """Выполнить один шаг симуляции"""
        self.episode_steps += 1
        
        # Спавн новых ТС
        self.spawn_vehicle()
        
        # Движение агента
        if self.agent and not self.agent.reached_goal and not self.agent.crashed:
            if agent_action is None:
                # Автоматическое движение к цели
                self.agent.move_towards_goal(self.goal_positions)
            else:
                # Движение по заданному действию
                self.agent.move(agent_action)
        
        # Движение ТС
        self.move_vehicles()
        
        # Проверка столкновений
        collision = self.check_collisions()
        
        # Проверка завершения эпизода
        done = False
        if self.agent:
            if self.agent.reached_goal:
                done = True
                self.success_history.append(1)
                self.steps_history.append(self.agent.steps_taken)
            elif self.agent.crashed:
                done = True
                self.success_history.append(0)
                self.steps_history.append(self.agent.steps_taken)
        
        return self.get_state(), done
    
    def run_episode(self, agent_start_idx=0, max_steps=1000):
        """Запустить один эпизод"""
        self.reset(agent_start_idx)
        
        for _ in range(max_steps):
            state, done = self.step()
            if done:
                break
        
        self.episodes_completed += 1
        
        return {
            'success': self.agent.reached_goal if self.agent else False,
            'steps': self.agent.steps_taken if self.agent else max_steps,
            'crashed': self.agent.crashed if self.agent else False
        }