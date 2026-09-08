from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.enums import RoadStatus
from app.models.road import Road
from app.schemas.route import RouteOptimizeRequest, RouteOptimizeResponse


router = APIRouter(prefix="/api/routes", tags=["Routes"])


@router.post(
    "/optimize",
    response_model=RouteOptimizeResponse,
    summary="Evaluate a safe route",
    description=(
        "Return currently usable roads for a route request. This frontend-ready placeholder "
        "does not perform network routing or calculate turn-by-turn directions."
    ),
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "origin_latitude": 27.12,
                        "origin_longitude": 93.52,
                        "destination_latitude": 27.20,
                        "destination_longitude": 93.60,
                        "max_risk_score": 80,
                    }
                }
            }
        }
    },
)
async def optimize_route(
    payload: RouteOptimizeRequest,
    db: Session = Depends(get_db),
) -> RouteOptimizeResponse:
    roads = list(
        db.execute(
            select(Road)
            .where(
                Road.status != RoadStatus.BLOCKED,
                (Road.risk_score.is_(None)) | (Road.risk_score <= payload.max_risk_score),
            )
            .order_by(Road.name)
        ).scalars().all()
    )
    route_status = "available" if roads else "no_safe_route"
    message = (
        "Route evaluation completed using available road records."
        if roads
        else "No road records satisfy the requested safety threshold."
    )
    return RouteOptimizeResponse(
        origin={
            "latitude": payload.origin_latitude,
            "longitude": payload.origin_longitude,
        },
        destination={
            "latitude": payload.destination_latitude,
            "longitude": payload.destination_longitude,
        },
        road_ids=[road.id for road in roads],
        route_status=route_status,
        estimated_distance_km=None,
        message=message,
    )
