from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.road import Road
from app.schemas.road import RoadResponse, RoadStatusUpdate


router = APIRouter(prefix="/api/roads", tags=["Roads"])


@router.get(
    "",
    response_model=list[RoadResponse],
    summary="List roads",
    description="Return all roads and their current accessibility status.",
)
async def list_roads(db: Session = Depends(get_db)) -> list[Road]:
    return list(db.execute(select(Road).order_by(Road.name)).scalars().all())


@router.get(
    "/{road_id}",
    response_model=RoadResponse,
    summary="Get a road",
    description="Return one road by its database ID.",
)
async def get_road(road_id: int, db: Session = Depends(get_db)) -> Road:
    road = db.get(Road, road_id)
    if road is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Road not found")
    return road


@router.put(
    "/{road_id}/status",
    response_model=RoadResponse,
    summary="Update road status",
    description="Update the accessibility status of a road.",
)
async def update_road_status(
    road_id: int,
    payload: RoadStatusUpdate,
    db: Session = Depends(get_db),
) -> Road:
    road = db.get(Road, road_id)
    if road is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Road not found")

    road.status = payload.status
    db.commit()
    db.refresh(road)
    return road
