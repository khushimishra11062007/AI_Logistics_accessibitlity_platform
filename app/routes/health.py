from fastapi import APIRouter

router = APIRouter()


@router.get(
    "/health",
    tags=["Health"],
    summary="Check service health",
    description="Returns the current availability status of the backend service.",
)
async def health_check() -> dict:
    return {"status": "healthy"}
