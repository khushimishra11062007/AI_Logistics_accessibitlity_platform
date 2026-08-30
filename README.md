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

## Endpoints

- `GET /` returns the backend status
- `GET /health` returns the health status
- `POST /api/risk/predict` returns ML-based risk prediction
- `GET /api/risk/current` returns the latest stored risk prediction
- `GET /api/risk/forecast` returns recent risk predictions

## Risk model and dataset

No production landslide dataset is included in this repository. The current project uses a synthetic demo dataset generator so the pipeline can be developed, tested, and extended without fabricating real-world historical disaster records.

Required dataset columns:

```text
latitude, longitude, rainfall_1h, rainfall_6h, rainfall_24h, soil_moisture, slope, elevation, historical_landslides, landslide_occurred
```

Synthetic dataset creation:

```powershell
\.venv\Scripts\python.exe -m app.ml.create_demo_dataset
```

This creates a demo CSV under:

```text
data/training/landslide_demo_dataset.csv
```

Training the model:

```powershell
\.venv\Scripts\python.exe -m app.ml.train
```

This trains a RandomForestClassifier, evaluates it, prints accuracy/precision/recall/F1/confusion matrix, and saves:

```text
models/landslide_model.pkl
models/scaler.pkl
```

The trained model files are intentionally not committed to Git because they may be large. Generate them locally using the command above.

## Prediction flow

The API remains compatible with the existing route contract:

```text
POST /api/risk/predict
    -> risk.py
    -> ai_service.py
    -> app.ml.predict
    -> trained model + scaler
    -> risk score + risk level + confidence
    -> PostgreSQL RiskPrediction storage
```

The placeholder logic has been replaced with a real ML pipeline but the public API contract is unchanged.

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
