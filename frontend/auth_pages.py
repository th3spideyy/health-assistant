"""
Authentication pages for Healthcare Planning Assistant
Login, signup, and user management
"""

import streamlit as st
import requests
import re
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8001"

def login_page():
    """Login page"""
    st.title("🔐 Login to Healthcare Planning Assistant")
    
    # Check if already logged in
    if 'session_id' in st.session_state and st.session_state.session_id:
        st.success("You are already logged in!")
        if st.button("Go to Dashboard"):
            st.session_state.page = "Dashboard"
            st.rerun()
        return
    
    with st.form("login_form"):
        st.subheader("Sign In")
        
        username = st.text_input(
            "Username*",
            placeholder="Enter your username",
            help="Your account username"
        )
        
        password = st.text_input(
            "Password*",
            type="password",
            placeholder="Enter your password",
            help="Your account password"
        )
        
        remember_me = st.checkbox("Remember me")
        
        submitted = st.form_submit_button("Login", type="primary")
        
        if submitted:
            if not username or not password:
                st.error("Please enter both username and password")
                return
            
            # Attempt login
            login_data = {
                "username": username,
                "password": password
            }
            
            with st.spinner("Signing in..."):
                response = api_call("POST", "/api/auth/login", login_data)
            
            if response and response.get("success"):
                # Store session
                st.session_state.session_id = response.get("session_id")
                st.session_state.user = response.get("user")
                st.session_state.logged_in = True
                
                st.success("✅ Login successful!")
                st.rerun()
            else:
                error_msg = response.get("detail", "Login failed") if response else "Connection error"
                st.error(f"❌ {error_msg}")
    
    # Streamlit markdown anchors do not switch tabs reliably; use a real button.
    st.markdown("---")
    st.caption("Don't have an account?")
    if st.button("📝 Sign up", key="go_signup"):
        st.session_state.auth_mode = "signup"
        st.rerun()

def signup_page():
    """Signup page"""
    st.title("📝 Sign Up - Healthcare Planning Assistant")
    
    with st.form("signup_form"):
        st.subheader("Create Account")
        
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input(
                "Username*",
                placeholder="Choose a username",
                help="Username must be 3-50 characters"
            )
            
            email = st.text_input(
                "Email*",
                type="default",
                placeholder="your.email@example.com",
                help="We'll use this for account notifications"
            )
        
        with col2:
            password = st.text_input(
                "Password*",
                type="password",
                placeholder="Create a strong password",
                help="Password must be 6-100 characters"
            )
            
            confirm_password = st.text_input(
                "Confirm Password*",
                type="password",
                placeholder="Re-enter your password"
            )
        
        full_name = st.text_input(
            "Full Name*",
            placeholder="John Doe",
            help="Your full name as it will appear on the system"
        )
        
        role = st.selectbox(
            "Account Type",
            ["user", "admin"],
            index=0,
            help="Select your account type"
        )
        
        # Terms and conditions
        agree_terms = st.checkbox(
            "I agree to the Terms of Service and Privacy Policy*",
            help="You must agree to continue"
        )
        
        submitted = st.form_submit_button("Create Account", type="primary")
        
        if submitted:
            # Validation
            if not username or not email or not password or not confirm_password or not full_name:
                st.error("Please fill in all required fields")
                return
            
            if len(username) < 3 or len(username) > 50:
                st.error("Username must be 3-50 characters")
                return
            
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                st.error("Please enter a valid email address")
                return
            
            if len(password) < 6 or len(password) > 100:
                st.error("Password must be 6-100 characters")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            if len(full_name) < 2 or len(full_name) > 100:
                st.error("Full name must be 2-100 characters")
                return
            
            if not agree_terms:
                st.error("You must agree to the Terms of Service")
                return
            
            # Create account
            signup_data = {
                "username": username,
                "email": email,
                "password": password,
                "full_name": full_name,
                "role": role
            }
            
            with st.spinner("Creating account..."):
                response = api_call("POST", "/api/auth/register", signup_data)
            
            if response and response.get("success"):
                # Auto-login after successful signup
                st.session_state.session_id = response.get("session_id")
                st.session_state.user = response.get("user")
                st.session_state.logged_in = True
                
                st.success("✅ Account created successfully!")
                st.info("Welcome to Healthcare Planning Assistant!")
                st.rerun()
            else:
                error_msg = response.get("detail", "Account creation failed") if response else "Connection error"
                st.error(f"❌ {error_msg}")
    
    st.markdown("---")
    st.caption("Already have an account?")
    if st.button("🔐 Login", key="go_login"):
        st.session_state.auth_mode = "login"
        st.rerun()

def profile_page():
    """User profile page"""
    st.title("👤 My Profile")
    
    # Check authentication
    if not st.session_state.get('logged_in'):
        st.error("Please login to view your profile")
        return
    
    user = st.session_state.get('user', {})
    
    # Profile form
    with st.form("profile_form"):
        st.subheader("Update Profile")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_full_name = st.text_input(
                "Full Name",
                value=user.get('full_name', ''),
                help="Update your full name"
            )
        
        with col2:
            new_email = st.text_input(
                "Email Address",
                value=user.get('email', ''),
                type="default",
                help="Update your email address"
            )
        
        # Display non-editable fields
        st.text_input("Username", value=user.get('username', ''), disabled=True)
        st.text_input("Account Type", value=user.get('role', ''), disabled=True)
        
        # Display account info
        st.subheader("Account Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Member Since", 
                     datetime.fromisoformat(user.get('created_at', '')).strftime('%Y-%m-%d') if user.get('created_at') else 'N/A')
        
        with col2:
            last_login = user.get('last_login')
            if last_login:
                st.metric("Last Login", datetime.fromisoformat(last_login).strftime('%Y-%m-%d %H:%M'))
            else:
                st.metric("Last Login", "Never")
        
        submitted = st.form_submit_button("Update Profile")
        
        if submitted:
            # Prepare update data
            update_data = {}
            if new_full_name != user.get('full_name', ''):
                update_data['full_name'] = new_full_name
            if new_email != user.get('email', ''):
                update_data['email'] = new_email
            
            if update_data:
                with st.spinner("Updating profile..."):
                    response = api_call("PUT", "/api/auth/profile", update_data)
                
                if response:
                    # Update session state
                    for key, value in update_data.items():
                        if key in st.session_state.user:
                            st.session_state.user[key] = value
                    
                    st.success("✅ Profile updated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to update profile")
            else:
                st.info("No changes to update")

def logout():
    """Logout user"""
    if 'session_id' in st.session_state:
        # Call logout API
        api_call("POST", "/api/auth/logout")
    
    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    
    st.success("✅ Logged out successfully!")
    st.info("You have been logged out. Redirecting to login page...")
    st.rerun()

def api_call(method, endpoint, data=None):
    """Make authenticated API calls"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        headers = {}
        
        # Add auth token if available
        if 'session_id' in st.session_state:
            headers['Authorization'] = f"Bearer {st.session_state.session_id}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to backend. Please make sure the server is running.")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def check_authentication():
    """Check if user is authenticated"""
    if 'session_id' in st.session_state:
        # Validate session with backend
        response = api_call("GET", "/api/auth/session")
        
        if not response:
            # Session invalid, clear it
            for key in list(st.session_state.keys()):
                if key.startswith('user') or key == 'session_id' or key == 'logged_in':
                    del st.session_state[key]
            return False
        
        return True
    
    return False
