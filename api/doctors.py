"""Doctor directory API for the Healthcare Planning Assistant."""
import json
import os
import re
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.auth_models import User
from auth import get_current_user

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(ROOT, "data", "doctors.json")
router = APIRouter()

DEFAULT_DOCTORS = [
    {"id": "dr_smith", "name": "Dr. Smith", "specialization": "Cardiologist", "email": "dr.smith@hospital.local", "phone": "", "available": True},
    {"id": "dr_jones", "name": "Dr. Jones", "specialization": "General Practitioner", "email": "dr.jones@hospital.local", "phone": "", "available": True},
    {"id": "dr_wilson", "name": "Dr. Wilson", "specialization": "Neurologist", "email": "dr.wilson@hospital.local", "phone": "", "available": True},
]

class DoctorCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    specialization: str = Field(..., min_length=2, max_length=100)
    email: Optional[str] = ""
    phone: Optional[str] = ""
    available: bool = True

class DoctorResponse(DoctorCreate):
    id: str


def _ensure_file():
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DOCTORS, f, indent=2)


def _load() -> list:
    _ensure_file()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return list(DEFAULT_DOCTORS)


def _save(doctors: list):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(doctors, f, indent=2)


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or uuid.uuid4().hex[:8]


def _admin(user: User):
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")


@router.get("/api/doctors", response_model=List[DoctorResponse])
async def list_doctors(current_user: User = Depends(get_current_user)):
    return _load()


@router.post("/api/doctors", response_model=DoctorResponse, status_code=201)
async def add_doctor(doctor: DoctorCreate, current_user: User = Depends(get_current_user)):
    _admin(current_user)
    doctors = _load()
    doctor_id = _slug(doctor.name)
    existing_ids = {d.get("id") for d in doctors}
    if doctor_id in existing_ids:
        doctor_id = f"{doctor_id}_{uuid.uuid4().hex[:6]}"
    item = {"id": doctor_id, **doctor.model_dump()}
    doctors.append(item)
    _save(doctors)
    return item


@router.put("/api/doctors/{doctor_id}", response_model=DoctorResponse)
async def update_doctor(doctor_id: str, doctor: DoctorCreate, current_user: User = Depends(get_current_user)):
    _admin(current_user)
    doctors = _load()
    for i, existing in enumerate(doctors):
        if existing.get("id") == doctor_id:
            item = {"id": doctor_id, **doctor.model_dump()}
            doctors[i] = item
            _save(doctors)
            return item
    raise HTTPException(status_code=404, detail="Doctor not found")


@router.delete("/api/doctors/{doctor_id}")
async def delete_doctor(doctor_id: str, current_user: User = Depends(get_current_user)):
    _admin(current_user)
    doctors = _load()
    remaining = [d for d in doctors if d.get("id") != doctor_id]
    if len(remaining) == len(doctors):
        raise HTTPException(status_code=404, detail="Doctor not found")
    _save(remaining)
    return {"success": True, "message": "Doctor removed"}
