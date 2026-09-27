"""
Authentication API endpoints for Healthcare Planning Assistant
User registration, login, logout, and session management
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

from src.auth_models import AuthManager, User, Session

# Shared auth manager singleton
auth_manager = AuthManager()

# Create auth router (NOT a standalone FastAPI app)
router = APIRouter()

# Security scheme
security = HTTPBearer(auto_error=False)

# ---------------------------------------------------------------------------
# Pydantic models for requests/responses
# ---------------------------------------------------------------------------

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., min_length=6, max_length=100, description="Password")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name")
    role: str = Field(default="user", description="User role")

class UserLogin(BaseModel):
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: str
    role: str
    created_at: str
    last_login: Optional[str] = None
    is_active: bool

class LoginResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None
    session_id: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    user: UserResponse
    expires_at: str


# ---------------------------------------------------------------------------
# Shared dependency: get current user from Bearer token
# ---------------------------------------------------------------------------

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[User]:
    """Get current user from session token"""
    if not credentials or not credentials.credentials:
        return None

    session_id = credentials.credentials
    user = auth_manager.get_user_by_session(session_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


# ---------------------------------------------------------------------------
# Authentication endpoints
# ---------------------------------------------------------------------------

@router.post("/register", response_model=LoginResponse)
async def register(user_data: UserRegister):
    """Register a new user"""
    try:
        for existing_user in auth_manager.users.values():
            if existing_user.username == user_data.username:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
            if existing_user.email == user_data.email:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

        user = auth_manager.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name,
            role=user_data.role
        )

        if not user:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create user")

        session = auth_manager.create_session(user)

        return LoginResponse(
            success=True,
            message="User registered successfully",
            user=UserResponse(**user.to_dict()),
            session_id=session.session_id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Registration failed: {str(e)}")


@router.post("/login", response_model=LoginResponse)
async def login(user_data: UserLogin):
    """Authenticate user and create session"""
    try:
        user = auth_manager.authenticate_user(user_data.username, user_data.password)

        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

        session = auth_manager.create_session(user)

        return LoginResponse(
            success=True,
            message="Login successful",
            user=UserResponse(**user.to_dict()),
            session_id=session.session_id
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Login failed: {str(e)}")


@router.post("/logout")
async def logout(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Logout user by invalidating session"""
    try:
        if not credentials or not credentials.credentials:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No session provided")

        auth_manager.logout(credentials.credentials)
        return {"success": True, "message": "Logout successful"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Logout failed: {str(e)}")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse(**current_user.to_dict())


@router.get("/session", response_model=SessionResponse)
async def get_session_info(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Get current session information"""
    try:
        if not credentials or not credentials.credentials:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No session provided")

        session_id = credentials.credentials
        session = auth_manager.sessions.get(session_id)
        user = auth_manager.get_user_by_session(session_id)

        if not session or not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")

        return SessionResponse(
            session_id=session.session_id,
            user=UserResponse(**user.to_dict()),
            expires_at=session.expires_at.isoformat()
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to get session info: {str(e)}")


@router.put("/profile", response_model=UserResponse)
async def update_profile(profile_data: dict, current_user: User = Depends(get_current_user)):
    """Update user profile"""
    try:
        allowed_fields = ['full_name', 'email']
        update_data = {k: v for k, v in profile_data.items() if k in allowed_fields}

        if 'email' in update_data:
            for user in auth_manager.users.values():
                if user.id != current_user.id and user.email == update_data['email']:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

        success = auth_manager.update_user(current_user.id, **update_data)

        if not success:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update profile")

        updated_user = auth_manager.get_user_by_id(current_user.id)
        return UserResponse(**updated_user.to_dict())

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Profile update failed: {str(e)}")


@router.get("/users", response_model=List[UserResponse])
async def list_users(current_user: User = Depends(get_current_user)):
    """List all users (admin only)"""
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

        return [UserResponse(**user.to_dict()) for user in auth_manager.users.values()]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to list users: {str(e)}")
