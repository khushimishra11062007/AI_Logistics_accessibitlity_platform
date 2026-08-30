from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.enums import IncidentStatus, IncidentType, Severity
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentResponse, IncidentUpdate

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])


@router.get(
    "",
    response_model=list[IncidentResponse],
    summary="List incidents",
    description="List reported incidents with optional filtering by type, severity, and status.",
)
async def list_incidents(
    type: IncidentType | None = Query(default=None, alias="type"),
    severity: Severity | None = None,
    status: IncidentStatus | None = None,
    district: str | None = None,
    db: Session = Depends(get_db),
):
    query = select(Incident)

    if type is not None:
        query = query.where(Incident.type == type)
    if severity is not None:
        query = query.where(Incident.severity == severity)
    if status is not None:
        query = query.where(Incident.status == status)
    if district is not None:
        query = query.where(Incident.description.ilike(f"%{district}%"))

    query = query.order_by(Incident.created_at.desc())
    incidents = db.execute(query).scalars().all()
    return incidents


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
    summary="Get an incident by ID",
    description="Retrieve a single incident report by its database ID.",
)
async def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")
    return incident


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Report an incident",
    description="Create a new incident report for a citizen or field officer.",
)
async def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    incident_data = payload.model_dump(exclude_none=True)
    if "status" not in incident_data or incident_data["status"] is None:
        incident_data["status"] = IncidentStatus.ACTIVE

    incident = Incident(**incident_data)
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


@router.put(
    "/{incident_id}",
    response_model=IncidentResponse,
    summary="Update an incident",
    description="Update an existing incident report. Use this to change status or amend the details.",
)
async def update_incident(
    incident_id: int,
    payload: IncidentUpdate,
    db: Session = Depends(get_db),
):
    incident = db.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    update_data = payload.model_dump(exclude_unset=True, exclude_none=True)
    for field, value in update_data.items():
        setattr(incident, field, value)

    db.commit()
    db.refresh(incident)
    return incident
