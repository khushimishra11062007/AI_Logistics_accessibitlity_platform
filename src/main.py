from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.app.api.routes import router

app = FastAPI(title="AI Smart Logistics Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "AI Smart Logistics Backend is running"}