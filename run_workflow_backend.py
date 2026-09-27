"""Launch the complete workflow FastAPI backend."""

import os
import subprocess
import sys


def main():
    root = os.path.dirname(os.path.abspath(__file__))
    api = os.path.join(root, "api")
    env = os.environ.copy()
    env["PYTHONPATH"] = root + os.pathsep + env.get("PYTHONPATH", "")
    print("Workflow API: http://localhost:8003")
    print("Docs:         http://localhost:8003/docs")
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "workflow_api:app",
         "--host", "127.0.0.1", "--port", "8003", "--reload"],
        cwd=api, env=env, check=False
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nWorkflow backend stopped.")
