import time
from collections import deque
from dataclasses import dataclass
from typing import Optional


@dataclass
class YawnResult:
    """Результат детекции зевания."""
    yawning: bool
    mar: float
    yawn_count: int
    excessive_yawning: bool
    warning: Optional[str] = None


class YawningDetector:
    """
    Детектор зевания на основе Mouth Aspect Ratio (MAR).
    
    Зевок характеризуется значительным и продолжительным открытием рта.
    """
    
    def __init__(self, 
                 mar_threshold: float = 0.6,
                 yawn_duration_frames: int = 15,
                 mar_history_size: int = 10,
                 yawn_rate_threshold: float = 3.0):
        """
        Args:
            mar_threshold: порог MAR для определения открытого рта
            yawn_duration_frames: минимальная длительность зевка в кадрах
            mar_history_size: размер истории MAR для сглаживания
            yawn_rate_threshold: порог частоты зевков в минуту для предупреждения
        """
        self.mar_threshold = mar_threshold
        self.yawn_duration_frames = yawn_duration_frames
        self.yawn_rate_threshold = yawn_rate_threshold
        
        self.mar_history = deque(maxlen=mar_history_size)
        self.mouth_open_frames = 0
        self.yawning = False
        self.yawn_count = 0
        self.yawn_timestamps = []
        
        self.last_mar = 0.0
    
    def update(self, mar: float) -> YawnResult:
        """
        Анализирует текущее значение MAR.
        
        Args:
            mar: Mouth Aspect Ratio (из FaceDetector)
        """
        now = time.time()
        
        self.mar_history.append(mar)
        smoothed_mar = sum(self.mar_history) / len(self.mar_history)
        self.last_mar = smoothed_mar
        
        mouth_open = smoothed_mar > self.mar_threshold
        
        if mouth_open:
            self.mouth_open_frames += 1
        else:
            if self.mouth_open_frames >= self.yawn_duration_frames:
                self.yawn_count += 1
                self.yawn_timestamps.append(now)
                self.yawning = True
            else:
                self.yawning = False
            self.mouth_open_frames = 0
        
        self.yawn_timestamps = [t for t in self.yawn_timestamps if now - t < 60.0]
        
        yawn_rate = len(self.yawn_timestamps)
        excessive = yawn_rate > self.yawn_rate_threshold and len(self.yawn_timestamps) > 1
        
        warning = None
        if self.yawning:
            warning = "Yawning detected"
        elif excessive:
            warning = f"Excessive yawning: {yawn_rate} times/min"
        
        return YawnResult(
            yawning=self.yawning,
            mar=smoothed_mar,
            yawn_count=self.yawn_count,
            excessive_yawning=excessive,
            warning=warning
        )
    
    def reset(self):
        self.mar_history.clear()
        self.mouth_open_frames = 0
        self.yawning = False
        self.yawn_count = 0
        self.yawn_timestamps.clear()
        self.last_mar = 0.0