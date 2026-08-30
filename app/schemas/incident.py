from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from app.models.enums import IncidentStatus, IncidentType, Severity


class IncidentBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: IncidentType = Field(..., description="Incident category")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude of the incident")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude of the incident")
    severity: Severity = Field(..., description="Incident severity")
    description: str = Field(..., min_length=1, max_length=5000, description="Description of the report")
    image_url: str | None = Field(default=None, max_length=500, description="Optional image URL for evidence")


class IncidentCreate(IncidentBase):
    status: IncidentStatus | None = Field(default=None, description="Optional incident status; defaults to ACTIVE")


class IncidentUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: IncidentType | None = Field(default=None, description="Updated incident category")
    latitude: float | None = Field(default=None, ge=-90, le=90, description="Updated latitude")
    longitude: float | None = Field(default=None, ge=-180, le=180, description="Updated longitude")
    severity: Severity | None = Field(default=None, description="Updated severity")
    description: str | None = Field(default=None, min_length=1, max_length=5000, description="Updated description")
    image_url: str | None = Field(default=None, max_length=500, description="Updated image URL")
    status: IncidentStatus | None = Field(default=None, description="Updated incident status")
    ai_classification: str | None = Field(default=None, max_length=150)
    ai_confidence: float | None = Field(default=None, ge=0, le=1)


class IncidentResponse(IncidentBase):
    id: int
    status: IncidentStatus
    reported_by: int | None = None
    created_at: datetime
    updated_at: datetime
    ai_classification: str | None = None
    ai_confidence: float | None = None
