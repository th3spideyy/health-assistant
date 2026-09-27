"""Secure Healthcare Planning Assistant with login, planning, progress and doctor management."""
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime

from auth_pages import login_page, signup_page, profile_page, logout, check_authentication, api_call

API_BASE_URL = "http://localhost:8001"

st.set_page_config(page_title="Healthcare Planning Assistant", page_icon="🏥", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.main-header{font-size:2.5rem;color:#2E86AB;text-align:center;margin-bottom:2rem}
.metric-card{background:#f8f9fa;padding:1rem;border-radius:.5rem;border-left:4px solid #2E86AB;margin:.5rem 0;color:#000}
.task-card{background:white;padding:1rem;border-radius:.5rem;border:1px solid #dee2e6;margin:.5rem 0;color:#000}
.priority-high{border-left:4px solid #dc3545}.priority-medium{border-left:4px solid #ffc107}.priority-low{border-left:4px solid #28a745}.priority-urgent{border-left:4px solid #6f42c1}
.stTextArea>div>div>textarea{color:#000!important}.stText{color:#000!important}
</style>
""", unsafe_allow_html=True)


def show_dashboard():
    user = st.session_state.get("user", {})
    st.markdown('<h1 class="main-header">🏥 Healthcare Planning Assistant</h1>', unsafe_allow_html=True)
    st.sidebar.markdown(f"### 👤 {user.get('full_name', 'User')}")
    st.sidebar.markdown(f"**Role:** {user.get('role', 'user').title()}")
    st.sidebar.title("Navigation")

    pages = [
        ("📋 Create Plan", "Create Plan"),
        ("📚 Plan History", "View Plans"),
        ("📈 Progress", "Progress"),
        ("👨‍⚕️ Doctors", "Doctors"),
        ("🏥 Resources", "Resources"),
        ("📊 Analytics", "Analytics"),
        ("👤 Profile", "Profile"),
    ]
    for label, key in pages:
        if st.sidebar.button(label, key=f"nav_{key}", use_container_width=True):
            st.session_state.current_page = key
            st.rerun()
    if st.sidebar.button("🚪 Logout", key="nav_logout", use_container_width=True):
        logout()

    page = st.session_state.get("current_page", "Create Plan")
    if page == "Create Plan": create_plan_page()
    elif page == "View Plans": view_plans_page()
    elif page == "Progress": progress_page()
    elif page == "Doctors": doctors_page()
    elif page == "Resources": resources_page()
    elif page == "Analytics": analytics_page()
    elif page == "Profile": profile_page()


def get_doctors():
    return api_call("GET", "/api/doctors") or []


def create_plan_page():
    st.header("📋 Create Healthcare Plan")
    doctors = get_doctors()
    specializations = sorted({d["specialization"] for d in doctors if d.get("specialization")})
    specialist_options = ["None"] + specializations

    with st.form("planning_form"):
        col1, col2 = st.columns(2)
        with col1:
            goal = st.selectbox("Healthcare Goal*", ["Treatment Options", "Emergency Care", "Routine Checkup", "Surgery Preparation"])
            age = st.number_input("Patient Age", min_value=0, max_value=120, value=65)
        with col2:
            condition = st.text_input("Condition/Symptoms", placeholder="e.g., chest pain, headache, routine checkup")
            constraint = st.selectbox("Constraints", ["None", "Urgent", "Limited Mobility", "Requires Anesthesia", "Routine"])
        specialist = st.selectbox("Specialist Preference", specialist_options)
        submitted = st.form_submit_button("🚀 Generate Plan", type="primary")

    # IMPORTANT: action buttons are outside st.form. Streamlit forbids st.button inside forms.
    if submitted:
        if not condition:
            st.error("Please describe the patient's condition")
        else:
            request_data = {
                "goal": goal,
                "patient_info": {"age": age, "condition": condition},
                "constraints": [constraint.lower()] if constraint != "None" else [],
                "preferences": {"specialist": specialist.lower()} if specialist != "None" else {},
            }
            with st.spinner("Generating healthcare plan..."):
                plan = api_call("POST", "/api/plan", request_data)
            if plan:
                st.session_state.current_plan = plan
                st.session_state.current_page = "Progress"
                st.success("✅ Plan generated successfully!")
                st.rerun()

    if st.session_state.get("current_plan"):
        display_plan(st.session_state.current_plan)


def display_plan(plan):
    st.subheader("📊 Execution Plan")
    cols = st.columns(4)
    cols[0].metric("Total Tasks", len(plan["tasks"]))
    cols[1].metric("Duration", f"{plan['total_duration']} min")
    high_priority = sum(1 for task in plan["tasks"] if task["priority"] in ["high", "urgent"])
    cols[2].metric("High Priority", high_priority)
    created_time = datetime.fromisoformat(plan["created_at"].replace("Z", "+00:00"))
    cols[3].metric("Created", created_time.strftime("%H:%M"))

    st.subheader("📋 Task Breakdown")
    priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
    for task in sorted(plan["tasks"], key=lambda x: priority_order.get(x["priority"], 4)):
        scheduled = ""
        if task.get("scheduled_time"):
            scheduled = f"<p><strong>Scheduled:</strong> {datetime.fromisoformat(task['scheduled_time'].replace('Z','+00:00')).strftime('%H:%M')}</p>"
        resources = ", ".join(task.get("required_resources", [])) or "None"
        st.markdown(f"""
        <div class="task-card priority-{task['priority']}" >
          <h4>{task['title']}</h4>
          <p><strong>Description:</strong> {task['description']}</p>
          <p><strong>Priority:</strong> {task['priority'].upper()} | <strong>Duration:</strong> {task['estimated_duration']} min | <strong>Status:</strong> {task['status'].upper()}</p>
          <p><strong>Resources:</strong> {resources}</p>{scheduled}
        </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📈 Open Progress", key="open_progress"):
            st.session_state.current_page = "Progress"
            st.rerun()
    with col2:
        st.download_button(
            "💾 Download Plan JSON",
            data=__import__("json").dumps(plan, indent=2),
            file_name="healthcare_plan.json",
            mime="application/json",
            key="download_plan",
        )


def progress_page():
    st.header("📈 Progress Tracking")
    plan = st.session_state.get("current_plan")
    if not plan or not plan.get("plan_id"):
        st.info("Create a healthcare plan first to track its progress.")
        return

    plan_id = plan["plan_id"]
    progress = api_call("GET", f"/api/plan/{plan_id}/progress")
    if not progress:
        return
    st.progress(progress["progress_percentage"] / 100, text=f"{progress['progress_percentage']:.1f}% complete")
    cols = st.columns(4)
    cols[0].metric("Total", progress["total_tasks"])
    cols[1].metric("Completed", progress["completed_tasks"])
    cols[2].metric("In Progress", progress["in_progress_tasks"])
    cols[3].metric("Remaining", progress["remaining_tasks"])

    st.subheader("Update Task Status")
    changed = False
    for task in plan["tasks"]:
        c1, c2, c3 = st.columns([4, 2, 1])
        with c1: st.write(f"**{task['title']}**")
        with c2:
            options = ["pending", "in_progress", "completed", "blocked"]
            new_status = st.selectbox("Status", options, index=options.index(task["status"]), key=f"status_{plan_id}_{task['id']}", label_visibility="collapsed")
        with c3:
            if st.button("Save", key=f"save_{plan_id}_{task['id']}"):
                result = api_call("PUT", f"/api/plan/{plan_id}/task/{task['id']}/status", {"status": new_status})
                if result:
                    task["status"] = new_status
                    changed = True
    if changed:
        st.success("Task status updated.")
        st.rerun()


def view_plans_page():
    st.header("📚 Plan History")
    result = api_call("GET", "/api/plans")
    plans = result.get("plans", []) if result else []
    if not plans:
        st.info("No plans have been created yet. Create your first plan from the Create Plan section.")
        return
    df = pd.DataFrame(plans)
    df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m-%d %H:%M")
    df.columns = ["Plan ID", "Goal", "Tasks", "Duration (min)", "Created", "Completed"]
    st.dataframe(df, use_container_width=True, hide_index=True)
    if st.session_state.get("current_plan"):
        st.subheader("Current Plan")
        st.json(st.session_state.current_plan)


def doctors_page():
    st.header("👨‍⚕️ Doctor Directory")
    st.caption("Manage the doctors available in the planning system. Adding/removing doctors requires an admin account.")
    doctors = get_doctors()
    if doctors:
        df = pd.DataFrame(doctors)
        df.columns = ["ID", "Name", "Specialization", "Email", "Phone", "Available"]
        st.dataframe(df, use_container_width=True, hide_index=True)

    user = st.session_state.get("user", {})
    if user.get("role") != "admin":
        st.info("You can view the doctor directory. Log in with an admin account to add or remove doctors.")
        return

    st.subheader("➕ Add Doctor")
    with st.form("add_doctor_form"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Doctor Name*", placeholder="Dr. Priya Sharma")
            specialization = st.text_input("Specialization*", placeholder="Pediatrician")
        with c2:
            email = st.text_input("Email", placeholder="doctor@hospital.com")
            phone = st.text_input("Phone", placeholder="+91 98765 43210")
        available = st.checkbox("Available for appointments", value=True)
        add = st.form_submit_button("Add Doctor", type="primary")
    if add:
        if not name.strip() or not specialization.strip():
            st.error("Doctor name and specialization are required.")
        else:
            result = api_call("POST", "/api/doctors", {"name": name.strip(), "specialization": specialization.strip(), "email": email.strip(), "phone": phone.strip(), "available": available})
            if result:
                st.success(f"✅ {name} added successfully.")
                st.rerun()

    if doctors:
        st.subheader("🗑️ Remove Doctor")
        labels = {f"{d['name']} — {d['specialization']}": d["id"] for d in doctors}
        selected = st.selectbox("Select doctor", list(labels.keys()), key="delete_doctor_select")
        if st.button("Remove Selected Doctor", type="secondary", key="remove_doctor"):
            result = api_call("DELETE", f"/api/doctors/{labels[selected]}")
            if result:
                st.success("Doctor removed.")
                st.rerun()


def resources_page():
    st.header("🏥 Resource Utilization")
    resources = api_call("GET", "/api/resources")
    if not resources:
        st.error("Failed to load resources")
        return
    cols = st.columns(4)
    total = len(resources)
    available = sum(1 for r in resources if r["available"])
    avg = sum(r["utilization_percentage"] for r in resources) / total if total else 0
    cols[0].metric("Total Resources", total)
    cols[1].metric("Available", f"{available}/{total}")
    cols[2].metric("Avg Utilization", f"{avg:.1f}%")
    cols[3].metric("Busy Resources", total - available)
    df = pd.DataFrame(resources)
    fig = px.bar(df, x="name", y="utilization_percentage", color="type", title="Resource Utilization by Type")
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    df["status"] = df["available"].apply(lambda x: "🟢 Available" if x else "🔴 Busy")
    display_df = df[["name", "type", "status", "capacity", "current_load", "utilization_percentage"]]
    display_df.columns = ["Name", "Type", "Status", "Capacity", "Current Load", "Utilization %"]
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def analytics_page():
    st.header("📊 Analytics Dashboard")
    plans = api_call("GET", "/api/plans")
    items = plans.get("plans", []) if plans else []
    total = len(items)
    tasks = sum(p.get("task_count", 0) for p in items)
    completed = sum(p.get("completed_tasks", 0) for p in items)
    cols = st.columns(3)
    cols[0].metric("Plans", total)
    cols[1].metric("Tasks", tasks)
    cols[2].metric("Completed Tasks", completed)
    if items:
        df = pd.DataFrame(items)
        fig = px.bar(df, x="goal", y="task_count", title="Tasks by Healthcare Goal")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Create a plan to start seeing analytics.")


def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if st.session_state.logged_in:
        if not check_authentication():
            st.session_state.logged_in = False
            st.error("Session expired. Please login again.")
            st.rerun()
            return
        show_dashboard()
    else:
        st.markdown('<h1 class="main-header">🏥 Healthcare Planning Assistant</h1>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        with tab1: login_page()
        with tab2: signup_page()

if __name__ == "__main__":
    main()
