from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.enums import RiskLevel


class Village(Base):
    __tablename__ = "villages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    district: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=False, index=True)
    population: Mapped[int | None] = mapped_column(Integer)
    risk_level: Mapped[RiskLevel] = mapped_column(default=RiskLevel.LOW, nullable=False, index=True)
