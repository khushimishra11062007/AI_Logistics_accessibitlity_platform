from dataclasses import dataclass

from app.models.enums import RiskLevel
from app.schemas.risk import RiskPredictionInput


@dataclass
class RiskPredictionResult:
    risk_score: float
    risk_level: RiskLevel
    model_confidence: float


def classify_risk_level(risk_score: float) -> RiskLevel:
    if risk_score <= 30:
        return RiskLevel.LOW
    if risk_score <= 60:
        return RiskLevel.MODERATE
    if risk_score <= 80:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


def generate_placeholder_risk_prediction(payload: RiskPredictionInput) -> RiskPredictionResult:
    """Generate a deterministic placeholder score until the real AI model is available.

    The route depends only on this function's result, so an ML implementation can replace this
    calculation later without changing the API contract.
    """
    weighted_score = (
        min(payload.rainfall_1h / 50, 1) * 10
        + min(payload.rainfall_6h / 150, 1) * 15
        + min(payload.rainfall_24h / 300, 1) * 20
        + (payload.soil_moisture / 100) * 15
        + (payload.slope / 60) * 15
        + min(payload.historical_landslides / 10, 1) * 15
        + min(max(payload.elevation, 0) / 3000, 1) * 10
    )
    risk_score = round(min(max(weighted_score, 0), 100), 2)

    return RiskPredictionResult(
        risk_score=risk_score,
        risk_level=classify_risk_level(risk_score),
        model_confidence=0.5,
    )
