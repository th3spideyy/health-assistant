"""
Working Healthcare Planning Assistant Frontend
Without authentication for immediate use
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8002"

# Page configuration
st.set_page_config(
    page_title="Healthcare Planning Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
        margin: 0.5rem 0;
        color: #000000;
    }
    .task-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
        color: #000000;
    }
    .priority-high { border-left: 4px solid #dc3545; }
    .priority-medium { border-left: 4px solid #ffc107; }
    .priority-low { border-left: 4px solid #28a745; }
    .priority-urgent { border-left: 4px solid #6f42c1; }
    .stTextArea > div > div > textarea {
        color: #000000 !important;
    }
    .stText {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# API helper functions
def api_call(method, endpoint, data=None):
    """Make API calls to the backend"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend. Please make sure to start the backend server first.")
        st.code("cd api && python simple_main.py")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def check_backend_connection():
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def create_plan_page():
    """Page for creating new healthcare plans"""
    st.header("📋 Create Healthcare Plan")
    
    # Input form
    with st.form("planning_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            goal = st.selectbox(
                "Healthcare Goal*",
                ["Treatment Options", "Emergency Care", "Routine Checkup", "Surgery Preparation"],
                help="Select the type of healthcare planning needed"
            )
            
            age = st.number_input(
                "Patient Age",
                min_value=0,
                max_value=120,
                value=65,
                help="Patient's age in years"
            )
        
        with col2:
            condition = st.text_input(
                "Condition/Symptoms",
                placeholder="e.g., chest pain, headache, routine checkup",
                help="Describe the patient's condition or symptoms"
            )
            
            constraint = st.selectbox(
                "Constraints",
                ["None", "Urgent", "Limited Mobility", "Requires Anesthesia", "Routine"],
                help="Any specific constraints or requirements"
            )
        
        specialist = st.selectbox(
            "Specialist Preference",
            ["None", "Cardiologist", "Neurologist", "General Practitioner", "Orthopedic"],
            help="Preferred specialist (if any)"
        )
        
        submitted = st.form_submit_button("🚀 Generate Plan", type="primary")
        
        if submitted:
            if not condition:
                st.error("Please describe the patient's condition")
                return
            
            # Prepare request data
            request_data = {
                "goal": goal,
                "patient_info": {
                    "age": age,
                    "condition": condition
                },
                "constraints": [constraint.lower()] if constraint != "None" else [],
                "preferences": {"specialist": specialist.lower()} if specialist != "None" else {}
            }
            
            # Show loading spinner
            with st.spinner("Generating healthcare plan..."):
                plan = api_call("POST", "/api/plan", request_data)
            
            if plan:
                st.session_state.current_plan = plan
                st.success("✅ Plan generated successfully!")
                display_plan(plan)
    
    # Display plan if it exists
    if st.session_state.get('current_plan'):
        display_plan(st.session_state.current_plan)

