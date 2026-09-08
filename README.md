# NER-SAFE Backend

This repository is the backend foundation for the NER-SAFE hackathon project.

## Project

NER-SAFE is an AI-powered disaster management platform for the North Eastern Region of India. The backend foundation is focused on:

- FastAPI application setup
- PostgreSQL configuration with SQLAlchemy
- JWT-ready configuration
- CORS setup for a React frontend
- risk management API with a replaceable ML pipeline
- modular architecture for future feature work

## Included structure

```text
app/
├── __init__.py
├── config.py
├── database.py
├── main.py
├── ml/
│   ├── __init__.py
│   ├── create_demo_dataset.py
│   ├── model.py
│   ├── predict.py
│   ├── preprocessing.py
│   └── train.py
├── models/
├── routes/
├── schemas/
├── services/
├── utils/
├── ...
data/
├── processed/
├── training/
models/
uploads/
tests/
requirements.txt
.env.example
README.md
```

## Install dependencies

```powershell
cd "C:\Users\HP\Desktop\hackathonproject\AI_Logistics_accessibitlity_platform.worktrees\ai-smart-logistics-backend-setup"
python -m venv .venv
\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Environment setup

```powershell
Copy-Item .env.example .env
```

Then update `.env` with your local database values.

Example:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ner_safe_db
SECRET_KEY=change-me-in-production
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Run the backend

```powershell
\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API documentation

FastAPI exposes the generated API documentation when the backend is running:

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI schema: `http://localhost:8000/openapi.json`
- ReDoc: `http://localhost:8000/redoc`
- Complete request/response reference: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)

## Endpoints

- `GET /` returns the backend status
- `GET /health` returns the health status
- `POST /api/risk/predict` returns a replaceable placeholder risk prediction
- `GET /api/risk/current` returns the latest stored risk prediction
- `GET /api/risk/forecast` returns recent risk predictions
- `GET /api/roads` and `GET /api/roads/{road_id}` return road accessibility data
- `PUT /api/roads/{road_id}/status` updates a road to `open`, `partially_blocked`, `high_risk`, or `blocked`
- `GET /api/villages` supports `state`, `district`, and `risk_level` filters
- `GET /api/villages/{village_id}` returns one village
- `GET /api/alerts` lists stored alerts
- `POST /api/alerts` creates an alert
- `POST /api/alerts/generate` generates an alert from a risk score
- `GET /api/emergency/priorities` returns ranked emergency response priorities

## Risk prediction flow

The API currently uses a deterministic placeholder calculation. It is intentionally not scientifically validated:

```text
POST /api/risk/predict
    -> risk.py
    -> ai_service.py
    -> placeholder score + risk level + confidence
    -> PostgreSQL RiskPrediction storage
```

The calculation is isolated in `app/services/ai_service.py` so the AI/ML implementation can replace it later without changing the public API.

## Testing

```powershell
\.venv\Scripts\python.exe -m pytest -q
```

Test the live endpoint with a sample request:

```powershell
curl -X POST "http://localhost:8000/api/risk/predict" `
  -H "Content-Type: application/json" `
  -d '{
    "latitude": 27.12,
    "longitude": 93.52,
    "rainfall_1h": 25,
    "rainfall_6h": 90,
    "rainfall_24h": 160,
    "soil_moisture": 72,
    "slope": 42,
    "elevation": 1800,
    "historical_landslides": 5
  }'
```

## Model limitations

- This is a hackathon prototype model.
- It is not scientifically validated for operational use.
- The current dataset is synthetic and should be replaced with a real landslide dataset later.
- Feature importance indicates correlation patterns only and does not imply causal impact.
