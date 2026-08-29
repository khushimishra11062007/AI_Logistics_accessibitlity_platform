from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import health_router
from app.utils.error_handlers import register_error_handlers


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="NER-SAFE backend foundation for disaster monitoring and emergency response intelligence.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_error_handlers(app)
    app.include_router(health_router)

    @app.get("/")
    async def root() -> dict:
        return {"message": "NER-SAFE Backend is running", "status": "online"}

    return app


app = create_app()
