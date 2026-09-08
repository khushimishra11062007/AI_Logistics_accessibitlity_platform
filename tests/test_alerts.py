from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.database import Base, get_db
from app.main import app
from app.services.alert_service import classify_risk_level


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


def test_create_and_list_alerts():
    response = client.post(
        "/api/alerts",
        json={
            "title": "Road Warning",
            "message": "Avoid the mountain road.",
            "severity": "high",
            "latitude": 27.12,
            "longitude": 93.52,
            "target": "road",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["title"] == "Road Warning"
    assert payload["severity"] == "high"
    assert payload["status"] == "active"
    assert payload["created_at"] is not None

    listed = client.get("/api/alerts")
    assert listed.status_code == 200
    assert any(alert["id"] == payload["id"] for alert in listed.json())


def test_generate_critical_alert():
    response = client.post(
        "/api/alerts/generate",
        json={
            "risk_score": 81,
            "latitude": 27.12,
            "longitude": 93.52,
            "target": "village",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["title"] == "Critical Landslide Risk"
    assert payload["message"] == "Critical landslide risk detected with a risk score of 81.00."
    assert payload["severity"] == "critical"
    assert payload["target"] == "village"
    assert payload["status"] == "active"


def test_alert_thresholds():
    expected = {
        0: "low",
        30: "low",
        31: "moderate",
        60: "moderate",
        61: "high",
        80: "high",
        81: "critical",
        100: "critical",
    }
    for score, level in expected.items():
        assert classify_risk_level(score).value == level
