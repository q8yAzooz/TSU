from collections import deque
import time
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
import numpy as np

from core.face_detector import FaceDetectionResult


class DrowsinessState(Enum):
    """Состояние усталости водителя."""
    ALERT = "alert"
    WARNING = "warning"
    DROWSY = "drowsy"


@dataclass
class DrowsinessResult:
    """Результат анализа усталости."""
    state: DrowsinessState
    perclos: float
    blink_count: int
    blink_rate: float
    avg_ear: float
    eyes_open: bool
    warnings: List[str]


class DrowsinessMonitor:
    """Мониторинг усталости: PERCLOS, частота морганий."""
    
    def __init__(self, 
                 perclos_threshold: float = 0.15,
                 ear_threshold: float = 0.20,
                 low_blink_rate_threshold: float = 8.0,
                 history_size: int = 30,
                 ear_smooth_size: int = 5,
                 blink_cooldown_frames: int = 3):
        
        self.perclos_threshold = perclos_threshold
        self.ear_threshold = ear_threshold
        self.low_blink_rate_threshold = low_blink_rate_threshold
        self.blink_cooldown_frames = blink_cooldown_frames
        
        self.eye_history = deque(maxlen=history_size)
        self.ear_history = deque(maxlen=ear_smooth_size)
        
        self.blink_count = 0
        self.blink_cooldown = 0
        self.last_eye_state = True
        
        self.start_time = time.time()
        self.last_update_time = self.start_time
    
    def update(self, face_result: FaceDetectionResult) -> DrowsinessResult:
        """Обновляет состояние на основе новых данных с лица."""
        now = time.time()
        
        if not face_result.success:
            return DrowsinessResult(
                state=DrowsinessState.ALERT,
                perclos=0.0,
                blink_count=self.blink_count,
                blink_rate=self._calculate_blink_rate(),
                avg_ear=0.0,
                eyes_open=True,
                warnings=[]
            )
        
        avg_ear = face_result.avg_ear
        
        self.ear_history.append(avg_ear)
        smoothed_ear = sum(self.ear_history) / len(self.ear_history)
        
        eyes_open = smoothed_ear > self.ear_threshold
        
        if self.blink_cooldown > 0:
            self.blink_cooldown -= 1
        
        if not eyes_open and self.last_eye_state and self.blink_cooldown == 0:
            self.blink_count += 1
            self.blink_cooldown = self.blink_cooldown_frames
        
        self.last_eye_state = eyes_open
        self.eye_history.append("CLOSED" if not eyes_open else "OPEN")
        
        perclos = self._calculate_perclos()
        blink_rate = self._calculate_blink_rate()
        
        state, warnings = self._evaluate_state(perclos, blink_rate, now)
        self.last_update_time = now
        
        return DrowsinessResult(
            state=state,
            perclos=perclos,
            blink_count=self.blink_count,
            blink_rate=blink_rate,
            avg_ear=smoothed_ear,
            eyes_open=eyes_open,
            warnings=warnings
        )
    
    def _calculate_perclos(self) -> float:
        """Вычисляет процент времени с закрытыми глазами."""
        if not self.eye_history:
            return 0.0
        closed = sum(1 for s in self.eye_history if s == "CLOSED")
        return closed / len(self.eye_history)
    
    def _calculate_blink_rate(self) -> float:
        """Вычисляет частоту морганий в минуту."""
        elapsed = time.time() - self.start_time
        if elapsed < 1.0:
            return 0.0
        return self.blink_count / (elapsed / 60.0)
    
    def _evaluate_state(self, perclos: float, blink_rate: float, now: float) -> tuple:
        """Оценивает состояние на основе метрик."""
        warnings = []
        state = DrowsinessState.ALERT
        
        elapsed = now - self.start_time
        
        if perclos > self.perclos_threshold:
            state = DrowsinessState.DROWSY
            warnings.append(f"DROWSY: PERCLOS {perclos:.1%}")
        elif perclos > self.perclos_threshold * 0.7:
            state = DrowsinessState.WARNING
        
        if blink_rate < self.low_blink_rate_threshold and elapsed > 30:
            if state == DrowsinessState.ALERT:
                state = DrowsinessState.WARNING
            warnings.append(f"Low blink rate: {blink_rate:.1f}/min")
        
        return state, warnings
    
    def reset(self) -> None:
        """Сбрасывает накопленную историю и счетчики."""
        self.eye_history.clear()
        self.ear_history.clear()
        self.blink_count = 0
        self.blink_cooldown = 0
        self.last_eye_state = True
        self.start_time = time.time()
        self.last_update_time = self.start_time