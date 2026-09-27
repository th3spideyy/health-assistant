"""
Setup script to create admin user for Healthcare Planning Assistant
"""

import sys
import os

# Add project root to path so src.auth_models resolves correctly
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from src.auth_models import AuthManager

def create_admin_user():
    """Create an admin user for the system"""
    auth_manager = AuthManager()

    # Check if admin already exists
    for user in auth_manager.users.values():
        if user.username == "admin":
            print("INFO: Admin user already exists")
            print("   Username: admin")
            print("   Password: admin123")
            return

    # Create admin user
    admin_user = auth_manager.create_user(
        username="admin",
        email="admin@healthcare.local",
        password="admin123",
        full_name="System Administrator",
        role="admin"
    )

    if admin_user:
        print("SUCCESS: Admin user created!")
        print("   Username: admin")
        print("   Password: admin123")
        print("   Role:     admin")
        print()
        print("Start backend:  python3 run_backend.py")
        print("Start frontend: python3 run_secure_frontend.py")
    else:
        print("FAILED: Could not create admin user")

if __name__ == "__main__":
    create_admin_user()
