from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.database import Base, get_db
from app.main import app
from app.models.enums import RiskLevel, RoadStatus
from app.models.road import Road
from app.models.village import Village


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


def seed_data() -> tuple[int, int]:
    db = TestingSessionLocal()
    road = Road(
        name="Mountain Link",
        start_lat=27.1,
        start_lon=93.4,
        end_lat=27.2,
        end_lon=93.5,
        status=RoadStatus.OPEN,
        risk_score=12.5,
    )
    village = Village(
        name="Hill Village",
        district="Papum Pare",
        state="Arunachal Pradesh",
        latitude=27.2,
        longitude=93.6,
        population=1200,
        risk_level=RiskLevel.HIGH,
    )
    db.add_all([road, village])
    db.commit()
    db.refresh(road)
    db.refresh(village)
    road_id, village_id = road.id, village.id
    db.close()
    return road_id, village_id


def test_road_endpoints():
    road_id, _ = seed_data()

    listed = client.get("/api/roads")
    assert listed.status_code == 200
    assert any(road["id"] == road_id for road in listed.json())

    detail = client.get(f"/api/roads/{road_id}")
    assert detail.status_code == 200
    assert detail.json()["status"] == "open"

    updated = client.put(
        f"/api/roads/{road_id}/status",
        json={"status": "high_risk"},
    )
    assert updated.status_code == 200
    assert updated.json()["status"] == "high_risk"


def test_village_endpoints_and_filters():
    _, village_id = seed_data()

    listed = client.get("/api/villages")
    assert listed.status_code == 200
    assert any(village["id"] == village_id for village in listed.json())

    detail = client.get(f"/api/villages/{village_id}")
    assert detail.status_code == 200
    assert detail.json()["name"] == "Hill Village"

    filtered = client.get(
        "/api/villages",
        params={
            "state": "Arunachal Pradesh",
            "district": "Papum Pare",
            "risk_level": "high",
        },
    )
    assert filtered.status_code == 200
    assert len(filtered.json()) >= 1
    assert any(village["id"] == village_id for village in filtered.json())


def test_missing_road_and_village_return_not_found():
    assert client.get("/api/roads/999999").status_code == 404
    assert client.get("/api/villages/999999").status_code == 404


def test_invalid_road_status_is_rejected():
    road_id, _ = seed_data()

    response = client.put(
        f"/api/roads/{road_id}/status",
        json={"status": "closed"},
    )

    assert response.status_code == 422
