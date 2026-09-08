from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.database import Base, get_db
from app.main import app
from app.models.enums import RiskLevel, RoadStatus
from app.models.risk_prediction import RiskPrediction
from app.models.road import Road
from app.models.village import Village


engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


client = TestClient(app)


def test_heavy_rainfall_simulation_and_reset():
    db = TestingSessionLocal()
    db.add(
        Village(
            name="Demo Zone",
            district="Demo",
            state="Demo",
            latitude=27.1,
            longitude=93.1,
            population=5000,
            risk_level=RiskLevel.HIGH,
        )
    )
    db.add(
        RiskPrediction(
            latitude=27.1,
            longitude=93.1,
            rainfall_1h=100,
            rainfall_6h=300,
            rainfall_24h=600,
            soil_moisture=90,
            slope=60,
            elevation=2000,
            historical_landslides=5,
            risk_score=75,
            risk_level=RiskLevel.HIGH,
            model_confidence=0.5,
        )
    )
    db.add(
        Road(
            name="Demo Road",
            start_lat=27.1,
            start_lon=93.1,
            end_lat=27.11,
            end_lon=93.11,
            status=RoadStatus.OPEN,
        )
    )
    db.commit()
    db.close()

    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db
    try:
        simulated = client.post("/api/simulation/heavy-rainfall")
        assert simulated.status_code == 200
        summary = simulated.json()
        assert summary["simulation"] == "HEAVY_RAINFALL"
        assert summary["affected_zones"] == 1
        assert summary["high_risk_zones"] == 1
        assert summary["blocked_roads"] == 1
        assert summary["alerts_generated"] == 1

        alerts = client.get("/api/alerts")
        assert alerts.status_code == 200
        assert alerts.json()[0]["severity"] == "critical"

        reset = client.post("/api/simulation/reset")
        assert reset.status_code == 200
        assert reset.json()["simulation"] == "RESET"
        assert client.get("/api/alerts").json() == []
        assert client.get("/api/roads").json()[0]["status"] == "open"
    finally:
        if previous_override is not None:
            app.dependency_overrides[get_db] = previous_override
