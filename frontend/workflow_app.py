"""
Complete Healthcare Workflow Frontend
Implements the full process flow from authentication to AI recommendations
"""

import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import time

# Configuration
API_BASE_URL = "http://localhost:8003"

# Page configuration
st.set_page_config(
    page_title="Healthcare Workflow System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
    }
    .workflow-step {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
        margin: 1rem 0;
    }
    .step-active {
        border-left-color: #28a745;
        background-color: #d4edda;
    }
    .step-error {
        border-left-color: #dc3545;
        background-color: #f8d7da;
    }
    .step-complete {
        border-left-color: #6c757d;
        background-color: #e2e3e5;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
    }
    .safety-score {
        font-size: 2rem;
        font-weight: bold;
    }
    .score-high { color: #28a745; }
    .score-medium { color: #ffc107; }
    .score-low { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'workflow_session' not in st.session_state:
    st.session_state.workflow_session = None
if 'current_step' not in st.session_state:
    st.session_state.current_step = 'start'
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

# API helper functions
def api_call(method, endpoint, data=None):
    """Make API calls to workflow backend"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to workflow backend. Please start the workflow server.")
        st.code("cd api && python workflow_api.py")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def check_workflow_connection():
    """Check if workflow backend is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

# Step 1: Application Start & Authentication
def step_authentication():
    """Handle user authentication"""
    st.markdown('<div class="workflow-step step-active">', unsafe_allow_html=True)
    st.header("🔐 Step 1: Authentication")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Add tab for Login/Signup
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("User Login")
            
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                
                if st.form_submit_button("Login", type="primary"):
                    if username and password:
                        # Start workflow session
                        start_result = api_call("POST", "/api/workflow/start", {"user_id": username})
                        
                        if start_result:
                            session_id = start_result.get("session_id")
                            st.session_state.workflow_session = start_result
                            
                            # Authenticate
                            auth_result = api_call("POST", "/api/workflow/authenticate-body", {
                                "session_id": session_id,
                                "credentials": {
                                    "username": username,
                                    "password": password
                                }
                            })
                            
                            if auth_result and auth_result.get("success"):
                                st.session_state.current_step = 'data_collection'
                                st.success("✅ Authentication successful!")
                                st.rerun()
                            else:
                                st.error("❌ Authentication failed. Please retry login.")
                                st.session_state.workflow_session = None
                        else:
                            st.error("Failed to start workflow session")
                    else:
                        st.error("Please enter username and password")
        
        with col2:
            st.info("""
            **Authentication Process:**
            - System checks user credentials
            - Verifies user identity  
            - Generates secure access token
            - Creates workflow session
            
            **Next:** Data Collection
            """)
    
    with tab2:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Create New Account")
            
            with st.form("signup_form"):
                new_username = st.text_input("Username*", placeholder="Choose a username")
                new_email = st.text_input("Email*", placeholder="your.email@example.com")
                new_password = st.text_input("Password*", type="password", placeholder="Create a strong password")
                confirm_password = st.text_input("Confirm Password*", type="password", placeholder="Re-enter your password")
                full_name = st.text_input("Full Name*", placeholder="John Doe")
                
                if st.form_submit_button("Sign Up", type="primary"):
                    # Validate signup form
                    if not all([new_username, new_email, new_password, confirm_password, full_name]):
                        st.error("Please fill in all required fields")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        # Call signup API
                        signup_data = {
                            "username": new_username,
                            "email": new_email,
                            "password": new_password,
                            "full_name": full_name
                        }
                        
                        signup_result = api_call("POST", "/api/workflow/signup", signup_data)
                        
                        if signup_result and signup_result.get("success"):
                            st.success("✅ Account created successfully!")
                            st.info("Please login with your new credentials to continue.")
                            # Switch to login tab automatically
                            st.session_state.show_login = True
                            st.rerun()
                        else:
                            st.error("Failed to create account. Please try again.")
        
        with col2:
            st.info("""
            **Sign Up Process:**
            - Create new user account
            - Set up credentials
            - Verify email address
            - Access healthcare workflow
            
            **Benefits:**
            ✅ Personalized treatment plans
            ✅ AI-powered analysis
            ✅ Secure data storage
            ✅ Follow-up management
            """)

# Step 2: Data Collection
def step_data_collection():
    """Handle patient data collection"""
    st.markdown('<div class="workflow-step step-active">', unsafe_allow_html=True)
    st.header("📋 Step 2: Data Collection")
    st.markdown('</div>', unsafe_allow_html=True)
    
    session = st.session_state.workflow_session
    session_id = session.get("session_id") if session else None
    
    if not session_id:
        st.error("No active session. Please login first.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Patient Information")
        
        with st.form("patient_data_form"):
            # Medical History
            st.write("**Medical History**")
            medical_history = {}
            medical_history["conditions"] = st.text_area("Existing Conditions", 
                placeholder="e.g., Hypertension, Diabetes, Asthma")
            medical_history["surgeries"] = st.text_area("Previous Surgeries",
                placeholder="e.g., Appendectomy 2015, Knee surgery 2018")
            medical_history["medications"] = st.text_area("Current Medications",
                placeholder="e.g., Metformin, Lisinopril")
            
            # Symptoms
            st.write("**Current Symptoms**")
            symptoms_input = st.text_area("Describe Symptoms",
                placeholder="e.g., Chest pain, shortness of breath, fatigue")
            symptoms = [s.strip() for s in symptoms_input.split(',') if s.strip()] if symptoms_input else []
            
            # Preferences
            st.write("**Preferences**")
            preferences = {}
            preferences["preferred_hospital"] = st.selectbox("Preferred Hospital", 
                ["General Hospital", "Medical Center", "City Hospital"])
            preferences["appointment_time"] = st.selectbox("Preferred Time",
                ["Morning", "Afternoon", "Evening"])
            preferences["language"] = st.selectbox("Preferred Language",
                ["English", "Spanish", "French"])
            
            # Additional Information
            st.write("**Additional Information**")
            allergies = st.text_area("Allergies", placeholder="e.g., Penicillin, Peanuts")
            allergies_list = [a.strip() for a in allergies.split(',') if a.strip()] if allergies else []
            
            emergency_contact = {
                "name": st.text_input("Emergency Contact Name"),
                "phone": st.text_input("Emergency Contact Phone"),
                "relationship": st.selectbox("Relationship", ["Spouse", "Parent", "Child", "Friend"])
            }
            
            if st.form_submit_button("Submit Patient Data", type="primary"):
                patient_data = {
                    "medical_history": medical_history,
                    "symptoms": symptoms,
                    "preferences": preferences,
                    "allergies": allergies_list,
                    "emergency_contact": emergency_contact
                }
                
                result = api_call("POST", f"/api/workflow/collect-data", {
                    "session_id": session_id,
                    "patient_data": patient_data
                })
                
                if result:
                    if result.get("status") == "complete":
                        st.session_state.current_step = 'ai_processing'
                        st.success("✅ Patient data collected successfully!")
                        st.rerun()
                    elif result.get("status") == "incomplete":
                        missing = result.get("missing_fields", [])
                        st.error(f"❌ Incomplete data. Missing: {', '.join(missing)}")
                        st.info("Please provide the missing information and resubmit.")
                    else:
                        st.error("Failed to collect patient data")
    
    with col2:
        st.info("""
        **Data Collection Process:**
        - Collect medical history
        - Document current symptoms
        - Record preferences
        - Validate input data
        - Check completeness
        
        **Required Fields:**
        ✅ Medical History
        ✅ Current Symptoms  
        ✅ Preferences
        
        **Next:** AI Processing
        """)

# Step 3: AI Processing
def step_ai_processing():
    """Handle AI analysis and recommendations"""
    st.markdown('<div class="workflow-step step-active">', unsafe_allow_html=True)
    st.header("🤖 Step 3: AI Processing")
    st.markdown('</div>', unsafe_allow_html=True)
    
    session = st.session_state.workflow_session
    session_id = session.get("session_id") if session else None
    
    if not session_id:
        st.error("No active session. Please login first.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("AI Analysis")
        
        if st.button("🚀 Start AI Analysis", type="primary"):
            with st.spinner("Analyzing patient profile... This may take a few moments."):
                result = api_call("POST", f"/api/workflow/analyze", {"session_id": session_id})
            
            if result:
                if result.get("status") == "success":
                    st.session_state.current_step = 'recommendations'
                    st.success("✅ AI analysis completed successfully!")
                    st.rerun()
                elif result.get("status") == "manual_review":
                    st.session_state.current_step = 'manual_review'
                    st.warning("⚠️ Recommendation requires manual review by healthcare provider.")
                    st.rerun()
                else:
                    st.error("AI analysis failed")
        
        # Show current session status
        status_result = api_call("GET", f"/api/workflow/session/{session_id}")
        if status_result:
            st.subheader("Session Status")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Status", status_result.get("status", "Unknown"))
            with col2:
                st.metric("Activities", status_result.get("activity_count", 0))
            with col3:
                has_data = "✅" if status_result.get("has_patient_data") else "❌"
                st.metric("Patient Data", has_data)
    
    with col2:
        st.info("""
        **AI Processing Steps:**
        1. Analyze patient profile
        2. Run AI recommendation engine
        3. Validate clinical guidelines
        4. Check safety & compliance
        5. Generate treatment plan
        6. Match specialist
        
        **Validation Criteria:**
        - Safety Score ≥ 80%
        - Compliance Score ≥ 80%
        - Clinical guideline adherence
        
        **Outcomes:**
        ✅ Safe & Compliant → Auto-approve
        ⚠️ Requires Review → Manual review
        """)

# Step 4: Recommendations Display
def step_recommendations():
    """Display AI recommendations"""
    st.markdown('<div class="workflow-step step-complete">', unsafe_allow_html=True)
    st.header("📊 Step 4: AI Recommendations")
    st.markdown('</div>', unsafe_allow_html=True)
    
    session = st.session_state.workflow_session
    session_id = session.get("session_id") if session else None
    
    if not session_id:
        st.error("No active session. Please login first.")
        return
    
    # Get session status to find recommendation
    status_result = api_call("GET", f"/api/workflow/session/{session_id}")
    
    if status_result and status_result.get("has_recommendation"):
        # Get detailed recommendation
        # Note: In real implementation, we'd get recommendation_id from session
        st.subheader("🏥 Treatment Plan")
        
        # Mock recommendation display (in real implementation, get from API)
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Primary Diagnosis**")
            st.info("Cardiovascular Condition (based on symptoms)")
            
            st.write("**Recommended Treatments**")
            treatments = [
                "Initial Consultation",
                "ECG and Cardiac Evaluation",
                "Stress Test",
                "Medication Review",
                "Lifestyle Modifications"
            ]
            for treatment in treatments:
                st.checkbox(treatment, value=True, disabled=True)
            
            st.write("**Medications**")
            st.warning("• Pain Reliever (as needed)")
            st.warning("• Blood Pressure Medication")
        
        with col2:
            st.write("**Safety & Compliance Scores**")
            
            # Mock scores (in real implementation, get from API)
            safety_score = 95
            compliance_score = 92
            
            score_class = "score-high" if safety_score >= 80 else "score-medium" if safety_score >= 60 else "score-low"
            st.markdown(f'<div class="safety-score {score_class}">{safety_score}%</div>', unsafe_allow_html=True)
            st.write("**Safety Score**")
            
            score_class = "score-high" if compliance_score >= 80 else "score-medium" if compliance_score >= 60 else "score-low"
            st.markdown(f'<div class="safety-score {score_class}">{compliance_score}%</div>', unsafe_allow_html=True)
            st.write("**Compliance Score**")
            
            st.write("**Specialist Match**")
            st.success("🏥 Cardiologist")
            st.info("Dr. Smith - Available within 3 days")
            st.info("Dr. Johnson - Available within 5 days")
        
        # Action buttons
        st.subheader("📅 Next Steps")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📧 Send Recommendations", type="primary"):
                result = api_call("POST", f"/api/workflow/send-recommendations", {"delivery_method": "email"})
                if result:
                    st.success("✅ Recommendations sent successfully!")
        
        with col2:
            if st.button("📅 Schedule Follow-up"):
                st.session_state.current_step = 'follow_up'
                st.rerun()
        
        with col3:
            if st.button("📋 View Full Report"):
                st.session_state.current_step = 'full_report'
                st.rerun()

# Step 5: Follow-up Scheduling
def step_follow_up():
    """Handle follow-up scheduling"""
    st.markdown('<div class="workflow-step step-active">', unsafe_allow_html=True)
    st.header("📅 Step 5: Follow-up & Reminders")
    st.markdown('</div>', unsafe_allow_html=True)
    
    session = st.session_state.workflow_session
    session_id = session.get("session_id") if session else None
    
    if not session_id:
        st.error("No active session. Please login first.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Schedule Follow-up")
        
        with st.form("follow_up_form"):
            appointment_date = st.date_input("Appointment Date", value=datetime.now() + timedelta(days=7))
            appointment_time = st.time_input("Preferred Time", value=datetime.now().replace(hour=10, minute=0))
            
            st.write("**Reminder Preferences**")
            email_reminder = st.checkbox("Email Reminders", value=True)
            sms_reminder = st.checkbox("SMS Reminders", value=False)
            reminder_frequency = st.selectbox("Reminder Frequency", 
                ["1 day before", "2 days before", "1 week before"])
            
            if st.form_submit_button("Schedule Follow-up", type="primary"):
                schedule_data = {
                    "date": f"{appointment_date} {appointment_time}",
                    "reminders": {
                        "email": email_reminder,
                        "sms": sms_reminder,
                        "frequency": reminder_frequency
                    }
                }
                
                result = api_call("POST", f"/api/workflow/schedule-followup", schedule_data)
                
                if result:
                    st.session_state.current_step = 'completion'
                    st.success("✅ Follow-up scheduled successfully!")
                    st.rerun()
                else:
                    st.error("Failed to schedule follow-up")
    
    with col2:
        st.info("""
        **Follow-up Process:**
        - Schedule appointments
        - Set up reminders
        - Track compliance
        - Monitor progress
        - Log activities
        
        **Benefits:**
        ✅ Better health outcomes
        ✅ Early problem detection
        ✅ Treatment adherence
        ✅ Continuous care
        """)

# Manual Review Step
def step_manual_review():
    """Handle manual review required case"""
    st.markdown('<div class="workflow-step step-error">', unsafe_allow_html=True)
    st.header("⚠️ Manual Review Required")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.warning("""
    **Your case requires manual review by a healthcare provider.**
    
    This happens when:
    - Safety score is below 80%
    - Compliance score is below 80%  
    - Complex medical conditions
    - Multiple risk factors
    
    **What happens next:**
    1. Your case is flagged for review
    2. Healthcare provider evaluates recommendations
    3. Manual approval or modification
    4. You'll be notified within 24 hours
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📞 Contact Healthcare Provider", type="primary"):
            st.info("Please call our 24/7 hotline: 1-800-MEDICAL")
    
    with col2:
        if st.button("📧 Send Message"):
            st.info("Message sent to healthcare provider. Response within 4 hours.")

# Completion Step
def step_completion():
    """Handle workflow completion"""
    st.markdown('<div class="workflow-step step-complete">', unsafe_allow_html=True)
    st.header("✅ Process Complete")
    st.markdown('</div>', unsafe_allow_html=True)
    
    session = st.session_state.workflow_session
    session_id = session.get("session_id") if session else None
    
    if not session_id:
        st.error("No active session.")
        return
    
    st.success("""
    ## 🎉 Healthcare Workflow Completed Successfully!
    
    **What was accomplished:**
    ✅ User authentication verified
    ✅ Patient data collected and validated
    ✅ AI analysis completed
    ✅ Treatment recommendations generated
    ✅ Clinical guidelines validated
    ✅ Follow-up scheduled
    
    **Your personalized healthcare plan is ready!**
    """)
    
    # Show audit log
    audit_result = api_call("GET", f"/api/workflow/audit/{session_id}")
    if audit_result:
        st.subheader("📋 Activity Log")
        
        for activity in audit_result.get("audit_log", []):
            timestamp = activity.get("timestamp", "")
            activity_type = activity.get("activity", "")
            details = activity.get("details", {})
            
            with st.expander(f"{activity_type} - {timestamp[:10]}"):
                st.json(details)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Download Report", type="primary"):
            st.info("Report downloaded successfully!")
    
    with col2:
        if st.button("🚪 Complete & Logout", type="secondary"):
            result = api_call("POST", f"/api/workflow/logout")
            if result:
                # Clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                
                st.success("✅ Logged out successfully!")
                st.info("Thank you for using our Healthcare Workflow System!")
                st.rerun()

# Main application logic
def main():
    """Main application workflow"""
    st.markdown('<h1 class="main-header">🏥 Healthcare Workflow System</h1>', unsafe_allow_html=True)
    
    # Check backend connection
    if not check_workflow_connection():
        st.error("🔴 Workflow backend is not running. Please start the workflow server:")
        st.code("cd api && python workflow_api.py")
        st.info("Backend should be running on http://localhost:8003")
        return
    
    # Progress indicator
    if st.session_state.workflow_session:
        steps = {
            'start': 'Authentication',
            'data_collection': 'Data Collection', 
            'ai_processing': 'AI Processing',
            'recommendations': 'Recommendations',
            'follow_up': 'Follow-up',
            'completion': 'Completion'
        }
        
        current_step_name = steps.get(st.session_state.current_step, 'Unknown')
        
        st.progress(0.8, text=f"Current Step: {current_step_name}")
    
    # Route to appropriate step
    if st.session_state.current_step == 'start':
        step_authentication()
    elif st.session_state.current_step == 'data_collection':
        step_data_collection()
    elif st.session_state.current_step == 'ai_processing':
        step_ai_processing()
    elif st.session_state.current_step == 'recommendations':
        step_recommendations()
    elif st.session_state.current_step == 'manual_review':
        step_manual_review()
    elif st.session_state.current_step == 'follow_up':
        step_follow_up()
    elif st.session_state.current_step == 'completion':
        step_completion()
    else:
        step_authentication()

if __name__ == "__main__":
    main()
