from app.routes.health import router as health_router
from app.routes.incidents import router as incidents_router
from app.routes.roads import router as roads_router
from app.routes.risk import router as risk_router
from app.routes.villages import router as villages_router

__all__ = ["health_router", "incidents_router", "risk_router", "roads_router", "villages_router"]
