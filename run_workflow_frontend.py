"""Launch the complete workflow Streamlit frontend."""

import os
import subprocess
import sys


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    app = os.path.join(root, "frontend", "workflow_app.py")
    if not os.path.isfile(app):
        raise FileNotFoundError("frontend/workflow_app.py was not found.")
    print("Workflow frontend: http://localhost:8505")
    print("Workflow backend:  http://localhost:8003")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", app, "--server.port", "8505"],
        cwd=root, check=False
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nWorkflow frontend stopped.")
