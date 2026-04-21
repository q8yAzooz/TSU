import cv2
import numpy as np
from dataclasses import dataclass
from typing import Optional, List, Tuple
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


@dataclass
class FaceDetectionResult:
    """Результат детекции лица."""
    success: bool
    landmarks: Optional[List] = None
    left_eye_points: Optional[np.ndarray] = None
    right_eye_points: Optional[np.ndarray] = None
    mouth_points: Optional[np.ndarray] = None
    face_bbox: Optional[Tuple[int, int, int, int]] = None
    left_ear: float = 0.0
    right_ear: float = 0.0
    avg_ear: float = 0.0
    mar: float = 0.0


class FaceDetector:
    """Детектор лица и лицевых ориентиров на базе MediaPipe Face Landmarker."""
    
    # Индексы для левого и правого глаза (контур)
    LEFT_EYE_INDICES = (362, 385, 387, 263, 373, 380)
    RIGHT_EYE_INDICES = (33, 160, 158, 133, 153, 144)
    
    # Индексы для рта (внешний контур)
    MOUTH_INDICES = (61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95)
    
    def __init__(self, model_path: str = 'models/face_landmarker.task'):
        if not self._model_exists(model_path):
            raise FileNotFoundError(
                f"Model not found: {model_path}\n"
                "Download from: https://storage.googleapis.com/mediapipe-models/"
                "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
            )
        
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.detector = vision.FaceLandmarker.create_from_options(options)
    
    def _model_exists(self, path: str) -> bool:
        import os
        return os.path.exists(path)
    
    def detect(self, frame: np.ndarray) -> FaceDetectionResult:
        """Выполняет детекцию лица на кадре."""
        h, w = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = self.detector.detect(mp_image)
        
        if not detection_result.face_landmarks:
            return FaceDetectionResult(success=False)
        
        landmarks = detection_result.face_landmarks[0]
        
        left_points = self._extract_points(landmarks, self.LEFT_EYE_INDICES, w, h)
        right_points = self._extract_points(landmarks, self.RIGHT_EYE_INDICES, w, h)
        mouth_points = self._extract_points(landmarks, self.MOUTH_INDICES, w, h)
        
        left_ear = self._calculate_ear(left_points)
        right_ear = self._calculate_ear(right_points)
        avg_ear = (left_ear + right_ear) / 2.0
        
        mar = self._calculate_mar(mouth_points)
        
        bbox = self._calculate_bbox(landmarks, w, h)
        
        return FaceDetectionResult(
            success=True,
            landmarks=landmarks,
            left_eye_points=left_points,
            right_eye_points=right_points,
            mouth_points=mouth_points,
            face_bbox=bbox,
            left_ear=left_ear,
            right_ear=right_ear,
            avg_ear=avg_ear,
            mar=mar
        )
    
    def _extract_points(self, landmarks, indices: Tuple[int, ...], w: int, h: int) -> np.ndarray:
        """Извлекает координаты точек по индексам."""
        points = []
        for idx in indices:
            landmark = landmarks[idx]
            points.append([int(landmark.x * w), int(landmark.y * h)])
        return np.array(points, dtype=np.int32)
    
    def _calculate_ear(self, points: np.ndarray) -> float:
        """Вычисляет Eye Aspect Ratio."""
        if len(points) < 6:
            return 0.0
        
        p1, p2, p3, p4, p5, p6 = points
        
        vertical_1 = np.linalg.norm(p2 - p6)
        vertical_2 = np.linalg.norm(p3 - p5)
        horizontal = np.linalg.norm(p1 - p4)
        
        if horizontal < 1e-6:
            return 0.0
        
        return (vertical_1 + vertical_2) / (2.0 * horizontal)
    
    def _calculate_mar(self, points: np.ndarray) -> float:
        """Вычисляет Mouth Aspect Ratio для детекции зевания."""
        if len(points) < 4:
            return 0.0
        
        vertical = np.linalg.norm(points[2] - points[6]) if len(points) > 6 else 0.0
        horizontal = np.linalg.norm(points[0] - points[4]) if len(points) > 4 else 0.0
        
        if horizontal < 1e-6:
            return 0.0
        
        return vertical / horizontal
    
    def _calculate_bbox(self, landmarks, w: int, h: int) -> Tuple[int, int, int, int]:
        """Вычисляет ограничивающую рамку лица."""
        x_coords = [int(lm.x * w) for lm in landmarks]
        y_coords = [int(lm.y * h) for lm in landmarks]
        
        x_min, x_max = max(0, min(x_coords)), min(w, max(x_coords))
        y_min, y_max = max(0, min(y_coords)), min(h, max(y_coords))
        
        return (x_min, y_min, x_max - x_min, y_max - y_min)
    
    def draw_eyes(self, frame: np.ndarray, result: FaceDetectionResult, 
                  color_open: Tuple[int, int, int] = (0, 255, 0),
                  color_closed: Tuple[int, int, int] = (0, 0, 255)) -> None:
        """Отрисовывает контуры глаз на кадре."""
        if not result.success:
            return
        
        eye_color = color_open if result.avg_ear > 0.20 else color_closed
        
        if result.left_eye_points is not None:
            hull = cv2.convexHull(result.left_eye_points)
            cv2.drawContours(frame, [hull], -1, eye_color, 2)
        
        if result.right_eye_points is not None:
            hull = cv2.convexHull(result.right_eye_points)
            cv2.drawContours(frame, [hull], -1, eye_color, 2)