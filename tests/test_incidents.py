from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.database import Base, get_db
from app.main import app

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


def test_create_incident():
    response = client.post(
        "/api/incidents",
        json={
            "type": "landslide",
            "latitude": 27.123,
            "longitude": 93.456,
            "severity": "high",
            "description": "Large crack observed near a road cut.",
            "image_url": "https://example.com/incident.jpg",
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["status"] == "active"
    assert payload["type"] == "landslide"
    assert payload["description"] == "Large crack observed near a road cut."


def test_list_incidents_with_filters():
    response = client.get("/api/incidents?type=landslide&severity=high&status=active")
    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) >= 1
    assert payload[0]["type"] == "landslide"
    assert payload[0]["severity"] == "high"
    assert payload[0]["status"] == "active"


def test_get_incident_by_id():
    created = client.post(
        "/api/incidents",
        json={
            "type": "flood",
            "latitude": 27.900,
            "longitude": 94.100,
            "severity": "medium",
            "description": "Water pooling along a slope road.",
        },
    )
    incident_id = created.json()["id"]
    response = client.get(f"/api/incidents/{incident_id}")
    assert response.status_code == 200
    assert response.json()["id"] == incident_id


def test_update_incident():
    created = client.post(
        "/api/incidents",
        json={
            "type": "road_blockage",
            "latitude": 26.700,
            "longitude": 92.100,
            "severity": "critical",
            "description": "Road blocked by debris.",
        },
    )
    incident_id = created.json()["id"]
    response = client.put(
        f"/api/incidents/{incident_id}",
        json={"status": "in_progress", "description": "Road is being cleared by team."},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"
    assert response.json()["description"] == "Road is being cleared by team."
