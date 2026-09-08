from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertGenerationRequest, AlertResponse
from app.services.alert_service import create_alert, generate_alert


router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get(
    "",
    response_model=list[AlertResponse],
    summary="List alerts",
    description="Return stored alerts ordered from newest to oldest.",
)
async def list_alerts(db: Session = Depends(get_db)) -> list[Alert]:
    return list(db.execute(select(Alert).order_by(Alert.created_at.desc())).scalars().all())


@router.post(
    "",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an alert",
    description="Store a manually created alert. No SMS or WhatsApp notification is sent.",
)
async def create_alert_endpoint(payload: AlertCreate, db: Session = Depends(get_db)) -> Alert:
    return create_alert(payload, db)


@router.post(
    "/generate",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate an alert from risk score",
    description="Generate and store an alert using the placeholder risk-level thresholds.",
)
async def generate_alert_endpoint(
    payload: AlertGenerationRequest,
    db: Session = Depends(get_db),
) -> Alert:
    return generate_alert(payload, db)
