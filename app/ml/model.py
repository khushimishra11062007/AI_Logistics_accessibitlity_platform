from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.ml.preprocessing import FEATURE_COLUMNS
from app.models.enums import RiskLevel

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "models" / "landslide_model.pkl"
SCALER_PATH = BASE_DIR / "models" / "scaler.pkl"


def risk_score_to_level(score: float) -> RiskLevel:
    if score <= 30:
        return RiskLevel.LOW
    if score <= 60:
        return RiskLevel.MODERATE
    if score <= 80:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


def get_feature_importance(model, feature_names: list[str] | None = None) -> dict[str, float]:
    if not hasattr(model, "feature_importances_"):
        return {}
    names = feature_names or FEATURE_COLUMNS
    importances = model.feature_importances_
    return {name: float(value) for name, value in zip(names, importances)}


def ensure_model_files_exist() -> None:
    if not MODEL_PATH.exists() or not SCALER_PATH.exists():
        raise FileNotFoundError("ML model is not trained. Run the training script first.")


def load_model_artifacts():
    import joblib

    ensure_model_files_exist()
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    return model, scaler


def predict_risk(features: dict) -> dict:
    model, scaler = load_model_artifacts()

    missing = [column for column in FEATURE_COLUMNS if column not in features]
    if missing:
        raise ValueError(f"Missing required feature values: {missing}")

    row = pd.DataFrame([features], columns=FEATURE_COLUMNS)
    transformed = scaler.transform(row[FEATURE_COLUMNS])
    probability = model.predict_proba(transformed)[0, 1]
    risk_score = int(round(float(probability * 100), 0))
    risk_level = risk_score_to_level(risk_score)
    model_confidence = float(max(probability, 1.0 - probability))

    return {
        "risk_score": max(0, min(100, risk_score)),
        "risk_level": risk_level,
        "model_confidence": round(model_confidence, 4),
    }
