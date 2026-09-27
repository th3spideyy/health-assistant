"""
Healthcare Planning Assistant Agent
Main agent class that orchestrates complex healthcare tasks through multi-step reasoning
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from .models import PlanningRequest, ExecutionPlan, HealthcareTask, TaskStatus
from .task_decomposer import HealthcareTaskDecomposer
from .resource_manager import MockResourceManager
from .scheduler import HealthcareScheduler

class HealthcarePlannerAgent:
    """
    Sophisticated Healthcare Planning Assistant Agent
    
    This agent orchestrates complex healthcare tasks through a multi-step reasoning loop:
    1. Receives high-level goal (e.g., 'Treatment Options')
    2. Decomposes objective into actionable steps
    3. Validates resource availability through mock interface tools
    4. Generates detailed execution schedule
    5. Handles dependencies and optimizes task sequences
    """
    
    def __init__(self):
        """Initialize the Healthcare Planner Agent"""
        self.resource_manager = MockResourceManager()
        self.task_decomposer = HealthcareTaskDecomposer()
        self.scheduler = HealthcareScheduler(self.resource_manager)
        self.current_plan = None
        self.execution_history = []
        
        print("🏥 Healthcare Planning Assistant Agent initialized")
        print("Ready to assist with complex healthcare task planning!")
    
    def process_request(self, goal: str, patient_info: Dict[str, Any] = None, 
                       constraints: List[str] = None, preferences: Dict[str, Any] = None) -> ExecutionPlan:
        """
        Process a healthcare planning request through multi-step reasoning
        
        Args:
            goal: High-level healthcare goal (e.g., 'Treatment Options')
            patient_info: Patient-specific information
            constraints: Any constraints or limitations
            preferences: Patient preferences or special requirements
            
        Returns:
            Detailed execution plan with optimized schedule
        """
        print(f"\n🎯 Processing Healthcare Request: {goal}")
        print("=" * 60)
        
        # Step 1: Create planning request
        request = PlanningRequest(
            goal=goal,
            patient_info=patient_info or {},
            constraints=constraints or [],
            preferences=preferences or {}
        )
        
        # Step 2: Decompose goal into actionable tasks
        print("📋 Step 1: Decomposing goal into actionable tasks...")
        tasks = self.task_decomposer.decompose_goal(request)
        print(f"   Generated {len(tasks)} tasks")
        
        # Step 3: Validate resource availability
        print("🔍 Step 2: Validating resource availability...")
        validation_results = self._validate_task_resources(tasks)
        self._display_validation_results(validation_results)
        
        # Step 4: Optimize task sequence
        print("⚡ Step 3: Optimizing task sequence...")
        optimized_tasks = self.scheduler.optimize_task_sequence(tasks)
        print(f"   Optimized task order for maximum efficiency")
        
        # Step 5: Create execution schedule
        print("📅 Step 4: Generating execution schedule...")
        execution_plan = self.scheduler.create_optimal_schedule(optimized_tasks)
        self.current_plan = execution_plan
        
        # Step 6: Display results
        print("✅ Step 5: Planning complete!")
        print(self.scheduler.get_schedule_summary(execution_plan))
        
        # Store in execution history
        self.execution_history.append({
            "timestamp": datetime.now(),
            "goal": goal,
            "plan": execution_plan
        })
        
        return execution_plan
    
    def _validate_task_resources(self, tasks: List[HealthcareTask]) -> Dict[str, Dict[str, bool]]:
        """Validate resource availability for all tasks"""
        validation_results = {}
        
        for task in tasks:
            task_validation = {}
            for resource_id in task.required_resources:
                task_validation[resource_id] = self.resource_manager.check_availability(resource_id)
            validation_results[task.id] = task_validation
        
        return validation_results
    
    def _display_validation_results(self, validation_results: Dict[str, Dict[str, bool]]):
        """Display resource validation results in a user-friendly way"""
        print("   Resource Validation Results:")
        
        all_available = True
        for task_id, resources in validation_results.items():
            for resource_id, available in resources.items():
                status = "✅" if available else "❌"
                resource_name = self.resource_manager.get_resource_info(resource_id)
                name = resource_name.name if resource_name else resource_id
                print(f"   {status} {name}")
                if not available:
                    all_available = False
        
        if all_available:
            print("   ✅ All required resources are available!")
        else:
            print("   ⚠️  Some resources may not be available - schedule adjusted accordingly")
    
    def get_current_plan(self) -> Optional[ExecutionPlan]:
        """Get the current execution plan"""
        return self.current_plan
    
    def update_task_status(self, task_id: str, status: TaskStatus):
        """Update the status of a specific task"""
        if self.current_plan:
            for task in self.current_plan.tasks:
                if task.id == task_id:
                    task.status = status
                    print(f"📝 Task '{task.title}' status updated to: {status.value}")
                    return True
        return False
    
    def get_task_progress(self) -> Dict[str, Any]:
        """Get progress information for the current plan"""
        if not self.current_plan:
            return {"message": "No active plan"}
        
        total_tasks = len(self.current_plan.tasks)
        completed_tasks = sum(1 for task in self.current_plan.tasks if task.status == TaskStatus.COMPLETED)
        in_progress_tasks = sum(1 for task in self.current_plan.tasks if task.status == TaskStatus.IN_PROGRESS)
        
        progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "progress_percentage": progress_percentage,
            "remaining_tasks": total_tasks - completed_tasks - in_progress_tasks
        }
    
    def get_resource_utilization(self) -> Dict[str, Any]:
        """Get current resource utilization information"""
        resources = self.resource_manager.list_all_resources()
        utilization = {}
        
        for resource_id, resource in resources.items():
            utilization[resource_id] = {
                "name": resource.name,
                "type": resource.type.value,
                "capacity": resource.capacity,
                "current_load": resource.current_load,
                "utilization_percentage": (resource.current_load / resource.capacity) * 100 if resource.capacity > 0 else 0,
                "available": resource.is_available()
            }
        
        return utilization
    
    def export_plan(self, filename: str = None) -> str:
        """Export the current plan to JSON format"""
        if not self.current_plan:
            return "No active plan to export"
        
        if filename is None:
            filename = f"healthcare_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        plan_data = {
            "goal": self.current_plan.goal,
            "total_duration": self.current_plan.total_duration,
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority.value,
                    "status": task.status.value,
                    "estimated_duration": task.estimated_duration,
                    "required_resources": task.required_resources,
                    "dependencies": task.dependencies,
                    "scheduled_time": self.current_plan.schedule.get(task.id, "").isoformat() if task.id in self.current_plan.schedule else None
                }
                for task in self.current_plan.tasks
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(plan_data, f, indent=2)
        
        return f"Plan exported to {filename}"
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get the history of all executed plans"""
        return [
            {
                "timestamp": entry["timestamp"].isoformat(),
                "goal": entry["goal"],
                "task_count": len(entry["plan"].tasks),
                "total_duration": entry["plan"].total_duration
            }
            for entry in self.execution_history
        ]
