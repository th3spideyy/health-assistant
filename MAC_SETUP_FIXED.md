# Fixed setup for macOS

Use Python 3.11 or 3.12. Do **not** use the `venv` folder that was bundled with the original ZIP.

## 1. Open Terminal and enter the project

```bash
cd "/path/to/project 2"
```

## 2. Create a clean virtual environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

If `python3.11` is not installed, install Python 3.11/3.12 first (for example with Homebrew), then repeat.

## 3. Install dependencies

```bash
pip install -r requirements.txt
pip install -r frontend/requirements.txt
```

## 4. Start the normal backend

Terminal 1:

```bash
python run_backend.py
```

Check:

- API: http://localhost:8001
- Docs: http://localhost:8001/docs
- Health: http://localhost:8001/health

## 5. Start the normal frontend

Terminal 2:

```bash
source .venv/bin/activate
python run_frontend.py
```

Open:

http://localhost:8501

## Alternative: complete workflow version

Terminal 1:

```bash
python run_workflow_backend.py
```

Terminal 2:

```bash
python run_workflow_frontend.py
```

Open:

http://localhost:8505

The workflow frontend talks to port 8003.

## Important

Do not run both normal and workflow backends for the same frontend.

The original secure frontend was configured for port 8002 even though the main FastAPI backend is on port 8001. That has been corrected.
