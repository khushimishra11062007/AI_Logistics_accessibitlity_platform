from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import AlertStatus, AlertTarget, RiskLevel


class AlertCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    message: str = Field(..., min_length=1, max_length=500)
    severity: RiskLevel
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    target: AlertTarget | None = None
    status: AlertStatus = AlertStatus.ACTIVE


class AlertGenerationRequest(BaseModel):
    risk_score: float = Field(..., ge=0, le=100)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    target: AlertTarget = AlertTarget.ALL


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    message: str
    severity: RiskLevel
    latitude: float | None = None
    longitude: float | None = None
    target: AlertTarget | None = None
    status: AlertStatus
    created_at: datetime
