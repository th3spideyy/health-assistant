"""
Scheduler for Healthcare Planning Assistant
Optimizes task sequences and creates execution schedules
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .models import HealthcareTask, ExecutionPlan, TaskStatus
from .resource_manager import MockResourceManager

class HealthcareScheduler:
    """Optimizes and schedules healthcare tasks"""
    
    def __init__(self, resource_manager: MockResourceManager):
        self.resource_manager = resource_manager
    
    def create_optimal_schedule(self, tasks: List[HealthcareTask], start_time: datetime = None) -> ExecutionPlan:
        """Create an optimized execution schedule for tasks"""
        if start_time is None:
            start_time = datetime.now()
        
        # Sort tasks by priority and dependencies
        sorted_tasks = self._sort_tasks_by_priority_and_dependencies(tasks)
        
        # Create schedule respecting dependencies and resource availability
        schedule = {}
        current_time = start_time
        total_duration = 0
        
        for task in sorted_tasks:
            # Find the earliest time this task can start
            earliest_start = self._find_earliest_start_time(task, sorted_tasks, schedule, current_time)
            
            # Schedule the task
            schedule[task.id] = earliest_start
            end_time = earliest_start + timedelta(minutes=task.estimated_duration)
            
            # Update current time if this task extends the schedule
            if end_time > current_time + timedelta(minutes=total_duration):
                total_duration = int((end_time - start_time).total_seconds() / 60)
            
            # Reserve resources for this task
            for resource_id in task.required_resources:
                self.resource_manager.reserve_resource(resource_id)
        
        return ExecutionPlan(
            goal="Healthcare Task Execution",
            tasks=sorted_tasks,
            schedule=schedule,
            total_duration=total_duration
        )
    
    def _sort_tasks_by_priority_and_dependencies(self, tasks: List[HealthcareTask]) -> List[HealthcareTask]:
        """Sort tasks by priority while respecting dependencies"""
        # Create a map of task IDs to tasks
        task_map = {task.id: task for task in tasks}
        
        # Topological sort to respect dependencies
        sorted_tasks = []
        visited = set()
        temp_visited = set()
        
        def visit(task: HealthcareTask):
            if task.id in temp_visited:
                raise ValueError(f"Circular dependency detected involving task: {task.title}")
            
            if task.id not in visited:
                temp_visited.add(task.id)
                
                # Visit all dependencies first
                for dep_id in task.dependencies:
                    if dep_id in task_map:
                        visit(task_map[dep_id])
                
                temp_visited.remove(task.id)
                visited.add(task.id)
                sorted_tasks.append(task)
        
        # Visit all tasks
        for task in tasks:
            if task.id not in visited:
                visit(task)
        
        # Sort by priority within dependency constraints
        priority_order = {
            "urgent": 0,
            "high": 1,
            "medium": 2,
            "low": 3
        }
        
        sorted_tasks.sort(key=lambda t: priority_order[t.priority.value])
        
        return sorted_tasks
    
    def _find_earliest_start_time(self, task: HealthcareTask, all_tasks: List[HealthcareTask], schedule: Dict[str, datetime], current_time: datetime) -> datetime:
        """Find the earliest time a task can start based on dependencies and resource availability"""
        earliest_start = current_time
        
        # Check dependencies
        for dep_id in task.dependencies:
            dep_task = next((t for t in all_tasks if t.id == dep_id), None)
            if dep_task and dep_id in schedule:
                dep_end_time = schedule[dep_id] + timedelta(minutes=dep_task.estimated_duration)
                earliest_start = max(earliest_start, dep_end_time)
        
        # Check resource availability (simplified - assumes resources become available after previous tasks)
        for resource_id in task.required_resources:
            if not self.resource_manager.check_availability(resource_id):
                # If resource is not available, delay by 30 minutes (simplified)
                earliest_start += timedelta(minutes=30)
        
        return earliest_start
    
    def optimize_task_sequence(self, tasks: List[HealthcareTask]) -> List[HealthcareTask]:
        """Optimize task sequence for maximum efficiency"""
        # Group tasks by resource requirements to minimize resource switching
        optimized_tasks = []
        remaining_tasks = tasks.copy()
        
        while remaining_tasks:
            # Find tasks with no unmet dependencies
            ready_tasks = [t for t in remaining_tasks if all(dep_id in [opt.id for opt in optimized_tasks] for dep_id in t.dependencies)]
            
            if not ready_tasks:
                # If no ready tasks, there might be circular dependencies
                # Take the next highest priority task
                ready_tasks = [max(remaining_tasks, key=lambda t: self._get_priority_score(t))]
            
            # Sort ready tasks by resource efficiency
            ready_tasks.sort(key=lambda t: self._get_efficiency_score(t))
            
            # Take the most efficient ready task
            next_task = ready_tasks[0]
            optimized_tasks.append(next_task)
            remaining_tasks.remove(next_task)
        
        return optimized_tasks
    
    def _get_priority_score(self, task: HealthcareTask) -> int:
        """Get numeric priority score for sorting"""
        priority_scores = {
            "urgent": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }
        return priority_scores.get(task.priority.value, 0)
    
    def _get_efficiency_score(self, task: HealthcareTask) -> int:
        """Calculate efficiency score based on resource requirements and duration"""
        # Lower score is better (more efficient)
        resource_score = len(task.required_resources) * 10
        duration_score = task.estimated_duration
        return resource_score + duration_score
    
    def get_schedule_summary(self, plan: ExecutionPlan) -> str:
        """Generate a human-readable summary of the execution plan"""
        summary = f"Healthcare Execution Plan\n"
        summary += f"{'='*50}\n"
        summary += f"Total Duration: {plan.total_duration} minutes\n"
        summary += f"Number of Tasks: {len(plan.tasks)}\n\n"
        
        for task in plan.tasks:
            start_time = plan.schedule.get(task.id, datetime.now())
            end_time = start_time + timedelta(minutes=task.estimated_duration)
            
            summary += f"Task: {task.title}\n"
            summary += f"  Priority: {task.priority.value.upper()}\n"
            summary += f"  Duration: {task.estimated_duration} minutes\n"
            summary += f"  Start: {start_time.strftime('%H:%M')}\n"
            summary += f"  End: {end_time.strftime('%H:%M')}\n"
            summary += f"  Resources: {', '.join(task.required_resources)}\n"
            if task.dependencies:
                summary += f"  Dependencies: {len(task.dependencies)} task(s)\n"
            summary += "\n"
        
        return summary
