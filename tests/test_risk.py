from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.database import Base, get_db
from app.main import app
from app.schemas.risk import RiskPredictionInput
from app.services.ai_service import classify_risk_level, generate_placeholder_risk_prediction

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
    assert result.model_confidence == 0.5


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
    assert payload["id"] is not None


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


def test_risk_level_thresholds():
    for expected, score in [("low", 30), ("moderate", 31), ("moderate", 60), ("high", 61), ("high", 80), ("critical", 81)]:
        assert classify_risk_level(score).value == expected
