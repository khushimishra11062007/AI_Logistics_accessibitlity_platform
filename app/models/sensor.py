from datetime import datetime

from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import SensorStatus, SensorType


class Sensor(Base):
    __tablename__ = "sensors"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    sensor_type: Mapped[SensorType] = mapped_column(nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    value: Mapped[float | None] = mapped_column(Float)
    unit: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[SensorStatus] = mapped_column(default=SensorStatus.ACTIVE, nullable=False, index=True)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True,
    )
