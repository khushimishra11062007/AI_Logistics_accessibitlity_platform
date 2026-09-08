from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.emergency import EmergencyPriorityResponse
from app.services.emergency_service import build_priority_list


router = APIRouter(prefix="/api/emergency", tags=["Emergency"])


@router.get(
    "/priorities",
    response_model=list[EmergencyPriorityResponse],
    summary="Get emergency response priorities",
    description="Rank village locations using risk, population, road accessibility, and active incident severity.",
)
async def get_emergency_priorities(
    db: Session = Depends(get_db),
) -> list[dict]:
    return build_priority_list(db)
