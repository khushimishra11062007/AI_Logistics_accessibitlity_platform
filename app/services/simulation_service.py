from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.models.enums import AlertTarget, RiskLevel, RoadStatus
from app.models.risk_prediction import RiskPrediction
from app.models.road import Road
from app.models.village import Village
from app.schemas.alert import AlertGenerationRequest
from app.schemas.risk import RiskPredictionInput
from app.services.alert_service import generate_alert
from app.services.ai_service import generate_placeholder_risk_prediction
from app.services.emergency_service import build_priority_list


@dataclass
class SimulationSnapshot:
    villages: dict[int, RiskLevel]
    predictions: dict[int, dict]
    roads: dict[int, tuple[RoadStatus, float | None]]
    alert_ids: set[int]


_baseline: SimulationSnapshot | None = None


def _take_snapshot(db: Session) -> SimulationSnapshot:
    villages = {
        village.id: village.risk_level
        for village in db.execute(select(Village)).scalars().all()
    }
    predictions = {}
    for prediction in db.execute(select(RiskPrediction)).scalars().all():
        predictions[prediction.id] = {
            "latitude": prediction.latitude,
            "longitude": prediction.longitude,
            "rainfall_1h": prediction.rainfall_1h,
            "rainfall_6h": prediction.rainfall_6h,
            "rainfall_24h": prediction.rainfall_24h,
            "soil_moisture": prediction.soil_moisture,
            "slope": prediction.slope,
            "elevation": prediction.elevation,
            "historical_landslides": prediction.historical_landslides,
            "risk_score": prediction.risk_score,
            "risk_level": prediction.risk_level,
            "model_confidence": prediction.model_confidence,
        }
    roads = {
        road.id: (road.status, road.risk_score)
        for road in db.execute(select(Road)).scalars().all()
    }
    alert_ids = {alert.id for alert in db.execute(select(Alert)).scalars().all()}
    return SimulationSnapshot(villages, predictions, roads, alert_ids)


def _nearest_prediction(village: Village, predictions: list[RiskPrediction]) -> RiskPrediction | None:
    if not predictions:
        return None
    return min(
        predictions,
        key=lambda prediction: (village.latitude - prediction.latitude) ** 2
        + (village.longitude - prediction.longitude) ** 2,
    )


def _nearest_road(village: Village, roads: list[Road]) -> Road | None:
    if not roads:
        return None
    return min(
        roads,
        key=lambda road: (village.latitude - (road.start_lat + road.end_lat) / 2) ** 2
        + (village.longitude - (road.start_lon + road.end_lon) / 2) ** 2,
    )


def _risk_level_for_score(score: float) -> RiskLevel:
    if score <= 30:
        return RiskLevel.LOW
    if score <= 60:
        return RiskLevel.MODERATE
    if score <= 80:
        return RiskLevel.HIGH
    return RiskLevel.CRITICAL


def simulate_heavy_rainfall(db: Session) -> dict:
    global _baseline
    if _baseline is None:
        _baseline = _take_snapshot(db)

    villages = list(
        db.execute(select(Village).order_by(Village.population.desc().nullslast())).scalars().all()
    )
    selected_villages = villages[:4]
    predictions = list(db.execute(select(RiskPrediction)).scalars().all())
    roads = list(db.execute(select(Road)).scalars().all())
    alerts_generated = 0
    high_risk_zones = 0
    blocked_roads = 0

    for village in selected_villages:
        prediction = _nearest_prediction(village, predictions)
        if prediction is None:
            prediction = RiskPrediction(
                latitude=village.latitude,
                longitude=village.longitude,
                rainfall_1h=0,
                rainfall_6h=0,
                rainfall_24h=0,
                soil_moisture=0,
                slope=30,
                elevation=1000,
                historical_landslides=0,
                risk_score=0,
                risk_level=RiskLevel.LOW,
                model_confidence=0.5,
            )
            db.add(prediction)
            db.flush()
            predictions.append(prediction)

        input_payload = RiskPredictionInput(
            latitude=prediction.latitude,
            longitude=prediction.longitude,
            rainfall_1h=min((prediction.rainfall_1h or 0) + 50, 500),
            rainfall_6h=min((prediction.rainfall_6h or 0) + 100, 1000),
            rainfall_24h=min((prediction.rainfall_24h or 0) + 200, 2000),
            soil_moisture=min((prediction.soil_moisture or 0) + 20, 100),
            slope=prediction.slope or 30,
            elevation=prediction.elevation or 1000,
            historical_landslides=prediction.historical_landslides or 0,
        )
        result = generate_placeholder_risk_prediction(input_payload)
        prediction.rainfall_1h = input_payload.rainfall_1h
        prediction.rainfall_6h = input_payload.rainfall_6h
        prediction.rainfall_24h = input_payload.rainfall_24h
        prediction.soil_moisture = input_payload.soil_moisture
        prediction.risk_score = result.risk_score
        prediction.risk_level = result.risk_level
        prediction.model_confidence = result.model_confidence
        village.risk_level = result.risk_level

        if result.risk_level in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
            high_risk_zones += 1
        if result.risk_level == RiskLevel.CRITICAL:
            generate_alert(
                AlertGenerationRequest(
                    risk_score=result.risk_score,
                    latitude=village.latitude,
                    longitude=village.longitude,
                    target=AlertTarget.VILLAGE,
                ),
                db,
            )
            alerts_generated += 1

        road = _nearest_road(village, roads)
        if road is not None:
            road.risk_score = result.risk_score
            if result.risk_level == RiskLevel.CRITICAL:
                road.status = RoadStatus.BLOCKED
                blocked_roads += 1
            elif result.risk_level == RiskLevel.HIGH:
                road.status = RoadStatus.HIGH_RISK

    build_priority_list(db)
    db.commit()
    return {
        "simulation": "HEAVY_RAINFALL",
        "affected_zones": len(selected_villages),
        "high_risk_zones": high_risk_zones,
        "blocked_roads": blocked_roads,
        "alerts_generated": alerts_generated,
    }


def reset_simulation(db: Session) -> dict:
    global _baseline
    if _baseline is None:
        return {
            "simulation": "RESET",
            "affected_zones": 0,
            "high_risk_zones": 0,
            "blocked_roads": 0,
            "alerts_generated": 0,
        }

    for village in db.execute(select(Village)).scalars().all():
        if village.id in _baseline.villages:
            village.risk_level = _baseline.villages[village.id]

    for prediction in db.execute(select(RiskPrediction)).scalars().all():
        original = _baseline.predictions.get(prediction.id)
        if original is not None:
            for field, value in original.items():
                setattr(prediction, field, value)
        else:
            db.delete(prediction)

    for road in db.execute(select(Road)).scalars().all():
        original = _baseline.roads.get(road.id)
        if original is not None:
            road.status, road.risk_score = original

    for alert in db.execute(select(Alert)).scalars().all():
        if alert.id not in _baseline.alert_ids:
            db.delete(alert)

    db.commit()
    _baseline = None
    return {
        "simulation": "RESET",
        "affected_zones": 0,
        "high_risk_zones": 0,
        "blocked_roads": 0,
        "alerts_generated": 0,
    }
