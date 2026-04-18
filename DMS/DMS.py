import cv2
import numpy as np
from collections import deque
import time
import sys

class DriverMonitoringSystem:
    def __init__(self):
        cascade_path = cv2.data.haarcascades
        
        self.face_cascade = cv2.CascadeClassifier(
            cascade_path + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cascade_path + 'haarcascade_eye.xml'
        )
        
        if self.face_cascade.empty():
            sys.exit(1)
        
        self.eye_history = deque(maxlen=30)
        self.blink_count = 0
        self.last_blink_time = time.time()
        self.start_time = time.time()
        self.last_eye_state = "OPEN"
        self.frame_count = 0
        self.eyes_closed_frames = 0
        
        self.EYE_CLOSED_FRAMES = 3 
        self.PERCLOS_THRESH = 0.15
        
        self.fps = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()
        
    def detect_eyes(self, face_roi):
        eyes = self.eye_cascade.detectMultiScale(
            face_roi,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(20, 20)
        )
        
        if len(eyes) >= 2:
            eyes = sorted(eyes, key=lambda e: e[1])
            return eyes[:2]
        return eyes
    
    def check_eyes_open(self, eye_roi):
        if eye_roi.size == 0:
            return False
        
        gray = cv2.cvtColor(eye_roi, cv2.COLOR_BGR2GRAY) if len(eye_roi.shape) == 3 else eye_roi
        
        _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        
        white_pixels = cv2.countNonZero(thresh)
        total_pixels = eye_roi.shape[0] * eye_roi.shape[1]
        
        ratio = white_pixels / total_pixels if total_pixels > 0 else 0
        
        return ratio > 0.05  
    
    def process_frame(self, frame):
        self.frame_count += 1
        self.fps_counter += 1
        
        now = time.time()
        if now - self.last_fps_time >= 1.0:
            self.fps = self.fps_counter
            self.fps_counter = 0
            self.last_fps_time = now
        
        output = frame.copy()
        h, w = output.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        state = "ATTENTIVE"
        warnings = []
        eyes_open = True
        perclos = 0.0
        
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )
        
        if len(faces) > 0:
            face = max(faces, key=lambda f: f[2] * f[3])
            x, y, fw, fh = face
            
            cv2.rectangle(output, (x, y), (x+fw, y+fh), (255, 0, 0), 2)
            
            face_roi = frame[y:y+fh, x:x+fw]
            
            eyes = self.detect_eyes(face_roi)
            
            eyes_open_count = 0
            for (ex, ey, ew, eh) in eyes:
                abs_x = x + ex
                abs_y = y + ey
                
                cv2.rectangle(output, (abs_x, abs_y), (abs_x+ew, abs_y+eh), (0, 255, 0), 2)
                
                eye_roi = face_roi[ey:ey+eh, ex:ex+ew]
                if self.check_eyes_open(eye_roi):
                    eyes_open_count += 1
            
            eyes_open = eyes_open_count >= 1
            eye_state = "OPEN" if eyes_open else "CLOSED"
            
            if eye_state == "CLOSED" and self.last_eye_state == "OPEN":
                self.blink_count += 1
                self.last_blink_time = now
            
            if eye_state == "CLOSED":
                self.eyes_closed_frames += 1
            
            self.last_eye_state = eye_state
            self.eye_history.append(eye_state)
            
            if self.eye_history:
                closed = sum(1 for s in self.eye_history if s == "CLOSED")
                perclos = closed / len(self.eye_history)
            
            if perclos > self.PERCLOS_THRESH:
                state = "DROWSY"
                warnings.append(f"DROWSY! PERCLOS: {perclos:.1%}")
            
            elapsed = max(0.1, now - self.start_time)
            blink_rate = self.blink_count / (elapsed / 60.0)
            
            if blink_rate < 8 and elapsed > 30:
                warnings.append(f"Low blink rate: {blink_rate:.1f}/min")
        
        self.draw_overlay(output, state, eyes_open, perclos, warnings)
        
        cv2.putText(output, f"FPS: {self.fps}", (w - 100, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        return output, state, warnings
    
    def draw_overlay(self, frame, state, eyes_open, perclos, warnings):
        overlay = frame.copy()
        cv2.rectangle(overlay, (5, 5), (400, 200), (0, 0, 0), -1)
        frame[:] = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)
        
        colors = {
            "ATTENTIVE": (0, 255, 0),
            "DISTRACTED": (0, 255, 255),
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
        
        cv2.putText(frame, f"PERCLOS: {perclos:.1%}", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y += 25
        
        elapsed = time.time() - self.start_time
        blink_rate = self.blink_count / (elapsed / 60.0) if elapsed > 0 else 0
        cv2.putText(frame, f"Blinks: {self.blink_count} ({blink_rate:.1f}/min)", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y += 25
        
        cv2.putText(frame, f"Time: {elapsed:.0f}s", (10, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        if warnings:
            y = 200
            for w in warnings[:3]:
                cv2.putText(frame, f"! {w}", (10, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                y += 25
    
    def run(self):
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        self.start_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            
            try:
                processed, state, warnings = self.process_frame(frame)
                cv2.imshow('DMS - OpenCV', processed)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.reset()
                elif key == ord('s'):
                    cv2.imwrite(f'screenshot_{time.strftime("%Y%m%d_%H%M%S")}.jpg', processed)
                    
            except Exception:
                cv2.imshow('DMS', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        cap.release()
        cv2.destroyAllWindows()
        self.print_summary()
    
    def reset(self):
        self.blink_count = 0
        self.frame_count = 0
        self.eyes_closed_frames = 0
        self.eye_history.clear()
        self.start_time = time.time()
    
    def print_summary(self):
        elapsed = time.time() - self.start_time
        
        if elapsed > 60:
            blink_rate = self.blink_count / (elapsed / 60.0)
        
        if self.eye_history:
            perclos = sum(1 for s in self.eye_history if s == "CLOSED") / len(self.eye_history)


def check_requirements():
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        if face_cascade.empty() or eye_cascade.empty():
            return False
            
    except Exception:
        return False
    
    return True


def main():
    if not check_requirements():
        return
    
    try:
        dms = DriverMonitoringSystem()
        dms.run()
    except KeyboardInterrupt:
        pass
    except Exception:
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()