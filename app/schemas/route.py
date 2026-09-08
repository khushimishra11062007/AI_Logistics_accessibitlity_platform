from pydantic import BaseModel, Field


class RouteOptimizeRequest(BaseModel):
    origin_latitude: float = Field(..., ge=-90, le=90)
    origin_longitude: float = Field(..., ge=-180, le=180)
    destination_latitude: float = Field(..., ge=-90, le=90)
    destination_longitude: float = Field(..., ge=-180, le=180)
    max_risk_score: float = Field(default=80, ge=0, le=100)


class RouteOptimizeResponse(BaseModel):
    origin: dict[str, float]
    destination: dict[str, float]
    road_ids: list[int]
    route_status: str
    estimated_distance_km: float | None = None
    message: str
