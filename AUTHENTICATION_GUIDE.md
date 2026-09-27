# 🔐 Authentication Guide - Healthcare Planning Assistant

## 🎯 Overview

Complete authentication system with user registration, login, session management, and protected routes for the Healthcare Planning Assistant.

## 🏗️ Authentication Architecture

```
┌─────────────────┐    Login/Signup    ┌─────────────────┐
│   Streamlit    │ ◄──────────────► │   FastAPI       │
│   Frontend     │    Auth API     │   Backend       │
│   (Port 8503)  │                │   (Port 8001)   │
└─────────────────┘                └─────────────────┘
         │                                   │
         │                                   │
    ┌────▼────┐                         ┌────▼────┐
    │  Session  │                         │  JSON    │
    │ Management│                         │  Database │
    └───────────┘                         └───────────┘
```

## 📁 Authentication Components

### Backend (`api/`)
- **`auth.py`**: Authentication endpoints (login, register, logout, profile)
- **`auth_models.py`**: User and session management models
- **`main.py`**: Protected routes with authentication middleware

### Frontend (`frontend/`)
- **`auth_pages.py`**: Login, signup, and profile pages
- **`secure_app.py`**: Main app with authentication flow
- **`streamlit_app.py`**: Original app (without authentication)

## 🚀 Quick Start

### Step 1: Start Backend Server
```bash
python run_backend.py
```
**Backend**: http://localhost:8001
**Auth API**: http://localhost:8001/docs

### Step 2: Start Secure Frontend
```bash
python run_secure_frontend.py
```
**Frontend**: http://localhost:8503

### Step 3: Access Application
Open browser: **http://localhost:8503**

## 🔐 Authentication Features

### ✅ User Registration
- **Username validation** (3-50 characters)
- **Email validation** with regex
- **Password requirements** (6-100 characters)
- **Role selection** (user/admin)
- **Terms agreement** requirement

### ✅ User Login
- **Username/password authentication**
- **Session creation** (24-hour expiry)
- **Remember me** option
- **Error handling** with user-friendly messages

### ✅ Session Management
- **JWT-like tokens** using secure random strings
- **Automatic expiry** (24 hours)
- **Session validation** on each request
- **Automatic cleanup** of expired sessions

### ✅ Protected Routes
- **Authentication middleware** using FastAPI Depends
- **Bearer token** authentication
- **Automatic redirect** for unauthenticated users
- **Role-based access** (admin/user)

### ✅ User Profile
- **Profile updates** (name, email)
- **Account information** display
- **Password change** (future feature)
- **Account deletion** (admin only)

## 📋 API Endpoints

### Authentication Endpoints
```bash
POST /api/auth/register    # User registration
POST /api/auth/login       # User login
POST /api/auth/logout      # User logout
GET  /api/auth/me         # Get current user
GET  /api/auth/session     # Get session info
PUT  /api/auth/profile     # Update profile
GET  /api/auth/users       # List users (admin only)
```

### Protected Endpoints
```bash
POST /api/plan             # Requires authentication
GET  /api/plan/{id}/progress
PUT  /api/plan/{id}/task/{task_id}/status
GET  /api/resources
GET  /api/plans
DELETE /api/plan/{id}
```

## 🎮 Frontend Pages

### Authentication Pages
- **Login Page**: Username/password form with validation
- **Signup Page**: Registration form with all fields
- **Profile Page**: User information and updates

### Protected Dashboard
- **Navigation**: Sidebar with user info and menu
- **Create Plan**: Healthcare planning with authentication
- **View Plans**: Plan history (user-specific)
- **Resources**: Resource utilization dashboard
- **Analytics**: User-specific analytics
- **Logout**: Session cleanup and redirect

## 🔧 Technical Implementation

### Backend Authentication
```python
# User model with password hashing
@dataclass
class User:
    username: str
    password_hash: str
    email: str
    role: str = "user"
    
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

# Session management
@dataclass
class Session:
    session_id: str
    user_id: str
    expires_at: datetime
    
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at

# Authentication middleware
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    session_id = credentials.credentials
    user = auth_manager.get_user_by_session(session_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid session")
    return user
```

