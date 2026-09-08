from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.simulation import SimulationSummary
from app.services.simulation_service import reset_simulation, simulate_heavy_rainfall


router = APIRouter(prefix="/api/simulation", tags=["Simulation"])


@router.post("/heavy-rainfall", response_model=SimulationSummary)
async def run_heavy_rainfall_simulation(db: Session = Depends(get_db)) -> dict:
    return simulate_heavy_rainfall(db)


@router.post("/reset", response_model=SimulationSummary)
async def reset_demo_simulation(db: Session = Depends(get_db)) -> dict:
    return reset_simulation(db)
