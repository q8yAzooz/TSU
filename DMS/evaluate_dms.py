"""
Скрипт для оценки производительности алгоритмов DMS на датасете NTHU-DDD
Поддерживает два бэкенда: OpenCV (каскады Хаара) и MediaPipe (Face Landmarker)
"""

import cv2
import numpy as np
import os
import sys
import time
from collections import deque
import json
from pathlib import Path

class DatasetEvaluator:
    """
    Универсальный класс для тестирования DMS-алгоритмов на наборах данных
    """
    
    def __init__(self, dataset_path, backend='mediapipe', model_path='face_landmarker.task'):
        """
        Инициализация оценщика
        
        Args:
            dataset_path: путь к корневой папке датасета NTHU-DDD
            backend: 'opencv' или 'mediapipe'
            model_path: путь к модели MediaPipe (только для mediapipe)
        """
        self.dataset_path = Path(dataset_path)
        self.backend = backend
        self.model_path = model_path
        
        # Метрики для оценки
        self.metrics = {
            'total_frames': 0,
            'face_detected_frames': 0,
            'eyes_detected_frames': 0,
            'blink_count': 0,
            'perclos_values': [],
            'processing_times': [],
            'ear_values': [] if backend == 'mediapipe' else None
        }
        
        # Инициализация детектора в зависимости от бэкенда
        if backend == 'opencv':
            self._init_opencv()
        elif backend == 'mediapipe':
            self._init_mediapipe()
        else:
            raise ValueError(f"Unsupported backend: {backend}")
    
    def _init_opencv(self):
        """Инициализация детектора на базе каскадов Хаара"""
        cascade_path = cv2.data.haarcascades
        
        self.face_cascade = cv2.CascadeClassifier(
            cascade_path + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cascade_path + 'haarcascade_eye.xml'
        )
        
        if self.face_cascade.empty():
            raise RuntimeError("Cannot load face cascade")
        
        self.eye_history = deque(maxlen=30)
        self.last_eye_state = "OPEN"
        self.blink_count = 0
        self.blink_cooldown = 0
        self.BLINK_COOLDOWN_FRAMES = 3
        self.EYE_CLOSED_FRAMES = 3
        
        self.backend_name = "OpenCV Haar Cascades"
        self.face_detection_success = False
        
    def _init_mediapipe(self):
        """Инициализация детектора на базе MediaPipe"""
        try:
            import mediapipe as mp
            from mediapipe.tasks import python
            from mediapipe.tasks.python import vision
            
            self.mp = mp
            self.python = python
            self.vision = vision
            
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(
                    f"Model file not found: {self.model_path}\n"
                    "Download from: https://storage.googleapis.com/mediapipe-models/"
                    "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
                )
            
            base_options = python.BaseOptions(model_asset_path=self.model_path)
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
            
            # Индексы для глаз (MediaPipe Face Mesh)
            self.LEFT_EYE_INDICES = [362, 385, 387, 263, 373, 380]
            self.RIGHT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
            
            self.ear_history = deque(maxlen=5)
            self.eye_history = deque(maxlen=30)
            self.blink_count = 0
            self.last_eye_state = True
            self.blink_cooldown = 0
            self.EAR_THRESHOLD = 0.20
            self.BLINK_COOLDOWN_FRAMES = 3
            
            self.backend_name = "MediaPipe Face Landmarker"
            self.face_detection_success = True
            
        except ImportError as e:
            raise ImportError(f"MediaPipe import error: {e}")
    
    def _calculate_ear(self, landmarks, indices, w, h):
        """Расчет Eye Aspect Ratio для MediaPipe"""
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
    
    def _check_eyes_open_opencv(self, eye_roi):
        """Проверка открытия глаз для OpenCV"""
        if eye_roi.size == 0:
            return False
        
        gray = cv2.cvtColor(eye_roi, cv2.COLOR_BGR2GRAY) if len(eye_roi.shape) == 3 else eye_roi
        _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
        white_pixels = cv2.countNonZero(thresh)
        total_pixels = eye_roi.shape[0] * eye_roi.shape[1]
        ratio = white_pixels / total_pixels if total_pixels > 0 else 0
        
        return ratio > 0.05
    
    def process_frame(self, frame):
        """
        Обработка одного кадра
        
        Returns:
            dict: результаты обработки кадра
        """
        start_time = time.time()
        
        result = {
            'face_detected': False,
            'eyes_detected': False,
            'eyes_open': True,
            'ear': None,
            'blink_registered': False,
            'perclos': 0.0
        }
        
        h, w = frame.shape[:2]
        
        if self.backend == 'opencv':
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100)
            )
            
            if len(faces) > 0:
                result['face_detected'] = True
                face = max(faces, key=lambda f: f[2] * f[3])
                x, y, fw, fh = face
                
                face_roi = frame[y:y+fh, x:x+fw]
                eyes = self.eye_cascade.detectMultiScale(
                    face_roi, scaleFactor=1.1, minNeighbors=5, minSize=(20, 20)
                )
                
                if len(eyes) >= 2:
                    result['eyes_detected'] = True
                    eyes = sorted(eyes, key=lambda e: e[1])[:2]
                    
                    eyes_open_count = 0
                    for (ex, ey, ew, eh) in eyes:
                        eye_roi = face_roi[ey:ey+eh, ex:ex+ew]
                        if self._check_eyes_open_opencv(eye_roi):
                            eyes_open_count += 1
                    
                    eyes_open = eyes_open_count >= 1
                    result['eyes_open'] = eyes_open
                    
                    eye_state = "OPEN" if eyes_open else "CLOSED"
                    
                    if eye_state == "CLOSED" and self.last_eye_state == "OPEN":
                        self.blink_count += 1
                        result['blink_registered'] = True
                    
                    self.last_eye_state = eye_state
                    self.eye_history.append(eye_state)
        
        elif self.backend == 'mediapipe':
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=rgb_frame)
            detection_result = self.detector.detect(mp_image)
            
            if detection_result.face_landmarks:
                result['face_detected'] = True
                result['eyes_detected'] = True
                
                face_landmarks = detection_result.face_landmarks[0]
                
                left_ear = self._calculate_ear(face_landmarks, self.LEFT_EYE_INDICES, w, h)
                right_ear = self._calculate_ear(face_landmarks, self.RIGHT_EYE_INDICES, w, h)
                avg_ear = (left_ear + right_ear) / 2.0
                
                self.ear_history.append(avg_ear)
                smoothed_ear = sum(self.ear_history) / len(self.ear_history)
                
                result['ear'] = smoothed_ear
                eyes_open = smoothed_ear > self.EAR_THRESHOLD
                result['eyes_open'] = eyes_open
                
                if self.blink_cooldown > 0:
                    self.blink_cooldown -= 1
                
                if not eyes_open and self.last_eye_state and self.blink_cooldown == 0:
                    self.blink_count += 1
                    self.blink_cooldown = self.BLINK_COOLDOWN_FRAMES
                    result['blink_registered'] = True
                
                self.last_eye_state = eyes_open
                self.eye_history.append("CLOSED" if not eyes_open else "OPEN")
        
        # Вычисление PERCLOS
        if self.eye_history:
            closed = sum(1 for s in self.eye_history if s in ("CLOSED", False))
            result['perclos'] = closed / len(self.eye_history)
        
        processing_time = (time.time() - start_time) * 1000
        result['processing_time_ms'] = processing_time
        
        return result
    
    def evaluate_video(self, video_path, label=None):
        """
        Оценка одного видеофайла
        
        Args:
            video_path: путь к видеофайлу
            label: метка класса (для информативности)
        
        Returns:
            dict: метрики для данного видео
        """
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            print(f"  Error: Cannot open video {video_path}")
            return None
        
        video_metrics = {
            'video_name': video_path.name,
            'label': label,
            'total_frames': 0,
            'face_detected_frames': 0,
            'eyes_detected_frames': 0,
            'blink_count': 0,
            'perclos_mean': 0.0,
            'perclos_max': 0.0,
            'processing_time_mean_ms': 0.0,
            'fps_mean': 0.0
        }
        
        perclos_values = []
        processing_times = []
        start_video_time = time.time()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            result = self.process_frame(frame)
            
            video_metrics['total_frames'] += 1
            
            if result['face_detected']:
                video_metrics['face_detected_frames'] += 1
            
            if result.get('eyes_detected', False):
                video_metrics['eyes_detected_frames'] += 1
            
            if result['blink_registered']:
                video_metrics['blink_count'] += 1
            
            perclos_values.append(result['perclos'])
            processing_times.append(result['processing_time_ms'])
        
        cap.release()
        
        total_time = time.time() - start_video_time
        
        if video_metrics['total_frames'] > 0:
            video_metrics['face_detection_rate'] = video_metrics['face_detected_frames'] / video_metrics['total_frames']
            video_metrics['eyes_detection_rate'] = video_metrics['eyes_detected_frames'] / video_metrics['total_frames']
            video_metrics['perclos_mean'] = np.mean(perclos_values) if perclos_values else 0.0
            video_metrics['perclos_max'] = np.max(perclos_values) if perclos_values else 0.0
            video_metrics['processing_time_mean_ms'] = np.mean(processing_times) if processing_times else 0.0
            video_metrics['fps_mean'] = video_metrics['total_frames'] / total_time if total_time > 0 else 0.0
        
        return video_metrics
    
    def evaluate_dataset(self, scenarios=None, max_videos=None):
        """
        Оценка всего датасета
        
        Args:
            scenarios: список сценариев для тестирования (например, ['alert', 'drowsy'])
            max_videos: максимальное количество видео для обработки
        
        Returns:
            dict: сводные метрики по датасету
        """
        print(f"\n{'='*60}")
        print(f"Dataset Evaluation - {self.backend_name}")
        print(f"Dataset path: {self.dataset_path}")
        print(f"{'='*60}\n")
        
        # Поиск видеофайлов в структуре NTHU-DDD
        video_files = []
        
        if scenarios is None:
            scenarios = ['alert', 'drowsy', 'drowsy_simulated']
        
        for scenario in scenarios:
            scenario_path = self.dataset_path / scenario
            if scenario_path.exists():
                for video_file in scenario_path.glob("*.avi"):
                    video_files.append((video_file, scenario))
                for video_file in scenario_path.glob("*.mp4"):
                    video_files.append((video_file, scenario))
        
        if not video_files:
            print(f"Error: No video files found in {self.dataset_path}")
            return None
        
        if max_videos:
            video_files = video_files[:max_videos]
        
        print(f"Found {len(video_files)} video files\n")
        
        all_video_metrics = []
        
        for i, (video_path, label) in enumerate(video_files, 1):
            print(f"[{i}/{len(video_files)}] Processing: {video_path.name} ({label})")
            
            video_metrics = self.evaluate_video(video_path, label)
            if video_metrics:
                all_video_metrics.append(video_metrics)
        
        # Агрегация метрик
        summary = {
            'backend': self.backend_name,
            'total_videos': len(all_video_metrics),
            'video_metrics': all_video_metrics,
            'aggregated': {}
        }
        
        if all_video_metrics:
            summary['aggregated'] = {
                'avg_face_detection_rate': np.mean([m['face_detection_rate'] for m in all_video_metrics]),
                'avg_eyes_detection_rate': np.mean([m.get('eyes_detection_rate', 0) for m in all_video_metrics]),
                'avg_perclos': np.mean([m['perclos_mean'] for m in all_video_metrics]),
                'avg_fps': np.mean([m['fps_mean'] for m in all_video_metrics]),
                'avg_processing_time_ms': np.mean([m['processing_time_mean_ms'] for m in all_video_metrics]),
                'total_blinks': sum([m['blink_count'] for m in all_video_metrics]),
                'total_frames': sum([m['total_frames'] for m in all_video_metrics])
            }
            
            # Группировка по сценариям
            by_scenario = {}
            for m in all_video_metrics:
                label = m['label']
                if label not in by_scenario:
                    by_scenario[label] = []
                by_scenario[label].append(m)
            
            summary['by_scenario'] = {}
            for scenario, metrics in by_scenario.items():
                summary['by_scenario'][scenario] = {
                    'videos_count': len(metrics),
                    'avg_perclos': np.mean([m['perclos_mean'] for m in metrics]),
                    'max_perclos': np.max([m['perclos_max'] for m in metrics]),
                    'avg_blink_count': np.mean([m['blink_count'] for m in metrics])
                }
        
        return summary
    
    def print_summary(self, summary):
        """Вывод сводных результатов"""
        if not summary:
            return
        
        print(f"\n{'='*60}")
        print(f"EVALUATION SUMMARY - {summary['backend']}")
        print(f"{'='*60}")
        
        agg = summary['aggregated']
        print(f"\nAggregated metrics ({summary['total_videos']} videos):")
        print(f"  Total frames processed: {agg['total_frames']}")
        print(f"  Face detection rate: {agg['avg_face_detection_rate']:.2%}")
        
        if self.backend == 'opencv':
            print(f"  Eyes detection rate: {agg['avg_eyes_detection_rate']:.2%}")
        
        print(f"  Average PERCLOS: {agg['avg_perclos']:.2%}")
        print(f"  Total blinks detected: {agg['total_blinks']}")
        print(f"  Average FPS: {agg['avg_fps']:.2f}")
        print(f"  Avg processing time: {agg['avg_processing_time_ms']:.2f} ms")
        
        if 'by_scenario' in summary:
            print(f"\nResults by scenario:")
            for scenario, metrics in summary['by_scenario'].items():
                print(f"\n  {scenario.upper()} ({metrics['videos_count']} videos):")
                print(f"    Avg PERCLOS: {metrics['avg_perclos']:.2%}")
                print(f"    Max PERCLOS: {metrics['max_perclos']:.2%}")
                print(f"    Avg blink count: {metrics['avg_blink_count']:.1f}")
        
        print(f"\n{'='*60}")
    
    def save_results(self, summary, output_path):
        """Сохранение результатов в JSON"""
        # Преобразуем numpy типы в стандартные Python
        def convert_numpy(obj):
            if isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(i) for i in obj]
            return obj
        
        summary_clean = convert_numpy(summary)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary_clean, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {output_path}")