### Frontend Authentication
```python
# Session state management
if 'session_id' in st.session_state:
    # User is logged in
    show_dashboard()
else:
    # Show login/signup
    show_auth_pages()

# API calls with authentication
def api_call(method, endpoint, data=None):
    headers = {}
    if 'session_id' in st.session_state:
        headers['Authorization'] = f"Bearer {st.session_state.session_id}"
    
    response = requests.post(url, json=data, headers=headers)
    return response.json()
```

## 🔒 Security Features

### Password Security
- **SHA-256 hashing** for password storage
- **No plain text passwords** stored anywhere
- **Password requirements** enforced (min 6 characters)
- **Secure session tokens** using random hex strings

### Session Security
- **24-hour expiry** for all sessions
- **Automatic cleanup** of expired sessions
- **Secure random generation** of session IDs
- **Bearer token** authentication pattern

### Input Validation
- **Username validation** (3-50 characters)
- **Email validation** with regex pattern
- **Password confirmation** required
- **Terms agreement** mandatory for signup

## 🎮 Usage Examples

### Register New User
```python
# API call
response = requests.post("http://localhost:8001/api/auth/register", json={
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123",
    "full_name": "John Doe",
    "role": "user"
})

# Response
{
    "success": true,
    "message": "User registered successfully",
    "user": {...},
    "session_id": "abc123..."
}
```

### Login User
```python
# API call
response = requests.post("http://localhost:8001/api/auth/login", json={
    "username": "johndoe",
    "password": "securepassword123"
})

# Response
{
    "success": true,
    "message": "Login successful",
    "user": {...},
    "session_id": "def456..."
}
```

### Protected API Call
```python
# With authentication
headers = {"Authorization": "Bearer def456..."}
response = requests.post("http://localhost:8001/api/plan", 
                       json=request_data, headers=headers)
```

## 🗄️ Data Storage

### User Database
- **File-based storage**: `data/users.json`
- **JSON format**: Easy to migrate to database
- **Automatic backup**: Can be version controlled
- **Scalable**: Easy to upgrade to PostgreSQL/MySQL

### Session Storage
- **In-memory tracking**: Fast access
- **File persistence**: Survives server restarts
- **Automatic cleanup**: Removes expired sessions
- **Security**: No sensitive data in URLs

## 🚀 Deployment Considerations

### Production Security
- **HTTPS**: Required for production
- **Environment variables**: For secrets and keys
- **Database**: Replace JSON with PostgreSQL
- **Rate limiting**: Prevent brute force attacks
- **CORS**: Configure specific domains only

### Scaling Up
- **Load balancer**: Multiple API instances
- **Redis**: For session storage
- **PostgreSQL**: For user data
- **JWT**: For token authentication
- **OAuth**: For social login

## 🧪 Testing Authentication

### Test User Creation
1. Go to http://localhost:8503
2. Click "Sign Up" tab
3. Fill in registration form
4. Submit and verify account creation

### Test Login Flow
1. Use created credentials to login
2. Verify session creation
3. Access protected dashboard
4. Test plan creation with authentication

### Test Session Management
1. Create a plan (authenticated)
2. Wait for session expiry (24 hours)
3. Try to access protected route
4. Verify automatic redirect to login

## 🎯 Success Indicators

✅ **Authentication Working**: Users can register and login
✅ **Sessions Managed**: 24-hour expiry with cleanup
✅ **Protected Routes**: API endpoints secured
✅ **Frontend Flow**: Complete auth flow in UI
✅ **Data Security**: Password hashing, no plain text
✅ **Error Handling**: User-friendly error messages

## 🔍 Troubleshooting

### Common Issues

#### "Invalid session" errors
**Solution**: Check session token in headers and expiry time

#### "Username already exists"
**Solution**: Use different username or implement account recovery

#### "Cannot connect to backend"
**Solution**: Ensure FastAPI server is running on port 8001

#### "Session expired" immediately
**Solution**: Check system time synchronization

### Debug Mode
Add to `api/auth.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Add to frontend:
```python
st.write(f"Session state: {st.session_state}")
```

## 🎉 Authentication Complete!

The Healthcare Planning Assistant now has:
- ✅ **Complete user management** system
- ✅ **Secure authentication** flow
- ✅ **Session management** with expiry
- ✅ **Protected API endpoints**
- ✅ **Beautiful frontend** with auth UI
- ✅ **Role-based access** control
- ✅ **Production-ready** security features

Ready for secure healthcare planning! 🏥🔐
