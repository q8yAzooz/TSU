import cv2
import numpy as np
import time
from typing import List, Tuple, Optional
from core.face_detector import FaceDetectionResult
from monitoring.drowsiness_monitor import DrowsinessResult, DrowsinessState
from alerts.alert_manager import AlertLevel


class Drawer:
    """Отрисовка информации на кадре."""
    
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale_small = 0.5
        self.font_scale_normal = 0.7
        self.font_scale_large = 1.0
        
    def draw(self, 
             frame: np.ndarray,
             face_result: FaceDetectionResult,
             drowsiness_result: DrowsinessResult,
             fps: float,
             active_warnings: List[str]) -> np.ndarray:
        """Основной метод отрисовки всей информации."""
        output = frame.copy()
        
        if face_result.success:
            self._draw_face_bbox(output, face_result)
            self._draw_eyes(output, face_result, drowsiness_result.eyes_open)
        
        self._draw_overlay_panel(output, drowsiness_result, fps)
        self._draw_warnings(output, active_warnings)
        self._draw_controls_hint(output)
        
        return output
    
    def _draw_face_bbox(self, frame: np.ndarray, result: FaceDetectionResult) -> None:
        if result.face_bbox:
            x, y, w, h = result.face_bbox
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
    
    def _draw_eyes(self, frame: np.ndarray, result: FaceDetectionResult, eyes_open: bool) -> None:
        color = (0, 255, 0) if eyes_open else (0, 0, 255)
        
        if result.left_eye_points is not None:
            hull = cv2.convexHull(result.left_eye_points)
            cv2.drawContours(frame, [hull], -1, color, 2)
        
        if result.right_eye_points is not None:
            hull = cv2.convexHull(result.right_eye_points)
            cv2.drawContours(frame, [hull], -1, color, 2)
    
    def _draw_overlay_panel(self, frame: np.ndarray, result: DrowsinessResult, fps: float) -> None:
        h, w = frame.shape[:2]
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (5, 5), (350, 200), (0, 0, 0), -1)
        frame[:] = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)
        
        state_colors = {
            DrowsinessState.ALERT: (0, 255, 0),
            DrowsinessState.WARNING: (0, 255, 255),
            DrowsinessState.DROWSY: (0, 0, 255)
        }
        state_color = state_colors.get(result.state, (255, 255, 255))
        
        y = 30
        cv2.putText(frame, f"State: {result.state.value.upper()}", (10, y),
                   self.font, self.font_scale_normal, state_color, 2)
        y += 30
        
        eye_color = (0, 255, 0) if result.eyes_open else (0, 0, 255)
        eye_status = "OPEN" if result.eyes_open else "CLOSED"
        cv2.putText(frame, f"Eyes: {eye_status}", (10, y),
                   self.font, self.font_scale_small, eye_color, 1)
        y += 25
        
        ear_color = (0, 255, 0) if result.avg_ear > 0.20 else (0, 0, 255)
        cv2.putText(frame, f"EAR: {result.avg_ear:.3f}", (10, y),
                   self.font, self.font_scale_small, ear_color, 1)
        y += 25
        
        cv2.putText(frame, f"PERCLOS: {result.perclos:.1%}", (10, y),
                   self.font, self.font_scale_small, (255, 255, 255), 1)
        y += 25
        
        cv2.putText(frame, f"Blinks: {result.blink_count} ({result.blink_rate:.1f}/min)", (10, y),
                   self.font, self.font_scale_small, (255, 255, 255), 1)
        
        cv2.putText(frame, f"FPS: {fps:.1f}", (w - 100, 30),
                   self.font, self.font_scale_small, (255, 255, 0), 2)
    
    def _draw_warnings(self, frame: np.ndarray, warnings: List[str]) -> None:
        if not warnings:
            return
        
        y = 210
        for i, warning in enumerate(warnings[:3]):
            cv2.putText(frame, f"! {warning}", (10, y),
                       self.font, self.font_scale_small, (0, 0, 255), 2)
            y += 25
    
    def _draw_controls_hint(self, frame: np.ndarray) -> None:
        h = frame.shape[0]
        cv2.putText(frame, "Q-Quit | R-Reset | S-Screenshot | +/- Threshold",
                   (10, h - 10), self.font, self.font_scale_small, (255, 255, 255), 1)