"""
FastAPI Backend for Healthcare Planning Assistant
RESTful API endpoints for healthcare task planning
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.planner_agent import HealthcarePlannerAgent
from src.models import TaskStatus
from src.auth_models import User
from auth import router as auth_router, get_current_user, auth_manager
from doctors import router as doctors_router

# Initialize FastAPI app
app = FastAPI(
    title="Healthcare Planning Assistant API",
    description="RESTful API for healthcare task planning and scheduling",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routes as a proper router
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(doctors_router, tags=["doctors"])

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
    plan_id: Optional[str] = None
    goal: str
    total_duration: int
    tasks: List[TaskResponse]
    created_at: str

class ProgressResponse(BaseModel):
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    progress_percentage: float
    remaining_tasks: int

class ResourceInfo(BaseModel):
    name: str
    type: str
    capacity: int
    current_load: int
    utilization_percentage: float
    available: bool

# In-memory storage for plans (in production, use a database)
plans_storage: Dict[str, Any] = {}

@app.get("/", response_class=HTMLResponse)
async def root():
    """A friendly, aesthetic landing page for the local API server."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>Healthcare Planning Assistant</title>
      <style>
        * { box-sizing: border-box; }
        body {
          margin: 0; min-height: 100vh; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          color: #10233f; background: linear-gradient(135deg, #eef7ff 0%, #f7fbff 45%, #e9f8f2 100%);
          display: flex; align-items: center; justify-content: center; padding: 28px;
        }
        .shell { max-width: 980px; width: 100%; }
        .hero {
          position: relative; overflow: hidden; background: rgba(255,255,255,.88);
          border: 1px solid rgba(29, 111, 164, .14); border-radius: 28px;
          padding: 48px; box-shadow: 0 24px 70px rgba(28, 78, 121, .14);
          backdrop-filter: blur(12px);
        }
        .hero:before {
          content: ""; position:absolute; width:260px; height:260px; border-radius:50%;
          background:#d9f1ff; right:-100px; top:-120px; opacity:.8;
        }
        .brand { display:flex; align-items:center; gap:14px; position:relative; }
        .logo {
          width:58px; height:58px; border-radius:17px; display:grid; place-items:center;
          background:linear-gradient(135deg,#1677b8,#20a88a); color:white; font-size:30px;
          box-shadow:0 10px 24px rgba(22,119,184,.24);
        }
        h1 { margin:0; font-size:clamp(2rem,4vw,3.25rem); letter-spacing:-1.5px; }
        .subtitle { color:#55708f; font-size:1.05rem; line-height:1.7; max-width:680px; margin:20px 0 30px; }
        .status {
          display:inline-flex; align-items:center; gap:9px; padding:8px 13px; border-radius:999px;
          background:#e8f8ef; color:#167344; font-weight:700; font-size:.9rem;
        }
        .dot { width:9px; height:9px; border-radius:50%; background:#20b26b; box-shadow:0 0 0 5px rgba(32,178,107,.12); }
        .grid { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-top:30px; }
        .card { background:#fff; border:1px solid #e5edf5; border-radius:18px; padding:22px; }
        .icon { font-size:24px; }
        .card h3 { margin:10px 0 7px; font-size:1.05rem; }
        .card p { margin:0; color:#667d96; line-height:1.55; font-size:.93rem; }
        .actions { display:flex; flex-wrap:wrap; gap:12px; margin-top:30px; }
        .btn {
          text-decoration:none; padding:13px 19px; border-radius:12px; font-weight:700;
          display:inline-flex; align-items:center; gap:8px; transition:.18s ease;
        }
        .btn.primary { background:#126fb0; color:white; box-shadow:0 10px 20px rgba(18,111,176,.2); }
        .btn.secondary { background:#eef5fb; color:#16547e; }
        .btn:hover { transform:translateY(-2px); }
        .footer { margin-top:25px; color:#7b8fa4; font-size:.85rem; text-align:center; }
        code { background:#f1f5f9; padding:3px 7px; border-radius:6px; }
        @media (max-width:700px) { .hero { padding:30px 22px; } .grid { grid-template-columns:1fr; } }
      </style>
    </head>
    <body>
      <main class="shell">
        <section class="hero">
          <div class="brand">
            <div class="logo">🏥</div>
            <div>
              <div class="status"><span class="dot"></span> API is running</div>
            </div>
          </div>
          <h1 style="margin-top:18px;">Healthcare Planning Assistant</h1>
          <p class="subtitle">Your local FastAPI service for healthcare task planning, scheduling, progress tracking, authentication, resources, and doctor management.</p>
          <div class="grid">
            <article class="card"><div class="icon">⚡</div><h3>FastAPI Backend</h3><p>REST endpoints are ready on <code>localhost:8001</code>.</p></article>
            <article class="card"><div class="icon">📋</div><h3>Planning Engine</h3><p>Create structured healthcare plans and track task progress.</p></article>
            <article class="card"><div class="icon">👨‍⚕️</div><h3>Doctor Management</h3><p>Manage doctors and connect specialist resources to your application.</p></article>
          </div>
          <div class="actions">
            <a class="btn primary" href="http://localhost:8501" target="_blank">🚀 Open Healthcare App</a>
            <a class="btn secondary" href="/docs">📚 API Documentation</a>
            <a class="btn secondary" href="/health">💚 Health Check</a>
          </div>
          <div class="footer">Healthcare Planning Assistant · Local Development Server · v1.0.0</div>
        </section>
      </main>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/plan", response_model=ExecutionPlanResponse)
async def create_plan(
    request: PlanningRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Create a healthcare execution plan"""
    try:
        patient_info = {}
        if request.patient_info:
            patient_info = {
                "age": request.patient_info.age,
                "condition": request.patient_info.condition,
                "history": request.patient_info.history
            }

        plan = agent.process_request(
            goal=request.goal,
            patient_info=patient_info,
            constraints=request.constraints or [],
            preferences=request.preferences or {}
        )

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
            plan_id=plan_id,
            goal=plan.goal,
            total_duration=plan.total_duration,
            tasks=tasks_response,
            created_at=datetime.now().isoformat()
        )

        plans_storage[plan_id] = {
            "plan": plan,
            "response": response,
            "created_at": datetime.now()
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create plan: {str(e)}")

@app.get("/api/plan/{plan_id}/progress", response_model=ProgressResponse)
async def get_plan_progress(plan_id: str, current_user: User = Depends(get_current_user)):
    """Get progress information for one stored plan."""
    if plan_id not in plans_storage:
        raise HTTPException(status_code=404, detail="Plan not found")
    tasks = plans_storage[plan_id]["response"].tasks
    total = len(tasks)
    completed = sum(1 for task in tasks if task.status == "completed")
    in_progress = sum(1 for task in tasks if task.status == "in_progress")
    remaining = total - completed
    percentage = round((completed / total) * 100, 1) if total else 0.0
    return ProgressResponse(
        total_tasks=total,
        completed_tasks=completed,
        in_progress_tasks=in_progress,
        progress_percentage=percentage,
        remaining_tasks=remaining,
    )

@app.put("/api/plan/{plan_id}/task/{task_id}/status")
async def update_task_status(plan_id: str, task_id: str, status: str, current_user: User = Depends(get_current_user)):
    """Update a task status inside one stored plan."""
    if plan_id not in plans_storage:
        raise HTTPException(status_code=404, detail="Plan not found")
    try:
        task_status = TaskStatus(status.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    response = plans_storage[plan_id]["response"]
    for task in response.tasks:
        if task.id == task_id:
            task.status = task_status.value
            return {"success": True, "message": f"Task status updated to {status}"}
    raise HTTPException(status_code=404, detail="Task not found")

@app.get("/api/resources", response_model=List[ResourceInfo])
async def get_resources():
    """Get current resource utilization information"""
    try:
        utilization = agent.get_resource_utilization()
        resources = []

        for resource_id, info in utilization.items():
            resources.append(ResourceInfo(
                name=info["name"],
                type=info["type"],
                capacity=info["capacity"],
                current_load=info["current_load"],
                utilization_percentage=info["utilization_percentage"],
                available=info["available"]
            ))

        return resources

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get resources: {str(e)}")

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
                "created_at": plan_data["created_at"].isoformat(),
                "completed_tasks": sum(1 for t in plan_data["response"].tasks if t.status == "completed")
            })

        return {"plans": plans}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list plans: {str(e)}")

@app.get("/api/plan/{plan_id}/export")
async def export_plan(plan_id: str):
    """Export a plan to JSON format"""
    try:
        if plan_id not in plans_storage:
            raise HTTPException(status_code=404, detail="Plan not found")

        plan = plans_storage[plan_id]["plan"]
        filename = f"healthcare_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        export_data = {
            "goal": plan.goal,
            "total_duration": plan.total_duration,
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
                    "scheduled_time": plan.schedule.get(task.id, "").isoformat() if task.id in plan.schedule else None
                }
                for task in plan.tasks
            ],
            "exported_at": datetime.now().isoformat()
        }

        return {"filename": filename, "data": export_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export plan: {str(e)}")

@app.delete("/api/plan/{plan_id}")
async def delete_plan(plan_id: str):
    """Delete a specific plan"""
    try:
        if plan_id not in plans_storage:
            raise HTTPException(status_code=404, detail="Plan not found")

        del plans_storage[plan_id]
        return {"message": "Plan deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete plan: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
