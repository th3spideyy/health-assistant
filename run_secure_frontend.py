"""
Secure frontend launcher for Healthcare Planning Assistant
"""

import subprocess
import sys
import os

def main():
    """Launch the secure Streamlit frontend with authentication"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    secure_app = os.path.join(project_root, "frontend", "secure_app.py")

    print("Starting Secure Healthcare Planning Assistant Frontend...")
    print("Frontend will be available at: http://localhost:8501")
    print("This version includes user authentication.")
    print("Press Ctrl+C to stop.")
    print("-" * 50)

    if not os.path.exists(secure_app):
        print(f"ERROR: frontend/secure_app.py not found at {secure_app}")
        return

    try:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", "secure_app.py",
             "--server.port", "8501"],
            cwd=os.path.join(project_root, "frontend")
        )
    except KeyboardInterrupt:
        print("\nFrontend server stopped.")
    except Exception as e:
        print(f"Error starting frontend: {e}")

if __name__ == "__main__":
    main()
