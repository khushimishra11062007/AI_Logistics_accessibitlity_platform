from fastapi import APIRouter, HTTPException, status

from app.schemas.route import RouteOptimizationRequest, RouteOptimizationResponse
from app.services.routing_service import optimize_route

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.post(
    "/optimize",
    response_model=RouteOptimizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Optimize a safe route",
    description="Returns a placeholder route optimization result. This endpoint is intentionally lightweight and can later be replaced by a real routing engine.",
)
async def optimize_route_endpoint(payload: RouteOptimizationRequest):
    try:
        result = optimize_route(payload.origin, payload.destination, payload.avoid_blocked)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return RouteOptimizationResponse(**result)
