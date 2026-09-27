# Streamlit Community Cloud deployment

## Repository structure

The Streamlit Cloud **Main file path** must be:

```text
streamlit_app.py
```

It is located in the repository root.

## Deploy

1. Push this project to GitHub.
2. Open Streamlit Community Cloud and choose **New app**.
3. Select your GitHub repository and branch (`main`).
4. Set **Main file path** to:
   `streamlit_app.py`
5. Deploy.

This cloud entry point is self-contained and does **not** call `http://localhost:8001`.

## Local run

```bash
streamlit run streamlit_app.py
```

The old FastAPI files are retained for local/API use, but they are not required for the Streamlit Cloud app.

## Persistence note

Streamlit Community Cloud can restart/rebuild apps, so JSON files are suitable for a demo but are not a durable production database. For production, move users, doctors, and plans to a hosted database.
