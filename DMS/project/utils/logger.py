import json
import os
import time
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import threading


class EventLogger:
    """
    Логирование опасных событий для последующего анализа.
    
    Сохраняет события в JSON-файл с возможностью настройки
    директории и формата именования.
    """
    
    def __init__(self, 
                 log_dir: str = "logs",
                 max_file_size_mb: float = 10.0,
                 auto_screenshot: bool = False):
        """
        Args:
            log_dir: директория для логов
            max_file_size_mb: максимальный размер файла лога перед ротацией
            auto_screenshot: сохранять скриншоты при критических событиях
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.max_file_size = max_file_size_mb * 1024 * 1024
        self.auto_screenshot = auto_screenshot
        
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"session_{self.session_id}.json"
        
        self.events: List[dict] = []
        self.start_time = time.time()
        self.frame_count = 0
        self.warning_count = 0
        self.critical_count = 0
        
        self._lock = threading.Lock()
        
        self._init_log_file()
    
    def _init_log_file(self):
        """Инициализирует файл лога метаданными сессии."""
        metadata = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "version": "1.0",
            "events": []
        }
        self._write_json(metadata)
    
    def log_event(self, 
                  event_type: str,
                  severity: str,
                  message: str,
                  details: Optional[Dict] = None,
                  frame: Optional[np.ndarray] = None):
        """
        Записывает событие в лог.
        
        Args:
            event_type: тип события (drowsiness, gaze_off_road, etc.)
            severity: важность (info, warning, critical)
            message: текстовое описание
            details: дополнительные данные (метрики, углы и т.д.)
            frame: кадр для сохранения скриншота (если включено)
        """
        with self._lock:
            event = {
                "timestamp": datetime.now().isoformat(),
                "elapsed_seconds": time.time() - self.start_time,
                "frame_number": self.frame_count,
                "type": event_type,
                "severity": severity,
                "message": message,
                "details": details or {}
            }
            
            self.events.append(event)
            
            if severity == "warning":
                self.warning_count += 1
            elif severity == "critical":
                self.critical_count += 1
            
            if self.auto_screenshot and frame is not None and severity == "critical":
                self._save_screenshot(frame, event_type)
            
            if len(self.events) % 10 == 0:
                self._flush()
    
    def log_metrics(self, metrics: Dict):
        """Записывает периодические метрики (PERCLOS, EAR, частота морганий)."""
        with self._lock:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "elapsed_seconds": time.time() - self.start_time,
                "frame_number": self.frame_count,
                "type": "metrics",
                "data": metrics
            }
            self.events.append(entry)
    
    def increment_frame(self):
        """Увеличивает счетчик кадров."""
        self.frame_count += 1
    
    def _save_screenshot(self, frame: np.ndarray, event_type: str):
        """Сохраняет скриншот при критическом событии."""
        import cv2
        
        screenshot_dir = self.log_dir / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = screenshot_dir / f"{self.session_id}_{event_type}_{timestamp}.jpg"
        
        cv2.imwrite(str(filename), frame)
    
    def _write_json(self, data: dict):
        """Записывает данные в JSON-файл."""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _flush(self):
        """Сбрасывает накопленные события в файл."""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"events": []}
        
        data["events"].extend(self.events)
        self._write_json(data)
        self.events.clear()
        
        if self.log_file.stat().st_size > self.max_file_size:
            self._rotate()
    
    def _rotate(self):
        """Ротирует файл лога при превышении максимального размера."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rotated = self.log_dir / f"session_{self.session_id}_{timestamp}.json"
        self.log_file.rename(rotated)
        self._init_log_file()
    
    def get_summary(self) -> Dict:
        """Возвращает сводку по сессии."""
        elapsed = time.time() - self.start_time
        
        return {
            "session_id": self.session_id,
            "duration_seconds": elapsed,
            "total_frames": self.frame_count,
            "avg_fps": self.frame_count / elapsed if elapsed > 0 else 0,
            "total_warnings": self.warning_count,
            "total_criticals": self.critical_count,
            "events_per_minute": (self.warning_count + self.critical_count) / (elapsed / 60) if elapsed > 0 else 0
        }
    
    def close(self):
        """Закрывает логгер, сбрасывая все накопленные данные."""
        with self._lock:
            summary = self.get_summary()
            
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = {"events": []}
            
            data["events"].extend(self.events)
            data["summary"] = summary
            data["end_time"] = datetime.now().isoformat()
            
            self._write_json(data)
            self.events.clear()