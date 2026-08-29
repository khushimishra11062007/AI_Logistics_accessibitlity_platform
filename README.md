# NER-SAFE Backend

This repository is the backend foundation for the NER-SAFE hackathon project.

## Project

NER-SAFE is an AI-powered disaster management platform for the North Eastern Region of India. The backend foundation is focused on:

- FastAPI application setup
- PostgreSQL configuration with SQLAlchemy
- JWT-ready configuration
- CORS setup for a React frontend
- basic health and root endpoints
- clean modular structure for future feature work

## Included structure

```text
app/
├── __init__.py
├── main.py
├── config.py
├── database.py
├── models/
├── schemas/
├── routes/
├── services/
├── utils/
├── ...
data/
uploads/
tests/
requirements.txt
.env.example
README.md
```

## Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# or .venv\Scripts\activate   # Windows PowerShell
pip install -r requirements.txt
```

## Environment setup

```bash
copy .env.example .env
```

Then update `.env` with your local database values.

## Run the backend

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

- `GET /` returns the backend status
- `GET /health` returns the health status

## Test endpoints

```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

Expected response for `/`:

```json
{
  "message": "NER-SAFE Backend is running",
  "status": "online"
}
```

Expected response for `/health`:

```json
{
  "status": "healthy"
}
```
