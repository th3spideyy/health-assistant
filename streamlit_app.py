"""Streamlit Cloud entry point for Healthcare Planning Assistant.

This version is self-contained: it does not require a separate FastAPI server or
localhost:8001. It is intended for Streamlit Community Cloud.
"""
import json
import os
import sys
import uuid
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.planner_agent import HealthcarePlannerAgent
from src.models import TaskStatus
from src.auth_models import AuthManager

st.set_page_config(
    page_title="Healthcare Planning Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = os.path.join(ROOT, "data")
DOCTORS_FILE = os.path.join(DATA_DIR, "doctors.json")

DEFAULT_DOCTORS = [
    {"id": "dr_smith", "name": "Dr. Smith", "specialization": "Cardiologist", "email": "dr.smith@hospital.local", "phone": "", "available": True},
    {"id": "dr_jones", "name": "Dr. Jones", "specialization": "General Practitioner", "email": "dr.jones@hospital.local", "phone": "", "available": True},
    {"id": "dr_wilson", "name": "Dr. Wilson", "specialization": "Neurologist", "email": "dr.wilson@hospital.local", "phone": "", "available": True},
]

CSS = """
<style>
[data-testid="stAppViewContainer"] { background: linear-gradient(135deg,#f5fbff 0%,#ffffff 55%,#f0fbf7 100%); }
.main-header { font-size: 2.7rem; font-weight: 800; color:#123c63; margin-bottom:.25rem; }
.subtitle { color:#60758a; margin-bottom:1.5rem; }
.card { background:white; border:1px solid #e3edf5; border-radius:18px; padding:20px; box-shadow:0 8px 25px rgba(31,78,121,.07); }
.task-card { background:white; padding:16px; border-radius:14px; border:1px solid #dfe8ef; margin:10px 0; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# One planner per Streamlit session.
if "planner" not in st.session_state:
    st.session_state.planner = HealthcarePlannerAgent()

@st.cache_resource
def get_auth_manager():
    return AuthManager(os.path.join(DATA_DIR, "users.json"))

auth = get_auth_manager()


def load_doctors():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DOCTORS_FILE):
        with open(DOCTORS_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DOCTORS, f, indent=2)
    try:
        with open(DOCTORS_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return list(DEFAULT_DOCTORS)


def save_doctors(doctors):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DOCTORS_FILE, "w", encoding="utf-8") as f:
        json.dump(doctors, f, indent=2)


def user_dict(user):
    return user.to_dict() if hasattr(user, "to_dict") else user


def login_screen():
    st.markdown('<div class="main-header">🏥 Healthcare Planning Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Plan healthcare tasks, coordinate resources, manage doctors and track progress.</div>', unsafe_allow_html=True)
    tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Sign Up"])

    with tab_login:
        st.subheader("Welcome back")
        with st.form("cloud_login_form"):
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="Your password")
            submit = st.form_submit_button("Login", type="primary", use_container_width=True)
        if submit:
            if not username or not password:
                st.error("Please enter your username and password.")
            else:
                user = auth.authenticate_user(username.strip(), password)
                if user:
                    session = auth.create_session(user)
                    st.session_state.logged_in = True
                    st.session_state.session_id = session.session_id
                    st.session_state.user = user_dict(user)
                    st.session_state.current_page = "Create Plan"
                    st.rerun()
                else:
                    st.error("Invalid username or password.")

    with tab_signup:
        st.subheader("Create your account")
        with st.form("cloud_signup_form"):
            c1, c2 = st.columns(2)
            with c1:
                username = st.text_input("Username*", key="signup_username")
                email = st.text_input("Email*", key="signup_email")
                full_name = st.text_input("Full Name*", key="signup_name")
            with c2:
                password = st.text_input("Password*", type="password", key="signup_password")
                confirm = st.text_input("Confirm Password*", type="password", key="signup_confirm")
                role = st.selectbox("Account Type", ["user", "admin"], key="signup_role")
            terms = st.checkbox("I agree to the Terms of Service and Privacy Policy*")
            submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)
        if submit:
            if not all([username, email, full_name, password, confirm]):
                st.error("Please fill in all required fields.")
            elif len(username) < 3 or len(username) > 50:
                st.error("Username must be 3–50 characters.")
            elif password != confirm:
                st.error("Passwords do not match.")
            elif len(password) < 6:
                st.error("Password must contain at least 6 characters.")
            elif not terms:
                st.error("Please agree to the Terms of Service.")
            elif auth.create_user(username.strip(), email.strip(), password, full_name.strip(), role):
                user = auth.authenticate_user(username.strip(), password)
                session = auth.create_session(user)
                st.session_state.logged_in = True
                st.session_state.session_id = session.session_id
                st.session_state.user = user_dict(user)
                st.success("Account created successfully.")
                st.rerun()
            else:
                st.error("Username or email already exists.")


def ensure_plan_id(plan):
    if "plan_id" not in plan:
        plan["plan_id"] = str(uuid.uuid4())
    return plan


def plan_to_dict(plan):
    return {
        "plan_id": plan.get("plan_id"),
        "goal": plan.get("goal"),
        "total_duration": plan.get("total_duration", 0),
        "created_at": plan.get("created_at", datetime.now().isoformat()),
        "tasks": plan.get("tasks", []),
    }


def create_plan():
    st.header("📋 Create Healthcare Plan")
    doctors = load_doctors()
    specializations = sorted({d.get("specialization", "") for d in doctors if d.get("specialization")})

    with st.form("planning_form"):
        c1, c2 = st.columns(2)
        with c1:
            goal = st.selectbox("Healthcare Goal", ["Treatment Options", "Emergency Care", "Routine Checkup", "Surgery Preparation"])
            age = st.number_input("Patient Age", min_value=0, max_value=120, value=65)
        with c2:
            condition = st.text_input("Condition / Symptoms", placeholder="e.g. chest pain, headache, routine checkup")
            constraint = st.selectbox("Constraints", ["None", "Urgent", "Limited Mobility", "Requires Anesthesia", "Routine"])
        specialist = st.selectbox("Specialist Preference", ["None"] + specializations)
        submit = st.form_submit_button("🚀 Generate Plan", type="primary", use_container_width=True)

    if submit:
        if not condition.strip():
            st.error("Please describe the patient's condition.")
        else:
            with st.spinner("Generating healthcare plan..."):
                plan = st.session_state.planner.process_request(
                    goal=goal,
                    patient_info={"age": age, "condition": condition.strip()},
                    constraints=[] if constraint == "None" else [constraint.lower()],
                    preferences={} if specialist == "None" else {"specialist": specialist.lower()},
                )
            tasks = []
            for task in plan.tasks:
                tasks.append({
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "priority": task.priority.value,
                    "status": task.status.value,
                    "estimated_duration": task.estimated_duration,
                    "required_resources": task.required_resources,
                    "dependencies": task.dependencies,
                    "scheduled_time": plan.schedule.get(task.id).isoformat() if task.id in plan.schedule else None,
                })
            st.session_state.current_plan = ensure_plan_id({
                "goal": plan.goal,
                "total_duration": plan.total_duration,
                "tasks": tasks,
                "created_at": datetime.now().isoformat(),
            })
            st.success("✅ Plan generated successfully.")

    if st.session_state.get("current_plan"):
        display_plan(st.session_state.current_plan)


def display_plan(plan):
    st.subheader("📊 Execution Plan")
    c = st.columns(4)
    c[0].metric("Total Tasks", len(plan["tasks"]))
    c[1].metric("Duration", f"{plan['total_duration']} min")
    c[2].metric("High Priority", sum(t["priority"] in ["high", "urgent"] for t in plan["tasks"]))
    c[3].metric("Goal", plan["goal"])
    for task in sorted(plan["tasks"], key=lambda x: {"urgent":0,"high":1,"medium":2,"low":3}.get(x["priority"],4)):
        resources = ", ".join(task.get("required_resources", [])) or "None"
        st.markdown(f"""<div class='task-card'><h4>{task['title']}</h4><p>{task['description']}</p><p><b>Priority:</b> {task['priority'].upper()} &nbsp; <b>Status:</b> {task['status'].upper()} &nbsp; <b>Duration:</b> {task['estimated_duration']} min</p><p><b>Resources:</b> {resources}</p></div>""", unsafe_allow_html=True)
    st.download_button("💾 Download Plan JSON", json.dumps(plan, indent=2), "healthcare_plan.json", "application/json")


def progress_page():
    st.header("📈 Progress Tracking")
    plan = st.session_state.get("current_plan")
    if not plan:
        st.info("Create a healthcare plan first.")
        return
    total = len(plan["tasks"])
    completed = sum(t["status"] == "completed" for t in plan["tasks"])
    in_progress = sum(t["status"] == "in_progress" for t in plan["tasks"])
    pct = completed / total * 100 if total else 0
    st.progress(pct / 100, text=f"{pct:.1f}% complete")
    c = st.columns(4)
    c[0].metric("Total", total); c[1].metric("Completed", completed); c[2].metric("In Progress", in_progress); c[3].metric("Remaining", total-completed-in_progress)

    for task in plan["tasks"]:
        c1, c2 = st.columns([4,2])
        c1.write(f"**{task['title']}**")
        options = ["pending", "in_progress", "completed", "blocked"]
        current = task["status"] if task["status"] in options else "pending"
        with c2:
            status = st.selectbox("Status", options, index=options.index(current), key=f"status_{task['id']}")
        if status != current:
            task["status"] = status
            st.rerun()


def history_page():
    st.header("📚 Plan History")
    history = st.session_state.get("plan_history", [])
    if st.session_state.get("current_plan") and not any(p.get("plan_id") == st.session_state.current_plan.get("plan_id") for p in history):
        st.session_state.plan_history = history + [plan_to_dict(st.session_state.current_plan)]
        history = st.session_state.plan_history
    if not history:
        st.info("No plans created in this session yet.")
        return
    rows = [{"Plan ID": p["plan_id"], "Goal": p["goal"], "Tasks": len(p["tasks"]), "Duration (min)": p["total_duration"], "Created": p["created_at"][:16]} for p in history]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def doctors_page():
    st.header("👨‍⚕️ Doctor Directory")
    doctors = load_doctors()
    if doctors:
        st.dataframe(pd.DataFrame(doctors), use_container_width=True, hide_index=True)
    user = st.session_state.get("user", {})
    if user.get("role") != "admin":
        st.info("You can view the doctor directory. Admin access is required to add or remove doctors.")
        return
    with st.form("add_doctor"):
        c1,c2=st.columns(2)
        with c1:
            name=st.text_input("Doctor Name*")
            specialization=st.text_input("Specialization*")
        with c2:
            email=st.text_input("Email")
            phone=st.text_input("Phone")
        available=st.checkbox("Available", True)
        add=st.form_submit_button("➕ Add Doctor", type="primary")
    if add:
        if not name.strip() or not specialization.strip():
            st.error("Doctor name and specialization are required.")
        else:
            new_id = name.lower().replace(" ", "_")
            doctors.append({"id":new_id,"name":name.strip(),"specialization":specialization.strip(),"email":email.strip(),"phone":phone.strip(),"available":available})
            save_doctors(doctors)
            st.success("Doctor added.")
            st.rerun()
    if doctors:
        labels={f"{d['name']} — {d['specialization']}":d['id'] for d in doctors}
        selected=st.selectbox("Doctor to remove", list(labels))
        if st.button("🗑️ Remove Selected Doctor"):
            save_doctors([d for d in doctors if d["id"] != labels[selected]])
            st.success("Doctor removed.")
            st.rerun()


def resources_page():
    st.header("🏥 Resource Utilization")
    resources = st.session_state.planner.get_resource_utilization()
    rows=[]
    for rid,r in resources.items():
        rows.append({"Name":r["name"],"Type":r["type"],"Capacity":r["capacity"],"Current Load":r["current_load"],"Utilization %":r["utilization_percentage"],"Status":"Available" if r["available"] else "Busy"})
    df=pd.DataFrame(rows)
    c=st.columns(4); c[0].metric("Resources",len(df)); c[1].metric("Available",sum(df["Status"]=="Available")); c[2].metric("Avg Utilization",f"{df['Utilization %'].mean():.1f}%"); c[3].metric("Busy",sum(df["Status"]=="Busy"))
    st.dataframe(df,use_container_width=True,hide_index=True)
    if not df.empty:
        fig=px.bar(df,x="Name",y="Utilization %",color="Type",title="Resource Utilization")
        st.plotly_chart(fig,use_container_width=True)


def analytics_page():
    st.header("📊 Analytics")
    history=st.session_state.get("plan_history",[])
    if not history:
        st.info("Create plans to see analytics.")
        return
    rows=[{"Goal":p["goal"],"Tasks":len(p["tasks"]),"Duration":p["total_duration"]} for p in history]
    df=pd.DataFrame(rows)
    c=st.columns(3); c[0].metric("Plans",len(df)); c[1].metric("Tasks",int(df["Tasks"].sum())); c[2].metric("Total Minutes",int(df["Duration"].sum()))
    st.plotly_chart(px.bar(df,x="Goal",y="Tasks",title="Tasks by Healthcare Goal"),use_container_width=True)


def profile_page():
    st.header("👤 My Profile")
    user=st.session_state.user
    st.write(f"**Username:** {user.get('username','')}")
    st.write(f"**Role:** {user.get('role','user').title()}")
    with st.form("profile"):
        name=st.text_input("Full Name",user.get("full_name","")); email=st.text_input("Email",user.get("email","")); save=st.form_submit_button("Update Profile")
    if save:
        updates={}
        if name!=user.get("full_name"): updates["full_name"]=name
        if email!=user.get("email"): updates["email"]=email
        if updates and auth.update_user(user["id"],**updates):
            st.session_state.user.update(updates); st.success("Profile updated."); st.rerun()
        else: st.info("No changes to update.")


def dashboard():
    user=st.session_state.user
    st.sidebar.markdown(f"### 👤 {user.get('full_name','User')}")
    st.sidebar.caption(f"Role: {user.get('role','user').title()}")
    pages=[("📋 Create Plan","Create Plan"),("📚 Plan History","Plan History"),("📈 Progress","Progress"),("👨‍⚕️ Doctors","Doctors"),("🏥 Resources","Resources"),("📊 Analytics","Analytics"),("👤 Profile","Profile")]
    for label,key in pages:
        if st.sidebar.button(label,use_container_width=True,key="nav_"+key): st.session_state.current_page=key; st.rerun()
    if st.sidebar.button("🚪 Logout",use_container_width=True):
        sid=st.session_state.get("session_id")
        if sid: auth.logout(sid)
        for k in list(st.session_state.keys()):
            if k not in ["planner"]: del st.session_state[k]
        st.rerun()
    st.markdown('<div class="main-header">🏥 Healthcare Planning Assistant</div>',unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Cloud-ready Streamlit application — no separate localhost backend required.</div>',unsafe_allow_html=True)
    page=st.session_state.get("current_page","Create Plan")
    {"Create Plan":create_plan,"Plan History":history_page,"Progress":progress_page,"Doctors":doctors_page,"Resources":resources_page,"Analytics":analytics_page,"Profile":profile_page}[page]()


if not st.session_state.get("logged_in"):
    login_screen()
else:
    current = auth.get_user_by_session(st.session_state.get("session_id", ""))
    if not current:
        st.session_state.clear(); st.session_state.planner=HealthcarePlannerAgent(); st.rerun()
    dashboard()
