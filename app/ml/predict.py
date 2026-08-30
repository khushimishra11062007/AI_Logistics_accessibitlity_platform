from __future__ import annotations

from app.ml.model import predict_risk as _predict_risk


def predict_risk(features: dict) -> dict:
    """Wrap the trained model and return a ML-based risk prediction.

    This function is the dedicated ML prediction interface. The API routes should call this
    function via ai_service.py, not call model internals directly.
    """
    return _predict_risk(features)
