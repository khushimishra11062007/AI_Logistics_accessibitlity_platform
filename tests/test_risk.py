from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.database import Base, get_db
from app.main import app
from app.ml.model import MODEL_PATH, SCALER_PATH
from app.ml.train import train_model
from app.schemas.risk import RiskPredictionInput
from app.services.ai_service import ModelNotTrainedError, generate_placeholder_risk_prediction

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def _ensure_model_exists() -> None:
    if not MODEL_PATH.exists() or not SCALER_PATH.exists():
        train_model()


_ensure_model_exists()


def test_model_training_creates_artifacts():
    assert MODEL_PATH.exists()
    assert SCALER_PATH.exists()


def test_predict_risk_score_and_level_are_valid():
    payload = RiskPredictionInput(
        latitude=27.12,
        longitude=93.52,
        rainfall_1h=25,
        rainfall_6h=90,
        rainfall_24h=160,
        soil_moisture=72,
        slope=42,
        elevation=1800,
        historical_landslides=5,
    )
    result = generate_placeholder_risk_prediction(payload)
    assert 0 <= result.risk_score <= 100
    assert result.risk_level.value in {"low", "moderate", "high", "critical"}


def test_missing_input_validation():
    response = client.post(
        "/api/risk/predict",
        json={
            "latitude": 27.12,
            "longitude": 93.52,
            "rainfall_1h": 25,
            "rainfall_6h": 90,
            "rainfall_24h": 160,
            "soil_moisture": 72,
            "slope": 42,
        },
    )
    assert response.status_code == 422


def test_model_not_found_handling():
    model_backup = MODEL_PATH.with_suffix(".bak")
    scaler_backup = SCALER_PATH.with_suffix(".bak")

    if MODEL_PATH.exists():
        MODEL_PATH.rename(model_backup)
    if SCALER_PATH.exists():
        SCALER_PATH.rename(scaler_backup)

    try:
        payload = RiskPredictionInput(
            latitude=27.12,
            longitude=93.52,
            rainfall_1h=25,
            rainfall_6h=90,
            rainfall_24h=160,
            soil_moisture=72,
            slope=42,
            elevation=1800,
            historical_landslides=5,
        )
        try:
            generate_placeholder_risk_prediction(payload)
            raise AssertionError("Expected ModelNotTrainedError")
        except ModelNotTrainedError:
            pass
    finally:
        if model_backup.exists():
            model_backup.rename(MODEL_PATH)
        if scaler_backup.exists():
            scaler_backup.rename(SCALER_PATH)


def test_predict_risk_creates_prediction_record():
    response = client.post(
        "/api/risk/predict",
        json={
            "latitude": 27.12,
            "longitude": 93.52,
            "rainfall_1h": 25,
            "rainfall_6h": 90,
            "rainfall_24h": 160,
            "soil_moisture": 72,
            "slope": 42,
            "elevation": 1800,
            "historical_landslides": 5,
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["risk_score"] >= 0
    assert payload["risk_level"] in ["low", "moderate", "high", "critical"]
    assert payload["model_confidence"] is not None


def test_get_current_risk_when_record_exists():
    response = client.get("/api/risk/current")
    assert response.status_code == 200
    payload = response.json()
    assert "risk_score" in payload
    assert "risk_level" in payload


def test_get_risk_forecast_returns_list():
    response = client.get("/api/risk/forecast")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) >= 1
