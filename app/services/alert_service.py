from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.enums import AlertStatus, AlertTarget, RiskLevel
from app.schemas.alert import AlertCreate, AlertGenerationRequest


def classify_risk_level(risk_score: float) -> RiskLevel:
    if risk_score <= 30:
        return RiskLevel.LOW
    if risk_score <= 60:
        return RiskLevel.MODERATE
    if risk_score <= 80:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


def build_generated_alert(payload: AlertGenerationRequest) -> Alert:
    severity = classify_risk_level(payload.risk_score)
    title = f"{severity.value.capitalize()} Landslide Risk"
    message = (
        f"{severity.value.capitalize()} landslide risk detected with a risk score "
        f"of {payload.risk_score:.2f}."
    )
    return Alert(
        title=title,
        message=message,
        severity=severity,
        latitude=payload.latitude,
        longitude=payload.longitude,
        target=payload.target,
        status=AlertStatus.ACTIVE,
    )


def create_alert(payload: AlertCreate, db: Session) -> Alert:
    alert = Alert(**payload.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def generate_alert(payload: AlertGenerationRequest, db: Session) -> Alert:
    alert = build_generated_alert(payload)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert
