# citymap.py - Карта города
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
import random
from collections import deque
import time

# Загружаем карту из файла
def load_map(filename):
    with open(filename, 'r') as f:
        return np.array([[int(char) for char in line.strip()] for line in f])
    
# Сохраняем карту в переменную
city_map = load_map('cmap.txt')
MAP_HEIGHT, MAP_WIDTH = city_map.shape

print(f"Размер карты: {MAP_HEIGHT} x {MAP_WIDTH}")

# Визуализация карты
def visualize_map(map_data, title="Карта города"):
    # Создаем цветовую карту
    colors = ['white', 'black', 'green', 'yellow', 'red']
    cmap = ListedColormap(colors)
    
    fig, ax = plt.subplots(figsize=(12, 12))
    im = ax.imshow(map_data, cmap=cmap, interpolation='nearest')
    
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

visualize_map(city_map)