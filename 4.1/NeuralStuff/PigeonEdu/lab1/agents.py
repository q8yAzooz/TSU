# agents.py - Классы для агента и транспортных средств
import numpy as np
import random
from collections import deque

class Vehicle:
    def __init__(self, start_pos, map_data, vehicle_id):
        self.id = vehicle_id
        self.position = start_pos
        self.map_data = map_data
        self.steps_remaining = random.randint(15, 150)
        self.last_direction = None
        self.active = True
        
    def get_possible_moves(self):
        """Получить все возможные направления движения"""
        x, y = self.position
        possible_moves = []
        
        # Проверяем все 4 направления
        directions = [(-1, 0, 'up'), (1, 0, 'down'), (0, -1, 'left'), (0, 1, 'right')]
        
        for dx, dy, direction in directions:
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < self.map_data.shape[0] and 
                0 <= new_y < self.map_data.shape[1] and 
                self.map_data[new_x, new_y] in [0, 2, 3, 4]):  # Можно двигаться по дорогам
                possible_moves.append((new_x, new_y, direction))
        
        return possible_moves
    
    def move(self):
        """Выполнить движение"""
        if not self.active or self.steps_remaining <= 0:
            self.active = False
            return False
        
        possible_moves = self.get_possible_moves()
        
        if not possible_moves:
            self.active = False
            return False
        
        # Выбор направления движения
        if self.last_direction and len(possible_moves) > 1:
            # Пытаемся продолжить движение в том же направлении с вероятностью 70%
            same_direction_moves = [move for move in possible_moves if move[2] == self.last_direction]
            
            if same_direction_moves and random.random() < 0.7:
                chosen_move = same_direction_moves[0]
            else:
                # На развилке выбираем случайное направление
                chosen_move = random.choice(possible_moves)
        else:
            # В тупике или первый ход
            chosen_move = random.choice(possible_moves)
        
        # Обновляем позицию и направление
        self.position = (chosen_move[0], chosen_move[1])
        self.last_direction = chosen_move[2]
        self.steps_remaining -= 1
        
        return True

class DeliveryAgent:
    def __init__(self, start_pos, map_data):
        self.start_pos = start_pos
        self.position = start_pos
        self.map_data = map_data
        self.path = [start_pos]
        self.steps_taken = 0
        self.reached_goal = False
        self.crashed = False
        
    def reset(self):
        """Сбросить агента в начальное положение"""
        self.position = self.start_pos
        self.path = [self.start_pos]
        self.steps_taken = 0
        self.reached_goal = False
        self.crashed = False
    
    def get_possible_moves(self):
        """Получить все возможные направления движения"""
        x, y = self.position
        possible_moves = []
        
        directions = [(-1, 0, 'up'), (1, 0, 'down'), (0, -1, 'left'), (0, 1, 'right')]
        
        for dx, dy, direction in directions:
            new_x, new_y = x + dx, y + dy
            if (0 <= new_x < self.map_data.shape[0] and 
                0 <= new_y < self.map_data.shape[1] and 
                self.map_data[new_x, new_y] in [0, 2, 3, 4]):  # Можно двигаться по дорогам
                possible_moves.append((new_x, new_y, direction))
        
        return possible_moves
    
    def move(self, direction):
        """Движение в заданном направлении"""
        x, y = self.position
        dx, dy = 0, 0
        
        if direction == 'up':
            dx = -1
        elif direction == 'down':
            dx = 1
        elif direction == 'left':
            dy = -1
        elif direction == 'right':
            dy = 1
        
        new_x, new_y = x + dx, y + dy
        
        # Проверяем, можно ли двигаться
        if (0 <= new_x < self.map_data.shape[0] and 
            0 <= new_y < self.map_data.shape[1] and 
            self.map_data[new_x, new_y] in [0, 2, 3, 4]):
            
            self.position = (new_x, new_y)
            self.path.append((new_x, new_y))
            self.steps_taken += 1
            
            # Проверяем, достиг ли цели
            if self.map_data[new_x, new_y] == 4:
                self.reached_goal = True
            
            return True
        
        return False
    
    def move_towards_goal(self, goal_positions):
        """Эвристическое движение к ближайшей цели"""
        if not goal_positions:
            return False
        
        # Находим ближайшую цель
        distances = [abs(self.position[0] - g[0]) + abs(self.position[1] - g[1]) for g in goal_positions]
        closest_goal = goal_positions[np.argmin(distances)]
        
        # Определяем лучшее направление
        possible_moves = self.get_possible_moves()
        
        if not possible_moves:
            return False
        
        # Оцениваем каждое возможное направление
        best_move = None
        min_distance = float('inf')
        
        for move_x, move_y, direction in possible_moves:
            dist_to_goal = abs(move_x - closest_goal[0]) + abs(move_y - closest_goal[1])
            if dist_to_goal < min_distance:
                min_distance = dist_to_goal
                best_move = direction
        
        if best_move:
            return self.move(best_move)
        
        return False