import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple, List
from collections import Counter
import time


@dataclass
class GazeZone:
    name: str
    pitch_range: Tuple[float, float]
    yaw_range: Tuple[float, float]


@dataclass
class GazeResult:
    success: bool
    zone: str = "unknown"
    looking_forward: bool = True
    yaw: float = 0.0
    pitch: float = 0.0
    confidence: float = 0.0


class GazeEstimator:
    """
    Оценка направления взгляда.
    
    Зоны определены относительно нейтрального положения головы.
    Углы: yaw — поворот влево-вправо, pitch — наклон вверх-вниз.
    
    ВАЖНО: Зоны откалиброваны для случая, когда камера находится
    прямо перед водителем (на руле/приборной панели).
    """
    
    # Расширенные зоны с перекрытиями
    ZONES = {
        "road": GazeZone("road", (-20.0, 5.0), (-25.0, 25.0)),
        "dashboard": GazeZone("dashboard", (5.0, 40.0), (-20.0, 20.0)),
        "left_mirror": GazeZone("left_mirror", (-20.0, 10.0), (25.0, 50.0)),
        "right_mirror": GazeZone("right_mirror", (-20.0, 10.0), (-50.0, -25.0)),
        "left_window": GazeZone("left_window", (-20.0, 10.0), (50.0, 80.0)),
        "right_window": GazeZone("right_window", (-20.0, 10.0), (-80.0, -50.0)),
        "lap": GazeZone("lap", (40.0, 70.0), (-20.0, 20.0)),
        "rearview": GazeZone("rearview", (-40.0, -20.0), (-15.0, 15.0)),
    }

    LEFT_IRIS = 468
    RIGHT_IRIS = 473
    LEFT_EYE_CENTER = 173
    RIGHT_EYE_CENTER = 398

    def __init__(self, history_size: int = 15):
        self.zone_history: List[str] = []
        self.history_size = history_size

    def estimate(self, landmarks: List[dict], head_yaw: float, head_pitch: float,
                 frame_width: int, frame_height: int) -> GazeResult:
        if landmarks is None:
            return GazeResult(success=False)

        iris_offset = self._calculate_iris_offset(landmarks, frame_width, frame_height)

        gaze_yaw = head_yaw + iris_offset[0]
        gaze_pitch = head_pitch + iris_offset[1]

        zone = self._classify_zone(gaze_pitch, gaze_yaw)

        self.zone_history.append(zone)
        if len(self.zone_history) > self.history_size:
            self.zone_history.pop(0)

        stable_zone = self._get_stable_zone()
        confidence = self._calculate_confidence(stable_zone)

        return GazeResult(
            success=True,
            zone=stable_zone,
            looking_forward=(stable_zone == "road"),
            yaw=gaze_yaw,
            pitch=gaze_pitch,
            confidence=confidence
        )

    def _get_xy(self, landmark: dict, width: int, height: int) -> Tuple[float, float]:
        return float(landmark['x']) * width, float(landmark['y']) * height

    def _calculate_iris_offset(self, landmarks: List[dict], width: int, height: int) -> Tuple[float, float]:
        max_idx = max(self.LEFT_IRIS, self.RIGHT_IRIS, self.LEFT_EYE_CENTER, self.RIGHT_EYE_CENTER)
        if len(landmarks) <= max_idx:
            return 0.0, 0.0

        left_iris_x, left_iris_y = self._get_xy(landmarks[self.LEFT_IRIS], width, height)
        right_iris_x, right_iris_y = self._get_xy(landmarks[self.RIGHT_IRIS], width, height)

        left_center_x, left_center_y = self._get_xy(landmarks[self.LEFT_EYE_CENTER], width, height)
        right_center_x, right_center_y = self._get_xy(landmarks[self.RIGHT_EYE_CENTER], width, height)

        left_offset_x = left_iris_x - left_center_x
        right_offset_x = right_iris_x - right_center_x
        avg_horizontal = (left_offset_x + right_offset_x) / 2.0
        horizontal_angle = avg_horizontal / width * 45.0

        left_offset_y = left_iris_y - left_center_y
        right_offset_y = right_iris_y - right_center_y
        avg_vertical = (left_offset_y + right_offset_y) / 2.0
        vertical_angle = -avg_vertical / height * 30.0

        return horizontal_angle, vertical_angle

    def _classify_zone(self, pitch: float, yaw: float) -> str:
        """Классифицирует зону по углам. Ищет наилучшее совпадение."""
        best_zone = "other"
        best_score = -1
        
        for zone_name, zone in self.ZONES.items():
            pitch_ok = zone.pitch_range[0] <= pitch <= zone.pitch_range[1]
            yaw_ok = zone.yaw_range[0] <= yaw <= zone.yaw_range[1]
            
            if pitch_ok and yaw_ok:
                pitch_center = (zone.pitch_range[0] + zone.pitch_range[1]) / 2
                yaw_center = (zone.yaw_range[0] + zone.yaw_range[1]) / 2
                pitch_span = (zone.pitch_range[1] - zone.pitch_range[0]) / 2
                yaw_span = (zone.yaw_range[1] - zone.yaw_range[0]) / 2
                
                if pitch_span > 0 and yaw_span > 0:
                    pitch_dist = abs(pitch - pitch_center) / pitch_span
                    yaw_dist = abs(yaw - yaw_center) / yaw_span
                    score = 2 - (pitch_dist + yaw_dist)
                else:
                    score = 1
                
                if score > best_score:
                    best_score = score
                    best_zone = zone_name
        
        return best_zone

    def _get_stable_zone(self) -> str:
        if not self.zone_history:
            return "road"
        counter = Counter(self.zone_history)
        return counter.most_common(1)[0][0]

    def _calculate_confidence(self, zone: str) -> float:
        if not self.zone_history:
            return 0.0
        return sum(1 for z in self.zone_history if z == zone) / len(self.zone_history)


class DistractionDetector:
    """Детектор длительного отвлечения взгляда от дороги."""
    
    def __init__(self, max_off_road_seconds: float = 2.0):
        self.max_off_road_seconds = max_off_road_seconds
        self.off_road_start: Optional[float] = None
        self.distracted = False
        self.warning_issued = False

    def update(self, looking_forward: bool, zone: str) -> Tuple[bool, Optional[str]]:
        now = time.time()

        if looking_forward or zone in ("road", "unknown"):
            self.off_road_start = None
            self.distracted = False
            self.warning_issued = False
            return False, None

        if self.off_road_start is None:
            self.off_road_start = now

        elapsed = now - self.off_road_start

        if elapsed > self.max_off_road_seconds:
            self.distracted = True
            if not self.warning_issued:
                self.warning_issued = True
                return True, f"Eyes off road for {elapsed:.1f}s (zone: {zone})"

        return self.distracted, None

    def reset(self):
        self.off_road_start = None
        self.distracted = False
        self.warning_issued = False