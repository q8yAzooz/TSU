import cv2
import numpy as np
from collections import deque
import time
import sys
import os

try:
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
except ImportError as e:
    print(f"MediaPipe import error: {e}")
    sys.exit(1)

class DriverMonitoringSystem:
    def __init__(self, model_path='face_landmarker.task'):
        if not os.path.exists(model_path):
            print(f"Model file '{model_path}' not found")
            sys.exit(1)
        
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
        
        self.LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
        self.RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
        
        self.ear_history = deque(maxlen=5)
        self.eye_history = deque(maxlen=30)
        self.blink_count = 0
        self.start_time = time.time()
        self.last_eye_state = True
        self.blink_cooldown = 0
        
        self.PERCLOS_THRESH = 0.15
        self.EAR_THRESHOLD = 0.20
        self.BLINK_COOLDOWN_FRAMES = 3
        
        self.fps = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()
        self.running = True
        
    def calculate_ear(self, landmarks, indices, w, h):
        points = []
        for idx in indices:
            landmark = landmarks[idx]
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            points.append(np.array([x, y]))
        
        if len(points) < 6:
            return 0.0
        
        vertical_1 = np.linalg.norm(points[1] - points[5])
        vertical_2 = np.linalg.norm(points[2] - points[4])
        horizontal = np.linalg.norm(points[0] - points[3])
        
        ear = (vertical_1 + vertical_2) / (2.0 * horizontal) if horizontal > 0 else 0.0
        return ear
    
    def process_frame(self, frame):
        self.fps_counter += 1
        now = time.time()
        
        if now - self.last_fps_time >= 1.0:
            self.fps = self.fps_counter
            self.fps_counter = 0
            self.last_fps_time = now
        
        output = frame.copy()
        h, w = output.shape[:2]
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = self.detector.detect(mp_image)
        
        state = "ATTENTIVE"
        warnings = []
        eyes_open = True
        perclos = 0.0
        avg_ear = 0.0
        
        if detection_result.face_landmarks:
            face_landmarks = detection_result.face_landmarks[0]
            
            left_ear = self.calculate_ear(face_landmarks, self.LEFT_EYE_INDICES, w, h)
            right_ear = self.calculate_ear(face_landmarks, self.RIGHT_EYE_INDICES, w, h)
            avg_ear = (left_ear + right_ear) / 2.0
            
            self.ear_history.append(avg_ear)
            smoothed_ear = sum(self.ear_history) / len(self.ear_history)
            
            left_points = []
            for idx in self.LEFT_EYE_INDICES:
                landmark = face_landmarks[idx]
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                left_points.append([x, y])
            
            right_points = []
            for idx in self.RIGHT_EYE_INDICES:
                landmark = face_landmarks[idx]
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                right_points.append([x, y])
            
            left_hull = cv2.convexHull(np.array(left_points))
            right_hull = cv2.convexHull(np.array(right_points))
            
            eye_color = (0, 255, 0) if smoothed_ear > self.EAR_THRESHOLD else (0, 0, 255)
            cv2.drawContours(output, [left_hull], -1, eye_color, 2)
            cv2.drawContours(output, [right_hull], -1, eye_color, 2)
            
            eyes_open = smoothed_ear > self.EAR_THRESHOLD
            
            if self.blink_cooldown > 0:
                self.blink_cooldown -= 1
            
            if not eyes_open and self.last_eye_state and self.blink_cooldown == 0:
                self.blink_count += 1
                self.blink_cooldown = self.BLINK_COOLDOWN_FRAMES
            
            self.last_eye_state = eyes_open
            self.eye_history.append("CLOSED" if not eyes_open else "OPEN")
            
            if self.eye_history:
                closed = sum(1 for s in self.eye_history if s == "CLOSED")
                perclos = closed / len(self.eye_history)
            
            if perclos > self.PERCLOS_THRESH:
                state = "DROWSY"
                warnings.append(f"DROWSY! PERCLOS: {perclos:.1%}")
        
        self.draw_overlay(output, state, eyes_open, perclos, avg_ear, warnings)
        
        cv2.putText(output, f"FPS: {self.fps}", (w - 100, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        cv2.putText(output, "Q-Quit | R-Reset | S-Screenshot | +/- Threshold", 
                   (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return output
    
    def draw_overlay(self, frame, state, eyes_open, perclos, ear, warnings):
        overlay = frame.copy()
        cv2.rectangle(overlay, (5, 5), (400, 220), (0, 0, 0), -1)
        frame[:] = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)
        
        colors = {
            "ATTENTIVE": (0, 255, 0),
            "DROWSY": (0, 0, 255)
        }
        color = colors.get(state, (255, 255, 255))
        
        y = 30
        cv2.putText(frame, f"State: {state}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        y += 30
        
        eye_status = "OPEN" if eyes_open else "CLOSED"
        eye_color = (0, 255, 0) if eyes_open else (0, 0, 255)
        cv2.putText(frame, f"Eyes: {eye_status}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, eye_color, 1)
        y += 25
        
        threshold_color = (0, 255, 0) if ear > self.EAR_THRESHOLD else (0, 0, 255)
        cv2.putText(frame, f"EAR: {ear:.3f} (thresh: {self.EAR_THRESHOLD:.2f})", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, threshold_color, 1)
        y += 25
        
        cv2.putText(frame, f"PERCLOS: {perclos:.1%}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y += 25
        
        elapsed = time.time() - self.start_time
        blink_rate = self.blink_count / (elapsed / 60.0) if elapsed > 0 else 0
        cv2.putText(frame, f"Blinks: {self.blink_count} ({blink_rate:.1f}/min)", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        if warnings:
            y = 230
            for w in warnings[:3]:
                cv2.putText(frame, f"! {w}", (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                y += 25
    
    def handle_key(self, key, frame):
        if key == ord('q') or key == ord('Q'):
            self.running = False
        elif key == ord('r') or key == ord('R'):
            self.blink_count = 0
            self.eye_history.clear()
            self.ear_history.clear()
            self.start_time = time.time()
            self.blink_cooldown = 0
        elif key == ord('s') or key == ord('S'):
            filename = f'screenshot_{time.strftime("%Y%m%d_%H%M%S")}.jpg'
            cv2.imwrite(filename, frame)
        elif key == ord('+') or key == ord('='):
            self.EAR_THRESHOLD = min(0.5, self.EAR_THRESHOLD + 0.01)
        elif key == ord('-') or key == ord('_'):
            self.EAR_THRESHOLD = max(0.1, self.EAR_THRESHOLD - 0.01)
    
    def run(self):
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("Error: Cannot open camera")
            return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        cv2.namedWindow('Driver Monitoring System', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Driver Monitoring System', 800, 600)
        
        self.start_time = time.time()
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            processed = self.process_frame(frame)
            cv2.imshow('Driver Monitoring System', processed)
            
            key = cv2.waitKey(30) & 0xFF
            if key != 255:
                self.handle_key(key, processed)
        
        cap.release()
        cv2.destroyAllWindows()


def main():
    dms = DriverMonitoringSystem()
    
    try:
        dms.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()