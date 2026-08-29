from datetime import datetime

from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import RoadStatus


class Road(Base):
    __tablename__ = "roads"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    start_lat: Mapped[float] = mapped_column(Float, nullable=False)
    start_lon: Mapped[float] = mapped_column(Float, nullable=False)
    end_lat: Mapped[float] = mapped_column(Float, nullable=False)
    end_lon: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[RoadStatus] = mapped_column(default=RoadStatus.OPEN, nullable=False, index=True)
    risk_score: Mapped[float | None] = mapped_column(Float, index=True)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True,
    )
