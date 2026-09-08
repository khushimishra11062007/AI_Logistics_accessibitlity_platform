from app.routes.alerts import router as alerts_router
from app.routes.emergency import router as emergency_router
from app.routes.health import router as health_router
from app.routes.incidents import router as incidents_router
from app.routes.roads import router as roads_router
from app.routes.simulation import router as simulation_router
from app.routes.risk import router as risk_router
from app.routes.villages import router as villages_router

__all__ = [
    "alerts_router",
    "emergency_router",
    "health_router",
    "incidents_router",
    "risk_router",
    "roads_router",
    "simulation_router",
    "villages_router",
]
