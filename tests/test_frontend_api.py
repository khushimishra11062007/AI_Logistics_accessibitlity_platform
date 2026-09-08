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


def test_frontend_routes_are_registered_and_return_json():
    response = client.get("/api/risk/forecast")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    for path in (
        "/api/incidents",
        "/api/roads",
        "/api/villages",
        "/api/alerts",
        "/api/emergency/priorities",
    ):
        response = client.get(path)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    route_response = client.post(
        "/api/routes/optimize",
        json={
            "origin_latitude": 27.12,
            "origin_longitude": 93.52,
            "destination_latitude": 27.2,
            "destination_longitude": 93.6,
        },
    )
    assert route_response.status_code == 200
    assert route_response.json()["route_status"] in {"available", "no_safe_route"}

    simulation = client.post("/api/simulation/reset")
    assert simulation.status_code == 200
    assert simulation.json()["simulation"] == "RESET"


def test_react_origins_receive_cors_headers():
    response = client.options(
        "/api/alerts",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"
