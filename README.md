# Luna

Luna is a personal AI companion with a FastAPI backend and a streaming web UI.

## Run locally

1. Create a virtual environment with Python 3.11 or newer.
2. Install dependencies: `pip install -r backend/requirements.txt`
3. Copy `backend/.env.example` to `backend/.env`, then add a newly rotated `GROQ_API_KEY`.
4. Start from the project root: `uvicorn backend.main:app --reload`
5. Open `http://127.0.0.1:8000`.

Run offline tests with: `python -m pytest backend/tests`

Set `LUNA_ADMIN_API_TOKEN` to enable the protected memory-admin endpoints. Send it as the `X-Admin-Token` header.
