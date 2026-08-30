from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import IncidentStatus, IncidentType, Severity


class Incident(Base):
    __tablename__ = "incidents"
    __table_args__ = (
        {"comment": "Disaster incidents reported by users or systems"},
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    type: Mapped[IncidentType] = mapped_column(nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    severity: Mapped[Severity] = mapped_column(nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500))
    ai_classification: Mapped[str | None] = mapped_column(String(150))
    ai_confidence: Mapped[float | None] = mapped_column(Float)
    status: Mapped[IncidentStatus] = mapped_column(default=IncidentStatus.ACTIVE, nullable=False, index=True)
    reported_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    reporter: Mapped["User"] = relationship(back_populates="reported_incidents")
