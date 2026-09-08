from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.routes import (
    alerts_router,
    emergency_router,
    health_router,
    incidents_router,
    risk_router,
    roads_router,
    routes_router,
    simulation_router,
    villages_router,
)
from app.utils.error_handlers import register_error_handlers


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="NER-SAFE backend foundation for disaster monitoring and emergency response intelligence.",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=[
            {
                "name": "Health",
                "description": "Service health and availability checks.",
            },
            {
                "name": "Alerts",
                "description": "Stored risk alerts and placeholder alert generation.",
            },
            {
                "name": "Incidents",
                "description": "Citizen and field-team incident reporting.",
            },
            {
                "name": "Emergency",
                "description": "Emergency response prioritization.",
            },
            {
                "name": "Risk",
                "description": "Landslide risk prediction and forecast history.",
            },
            {
                "name": "Roads",
                "description": "Road accessibility and status monitoring.",
            },
            {
                "name": "Routes",
                "description": "Frontend-ready route safety evaluation.",
            },
            {
                "name": "Villages",
                "description": "Village locations, population, and risk-level monitoring.",
            },
            {
                "name": "Simulation",
                "description": "Demo-only disaster simulation controls.",
            },
        ],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def startup_event() -> None:
        init_db()

    register_error_handlers(app)
    app.include_router(alerts_router)
    app.include_router(emergency_router)
    app.include_router(health_router)
    app.include_router(incidents_router)
    app.include_router(risk_router)
    app.include_router(roads_router)
    app.include_router(routes_router)
    app.include_router(simulation_router)
    app.include_router(villages_router)

    @app.get("/")
    async def root() -> dict:
        return {"message": "NER-SAFE Backend is running", "status": "online"}

    return app


app = create_app()
