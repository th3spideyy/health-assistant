"""
Complete Healthcare Workflow API
Implements the full process flow with authentication, data collection, AI processing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from src.healthcare_workflow import HealthcareWorkflowEngine

# Initialize workflow engine
workflow_engine = HealthcareWorkflowEngine()

# Create FastAPI app
app = FastAPI(
    title="Healthcare Workflow API",
    description="Complete healthcare process flow from authentication to AI recommendations",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"] ,
)

# Root endpoint - avoids a 404 when opening the backend URL directly
@app.get("/")
async def root():
    return {
        "status": "running",
        "service": "Healthcare Workflow API",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Pydantic models
class LoginCredentials(BaseModel):
    username: str
    password: str

class SignupCredentials(BaseModel):
    username: str
    email: str
    password: str
    full_name: str

class PatientDataInput(BaseModel):
    medical_history: Dict[str, Any] = Field(default_factory=dict)
    symptoms: List[str] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    allergies: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    emergency_contact: Dict[str, str] = Field(default_factory=dict)
    insurance_info: Dict[str, str] = Field(default_factory=dict)

class FollowUpSchedule(BaseModel):
    date: str
    reminders: Dict[str, Any] = Field(default_factory=dict)

# Step 1: Application Start & Authentication
@app.post("/api/workflow/start")
async def start_application(user_data: Dict[str, str]):
    """Start new healthcare workflow session"""
    try:
        user_id = user_data.get("user_id")
        if not user_id:
            raise HTTPException(status_code=422, detail="user_id field is required")
        
        session = workflow_engine.start_application(user_id)
        return {
            "session_id": session.session_id,
            "access_token": session.access_token,
            "status": session.status,
            "message": "Application started successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start application: {str(e)}")

@app.post("/api/workflow/signup")
async def signup_user(credentials: SignupCredentials):
    """Register new user account"""
    try:
        # Mock user registration (in real system, use database)
        user_id = f"user_{credentials.username}_{int(datetime.now().timestamp())}"
        
        return {
            "success": True,
            "user_id": user_id,
            "message": "Account created successfully. Please login to continue."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

@app.post("/api/workflow/authenticate")
async def authenticate_user(session_id: str, credentials: LoginCredentials):
    """Authenticate user and verify identity"""
    try:
        success = workflow_engine.authenticate_user(session_id, credentials.dict())
        
        if success:
            access_token = workflow_engine.generate_access_token(session_id)
            return {
                "success": True,
                "access_token": access_token,
                "message": "Authentication successful"
            }
        else:
            return {
                "success": False,
                "message": "Authentication failed. Please retry login."
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

@app.post("/api/workflow/authenticate-body")
async def authenticate_user_body(auth_data: Dict[str, Any]):
    """Authenticate user and verify identity (body version)"""
    try:
        session_id = auth_data.get("session_id")
        credentials = auth_data.get("credentials")
        
        if not session_id or not credentials:
            raise HTTPException(status_code=422, detail="session_id and credentials are required")
        
        success = workflow_engine.authenticate_user(session_id, credentials)
        
        if success:
            access_token = workflow_engine.generate_access_token(session_id)
            return {
                "success": True,
                "access_token": access_token,
                "message": "Authentication successful"
            }
        else:
            return {
                "success": False,
                "message": "Authentication failed. Please retry login."
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

# Step 2: Data Collection
@app.post("/api/workflow/collect-data")
async def collect_patient_data(request_data: Dict[str, Any]):
    """Collect and validate patient data"""
    try:
        session_id = request_data.get("session_id")
        patient_data = request_data.get("patient_data")
        
        if not session_id or not patient_data:
            raise HTTPException(status_code=422, detail="session_id and patient_data are required")
        
        result = workflow_engine.collect_patient_data(session_id, patient_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data collection error: {str(e)}")

@app.put("/api/workflow/update-data")
async def update_patient_data(request_data: Dict[str, Any]):
    """Update incomplete patient data"""
    try:
        session_id = request_data.get("session_id")
        updates = request_data.get("updates")
        
        if not session_id or not updates:
            raise HTTPException(status_code=422, detail="session_id and updates are required")
        
        result = workflow_engine.update_patient_data(session_id, updates)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data update error: {str(e)}")

# Step 3: AI Processing
@app.post("/api/workflow/analyze")
async def analyze_patient_profile(request_data: Dict[str, str]):
    """Run AI recommendation engine on patient profile"""
    try:
        session_id = request_data.get("session_id")
        
        if not session_id:
            raise HTTPException(status_code=422, detail="session_id is required")
        
        result = workflow_engine.analyze_patient_profile(session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis error: {str(e)}")

# Step 4: Post-Recommendation Process
@app.post("/api/workflow/schedule-followup")
async def schedule_follow_up(request_data: Dict[str, Any]):
    """Schedule follow-up appointments and reminders"""
    try:
        session_id = request_data.get("session_id")
        schedule = request_data.get("schedule")
        
        if not session_id or not schedule:
            raise HTTPException(status_code=422, detail="session_id and schedule are required")
        
        result = workflow_engine.schedule_follow_up(session_id, schedule)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheduling error: {str(e)}")

@app.post("/api/workflow/send-recommendations")
async def send_recommendations(request_data: Dict[str, Any]):
    """Send recommendations to user"""
    try:
        session_id = request_data.get("session_id")
        delivery_method = request_data.get("delivery_method", "email")
        
        if not session_id:
            raise HTTPException(status_code=422, detail="session_id is required")
        
        result = workflow_engine.send_recommendations(session_id, delivery_method)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delivery error: {str(e)}")

# Step 5: Process Completion
@app.post("/api/workflow/logout")
async def logout_user(request_data: Dict[str, str]):
    """Complete workflow and logout user"""
    try:
        session_id = request_data.get("session_id")
        
        if not session_id:
            raise HTTPException(status_code=422, detail="session_id is required")
        
        result = workflow_engine.logout_user(session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Logout error: {str(e)}")

# Additional endpoints for monitoring
@app.get("/api/workflow/session/{session_id}")
async def get_session_status(session_id: str):
    """Get current session status and progress"""
    try:
        session = workflow_engine.active_sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "status": session.status,
            "last_activity": session.last_activity.isoformat(),
            "has_patient_data": session.patient_data is not None,
            "has_recommendation": session.recommendation is not None,
            "activity_count": len(session.audit_log)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session error: {str(e)}")

@app.get("/api/workflow/audit/{session_id}")
async def get_audit_log(session_id: str):
    """Get audit log for a session"""
    try:
        session = workflow_engine.active_sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": session.session_id,
            "audit_log": session.audit_log,
            "total_activities": len(session.audit_log)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audit error: {str(e)}")

@app.get("/api/workflow/recommendation/{recommendation_id}")
async def get_recommendation_details(recommendation_id: str):
    """Get detailed recommendation information"""
    try:
        recommendation = workflow_engine.recommendation_cache.get(recommendation_id)
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        return {
            "recommendation_id": recommendation.recommendation_id,
            "patient_id": recommendation.patient_id,
            "treatment_plan": recommendation.treatment_plan,
            "specialist_match": recommendation.specialist_match,
            "safety_score": recommendation.safety_score,
            "compliance_score": recommendation.compliance_score,
            "requires_manual_review": recommendation.requires_manual_review,
            "clinical_guidelines": recommendation.clinical_guidelines,
            "generated_at": recommendation.generated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation error: {str(e)}")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(workflow_engine.active_sessions),
        "patient_records": len(workflow_engine.patient_database),
        "recommendations": len(workflow_engine.recommendation_cache)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
