from pydantic import BaseModel, ConfigDict


class EmergencyPriorityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    location: str
    priority_score: float
    priority_level: str
    risk_score: float
    population: int
    road_status: str
