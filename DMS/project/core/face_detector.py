import cv2
import numpy as np
from dataclasses import dataclass
from typing import Optional, List, Tuple
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


@dataclass
class FaceDetectionResult:
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
    LEFT_EYE_INDICES = (362, 385, 387, 263, 373, 380)
    RIGHT_EYE_INDICES = (33, 160, 158, 133, 153, 144)
    MOUTH_INDICES = (61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95)

    def __init__(self, model_path: str = 'models/face_landmarker.task'):
        if not self._model_exists(model_path):
            raise FileNotFoundError(f"Model not found: {model_path}")

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
        h, w = frame.shape[:2]
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = self.detector.detect(mp_image)

        if not detection_result.face_landmarks:
            return FaceDetectionResult(success=False)

        raw_landmarks = detection_result.face_landmarks[0]
        
        landmarks = []
        for lm in raw_landmarks:
            landmarks.append({'x': float(lm.x), 'y': float(lm.y), 'z': float(lm.z)})

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

    def _extract_points(self, landmarks: List[dict], indices: Tuple[int, ...], w: int, h: int) -> np.ndarray:
        points = []
        for idx in indices:
            lm = landmarks[idx]
            points.append([lm['x'] * w, lm['y'] * h])
        return np.array(points, dtype=np.int32)

    def _calculate_ear(self, points: np.ndarray) -> float:
        if len(points) < 6:
            return 0.0
        p1, p2, p3, p4, p5, p6 = points.astype(np.float64)
        vertical_1 = np.linalg.norm(p2 - p6)
        vertical_2 = np.linalg.norm(p3 - p5)
        horizontal = np.linalg.norm(p1 - p4)
        if horizontal < 1e-6:
            return 0.0
        return (vertical_1 + vertical_2) / (2.0 * horizontal)

    def _calculate_mar(self, points: np.ndarray) -> float:
        if len(points) < 8:
            return 0.0
        pts = points.astype(np.float64)
        vertical = np.linalg.norm(pts[2] - pts[6])
        horizontal = np.linalg.norm(pts[0] - pts[4])
        if horizontal < 1e-6:
            return 0.0
        return vertical / horizontal

    def _calculate_bbox(self, landmarks: List[dict], w: int, h: int) -> Tuple[int, int, int, int]:
        x_coords = [lm['x'] * w for lm in landmarks]
        y_coords = [lm['y'] * h for lm in landmarks]
        x_min, x_max = max(0, int(min(x_coords))), min(w, int(max(x_coords)))
        y_min, y_max = max(0, int(min(y_coords))), min(h, int(max(y_coords)))
        return (x_min, y_min, x_max - x_min, y_max - y_min)