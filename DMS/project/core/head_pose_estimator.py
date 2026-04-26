import cv2
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple, List


@dataclass
class HeadPoseResult:
    success: bool
    pitch: float = 0.0
    yaw: float = 0.0
    roll: float = 0.0
    looking_forward: bool = True
    warnings: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class HeadPoseEstimator:
    LANDMARK_INDICES = {
        'nose_tip': 1,
        'chin': 152,
        'left_eye_inner': 159,
        'right_eye_inner': 386,
        'left_mouth': 61,
        'right_mouth': 291,
    }

    MODEL_3D = np.array([
        [0.0, 0.0, 0.0],
        [0.0, -63.6, -12.5],
        [-30.0, 17.5, -40.0],
        [30.0, 17.5, -40.0],
        [-28.0, -28.0, -53.0],
        [28.0, -28.0, -53.0],
    ], dtype=np.float64)

    YAW_FORWARD_THRESHOLD = 20.0
    PITCH_FORWARD_THRESHOLD = 15.0
    YAW_EXTREME_THRESHOLD = 45.0
    PITCH_EXTREME_THRESHOLD = 40.0

    def __init__(self, camera_matrix: Optional[np.ndarray] = None,
                 dist_coeffs: Optional[np.ndarray] = None):
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs if dist_coeffs is not None else np.zeros((4, 1))

    def _get_landmark_value(self, lm, key: str) -> float:
        if isinstance(lm, dict):
            val = lm.get(key, 0.0)
        elif hasattr(lm, key):
            val = getattr(lm, key)
        elif isinstance(lm, (list, tuple, np.ndarray)):
            idx = 0 if key == 'x' else (1 if key == 'y' else 2)
            val = lm[idx] if idx < len(lm) else 0.0
        else:
            return 0.0
        
        if isinstance(val, np.ndarray):
            val = val.item() if val.size == 1 else float(val.flat[0])
        elif isinstance(val, (list, tuple)):
            val = float(val[0]) if len(val) > 0 else 0.0
        
        return float(val)

    def estimate(self, landmarks, frame_width: int, frame_height: int) -> HeadPoseResult:
        if landmarks is None:
            return HeadPoseResult(success=False)

        image_points = self._extract_2d_points(landmarks, frame_width, frame_height)

        if len(image_points) < 4:
            return HeadPoseResult(success=False)

        cam_matrix = self._get_camera_matrix(frame_width, frame_height)

        success, rvec, tvec = cv2.solvePnP(
            self.MODEL_3D, image_points, cam_matrix, self.dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return HeadPoseResult(success=False)

        rotation_matrix, _ = cv2.Rodrigues(rvec)
        pitch, yaw, roll = self._decompose_rotation(rotation_matrix)

        looking_forward = (abs(yaw) < self.YAW_FORWARD_THRESHOLD and
                          abs(pitch) < self.PITCH_FORWARD_THRESHOLD)

        warnings = self._evaluate_warnings(pitch, yaw, roll)

        return HeadPoseResult(
            success=True,
            pitch=float(pitch), yaw=float(yaw), roll=float(roll),
            looking_forward=looking_forward, warnings=warnings
        )

    def _extract_2d_points(self, landmarks, width: int, height: int) -> np.ndarray:
        points = []
        for idx in self.LANDMARK_INDICES.values():
            if idx < len(landmarks):
                lm = landmarks[idx]
                try:
                    x = float(self._get_landmark_value(lm, 'x')) * float(width)
                    y = float(self._get_landmark_value(lm, 'y')) * float(height)
                    points.append([x, y])
                except (TypeError, ValueError, IndexError):
                    continue
        return np.array(points, dtype=np.float64)

    def _get_camera_matrix(self, width: int, height: int) -> np.ndarray:
        if self.camera_matrix is not None:
            return self.camera_matrix
        focal = float(width)
        return np.array([
            [focal, 0, width / 2.0],
            [0, focal, height / 2.0],
            [0, 0, 1]
        ], dtype=np.float64)

    def _decompose_rotation(self, R: np.ndarray) -> Tuple[float, float, float]:
        """
        Корректное разложение матрицы поворота на pitch, yaw, roll.
        
        Используется стандартная модель:
        - pitch: поворот вокруг оси X (вверх-вниз), положительный = голова вверх
        - yaw: поворот вокруг оси Y (влево-вправо), положительный = голова вправо
        - roll: поворот вокруг оси Z (наклон), положительный = наклон вправо
        """
        pitch = np.arctan2(-R[1, 2], R[1, 1])
        yaw = np.arcsin(np.clip(R[1, 0], -1.0, 1.0))
        roll = np.arctan2(-R[2, 0], R[0, 0])
        
        pitch = np.degrees(pitch)
        yaw = np.degrees(yaw)
        roll = np.degrees(roll)
        
        if abs(yaw) > 90:
            pitch = np.degrees(np.arctan2(R[1, 2], -R[1, 1]))
            yaw = np.degrees(np.pi - yaw) if yaw > 0 else np.degrees(-np.pi - yaw)
            roll = np.degrees(np.arctan2(R[2, 0], -R[0, 0]))
        
        return pitch, yaw, roll

    def _evaluate_warnings(self, pitch: float, yaw: float, roll: float) -> List[str]:
        warnings = []
        
        if abs(yaw) > self.YAW_EXTREME_THRESHOLD:
            direction = "right" if yaw > 0 else "left"
            warnings.append(f"Head turned far {direction}")
        
        if pitch > self.PITCH_EXTREME_THRESHOLD:
            warnings.append("Head tilted up severely")
        elif pitch < -self.PITCH_EXTREME_THRESHOLD:
            warnings.append("Head drooping (possible microsleep)")
        
        if abs(roll) > 30.0:
            warnings.append("Head tilted excessively")
        
        return warnings

    def draw_pose_axes(self, frame: np.ndarray, landmarks,
                       frame_width: int, frame_height: int) -> None:
        image_points = self._extract_2d_points(landmarks, frame_width, frame_height)

        if len(image_points) < 4:
            return

        cam_matrix = self._get_camera_matrix(frame_width, frame_height)

        success, rvec, tvec = cv2.solvePnP(
            self.MODEL_3D, image_points, cam_matrix, self.dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )

        if not success:
            return

        nose_tip = tuple(image_points[0].astype(int))

        axis_length = 80.0
        axis_3d = np.array([
            [axis_length, 0, 0],
            [0, -axis_length, 0],
            [0, 0, -axis_length]
        ], dtype=np.float64)

        axis_2d, _ = cv2.projectPoints(axis_3d, rvec, tvec, cam_matrix, self.dist_coeffs)
        axis_2d = axis_2d.reshape(-1, 2).astype(int)

        colors = [
            (0, 0, 255),   # X — красный (вправо)
            (0, 255, 0),   # Y — зеленый (вверх)
            (255, 0, 0)    # Z — синий (к камере)
        ]

        for point, color in zip(axis_2d, colors):
            cv2.line(frame, nose_tip, tuple(point), color, 2)


class NodDetector:
    def __init__(self, history_size: int = 50,
                 nod_threshold: float = 15.0,
                 nod_frequency_threshold: float = 3.0):
        self.history_size = history_size
        self.nod_threshold = nod_threshold
        self.nod_frequency_threshold = nod_frequency_threshold
        self.pitch_history: List[float] = []
        self.nod_timestamps: List[float] = []
        self.nodding = False
        self.last_pitch: Optional[float] = None

    def update(self, pitch: float) -> Tuple[bool, bool]:
        import time
        now = time.time()
        self.pitch_history.append(pitch)
        if len(self.pitch_history) > self.history_size:
            self.pitch_history.pop(0)
        if self.last_pitch is None:
            self.last_pitch = pitch
            return False, False
        pitch_change = self.last_pitch - pitch
        self.last_pitch = pitch
        if pitch_change > self.nod_threshold:
            self.nodding = True
            self.nod_timestamps.append(now)
        if pitch > -10.0 and self.nodding:
            self.nodding = False
        self.nod_timestamps = [t for t in self.nod_timestamps if now - t < 60.0]
        nod_rate = len(self.nod_timestamps)
        excessive = nod_rate > self.nod_frequency_threshold and len(self.pitch_history) > 10
        return self.nodding, excessive