"""
Authentication models for Healthcare Planning Assistant
User management and session handling
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import hashlib
import secrets
import json
import os

# Resolve the project root directory regardless of CWD
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@dataclass
class User:
    """User model for authentication"""
    id: str
    username: str
    email: str
    password_hash: str
    full_name: str
    role: str = "user"  # user, admin
    created_at: datetime = None
    last_login: Optional[datetime] = None
    is_active: bool = True

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "is_active": self.is_active
        }

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str) -> bool:
        """Verify password against hash"""
        return self.password_hash == self.hash_password(password)


@dataclass
class Session:
    """Session model for user authentication"""
    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    is_active: bool = True

    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.now() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
            "is_active": self.is_active
        }


class AuthManager:
    """Authentication manager for user and session management"""

    def __init__(self, data_file: str = None):
        # Default to project_root/data/users.json regardless of working directory
        if data_file is None:
            data_file = os.path.join(_PROJECT_ROOT, "data", "users.json")
        self.data_file = data_file
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self._load_data()

    def _load_data(self):
        """Load users and sessions from file"""
        try:
            data_dir = os.path.dirname(self.data_file)
            if data_dir:
                os.makedirs(data_dir, exist_ok=True)

            if os.path.exists(self.data_file):
                with open(self.data_file, "r") as f:
                    data = json.load(f)

                    # Load users
                    for user_id, user_data in data.get("users", {}).items():
                        try:
                            user_data["created_at"] = datetime.fromisoformat(user_data["created_at"])
                            if user_data.get("last_login"):
                                user_data["last_login"] = datetime.fromisoformat(user_data["last_login"])
                            # Skip users without password_hash (corrupted records)
                            if "password_hash" not in user_data or not user_data["password_hash"]:
                                print(f"Warning: User '{ user_data.get('username', user_id) }' has no password_hash - skipping. Run setup_admin.py to reset.")
                                continue
                            self.users[user_id] = User(**user_data)
                        except Exception as ue:
                            print(f"Warning: Failed to load user {user_id}: {ue}")

                    # Load sessions
                    for session_id, session_data in data.get("sessions", {}).items():
                        try:
                            session_data["created_at"] = datetime.fromisoformat(session_data["created_at"])
                            session_data["expires_at"] = datetime.fromisoformat(session_data["expires_at"])
                            self.sessions[session_id] = Session(**session_data)
                        except Exception as se:
                            print(f"Warning: Failed to load session {session_id}: {se}")
        except Exception as e:
            print(f"Error loading auth data: {e}")

    def _save_data(self):
        """Save users and sessions to file (including password_hash for persistence)"""
        try:
            users_data = {}
            for user_id, user in self.users.items():
                user_dict = user.to_dict()
                user_dict["password_hash"] = user.password_hash  # required for reload
                users_data[user_id] = user_dict

            data = {
                "users": users_data,
                "sessions": {sid: s.to_dict() for sid, s in self.sessions.items()}
            }

            with open(self.data_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving auth data: {e}")

    def create_user(self, username: str, email: str, password: str, full_name: str, role: str = "user") -> Optional[User]:
        """Create a new user"""
        for user in self.users.values():
            if user.username == username or user.email == email:
                return None

        user_id = secrets.token_hex(16)
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=User.hash_password(password),
            full_name=full_name,
            role=role
        )

        self.users[user_id] = user
        self._save_data()
        return user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        for user in self.users.values():
            if user.username == username and user.verify_password(password):
                user.last_login = datetime.now()
                self._save_data()
                return user
        return None

    def create_session(self, user: User) -> Session:
        """Create a new session for user"""
        self._cleanup_expired_sessions()

        session_id = secrets.token_hex(32)
        now = datetime.now()
        session = Session(
            session_id=session_id,
            user_id=user.id,
            created_at=now,
            expires_at=now + timedelta(hours=24)
        )

        self.sessions[session_id] = session
        self._save_data()
        return session

    def get_user_by_session(self, session_id: str) -> Optional[User]:
        """Get user by session ID"""
        session = self.sessions.get(session_id)
        if session and not session.is_expired():
            return self.users.get(session.user_id)

        if session and session.is_expired():
            del self.sessions[session_id]
            self._save_data()

        return None

    def logout(self, session_id: str):
        """Logout user by removing session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save_data()

    def _cleanup_expired_sessions(self):
        """Remove expired sessions"""
        expired = [sid for sid, s in self.sessions.items() if s.is_expired()]
        for sid in expired:
            del self.sessions[sid]

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.users.get(user_id)

    def update_user(self, user_id: str, **kwargs) -> bool:
        """Update user information"""
        if user_id not in self.users:
            return False

        user = self.users[user_id]
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        self._save_data()
        return True