def display_plan(plan):
    """Display a healthcare plan"""
    st.subheader("📊 Execution Plan")
    
    # Plan summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Tasks", len(plan["tasks"]))
    
    with col2:
        st.metric("Duration", f"{plan['total_duration']} min")
    
    with col3:
        high_priority = sum(1 for task in plan["tasks"] if task["priority"] in ["high", "urgent"])
        st.metric("High Priority", high_priority)
    
    with col4:
        created_time = datetime.fromisoformat(plan["created_at"].replace("Z", "+00:00"))
        st.metric("Created", created_time.strftime("%H:%M"))
    
    # Tasks display
    st.subheader("📋 Task Breakdown")
    
    # Group tasks by priority
    priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    sorted_tasks = sorted(plan["tasks"], key=lambda x: priority_order.get(x["priority"], 4))
    
    for task in sorted_tasks:
        priority_class = f"priority-{task['priority']}"
        
        with st.container():
            st.markdown(f"""
            <div class="task-card {priority_class}">
                <h4>{task['title']}</h4>
                <p><strong>Description:</strong> {task['description']}</p>
                <p><strong>Priority:</strong> {task['priority'].upper()} | 
                   <strong>Duration:</strong> {task['estimated_duration']} min | 
                   <strong>Status:</strong> {task['status'].upper()}</p>
                <p><strong>Resources:</strong> {', '.join(task['required_resources'])}</p>
                {f"<p><strong>Scheduled:</strong> {datetime.fromisoformat(task['scheduled_time'].replace('Z', '+00:00')).strftime('%H:%M')}</p>" if task['scheduled_time'] else ""}
                {f"<p><strong>Dependencies:</strong> {len(task['dependencies'])} task(s)</p>" if task['dependencies'] else ""}
            </div>
            """, unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📈 Update Progress"):
            st.info("Progress tracking coming soon!")
    
    with col2:
        if st.button("💾 Export Plan"):
            st.json(plan, expanded=True)
            st.success("Plan data displayed above. You can copy and save it.")
    
    with col3:
        if st.button("🔄 Refresh Status"):
            st.rerun()

def view_plans_page():
    """Page for viewing existing plans"""
    st.header("📚 Plan History")
    
    # Get all plans
    plans_response = api_call("GET", "/api/plans")
    
    if not plans_response:
        st.error("Failed to load plans")
        return
    
    plans = plans_response.get("plans", [])
    
    if not plans:
        st.info("No plans created yet. Create your first plan!")
        return
    
    # Display plans in a table
    df = pd.DataFrame(plans)
    st.dataframe(df, use_container_width=True)
    
    # Plan details
    if plans:
        selected_plan = st.selectbox("Select a plan to view details", 
                                 options=[p["goal"] for p in plans])
        
        if selected_plan:
            plan = next(p for p in plans if p["goal"] == selected_plan)
            st.json(plan, expanded=True)

def resources_page():
    """Page for viewing resource utilization"""
    st.header("🏥 Resource Utilization")
    
    # Mock resources data (since we don't have resources endpoint in simple backend)
    resources = [
        {"name": "Operating Room 1", "type": "Facility", "available": True, "utilization": 75},
        {"name": "Dr. Smith", "type": "Doctor", "available": False, "utilization": 90},
        {"name": "ICU Bed 3", "type": "Equipment", "available": True, "utilization": 45},
        {"name": "MRI Scanner", "type": "Equipment", "available": True, "utilization": 60},
        {"name": "Emergency Room", "type": "Facility", "available": False, "utilization": 95},
    ]
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_resources = len(resources)
        st.metric("Total Resources", total_resources)
    
    with col2:
        available = sum(1 for r in resources if r["available"])
        st.metric("Available", f"{available}/{total_resources}")
    
    with col3:
        avg_utilization = sum(r["utilization"] for r in resources) / len(resources)
        st.metric("Avg Utilization", f"{avg_utilization:.1f}%")
    
    with col4:
        busy_resources = sum(1 for r in resources if not r["available"])
        st.metric("Busy Resources", busy_resources)
    
    # Resource utilization chart
    st.subheader("📊 Resource Utilization Chart")
    
    df = pd.DataFrame(resources)
    fig = px.bar(
        df,
        x="name",
        y="utilization",
        color="type",
        title="Resource Utilization by Type",
        labels={"utilization": "Utilization (%)", "name": "Resource Name"}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Resource details table
    st.subheader("📋 Resource Details")
    
    # Add status indicator
    df["status"] = df["available"].apply(lambda x: "🟢 Available" if x else "🔴 Busy")
    
    # Reorder columns
    display_df = df[["name", "type", "status", "utilization"]]
    display_df.columns = ["Name", "Type", "Status", "Utilization %"]
    
    st.dataframe(display_df, use_container_width=True)

def analytics_page():
    """Page for analytics and insights"""
    st.header("📈 Analytics Dashboard")
    
    # Show current plan stats if available
    if st.session_state.get('current_plan'):
        plan = st.session_state.current_plan
        
        st.subheader("Current Plan Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Tasks", len(plan["tasks"]))
        
        with col2:
            st.metric("Duration", f"{plan['total_duration']} min")
        
        with col3:
            urgent_tasks = sum(1 for task in plan["tasks"] if task["priority"] == "urgent")
            st.metric("Urgent Tasks", urgent_tasks)
        
        with col4:
            created_time = datetime.fromisoformat(plan["created_at"].replace("Z", "+00:00"))
            st.metric("Created", created_time.strftime("%Y-%m-%d"))
        
        # Task priority distribution
        st.subheader("Task Priority Distribution")
        priorities = [task["priority"] for task in plan["tasks"]]
        priority_counts = pd.Series(priorities).value_counts()
        
        fig = px.pie(
            values=priority_counts.values,
            names=priority_counts.index,
            title="Task Priority Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Create a plan to see analytics!")

def main():
    """Main application"""
    st.markdown('<h1 class="main-header">🏥 Healthcare Planning Assistant</h1>', unsafe_allow_html=True)
    
    # Check backend connection
    if not check_backend_connection():
        st.error("🔴 Backend server is not running. Please start the backend first:")
        st.code("cd api && python simple_main.py")
        st.info("Backend should be running on http://localhost:8002")
        return
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["Create Plan", "View Plans", "Resources", "Analytics"])
    
    if page == "Create Plan":
        create_plan_page()
    elif page == "View Plans":
        view_plans_page()
    elif page == "Resources":
        resources_page()
    elif page == "Analytics":
        analytics_page()

if __name__ == "__main__":
    main()
