from enum import Enum
from typing import List, Optional
import time
from collections import deque


class AlertLevel(Enum):
    """Уровни тревоги."""
    INFO = 0
    WARNING = 1
    CRITICAL = 2


class AlertManager:
    """Управление оповещениями с подавлением повторяющихся срабатываний."""
    
    def __init__(self, 
                 cooldown_seconds: float = 3.0,
                 critical_cooldown: float = 1.0,
                 enable_console: bool = True):
        
        self.cooldown_seconds = cooldown_seconds
        self.critical_cooldown = critical_cooldown
        self.enable_console = enable_console
        
        self.last_alert_time = {level: 0.0 for level in AlertLevel}
        self.active_warnings: List[str] = []
        self.warning_history = deque(maxlen=50)
    
    def trigger(self, level: AlertLevel, message: str) -> bool:
        """
        Вызывает оповещение заданного уровня.
        Возвращает True, если оповещение действительно выдано (не подавлено).
        """
        now = time.time()
        cooldown = self.critical_cooldown if level == AlertLevel.CRITICAL else self.cooldown_seconds
        
        if now - self.last_alert_time[level] < cooldown:
            return False
        
        self.last_alert_time[level] = now
        self.warning_history.append((now, level, message))
        
        if level != AlertLevel.INFO:
            self.active_warnings.append(message)
        
        if self.enable_console:
            prefix = {AlertLevel.INFO: "[INFO]", 
                      AlertLevel.WARNING: "[WARNING]", 
                      AlertLevel.CRITICAL: "[CRITICAL]"}
            print(f"{prefix[level]} {message}")
        
        return True
    
    def clear_warnings(self) -> None:
        """Очищает список активных предупреждений."""
        self.active_warnings.clear()
    
    def get_active_warnings(self, max_count: int = 3) -> List[str]:
        """Возвращает список активных предупреждений."""
        return self.active_warnings[-max_count:] if self.active_warnings else []
    
    def get_color_for_level(self, level: AlertLevel) -> tuple:
        """Возвращает цвет BGR для уровня тревоги."""
        colors = {
            AlertLevel.INFO: (255, 255, 255),
            AlertLevel.WARNING: (0, 255, 255),
            AlertLevel.CRITICAL: (0, 0, 255)
        }
        return colors.get(level, (255, 255, 255))