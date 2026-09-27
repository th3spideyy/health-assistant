# 🚀 Setup Guide - Healthcare Planning Assistant

## 📋 Prerequisites

- Python 3.8 or higher
- Internet connection for package installation

## ⚡ Quick Start

### Step 1: Install Dependencies
```bash
# Install backend dependencies
pip install fastapi uvicorn pydantic python-multipart

# Install frontend dependencies  
pip install streamlit requests pandas plotly
```

### Step 2: Start Backend Server
```bash
python run_backend.py
```
**Expected Output:**
```
🚀 Starting Healthcare Planning Assistant Backend...
📍 API will be available at: http://localhost:8000
📚 API Documentation: http://localhost:8000/docs
⏹️  Press Ctrl+C to stop the server
--------------------------------------------------
🏥 Healthcare Planning Assistant initialized
Ready to assist with complex healthcare task planning!
INFO:     Started server process [xxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Start Frontend (New Terminal)
```bash
python run_frontend.py
```
**Expected Output:**
```
🖥️  Starting Healthcare Planning Assistant Frontend...
🌐 Frontend will be available at: http://localhost:8501
⏹️  Press Ctrl+C to stop the server
--------------------------------------------------
📦 Checking frontend dependencies...
📦 Installing frontend dependencies...
🌐  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Step 4: Access the Application
Open your browser and go to: **http://localhost:8501**

## 🔧 Manual Setup (Alternative)

### Backend Setup
```bash
cd api
pip install -r requirements.txt
python main.py
```

### Frontend Setup  
```bash
cd frontend
pip install -r requirements.txt
streamlit run streamlit_app.py --server.port 8501
```

## 🧪 Testing the System

### Test Backend API
```bash
# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"2024-02-19T16:30:00.000Z"}
```

### Test Frontend Connection
1. Open http://localhost:8501
2. If backend is running, you'll see the full interface
3. If backend is not running, you'll see an error message

## 🎮 First Time Usage

### 1. Create Your First Plan
1. Navigate to **Create Plan** page
2. Fill in the form:
   - **Goal**: Treatment Options
   - **Age**: 72
   - **Condition**: Chest pain
   - **Constraints**: Limited Mobility
   - **Specialist**: Cardiologist
3. Click **🚀 Generate Plan**

### 2. Review Results
- **Execution Plan Tab**: View all tasks with schedules
- **Progress Tab**: Track task completion
- **Resources Tab**: Monitor resource utilization

### 3. Explore Features
- **View Plans**: See plan history
- **Resources**: Check resource availability
- **Analytics**: View planning insights

## 🐛 Troubleshooting

### Common Issues

#### 1. "Cannot connect to backend"
**Solution**: Make sure the FastAPI server is running
```bash
python run_backend.py
```

#### 2. "ModuleNotFoundError: No module named 'src'"
**Solution**: Run from project root directory
```bash
cd /path/to/healthcare-planning-assistant
python run_backend.py
```

#### 3. "Port already in use"
**Solution**: Change ports or kill existing processes
```bash
# Kill processes on ports 8000 and 8501
netstat -ano | findstr :8000
netstat -ano | findstr :8501
```

#### 4. Frontend shows loading spinner forever
**Solution**: Check browser console for errors, ensure backend is accessible

### Port Conflicts
If ports 8000 or 8501 are busy, modify the launch scripts:

**Backend (api/main.py):**
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)  # Changed to 8001
```

**Frontend (run_frontend.py):**
```python
subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8502"])
```

### Dependency Issues
```bash
# Clean install
pip uninstall fastapi uvicorn streamlit -y
pip install fastapi uvicorn streamlit requests pandas plotly
```

## 🔍 Verification Checklist

- [ ] Backend starts without errors
- [ ] Frontend starts without errors  
- [ ] API health check works: `curl http://localhost:8000/health`
- [ ] Frontend loads at http://localhost:8501
- [ ] Can create a healthcare plan
- [ ] Can view resource utilization
- [ ] Can see analytics dashboard

## 🎯 Success Indicators

✅ **Backend Running**: API server responds at http://localhost:8000
✅ **Frontend Running**: Web interface loads at http://localhost:8501  
✅ **Connection Working**: No "cannot connect" errors
✅ **Plan Generation**: Successfully creates healthcare plans
✅ **Data Display**: Shows tasks, resources, and analytics

## 📚 API Documentation

Once backend is running, visit:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🚀 Production Deployment

For production use, consider:
- **Docker**: Containerize both services
- **Environment Variables**: Configure ports and URLs
- **Database**: Replace in-memory storage with PostgreSQL
- **Authentication**: Add user authentication
- **HTTPS**: Configure SSL certificates

## 🎉 Ready to Go!

If you see both servers running without errors and can access the web interface, your Healthcare Planning Assistant is ready for use! 🏥✨
