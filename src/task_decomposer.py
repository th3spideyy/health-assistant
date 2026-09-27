"""
Task Decomposer for Healthcare Planning Assistant
Breaks down high-level healthcare goals into actionable tasks
"""

from typing import List, Dict, Any
from .models import HealthcareTask, PlanningRequest, TaskPriority, ResourceType
import uuid

class HealthcareTaskDecomposer:
    """Decomposes high-level healthcare goals into specific tasks"""
    
    def __init__(self):
        self.task_templates = self._initialize_task_templates()
    
    def _initialize_task_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize predefined task templates for common healthcare scenarios"""
        return {
            "treatment_options": [
                {
                    "title": "Initial Patient Assessment",
                    "description": "Comprehensive evaluation of patient's current condition",
                    "priority": TaskPriority.HIGH,
                    "duration": 45,
                    "resources": ["dr_jones", "room_101"],
                    "dependencies": []
                },
                {
                    "title": "Diagnostic Tests",
                    "description": "Order and conduct necessary diagnostic tests",
                    "priority": TaskPriority.HIGH,
                    "duration": 60,
                    "resources": ["blood_lab", "xray_machine"],
                    "dependencies": ["Initial Patient Assessment"]
                },
                {
                    "title": "Specialist Consultation",
                    "description": "Consult with appropriate specialists based on diagnosis",
                    "priority": TaskPriority.MEDIUM,
                    "duration": 30,
                    "resources": ["dr_smith"],
                    "dependencies": ["Diagnostic Tests"]
                },
                {
                    "title": "Treatment Plan Development",
                    "description": "Create comprehensive treatment plan based on all findings",
                    "priority": TaskPriority.HIGH,
                    "duration": 40,
                    "resources": ["dr_smith", "dr_jones"],
                    "dependencies": ["Specialist Consultation"]
                }
            ],
            "emergency_care": [
                {
                    "title": "Triage Assessment",
                    "description": "Rapid assessment of patient's emergency status",
                    "priority": TaskPriority.URGENT,
                    "duration": 15,
                    "resources": ["nurse_1"],
                    "dependencies": []
                },
                {
                    "title": "Emergency Stabilization",
                    "description": "Immediate life-saving interventions",
                    "priority": TaskPriority.URGENT,
                    "duration": 30,
                    "resources": ["dr_jones", "room_102"],
                    "dependencies": ["Triage Assessment"]
                },
                {
                    "title": "Emergency Diagnostic Tests",
                    "description": "Critical diagnostic tests for emergency evaluation",
                    "priority": TaskPriority.HIGH,
                    "duration": 45,
                    "resources": ["blood_lab", "ultrasound"],
                    "dependencies": ["Emergency Stabilization"]
                }
            ],
            "routine_checkup": [
                {
                    "title": "Vital Signs Check",
                    "description": "Measure and record patient vital signs",
                    "priority": TaskPriority.MEDIUM,
                    "duration": 20,
                    "resources": ["nurse_1"],
                    "dependencies": []
                },
                {
                    "title": "Physical Examination",
                    "description": "Complete physical examination by doctor",
                    "priority": TaskPriority.MEDIUM,
                    "duration": 30,
                    "resources": ["dr_jones", "room_101"],
                    "dependencies": ["Vital Signs Check"]
                },
                {
                    "title": "Health Counseling",
                    "description": "Provide health advice and preventive care recommendations",
                    "priority": TaskPriority.LOW,
                    "duration": 25,
                    "resources": ["dr_jones"],
                    "dependencies": ["Physical Examination"]
                }
            ],
            "surgery_preparation": [
                {
                    "title": "Pre-operative Assessment",
                    "description": "Complete medical evaluation before surgery",
                    "priority": TaskPriority.HIGH,
                    "duration": 60,
                    "resources": ["dr_smith", "blood_lab"],
                    "dependencies": []
                },
                {
                    "title": "Anesthesia Consultation",
                    "description": "Evaluate patient for anesthesia compatibility",
                    "priority": TaskPriority.HIGH,
                    "duration": 30,
                    "resources": ["dr_wilson"],
                    "dependencies": ["Pre-operative Assessment"]
                },
                {
                    "title": "Surgical Planning",
                    "description": "Final surgical plan and preparation",
                    "priority": TaskPriority.HIGH,
                    "duration": 45,
                    "resources": ["dr_smith", "or_1"],
                    "dependencies": ["Anesthesia Consultation"]
                }
            ]
        }
    
    def decompose_goal(self, request: PlanningRequest) -> List[HealthcareTask]:
        """Decompose a high-level goal into specific healthcare tasks"""
        goal_lower = request.goal.lower()
        
        # Determine which template to use based on the goal
        if "treatment" in goal_lower or "therapy" in goal_lower:
            template_key = "treatment_options"
        elif "emergency" in goal_lower or "urgent" in goal_lower:
            template_key = "emergency_care"
        elif "checkup" in goal_lower or "routine" in goal_lower or "annual" in goal_lower:
            template_key = "routine_checkup"
        elif "surgery" in goal_lower or "operation" in goal_lower or "procedure" in goal_lower:
            template_key = "surgery_preparation"
        else:
            # Default to treatment options for unknown goals
            template_key = "treatment_options"
        
        tasks = []
        task_map = {}  # Map task titles to their IDs for dependency resolution
        
        if template_key in self.task_templates:
            for template in self.task_templates[template_key]:
                task = HealthcareTask(
                    id=str(uuid.uuid4()),
                    title=template["title"],
                    description=template["description"],
                    priority=template["priority"],
                    estimated_duration=template["duration"],
                    required_resources=template["resources"],
                    dependencies=[]
                )
                
                tasks.append(task)
                task_map[template["title"]] = task.id
        
            # Resolve dependencies using task titles
            for i, task in enumerate(tasks):
                template = self.task_templates[template_key][i]
                resolved_dependencies = []
                for dep_title in template["dependencies"]:
                    if dep_title in task_map:
                        resolved_dependencies.append(task_map[dep_title])
                task.dependencies = resolved_dependencies
        
        # Customize tasks based on patient information and constraints
        self._customize_tasks(tasks, request)
        
        return tasks
    
    def _customize_tasks(self, tasks: List[HealthcareTask], request: PlanningRequest):
        """Customize tasks based on patient information and constraints"""
        # Adjust priority based on patient age
        if "age" in request.patient_info:
            age = request.patient_info["age"]
            if age > 65:
                # Increase priority for elderly patients
                for task in tasks:
                    if task.priority == TaskPriority.LOW:
                        task.priority = TaskPriority.MEDIUM
                    elif task.priority == TaskPriority.MEDIUM:
                        task.priority = TaskPriority.HIGH
        
        # Adjust duration based on complexity constraints
        if "complexity" in request.constraints:
            if "high" in request.constraints:
                for task in tasks:
                    task.estimated_duration = int(task.estimated_duration * 1.5)
        
        # Add specific requirements based on preferences
        if "specialist" in request.preferences:
            specialist = request.preferences["specialist"]
            for task in tasks:
                if "Consultation" in task.title or "Specialist" in task.title:
                    # Update resource requirements to match preferred specialist
                    for i, resource in enumerate(task.required_resources):
                        if resource.startswith("dr_"):
                            task.required_resources[i] = f"dr_{specialist.lower()}"
