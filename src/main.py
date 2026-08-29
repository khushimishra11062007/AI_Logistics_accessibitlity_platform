from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(title="AI Smart Logistics Backend")
app.include_router(router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "AI Smart Logistics Backend is running"}
