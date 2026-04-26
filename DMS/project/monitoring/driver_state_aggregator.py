from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
import time

from monitoring.drowsiness_monitor import DrowsinessResult, DrowsinessState
from core.head_pose_estimator import HeadPoseResult
from core.gaze_estimator import GazeResult
from core.yawning_detector import YawnResult


class OverallState(Enum):
    """Общее состояние водителя."""
    ATTENTIVE = "attentive"
    WARNING = "warning"
    CRITICAL = "critical"


class EventType(Enum):
    """Типы опасных событий."""
    DROWSINESS = "drowsiness"
    YAWNING = "yawning"
    GAZE_OFF_ROAD = "gaze_off_road"
    HEAD_DROOPING = "head_drooping"
    HEAD_TURNED = "head_turned"
    EXCESSIVE_NODDING = "excessive_nodding"


@dataclass
class AggregatedState:
    """Агрегированное состояние водителя."""
    overall: OverallState
    events: List[dict] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)
    
    # Компоненты
    drowsiness: Optional[DrowsinessResult] = None
    head_pose: Optional[HeadPoseResult] = None
    gaze: Optional[GazeResult] = None
    yawn: Optional[YawnResult] = None


class DriverStateAggregator:
    """
    Агрегатор состояний водителя.
    
    Собирает данные от всех мониторов, формирует единую оценку
    и приоритизирует предупреждения.
    """
    
    # Приоритеты событий (0 — высший)
    EVENT_PRIORITY = {
        EventType.HEAD_DROOPING: 0,
        EventType.DROWSINESS: 1,
        EventType.GAZE_OFF_ROAD: 2,
        EventType.EXCESSIVE_NODDING: 3,
        EventType.YAWNING: 4,
        EventType.HEAD_TURNED: 5,
    }
    
    def __init__(self, max_warnings: int = 3):
        self.max_warnings = max_warnings
        self.previous_state = OverallState.ATTENTIVE
        self.state_start_time = time.time()
    
    def aggregate(self,
                  drowsiness: Optional[DrowsinessResult] = None,
                  head_pose: Optional[HeadPoseResult] = None,
                  gaze: Optional[GazeResult] = None,
                  yawn: Optional[YawnResult] = None) -> AggregatedState:
        """
        Собирает и анализирует все доступные данные.
        Возвращает агрегированное состояние с приоритизированными предупреждениями.
        """
        events = []
        warnings = []
        now = time.time()
        
        if drowsiness is not None and drowsiness.state != DrowsinessState.ALERT:
            if drowsiness.state == DrowsinessState.DROWSY:
                events.append({
                    "type": EventType.DROWSINESS,
                    "priority": self.EVENT_PRIORITY[EventType.DROWSINESS],
                    "message": f"PERCLOS: {drowsiness.perclos:.1%}",
                    "timestamp": now
                })
                warnings.extend(drowsiness.warnings)
        
        if yawn is not None:
            if yawn.yawning:
                events.append({
                    "type": EventType.YAWNING,
                    "priority": self.EVENT_PRIORITY[EventType.YAWNING],
                    "message": "Yawning",
                    "timestamp": now
                })
                if yawn.warning:
                    warnings.append(yawn.warning)
            
            if yawn.excessive_yawning and not yawn.yawning:
                events.append({
                    "type": EventType.EXCESSIVE_NODDING,
                    "priority": self.EVENT_PRIORITY[EventType.EXCESSIVE_NODDING],
                    "message": "Excessive yawning",
                    "timestamp": now
                })
                if yawn.warning:
                    warnings.append(yawn.warning)
        
        if head_pose is not None and head_pose.success:
            for warning in head_pose.warnings:
                if "drooping" in warning or "microsleep" in warning:
                    events.append({
                        "type": EventType.HEAD_DROOPING,
                        "priority": self.EVENT_PRIORITY[EventType.HEAD_DROOPING],
                        "message": warning,
                        "timestamp": now
                    })
                    warnings.append(warning)
                elif "turned" in warning:
                    events.append({
                        "type": EventType.HEAD_TURNED,
                        "priority": self.EVENT_PRIORITY[EventType.HEAD_TURNED],
                        "message": warning,
                        "timestamp": now
                    })
                    warnings.append(warning)
        
        if gaze is not None and gaze.success and not gaze.looking_forward:
            events.append({
                "type": EventType.GAZE_OFF_ROAD,
                "priority": self.EVENT_PRIORITY[EventType.GAZE_OFF_ROAD],
                "message": f"Gaze: {gaze.zone}",
                "timestamp": now
            })
        
        events.sort(key=lambda e: e["priority"])
        warnings = self._prioritize_warnings(warnings)
        
        overall = self._determine_overall_state(events)
        
        if overall != self.previous_state:
            self.state_start_time = now
            self.previous_state = overall
        
        return AggregatedState(
            overall=overall,
            events=events,
            warnings=warnings[:self.max_warnings],
            timestamp=now,
            drowsiness=drowsiness,
            head_pose=head_pose,
            gaze=gaze,
            yawn=yawn
        )
    
    def _determine_overall_state(self, events: List[dict]) -> OverallState:
        """Определяет общее состояние по событиям."""
        if not events:
            return OverallState.ATTENTIVE
        
        highest_priority = min(e["priority"] for e in events)
        
        if highest_priority <= 1:
            return OverallState.CRITICAL
        elif highest_priority <= 3:
            return OverallState.WARNING
        
        return OverallState.ATTENTIVE
    
    def _prioritize_warnings(self, warnings: List[str]) -> List[str]:
        """Убирает дубликаты и сортирует предупреждения."""
        seen = set()
        unique = []
        for w in warnings:
            if w not in seen:
                seen.add(w)
                unique.append(w)
        return unique
    
    def reset(self):
        self.previous_state = OverallState.ATTENTIVE
        self.state_start_time = time.time()