"""
Data models for Healthcare Planning Assistant Agent
Simple, entry-level models for healthcare task management
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

class TaskPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ResourceType(Enum):
    DOCTOR = "doctor"
    NURSE = "nurse"
    EQUIPMENT = "equipment"
    ROOM = "room"
    MEDICATION = "medication"
    LAB = "lab"

@dataclass
class Resource:
    """Represents a healthcare resource"""
    id: str
    name: str
    type: ResourceType
    available: bool = True
    capacity: int = 1
    current_load: int = 0
    
    def is_available(self) -> bool:
        return self.available and self.current_load < self.capacity

@dataclass
class HealthcareTask:
    """Represents a single healthcare task"""
    id: str
    title: str
    description: str
    priority: TaskPriority
    status: TaskStatus = TaskStatus.PENDING
    estimated_duration: int = 30  # minutes
    dependencies: List[str] = None
    required_resources: List[Resource] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.required_resources is None:
            self.required_resources = []
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class ExecutionPlan:
    """Represents a complete execution plan for healthcare tasks"""
    goal: str
    tasks: List[HealthcareTask]
    schedule: Dict[str, datetime] = None
    total_duration: int = 0
    
    def __post_init__(self):
        if self.schedule is None:
            self.schedule = {}

@dataclass
class PlanningRequest:
    """Represents a planning request from user"""
    goal: str
    patient_info: Dict[str, Any] = None
    constraints: List[str] = None
    preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.patient_info is None:
            self.patient_info = {}
        if self.constraints is None:
            self.constraints = []
        if self.preferences is None:
            self.preferences = {}
