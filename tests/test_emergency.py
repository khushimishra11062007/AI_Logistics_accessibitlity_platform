from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.database import Base, get_db
from app.main import app
from app.models.enums import IncidentStatus, RiskLevel, RoadStatus, Severity
from app.models.incident import Incident
from app.models.risk_prediction import RiskPrediction
from app.models.road import Road
from app.models.village import Village
from app.services.emergency_service import calculate_priority_score, priority_level


engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
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


def test_emergency_priorities_rank_database_locations():
    db = TestingSessionLocal()
    db.add_all(
        [
            Village(
                name="Critical Village",
                district="D1",
                state="S1",
                latitude=27.1,
                longitude=93.1,
                population=5000,
                risk_level=RiskLevel.CRITICAL,
            ),
            Village(
                name="Low Village",
                district="D1",
                state="S1",
                latitude=28.1,
                longitude=94.1,
                population=100,
                risk_level=RiskLevel.LOW,
            ),
        ]
    )
    db.add(
        RiskPrediction(
            latitude=27.1,
            longitude=93.1,
            rainfall_1h=10,
            rainfall_6h=20,
            rainfall_24h=30,
            soil_moisture=50,
            slope=30,
            elevation=1000,
            historical_landslides=2,
            risk_score=90,
            risk_level=RiskLevel.CRITICAL,
            model_confidence=0.5,
        )
    )
    db.add(
        Road(
            name="Blocked Access",
            start_lat=27.1,
            start_lon=93.1,
            end_lat=27.11,
            end_lon=93.11,
            status=RoadStatus.BLOCKED,
        )
    )
    db.add(
        Incident(
            type="landslide",
            latitude=27.1,
            longitude=93.1,
            severity=Severity.CRITICAL,
            description="Major slope failure",
            status=IncidentStatus.ACTIVE,
        )
    )
    db.commit()
    db.close()

    # Other module-level test clients share the application override; restore it afterwards.
    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.get("/api/emergency/priorities")
    finally:
        if previous_override is not None:
            app.dependency_overrides[get_db] = previous_override

    assert response.status_code == 200
    priorities = response.json()
    critical = next(item for item in priorities if item["location"] == "Critical Village")
    assert priorities[0]["location"] == "Critical Village"
    assert critical["priority_level"] == "P1"
    assert critical["risk_score"] == 90
    assert critical["road_status"] == "blocked"
    assert critical["population"] == 5000


def test_priority_score_levels_are_modifiable_and_bounded():
    assert priority_level(70) == "P1"
    assert priority_level(40) == "P2"
    assert priority_level(39.99) == "P3"
    assert calculate_priority_score(
        type(
            "Components",
            (),
            {
                "risk_score": 100,
                "population": 10000,
                "road_status": RoadStatus.BLOCKED,
                "incident_severity": Severity.CRITICAL,
            },
        )()
    ) == 100
