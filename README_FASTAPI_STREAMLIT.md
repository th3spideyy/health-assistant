# 🏥 Healthcare Planning Assistant - FastAPI + Streamlit

## 🎯 Overview

Modern web-based Healthcare Planning Assistant with **FastAPI backend** and **Streamlit frontend**. This architecture provides a scalable, production-ready solution with RESTful API and beautiful web interface.

## 🏗️ Architecture

```
┌─────────────────┐    HTTP API    ┌─────────────────┐
│   Streamlit     │ ◄──────────────► │    FastAPI      │
│   Frontend      │                │    Backend      │
│   (Port 8501)   │                │   (Port 8000)   │
└─────────────────┘                └─────────────────┘
         │                                   │
         │                                   │
    ┌────▼────┐                         ┌────▼────┐
    │  User   │                         │ Healthcare│
    │Interface│                         │ Planning │
    │         │                         │  Agent   │
    └─────────┘                         └─────────┘
```

## 🚀 Quick Start

### Step 1: Start Backend Server
```bash
python run_backend.py
```
This will start the FastAPI server at `http://localhost:8000`

### Step 2: Start Frontend (in new terminal)
```bash
python run_frontend.py
```
This will start the Streamlit frontend at `http://localhost:8501`

### Step 3: Access the Application
Open your browser and go to `http://localhost:8501`

## 📁 Project Structure

```
healthcare-planning-assistant/
├── api/                          # FastAPI Backend
│   ├── main.py                   # Main FastAPI application
│   └── requirements.txt          # Backend dependencies
├── frontend/                     # Streamlit Frontend
│   ├── streamlit_app.py          # Main Streamlit application
│   └── requirements.txt          # Frontend dependencies
├── src/                          # Core Healthcare Planning Logic
│   ├── planner_agent.py           # Main planning agent
│   ├── models.py                 # Data models
│   ├── task_decomposer.py        # Task decomposition
│   ├── resource_manager.py       # Resource management
│   └── scheduler.py             # Scheduling logic
├── run_backend.py               # Backend launcher
├── run_frontend.py              # Frontend launcher
└── README_FASTAPI_STREAMLIT.md  # This file
```

## 🔧 API Endpoints

### Core Planning
- `POST /api/plan` - Create healthcare plan
- `GET /api/plan/{plan_id}/progress` - Get plan progress
- `PUT /api/plan/{plan_id}/task/{task_id}/status` - Update task status
- `GET /api/plans` - List all plans
- `DELETE /api/plan/{plan_id}` - Delete plan

### Resources
- `GET /api/resources` - Get resource utilization

### System
- `GET /` - API info
- `GET /health` - Health check

## 🖥️ Frontend Features

### 📋 Create Plan Page
- **Intuitive Forms**: Dropdown menus and input fields
- **Real-time Validation**: Input validation and error handling
- **Progress Tracking**: Live updates during plan generation
- **Visual Task Display**: Priority-based task cards

### 📚 View Plans Page
- **Plan History**: Table of all created plans
- **Detailed View**: Expandable task information
- **Status Management**: Update task progress
- **Export Functionality**: JSON export capability

### 🏥 Resources Page
- **Utilization Dashboard**: Visual resource charts
- **Real-time Status**: Current availability
- **Resource Details**: Capacity and load information
- **Type Filtering**: Group by resource type

### 📈 Analytics Page
- **Planning Metrics**: Key performance indicators
- **Visual Charts**: Duration distribution, task complexity
- **Historical Data**: Trends and patterns
- **Summary Statistics**: Comprehensive analytics

## 🎮 Usage Example

### 1. Create a Healthcare Plan
1. Navigate to **Create Plan** page
2. Fill in patient information:
   - Goal: "Treatment Options"
   - Age: 72
   - Condition: "Chest pain"
   - Constraints: "Limited Mobility"
   - Specialist: "Cardiologist"
3. Click **🚀 Generate Plan**

### 2. Review Generated Plan
- View task breakdown with priorities
- Check resource assignments
- Review schedule and dependencies
- Update task progress as needed

