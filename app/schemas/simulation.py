from pydantic import BaseModel


class SimulationSummary(BaseModel):
    simulation: str
    affected_zones: int
    high_risk_zones: int
    blocked_roads: int
    alerts_generated: int
