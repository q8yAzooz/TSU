import cv2
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from core.face_detector import FaceDetector
from core.head_pose_estimator import HeadPoseEstimator, NodDetector
from core.gaze_estimator import GazeEstimator, DistractionDetector
from core.yawning_detector import YawningDetector
from monitoring.drowsiness_monitor import DrowsinessMonitor
from monitoring.driver_state_aggregator import DriverStateAggregator, OverallState
from alerts.alert_manager import AlertManager, AlertLevel
from utils.video_capture import VideoCapture
from utils.drawer import Drawer
from utils.logger import EventLogger
from utils.config import load_config


class DriverMonitoringApp:
    
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
        self.head_pose_estimator = HeadPoseEstimator()
        self.nod_detector = NodDetector()
        self.gaze_estimator = GazeEstimator()
        self.distraction_detector = DistractionDetector(max_off_road_seconds=2.0)
        self.yawning_detector = YawningDetector()
        self.drowsiness_monitor = DrowsinessMonitor(
            perclos_threshold=self.config.perclos_threshold,
            ear_threshold=self.config.ear_threshold
        )
        self.state_aggregator = DriverStateAggregator()
        
        self.alert_manager = AlertManager(
            cooldown_seconds=self.config.alert_cooldown,
            enable_console=self.config.enable_console_logging
        )
        
        self.logger = EventLogger(
            log_dir="logs",
            auto_screenshot=True
        )
        
        self.drawer = Drawer()
        
        self.running = True
        self.paused = False
        
        self.fps = 0.0
        self.frame_count = 0
        self.last_fps_time = time.time()
    
    def run(self):
        print("\nDriver Monitoring System")
        print("=" * 50)
        print("Modules: Face Detection | Drowsiness | Head Pose | Gaze | Yawning")
        print("Controls: Q-Quit | R-Reset | S-Screenshot | +/- Threshold | SPACE-Pause")
        print("=" * 50 + "\n")
        
        while self.running:
            ret, frame = self.capture.read()
            if not ret or frame is None:
                continue
            
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            
            if not self.paused:
                face_result = self.face_detector.detect(frame)
                
                if face_result.success:
                    head_pose = self.head_pose_estimator.estimate(
                        face_result.landmarks, w, h
                    )
                    
                    is_nodding, excessive_nodding = self.nod_detector.update(head_pose.pitch)
                    
                    gaze = self.gaze_estimator.estimate(
                        face_result.landmarks, head_pose.yaw, head_pose.pitch, w, h
                    )
                    
                    is_distracted, distraction_warning = self.distraction_detector.update(
                        gaze.looking_forward, gaze.zone
                    )
                    
                    yawn = self.yawning_detector.update(face_result.mar)
                    
                    drowsiness = self.drowsiness_monitor.update(face_result)
                    
                    aggregated = self.state_aggregator.aggregate(
                        drowsiness=drowsiness,
                        head_pose=head_pose,
                        gaze=gaze,
                        yawn=yawn
                    )
                    
                    self.alert_manager.clear_warnings()
                    
                    if aggregated.overall != OverallState.ATTENTIVE:
                        level_map = {
                            OverallState.WARNING: AlertLevel.WARNING,
                            OverallState.CRITICAL: AlertLevel.CRITICAL
                        }
                        level = level_map.get(aggregated.overall, AlertLevel.INFO)
                        for w in aggregated.warnings:
                            if self.alert_manager.trigger(level, w):
                                self.logger.log_event(
                                    event_type="alert",
                                    severity=level.name.lower(),
                                    message=w,
                                    details={"perclos": drowsiness.perclos if drowsiness else None},
                                    frame=frame if level == AlertLevel.CRITICAL else None
                                )
                    
                    self.head_pose_estimator.draw_pose_axes(frame, face_result.landmarks, w, h)
                else:
                    head_pose = None
                    gaze = None
                    yawn = None
                    drowsiness = None
                    aggregated = None
                
                self.logger.increment_frame()
            
            self._update_fps()
            
            output = self.drawer.draw(
                frame, face_result, drowsiness, aggregated,
                self.fps, self.alert_manager.get_active_warnings()
            )
            
            cv2.imshow('Driver Monitoring System', output)
            self._handle_key(cv2.waitKey(30) & 0xFF, output)
        
        self.cleanup()
    
    def _update_fps(self):
        self.frame_count += 1
        now = time.time()
        elapsed = now - self.last_fps_time
        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.last_fps_time = now
    
    def _handle_key(self, key: int, frame):
        if key == ord('q') or key == ord('Q'):
            self.running = False
        elif key == ord('r') or key == ord('R'):
            self.drowsiness_monitor.reset()
            self.yawning_detector.reset()
            self.distraction_detector.reset()
            self.state_aggregator.reset()
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
        self.capture.release()
        cv2.destroyAllWindows()
        summary = self.logger.get_summary()
        print(f"\nSession Summary:")
        print(f"  Duration: {summary['duration_seconds']:.1f}s")
        print(f"  Avg FPS: {summary['avg_fps']:.1f}")
        print(f"  Warnings: {summary['total_warnings']}")
        print(f"  Criticals: {summary['total_criticals']}")
        self.logger.close()


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