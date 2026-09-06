from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.risk_prediction import RiskPrediction
from app.schemas.risk import RiskPredictionInput, RiskPredictionResponse
from app.services.ai_service import generate_placeholder_risk_prediction

router = APIRouter(prefix="/api/risk", tags=["Risk"])


@router.post(
    "/predict",
    response_model=RiskPredictionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a landslide risk prediction",
    description="Generate and store a placeholder landslide risk score. This calculation is not scientifically validated and will be replaced by the AI model.",
)
async def predict_risk(payload: RiskPredictionInput, db: Session = Depends(get_db)):
    result = generate_placeholder_risk_prediction(payload)
    prediction = RiskPrediction(
        latitude=payload.latitude,
        longitude=payload.longitude,
        rainfall_1h=payload.rainfall_1h,
        rainfall_6h=payload.rainfall_6h,
        rainfall_24h=payload.rainfall_24h,
        soil_moisture=payload.soil_moisture,
        slope=payload.slope,
        elevation=payload.elevation,
        historical_landslides=payload.historical_landslides,
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        model_confidence=result.model_confidence,
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)

    return prediction


@router.get(
    "/current",
    response_model=RiskPredictionResponse,
    summary="Get latest risk prediction",
    description="Returns the most recent saved risk prediction for the dataset using the latest database record.",
)
async def get_current_risk(db: Session = Depends(get_db)):
    latest = db.execute(
        select(RiskPrediction).order_by(RiskPrediction.prediction_time.desc()).limit(1)
    ).scalar_one_or_none()

    if latest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No risk prediction found")

    return latest


@router.get(
    "/forecast",
    response_model=list[RiskPredictionResponse],
    summary="Get forecast risk history",
    description="Returns recent stored risk predictions as a simple forecast history list. Replace this in a future iteration with a more advanced forecast model.",
)
async def get_risk_forecast(
    limit: int = Query(default=5, ge=1, le=20, description="Maximum number of recent risk predictions to return"),
    db: Session = Depends(get_db),
):
    rows = db.execute(
        select(RiskPrediction).order_by(RiskPrediction.prediction_time.desc()).limit(limit)
    ).scalars().all()

    return rows
