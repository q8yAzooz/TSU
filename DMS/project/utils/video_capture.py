import cv2
import time
from typing import Tuple, Optional
import numpy as np

class VideoCapture:
    """Обертка над cv2.VideoCapture с обработкой ошибок и переподключением."""
    
    def __init__(self, source: int = 0, width: int = 640, height: int = 480, fps: int = 30):
        self.source = source
        self.width = width
        self.height = height
        self.target_fps = fps
        
        self.cap: Optional[cv2.VideoCapture] = None
        self._init_capture()
    
    def _init_capture(self) -> bool:
        """Инициализирует захват видео."""
        self.cap = cv2.VideoCapture(self.source)
        
        if not self.cap.isOpened():
            return False
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.cap.set(cv2.CAP_PROP_FPS, self.target_fps)
        
        return True
    
    def read(self) -> Tuple[bool, Optional[np.ndarray]]:
        """Читает кадр. Возвращает (успех, кадр)."""
        if self.cap is None:
            return False, None
        
        ret, frame = self.cap.read()
        
        if not ret:
            time.sleep(0.1)
            ret, frame = self.cap.read()
        
        return ret, frame
    
    def release(self) -> None:
        """Освобождает ресурсы."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
    
    def is_opened(self) -> bool:
        return self.cap is not None and self.cap.isOpened()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()