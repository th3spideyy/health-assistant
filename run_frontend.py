"""Launch the Streamlit frontend reliably from any working directory."""

import os
import subprocess
import sys


def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    app = os.path.join(project_root, "frontend", "secure_app.py")
    req = os.path.join(project_root, "frontend", "requirements.txt")
    if not os.path.isfile(app):
        raise FileNotFoundError("frontend/secure_app.py was not found.")

    print("Starting Healthcare Planning Assistant Frontend...")
    print("Frontend: http://localhost:8501 (Login / Sign Up)")
    print("Backend must be running on: http://localhost:8001")
    print("-" * 50)

    # Install into the currently active environment. No bundled venv is used.
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", req], check=True)
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", app, "--server.port", "8501"],
        cwd=project_root,
        check=False,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nFrontend stopped.")
