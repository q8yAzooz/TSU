import cv2
import numpy as np
from typing import List, Optional

from core.face_detector import FaceDetectionResult
from monitoring.drowsiness_monitor import DrowsinessResult, DrowsinessState
from monitoring.driver_state_aggregator import AggregatedState, OverallState


class Drawer:
    """Отрисовка информации на кадре."""
    
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale_small = 0.5
        self.font_scale_normal = 0.7
    
    def draw(self,
             frame: np.ndarray,
             face_result: Optional[FaceDetectionResult],
             drowsiness_result: Optional[DrowsinessResult],
             aggregated: Optional[AggregatedState],
             fps: float,
             active_warnings: List[str]) -> np.ndarray:
        """Основной метод отрисовки всей информации."""
        output = frame.copy()
        
        if face_result is not None and face_result.success:
            self._draw_face_bbox(output, face_result)
            if drowsiness_result is not None:
                self._draw_eyes(output, face_result, drowsiness_result.eyes_open)
        
        self._draw_overlay_panel(output, drowsiness_result, aggregated, fps)
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
    
    def _draw_overlay_panel(self,
                            frame: np.ndarray,
                            drowsiness: Optional[DrowsinessResult],
                            aggregated: Optional[AggregatedState],
                            fps: float) -> None:
        h, w = frame.shape[:2]
        
        overlay = frame.copy()
        cv2.rectangle(overlay, (5, 5), (380, 250), (0, 0, 0), -1)
        frame[:] = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)
        
        state = aggregated.overall if aggregated else OverallState.ATTENTIVE
        state_colors = {
            OverallState.ATTENTIVE: (0, 255, 0),
            OverallState.WARNING: (0, 255, 255),
            OverallState.CRITICAL: (0, 0, 255)
        }
        state_color = state_colors.get(state, (255, 255, 255))
        
        y = 30
        cv2.putText(frame, f"State: {state.value.upper()}", (10, y),
                   self.font, self.font_scale_normal, state_color, 2)
        y += 30
        
        if drowsiness is not None:
            eye_color = (0, 255, 0) if drowsiness.eyes_open else (0, 0, 255)
            eye_status = "OPEN" if drowsiness.eyes_open else "CLOSED"
            cv2.putText(frame, f"Eyes: {eye_status}", (10, y),
                       self.font, self.font_scale_small, eye_color, 1)
            y += 25
            
            ear_color = (0, 255, 0) if drowsiness.avg_ear > 0.20 else (0, 0, 255)
            cv2.putText(frame, f"EAR: {drowsiness.avg_ear:.3f}", (10, y),
                       self.font, self.font_scale_small, ear_color, 1)
            y += 25
            
            cv2.putText(frame, f"PERCLOS: {drowsiness.perclos:.1%}", (10, y),
                       self.font, self.font_scale_small, (255, 255, 255), 1)
            y += 25
            
            cv2.putText(frame, f"Blinks: {drowsiness.blink_count} ({drowsiness.blink_rate:.1f}/min)", (10, y),
                       self.font, self.font_scale_small, (255, 255, 255), 1)
            y += 25
        
        if aggregated is not None:
            if aggregated.gaze is not None and aggregated.gaze.success:
                zone_color = (0, 255, 0) if aggregated.gaze.looking_forward else (0, 255, 255)
                cv2.putText(frame, f"Gaze: {aggregated.gaze.zone}", (10, y),
                           self.font, self.font_scale_small, zone_color, 1)
                y += 25
            
            if aggregated.yawn is not None and aggregated.yawn.mar > 0:
                yawn_color = (0, 0, 255) if aggregated.yawn.yawning else (255, 255, 255)
                cv2.putText(frame, f"MAR: {aggregated.yawn.mar:.3f}", (10, y),
                           self.font, self.font_scale_small, yawn_color, 1)
                y += 25
            
            if aggregated.head_pose is not None and aggregated.head_pose.success:
                cv2.putText(frame, f"Pose: Y{aggregated.head_pose.yaw:.0f} P{aggregated.head_pose.pitch:.0f}",
                           (10, y), self.font, self.font_scale_small, (255, 255, 255), 1)
                y += 25
        
        cv2.putText(frame, f"FPS: {fps:.1f}", (w - 100, 30),
                   self.font, self.font_scale_small, (255, 255, 0), 2)
    
    def _draw_warnings(self, frame: np.ndarray, warnings: List[str]) -> None:
        if not warnings:
            return
        
        y = 260
        for i, warning in enumerate(warnings[:3]):
            cv2.putText(frame, f"! {warning}", (10, y),
                       self.font, self.font_scale_small, (0, 0, 255), 2)
            y += 25
    
    def _draw_controls_hint(self, frame: np.ndarray) -> None:
        h = frame.shape[0]
        cv2.putText(frame, "Q-Quit | R-Reset | S-Screenshot | +/- Threshold | SPACE-Pause",
                   (10, h - 10), self.font, self.font_scale_small, (255, 255, 255), 1)