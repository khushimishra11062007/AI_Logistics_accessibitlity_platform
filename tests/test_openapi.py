from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_swagger_ui_is_available():
    response = client.get("/docs")

    assert response.status_code == 200
    assert "Swagger UI" in response.text


def test_openapi_schema_describes_api():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "NER-SAFE Backend"
    assert "/api/risk/predict" in schema["paths"]
    assert "/api/incidents" in schema["paths"]
    assert "/api/roads" in schema["paths"]
    assert "/api/roads/{road_id}/status" in schema["paths"]
    assert "/api/villages" in schema["paths"]
    assert "/api/villages/{village_id}" in schema["paths"]
    assert "/api/alerts" in schema["paths"]
    assert "/api/alerts/generate" in schema["paths"]
    assert "/api/emergency/priorities" in schema["paths"]
    assert schema["paths"]["/health"]["get"]["tags"] == ["Health"]
