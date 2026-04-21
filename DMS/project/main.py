import cv2
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.face_detector import FaceDetector
from monitoring.drowsiness_monitor import DrowsinessMonitor
from alerts.alert_manager import AlertManager, AlertLevel
from utils.video_capture import VideoCapture
from utils.drawer import Drawer
from utils.config import load_config


class DriverMonitoringApp:
    """Главный класс приложения."""
    
    def __init__(self, config_path: str = None):
        self.config = load_config(config_path)
        
        self.capture = VideoCapture(
            source=self.config.camera_id,
            width=self.config.camera_width,
            height=self.config.camera_height,
            fps=self.config.camera_fps
        )
        
        if not self.capture.is_opened():
            raise RuntimeError("Cannot open camera")
        
        self.face_detector = FaceDetector(model_path=self.config.model_path)
        self.drowsiness_monitor = DrowsinessMonitor(
            perclos_threshold=self.config.perclos_threshold,
            ear_threshold=self.config.ear_threshold,
            low_blink_rate_threshold=self.config.low_blink_rate_threshold
        )
        self.alert_manager = AlertManager(
            cooldown_seconds=self.config.alert_cooldown,
            enable_console=self.config.enable_console_logging
        )
        self.drawer = Drawer()
        
        self.running = True
        self.paused = False
        
        self.fps = 0.0
        self.frame_count = 0
        self.last_fps_time = time.time()
    
    def run(self):
        """Главный цикл приложения."""
        print("\nDriver Monitoring System")
        print("=" * 40)
        print("Controls: Q-Quit | R-Reset | S-Screenshot | +/- Threshold | SPACE-Pause")
        print("=" * 40 + "\n")
        
        while self.running:
            ret, frame = self.capture.read()
            if not ret or frame is None:
                continue
            
            frame = cv2.flip(frame, 1)
            
            if not self.paused:
                face_result = self.face_detector.detect(frame)
                drowsiness_result = self.drowsiness_monitor.update(face_result)
                
                self.alert_manager.clear_warnings()
                
                if drowsiness_result.state.value in ("warning", "drowsy"):
                    level = AlertLevel.CRITICAL if drowsiness_result.state.value == "drowsy" else AlertLevel.WARNING
                    for warning in drowsiness_result.warnings:
                        self.alert_manager.trigger(level, warning)
            else:
                face_result = None
                drowsiness_result = self.drowsiness_monitor.update(face_result) if face_result else None
            
            self._update_fps()
            
            if face_result and drowsiness_result:
                output = self.drawer.draw(
                    frame, face_result, drowsiness_result,
                    self.fps, self.alert_manager.get_active_warnings()
                )
            else:
                output = frame
                self._draw_status(output, "PAUSED" if self.paused else "NO FACE")
            
            cv2.imshow('Driver Monitoring System', output)
            
            self._handle_key(cv2.waitKey(30) & 0xFF, output)
        
        self.cleanup()
    
    def _update_fps(self):
        """Обновляет счетчик FPS."""
        self.frame_count += 1
        now = time.time()
        elapsed = now - self.last_fps_time
        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.last_fps_time = now
    
    def _draw_status(self, frame, text: str):
        """Отрисовывает статусное сообщение."""
        h, w = frame.shape[:2]
        cv2.putText(frame, text, (w // 2 - 50, h // 2),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        cv2.putText(frame, "Q-Quit | R-Reset | S-Screenshot | +/- Threshold | SPACE-Pause",
                   (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def _handle_key(self, key: int, frame):
        """Обрабатывает нажатия клавиш."""
        if key == ord('q') or key == ord('Q'):
            self.running = False
        elif key == ord('r') or key == ord('R'):
            self.drowsiness_monitor.reset()
            self.alert_manager.clear_warnings()
            print("Reset")
        elif key == ord('s') or key == ord('S'):
            filename = f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
            cv2.imwrite(filename, frame)
            print(f"Saved: {filename}")
        elif key == ord('+') or key == ord('='):
            self.drowsiness_monitor.ear_threshold = min(0.5, self.drowsiness_monitor.ear_threshold + 0.01)
            print(f"EAR Threshold: {self.drowsiness_monitor.ear_threshold:.2f}")
        elif key == ord('-') or key == ord('_'):
            self.drowsiness_monitor.ear_threshold = max(0.1, self.drowsiness_monitor.ear_threshold - 0.01)
            print(f"EAR Threshold: {self.drowsiness_monitor.ear_threshold:.2f}")
        elif key == ord(' '):
            self.paused = not self.paused
            print("Paused" if self.paused else "Resumed")
    
    def cleanup(self):
        """Освобождает ресурсы."""
        self.capture.release()
        cv2.destroyAllWindows()
        print("\nApplication closed")


def main():
    try:
        app = DriverMonitoringApp()
        app.run()
    except KeyboardInterrupt:
        print("\nInterrupted")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()