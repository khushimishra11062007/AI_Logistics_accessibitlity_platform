from app.routes.health import router as health_router
from app.routes.incidents import router as incidents_router
from app.routes.risk import router as risk_router
from app.routes.routes import router as routes_router

__all__ = ["health_router", "incidents_router", "risk_router", "routes_router"]
