from dataclasses import dataclass

from app.ml.predict import predict_risk as run_ml_prediction
from app.models.enums import RiskLevel
from app.schemas.risk import RiskPredictionInput


class ModelNotTrainedError(RuntimeError):
    pass


@dataclass
class RiskPredictionResult:
    risk_score: float
    risk_level: RiskLevel
    model_confidence: float


def generate_placeholder_risk_prediction(payload: RiskPredictionInput) -> RiskPredictionResult:
    """Generate a risk prediction using the replaceable ML pipeline.

    Do not change the public API contract. The route continues to call this function, but the
    implementation now delegates to the trained ML model under app/ml.
    """
    try:
        raw_result = run_ml_prediction(payload.model_dump())
    except FileNotFoundError as exc:
        raise ModelNotTrainedError("ML model is not trained. Run the training script first.") from exc

    return RiskPredictionResult(
        risk_score=raw_result["risk_score"],
        risk_level=RiskLevel(raw_result["risk_level"].lower()),
        model_confidence=raw_result["model_confidence"],
    )
