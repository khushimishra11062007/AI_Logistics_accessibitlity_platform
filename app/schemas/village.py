from pydantic import BaseModel, ConfigDict

from app.models.enums import RiskLevel


class VillageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    district: str
    state: str
    latitude: float
    longitude: float
    population: int | None = None
    risk_level: RiskLevel
