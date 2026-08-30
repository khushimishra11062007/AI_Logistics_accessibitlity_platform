from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.enums import RiskLevel
from app.models.risk_prediction import RiskPrediction
from app.schemas.risk import RiskPredictionInput, RiskPredictionResponse
from app.services.ai_service import generate_placeholder_risk_prediction

router = APIRouter(prefix="/api/risk", tags=["Risk"])


@router.post(
    "/predict",
    response_model=RiskPredictionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a landslide risk prediction",
    description="Generate a landslide risk score using the current ML pipeline. The API contract remains stable while the underlying model implementation can be replaced later.",
)
async def predict_risk(payload: RiskPredictionInput, db: Session = Depends(get_db)):
    try:
        result = generate_placeholder_risk_prediction(payload)
    except Exception as exc:
        if "ML model is not trained" in str(exc):
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
        raise

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

    return RiskPredictionResponse(
        id=prediction.id,
        latitude=prediction.latitude,
        longitude=prediction.longitude,
        rainfall_1h=prediction.rainfall_1h,
        rainfall_6h=prediction.rainfall_6h,
        rainfall_24h=prediction.rainfall_24h,
        soil_moisture=prediction.soil_moisture,
        slope=prediction.slope,
        elevation=prediction.elevation,
        historical_landslides=prediction.historical_landslides,
        risk_score=prediction.risk_score,
        risk_level=prediction.risk_level,
        model_confidence=prediction.model_confidence,
        prediction_time=prediction.prediction_time,
    )


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

    return RiskPredictionResponse(
        id=latest.id,
        latitude=latest.latitude,
        longitude=latest.longitude,
        rainfall_1h=latest.rainfall_1h,
        rainfall_6h=latest.rainfall_6h,
        rainfall_24h=latest.rainfall_24h,
        soil_moisture=latest.soil_moisture,
        slope=latest.slope,
        elevation=latest.elevation,
        historical_landslides=latest.historical_landslides,
        risk_score=latest.risk_score,
        risk_level=latest.risk_level,
        model_confidence=latest.model_confidence,
        prediction_time=latest.prediction_time,
    )


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

    return [
        RiskPredictionResponse(
            id=row.id,
            latitude=row.latitude,
            longitude=row.longitude,
            rainfall_1h=row.rainfall_1h,
            rainfall_6h=row.rainfall_6h,
            rainfall_24h=row.rainfall_24h,
            soil_moisture=row.soil_moisture,
            slope=row.slope,
            elevation=row.elevation,
            historical_landslides=row.historical_landslides,
            risk_score=row.risk_score,
            risk_level=row.risk_level,
            model_confidence=row.model_confidence,
            prediction_time=row.prediction_time,
        )
        for row in rows
    ]
