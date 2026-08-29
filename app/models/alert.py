from datetime import datetime

from sqlalchemy import DateTime, Float, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import AlertStatus, AlertTarget, Severity


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    severity: Mapped[Severity] = mapped_column(nullable=False, index=True)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    target: Mapped[AlertTarget | None] = mapped_column(index=True)
    status: Mapped[AlertStatus] = mapped_column(default=AlertStatus.ACTIVE, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
