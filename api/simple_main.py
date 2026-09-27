"""
Simple FastAPI Backend for Healthcare Planning Assistant
Basic version without authentication for testing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import asyncio
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.planner_agent import HealthcarePlannerAgent
from src.models import TaskStatus

# Initialize FastAPI app
app = FastAPI(
    title="Healthcare Planning Assistant API",
    description="RESTful API for healthcare task planning and scheduling",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global agent instance
agent = HealthcarePlannerAgent()

# Pydantic models for API
class PatientInfo(BaseModel):
    age: Optional[int] = None
    condition: Optional[str] = None
    history: Optional[str] = None

class PlanningRequest(BaseModel):
    goal: str = Field(..., description="Healthcare goal (e.g., 'Treatment Options')")
    patient_info: Optional[PatientInfo] = None
    constraints: Optional[List[str]] = []
    preferences: Optional[Dict[str, Any]] = {}

class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    priority: str
    status: str
    estimated_duration: int
    required_resources: List[str]
    dependencies: List[str]
    scheduled_time: Optional[str] = None

class ExecutionPlanResponse(BaseModel):
    goal: str
    total_duration: int
    tasks: List[TaskResponse]
    created_at: str

# In-memory storage for plans (in production, use database)
plans_storage = {}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Healthcare Planning Assistant API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/plan", response_model=ExecutionPlanResponse)
async def create_plan(request: PlanningRequest):
    """
    Create a healthcare execution plan
    
    Args:
        request: Planning request with goal, patient info, constraints, and preferences
    
    Returns:
        Execution plan with tasks and schedule
    """
    try:
        # Convert request to agent format
        patient_info = {}
        if request.patient_info:
            patient_info = {
                "age": request.patient_info.age,
                "condition": request.patient_info.condition,
                "history": request.patient_info.history
            }
        
        # Generate plan using agent
        plan = agent.process_request(
            goal=request.goal,
            patient_info=patient_info,
            constraints=request.constraints or [],
            preferences=request.preferences or {}
        )
        
        # Convert to response format
        plan_id = str(uuid.uuid4())
        tasks_response = []
        
        for task in plan.tasks:
            scheduled_time = None
            if task.id in plan.schedule:
                scheduled_time = plan.schedule[task.id].isoformat()
            
            tasks_response.append(TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                priority=task.priority.value,
                status=task.status.value,
                estimated_duration=task.estimated_duration,
                required_resources=task.required_resources,
                dependencies=task.dependencies,
                scheduled_time=scheduled_time
            ))
        
        response = ExecutionPlanResponse(
            goal=plan.goal,
            total_duration=plan.total_duration,
            tasks=tasks_response,
            created_at=datetime.now().isoformat()
        )
        
        # Store plan
        plans_storage[plan_id] = {
            "plan": plan,
            "response": response,
            "created_at": datetime.now()
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create plan: {str(e)}"
        )

@app.get("/api/plans")
async def list_plans():
    """List all created plans"""
    try:
        plans = []
        for plan_id, plan_data in plans_storage.items():
            plans.append({
                "id": plan_id,
                "goal": plan_data["response"].goal,
                "task_count": len(plan_data["response"].tasks),
                "total_duration": plan_data["response"].total_duration,
                "created_at": plan_data["created_at"].isoformat()
            })
        
        return {"plans": plans}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list plans: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
