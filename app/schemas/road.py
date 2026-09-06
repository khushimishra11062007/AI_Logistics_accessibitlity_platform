from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import RoadStatus


class RoadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    status: RoadStatus
    risk_score: float | None = None
    last_updated: datetime


class RoadStatusUpdate(BaseModel):
    status: RoadStatus