### 3. Monitor Resources
- Go to **Resources** page
- View utilization charts
- Check resource availability
- Monitor capacity usage

### 4. Analyze Performance
- Visit **Analytics** page
- Review planning metrics
- Analyze duration trends
- Export insights

## 🔌 API Integration

### Example API Call
```python
import requests

# Create a plan
response = requests.post("http://localhost:8000/api/plan", json={
    "goal": "Treatment Options",
    "patient_info": {
        "age": 72,
        "condition": "Chest pain"
    },
    "constraints": ["limited mobility"],
    "preferences": {"specialist": "cardiologist"}
})

plan = response.json()
print(f"Generated {len(plan['tasks'])} tasks")
```

### Response Format
```json
{
  "goal": "Treatment Options",
  "total_duration": 165,
  "tasks": [
    {
      "id": "uuid-string",
      "title": "Initial Patient Assessment",
      "description": "Comprehensive evaluation...",
      "priority": "high",
      "status": "pending",
      "estimated_duration": 45,
      "required_resources": ["dr_jones", "room_101"],
      "dependencies": [],
      "scheduled_time": "2024-02-19T16:15:00"
    }
  ],
  "created_at": "2024-02-19T16:10:00"
}
```

## 🎨 UI/UX Features

### Modern Design
- **Clean Interface**: Professional healthcare theme
- **Responsive Layout**: Works on all screen sizes
- **Color Coding**: Priority-based visual indicators
- **Interactive Elements**: Expandable cards and filters

### User Experience
- **Real-time Updates**: Live status changes
- **Error Handling**: User-friendly error messages
- **Progress Indicators**: Loading spinners and progress bars
- **Navigation**: Intuitive sidebar menu

### Data Visualization
- **Charts**: Plotly integration for analytics
- **Progress Bars**: Visual resource utilization
- **Metrics Cards**: Key performance indicators
- **Tables**: Sortable and filterable data

## 🚀 Deployment Options

### Development
```bash
# Backend
cd api && python main.py

# Frontend  
cd frontend && streamlit run streamlit_app.py
```

### Production
```bash
# Backend with Gunicorn
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api.main:app

# Frontend with Streamlit Cloud or Docker
docker build -t healthcare-frontend .
docker run -p 8501:8501 healthcare-frontend
```

## 🔧 Configuration

### Environment Variables
```bash
# Backend
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
API_BASE_URL=http://localhost:8000
FRONTEND_PORT=8501
```

### CORS Configuration
In production, update CORS settings in `api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domains
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## 🎯 Key Benefits

### ✅ Modern Architecture
- **Separation of Concerns**: Frontend and backend decoupled
- **RESTful API**: Standardized communication
- **Scalable Design**: Easy to extend and maintain
- **Production Ready**: Suitable for real deployment

### ✅ Enhanced Features
- **Real-time Updates**: Live status tracking
- **Data Visualization**: Interactive charts and graphs
- **User Management**: Session state and history
- **Export Capabilities**: JSON and CSV exports

### ✅ Developer Experience
- **Hot Reload**: Instant development feedback
- **API Documentation**: Auto-generated OpenAPI docs
- **Type Safety**: Pydantic models for validation
- **Error Handling**: Comprehensive error management

## 🎓 Educational Value

This implementation demonstrates:
- **Full-Stack Development**: Frontend + Backend integration
- **API Design**: RESTful architecture principles
- **Modern Web Tech**: FastAPI + Streamlit best practices
- **Healthcare AI**: Real-world application domain
- **Data Visualization**: Plotly and analytics
- **Production Patterns**: Scalable architecture

## 🎉 Success!

You now have a modern, production-ready Healthcare Planning Assistant with:
- ✅ **FastAPI Backend**: RESTful API with auto-documentation
- ✅ **Streamlit Frontend**: Beautiful, interactive web interface
- ✅ **Real-time Features**: Live updates and progress tracking
- ✅ **Analytics Dashboard**: Comprehensive insights and metrics
- ✅ **Modern Architecture**: Scalable and maintainable codebase

The application is ready for development, testing, and production deployment! 🚀
