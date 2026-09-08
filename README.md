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
- `POST /api/simulation/heavy-rainfall` runs the demo heavy-rainfall simulation
- `POST /api/simulation/reset` restores the pre-simulation demo state

## React frontend API quick reference

Base URL: `http://localhost:8000`

All successful collection endpoints return JSON arrays. Create and action endpoints return one
JSON object or a summary object. Validation errors use HTTP `422` with a `detail` field.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/risk/current` | Get the latest stored risk prediction |
| `GET` | `/api/risk/forecast?limit=5` | Get recent risk prediction history |
| `GET` | `/api/incidents` | List incidents |
| `POST` | `/api/incidents` | Create an incident |
| `GET` | `/api/roads` | List roads and accessibility statuses |
| `GET` | `/api/villages` | List villages and risk levels |
| `GET` | `/api/alerts` | List stored alerts |
| `GET` | `/api/emergency/priorities` | Get ranked emergency response locations |
| `POST` | `/api/routes/optimize` | Evaluate usable roads for a route request |
| `POST` | `/api/simulation/heavy-rainfall` | Run the demo heavy-rainfall simulation |
| `POST` | `/api/simulation/reset` | Restore the pre-simulation demo state |

### Risk current

Request: no body.

Response:

```json
{
  "id": 1,
  "latitude": 27.12,
  "longitude": 93.52,
  "rainfall_1h": 25,
  "rainfall_6h": 90,
  "rainfall_24h": 160,
  "soil_moisture": 72,
  "slope": 42,
  "elevation": 1800,
  "historical_landslides": 5,
  "risk_score": 68.42,
  "risk_level": "high",
  "model_confidence": 0.5,
  "prediction_time": "2026-09-06T10:35:00Z"
}
```

### Incidents

Request:

```json
{
  "type": "landslide",
  "latitude": 27.123,
  "longitude": 93.456,
  "severity": "high",
  "description": "Large crack observed near a road cut."
}
```

Response:

```json
{
  "id": 1,
  "type": "landslide",
  "latitude": 27.123,
  "longitude": 93.456,
  "severity": "high",
  "description": "Large crack observed near a road cut.",
  "image_url": null,
  "status": "active",
  "reported_by": null,
  "created_at": "2026-09-06T10:30:00Z",
  "updated_at": "2026-09-06T10:30:00Z",
  "ai_classification": null,
  "ai_confidence": null
}
```

### Roads, villages, alerts, and emergency priorities

Request: no body for these `GET` endpoints.

Example road response:

```json
{
  "id": 1,
  "name": "Mountain Link",
  "start_lat": 27.1,
  "start_lon": 93.4,
  "end_lat": 27.2,
  "end_lon": 93.5,
  "status": "open",
  "risk_score": 12.5,
  "last_updated": "2026-09-06T10:40:00Z"
}
```

Example emergency priority response:

```json
{
  "location": "Hill Village",
  "priority_score": 82.5,
  "priority_level": "P1",
  "risk_score": 90.0,
  "population": 5000,
  "road_status": "blocked"
}
```

### Route evaluation

Request:

```json
{
  "origin_latitude": 27.12,
  "origin_longitude": 93.52,
  "destination_latitude": 27.2,
  "destination_longitude": 93.6,
  "max_risk_score": 80
}
```

Response:

```json
{
  "origin": {"latitude": 27.12, "longitude": 93.52},
  "destination": {"latitude": 27.2, "longitude": 93.6},
  "road_ids": [1, 2],
  "route_status": "available",
  "estimated_distance_km": null,
  "message": "Route evaluation completed using available road records."
}
```

This is currently a route-safety placeholder; turn-by-turn optimization is not implemented.

### Simulation

Request: no body.

Response:

```json
{
  "simulation": "HEAVY_RAINFALL",
  "affected_zones": 4,
  "high_risk_zones": 3,
  "blocked_roads": 2,
  "alerts_generated": 5
}
```

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