def main():
    """
    Пример запуска:
    python evaluate_dms.py --dataset /path/to/NTHU-DDD --backend mediapipe
    python evaluate_dms.py --dataset /path/to/NTHU-DDD --backend opencv --max-videos 5
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Evaluate DMS algorithms on dataset')
    parser.add_argument('--dataset', type=str, required=True,
                        help='Path to NTHU-DDD dataset root folder')
    parser.add_argument('--backend', type=str, default='mediapipe',
                        choices=['opencv', 'mediapipe'],
                        help='Detection backend')
    parser.add_argument('--model', type=str, default='face_landmarker.task',
                        help='Path to MediaPipe model (only for mediapipe)')
    parser.add_argument('--max-videos', type=int, default=None,
                        help='Maximum number of videos to process')
    parser.add_argument('--output', type=str, default=None,
                        help='Output JSON file path')
    
    args = parser.parse_args()
    
    # Создаем оценщик
    evaluator = DatasetEvaluator(
        dataset_path=args.dataset,
        backend=args.backend,
        model_path=args.model
    )
    
    # Запускаем оценку
    summary = evaluator.evaluate_dataset(
        max_videos=args.max_videos
    )
    
    # Выводим результаты
    evaluator.print_summary(summary)
    
    # Сохраняем результаты
    if args.output:
        evaluator.save_results(summary, args.output)
    else:
        default_output = f"evaluation_{args.backend}_{time.strftime('%Y%m%d_%H%M%S')}.json"
        evaluator.save_results(summary, default_output)


if __name__ == "__main__":
    main()