from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.enums import RiskLevel
from app.models.village import Village
from app.schemas.village import VillageResponse


router = APIRouter(prefix="/api/villages", tags=["Villages"])


@router.get(
    "",
    response_model=list[VillageResponse],
    summary="List villages",
    description="Return villages with optional state, district, and risk-level filters.",
)
async def list_villages(
    state: str | None = Query(default=None, description="Filter by state"),
    district: str | None = Query(default=None, description="Filter by district"),
    risk_level: RiskLevel | None = Query(default=None, description="Filter by risk level"),
    db: Session = Depends(get_db),
) -> list[Village]:
    query = select(Village)
    if state is not None:
        query = query.where(Village.state == state)
    if district is not None:
        query = query.where(Village.district == district)
    if risk_level is not None:
        query = query.where(Village.risk_level == risk_level)

    return list(db.execute(query.order_by(Village.name)).scalars().all())


@router.get(
    "/{village_id}",
    response_model=VillageResponse,
    summary="Get a village",
    description="Return one village by its database ID.",
)
async def get_village(village_id: int, db: Session = Depends(get_db)) -> Village:
    village = db.get(Village, village_id)
    if village is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Village not found")
    return village
