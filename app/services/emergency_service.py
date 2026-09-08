from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import IncidentStatus, RiskLevel, RoadStatus, Severity
from app.models.incident import Incident
from app.models.risk_prediction import RiskPrediction
from app.models.road import Road
from app.models.village import Village


@dataclass
class PriorityComponents:
    risk_score: float
    population: int
    road_status: RoadStatus
    incident_severity: Severity | None


def risk_level_score(risk_level: RiskLevel) -> float:
    return {
        RiskLevel.LOW: 15.0,
        RiskLevel.MODERATE: 45.0,
        RiskLevel.HIGH: 70.0,
        RiskLevel.CRITICAL: 90.0,
    }[risk_level]


def road_accessibility_score(status: RoadStatus) -> float:
    return {
        RoadStatus.OPEN: 0.0,
        RoadStatus.PARTIALLY_BLOCKED: 50.0,
        RoadStatus.HIGH_RISK: 75.0,
        RoadStatus.BLOCKED: 100.0,
    }[status]


def incident_severity_score(severity: Severity | None) -> float:
    return {
        None: 0.0,
        Severity.LOW: 25.0,
        Severity.MEDIUM: 50.0,
        Severity.HIGH: 75.0,
        Severity.CRITICAL: 100.0,
    }[severity]


def calculate_priority_score(components: PriorityComponents) -> float:
    population_score = min(components.population / 10_000 * 100, 100)
    score = (
        components.risk_score * 0.4
        + population_score * 0.2
        + road_accessibility_score(components.road_status) * 0.2
        + incident_severity_score(components.incident_severity) * 0.2
    )
    return round(min(max(score, 0), 100), 2)


def priority_level(priority_score: float) -> str:
    if priority_score >= 70:
        return "P1"
    if priority_score >= 40:
        return "P2"
    return "P3"


def _distance(latitude: float, longitude: float, other_latitude: float, other_longitude: float) -> float:
    return (latitude - other_latitude) ** 2 + (longitude - other_longitude) ** 2


def _nearest_prediction(village: Village, predictions: list[RiskPrediction]) -> RiskPrediction | None:
    if not predictions:
        return None
    return min(
        predictions,
        key=lambda prediction: _distance(
            village.latitude,
            village.longitude,
            prediction.latitude,
            prediction.longitude,
        ),
    )


def _nearest_road(village: Village, roads: list[Road]) -> Road | None:
    if not roads:
        return None
    return min(
        roads,
        key=lambda road: _distance(
            village.latitude,
            village.longitude,
            (road.start_lat + road.end_lat) / 2,
            (road.start_lon + road.end_lon) / 2,
        ),
    )


def _nearest_incident(village: Village, incidents: list[Incident]) -> Incident | None:
    if not incidents:
        return None
    return min(
        incidents,
        key=lambda incident: _distance(
            village.latitude,
            village.longitude,
            incident.latitude,
            incident.longitude,
        ),
    )


def build_priority_list(db: Session) -> list[dict]:
    villages = list(db.execute(select(Village)).scalars().all())
    predictions = list(
        db.execute(select(RiskPrediction).order_by(RiskPrediction.prediction_time.desc())).scalars().all()
    )
    roads = list(db.execute(select(Road)).scalars().all())
    incidents = list(
        db.execute(
            select(Incident).where(
                Incident.status.in_([IncidentStatus.ACTIVE, IncidentStatus.OPEN, IncidentStatus.IN_PROGRESS])
            )
        ).scalars().all()
    )

    priorities = []
    for village in villages:
        prediction = _nearest_prediction(village, predictions)
        road = _nearest_road(village, roads)
        incident = _nearest_incident(village, incidents)
        components = PriorityComponents(
            risk_score=prediction.risk_score if prediction else risk_level_score(village.risk_level),
            population=village.population or 0,
            road_status=road.status if road else RoadStatus.OPEN,
            incident_severity=incident.severity if incident else None,
        )
        score = calculate_priority_score(components)
        priorities.append(
            {
                "location": village.name,
                "priority_score": score,
                "priority_level": priority_level(score),
                "risk_score": round(components.risk_score, 2),
                "population": components.population,
                "road_status": components.road_status.value,
            }
        )

    return sorted(priorities, key=lambda item: item["priority_score"], reverse=True)
