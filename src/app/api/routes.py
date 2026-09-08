from fastapi import APIRouter, HTTPException
from typing import Optional

router = APIRouter()

# Temporary in-memory data for frontend integration
incidents = [
    {
        "id": 1,
        "type": "Road Block",
        "latitude": 28.67,
        "longitude": 77.43,
        "severity": "high",
        "description": "Road blocked due to heavy rainfall",
        "status": "active"
    }
]

roads = [
    {
        "id": 1,
        "name": "NH-9",
        "status": "open"
    }
]

villages = [
    {
        "id": 1,
        "name": "Sample Village",
        "district": "Ghaziabad"
    }
]


@router.get("/health")
async def health():
    return {"status": "ok"}


# ---------------- INCIDENTS ----------------

@router.get("/incidents")
async def get_incidents(
    type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    district: Optional[str] = None
):
    return incidents


@router.get("/incidents/{incident_id}")
async def get_incident(incident_id: int):
    for incident in incidents:
        if incident["id"] == incident_id:
            return incident

    raise HTTPException(status_code=404, detail="Incident not found")


@router.post("/incidents")
async def create_incident(payload: dict):
    new_id = len(incidents) + 1

    incident = {
        "id": new_id,
        **payload
    }

    incidents.append(incident)
    return incident


# ---------------- RISK ----------------

@router.post("/risk/predict")
async def predict_risk(payload: dict):
    return {
        "risk_level": "medium",
        "risk_score": 0.5,
        "message": "Risk prediction generated successfully"
    }


@router.get("/risk/current")
async def current_risk():
    return {
        "risk_level": "medium",
        "risk_score": 0.5
    }


@router.get("/risk/forecast")
async def risk_forecast(limit: int = 5):
    return [
        {
            "day": i + 1,
            "risk_level": "medium",
            "risk_score": 0.5
        }
        for i in range(limit)
    ]


# ---------------- ROADS ----------------

@router.get("/roads")
async def get_roads():
    return roads


@router.get("/roads/{road_id}")
async def get_road(road_id: int):
    for road in roads:
        if road["id"] == road_id:
            return road

    raise HTTPException(status_code=404, detail="Road not found")


@router.put("/roads/{road_id}/status")
async def update_road_status(road_id: int, payload: dict):
    for road in roads:
        if road["id"] == road_id:
            road["status"] = payload.get("status", road["status"])
            return road

    raise HTTPException(status_code=404, detail="Road not found")


# ---------------- VILLAGES ----------------

@router.get("/villages")
async def get_villages():
    return villages


@router.get("/villages/{village_id}")
async def get_village(village_id: int):
    for village in villages:
        if village["id"] == village_id:
            return village

    raise HTTPException(status_code=404, detail="Village not found")