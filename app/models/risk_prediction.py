from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import RiskLevel


class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    rainfall_1h: Mapped[float | None] = mapped_column(Float)
    rainfall_6h: Mapped[float | None] = mapped_column(Float)
    rainfall_24h: Mapped[float | None] = mapped_column(Float)
    soil_moisture: Mapped[float | None] = mapped_column(Float)
    slope: Mapped[float | None] = mapped_column(Float)
    elevation: Mapped[float | None] = mapped_column(Float)
    historical_landslides: Mapped[int | None] = mapped_column(Integer)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    risk_level: Mapped[RiskLevel] = mapped_column(nullable=False, index=True)
    model_confidence: Mapped[float | None] = mapped_column(Float)
    prediction_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
