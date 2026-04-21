from dataclasses import dataclass
from typing import Optional
import json
import os


@dataclass
class Config:
    """Конфигурация приложения."""
    camera_id: int = 0
    camera_width: int = 640
    camera_height: int = 480
    camera_fps: int = 30
    
    model_path: str = "models/face_landmarker.task"
    
    perclos_threshold: float = 0.15
    ear_threshold: float = 0.20
    low_blink_rate_threshold: float = 8.0
    
    alert_cooldown: float = 3.0
    enable_console_logging: bool = True
    
    def save(self, path: str) -> None:
        """Сохраняет конфигурацию в JSON."""
        with open(path, 'w') as f:
            json.dump(self.__dict__, f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'Config':
        """Загружает конфигурацию из JSON."""
        if not os.path.exists(path):
            return cls()
        
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)


def load_config(path: Optional[str] = None) -> Config:
    """Загружает конфигурацию. Если путь не указан, возвращает значения по умолчанию."""
    if path and os.path.exists(path):
        return Config.load(path)
    return Config()