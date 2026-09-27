"""Launch the FastAPI backend reliably from any working directory."""

import os
import subprocess
import sys


def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    api_dir = os.path.join(project_root, "api")
    if not os.path.isfile(os.path.join(api_dir, "main.py")):
        raise FileNotFoundError("api/main.py was not found.")

    env = os.environ.copy()
    env["PYTHONPATH"] = project_root + os.pathsep + env.get("PYTHONPATH", "")

    print("Starting Healthcare Planning Assistant Backend...")
    print("API:  http://localhost:8001")
    print("Docs: http://localhost:8001/docs")
    print("Press Ctrl+C to stop.")
    print("-" * 50)

    subprocess.run(
        [sys.executable, "-m", "uvicorn", "main:app",
         "--host", "127.0.0.1", "--port", "8001", "--reload"],
        cwd=api_dir,
        env=env,
        check=False,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBackend stopped.")
