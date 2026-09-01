from __future__ import annotations

from pydantic import BaseModel, Field


class RouteOptimizationRequest(BaseModel):
    origin: str = Field(..., description="Starting location name or route node.")
    destination: str = Field(..., description="Destination location name or route node.")
    avoid_blocked: bool = Field(default=True, description="Whether blocked roads should be avoided.")
    route_type: str = Field(default="safe", description="Route preference, currently reserved for future route policy logic.")


class RouteOptimizationResponse(BaseModel):
    origin: str
    destination: str
    optimized_route: list[str]
    total_distance_km: float
    estimated_duration_minutes: int
    safety_score: int
    blocked_segments: list[str] = Field(default_factory=list)
    message: str = "Placeholder route optimization result. Replace with real routing logic later."
