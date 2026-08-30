from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import RiskLevel


class RiskPredictionInput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    latitude: float = Field(..., ge=-90, le=90, description="Latitude of the location")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude of the location")
    rainfall_1h: float = Field(..., ge=0, description="Rainfall in the last 1 hour (mm)")
    rainfall_6h: float = Field(..., ge=0, description="Rainfall in the last 6 hours (mm)")
    rainfall_24h: float = Field(..., ge=0, description="Rainfall in the last 24 hours (mm)")
    soil_moisture: float = Field(..., ge=0, le=100, description="Soil moisture percentage")
    slope: float = Field(..., ge=0, le=90, description="Slope angle in degrees")
    elevation: float = Field(..., ge=-500, description="Elevation in meters")
    historical_landslides: int = Field(..., ge=0, description="Count of historical landslides in that region")


class RiskPredictionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    latitude: float
    longitude: float
    rainfall_1h: float | None = None
    rainfall_6h: float | None = None
    rainfall_24h: float | None = None
    soil_moisture: float | None = None
    slope: float | None = None
    elevation: float | None = None
    historical_landslides: int | None = None
    risk_score: float
    risk_level: RiskLevel
    model_confidence: float | None = None
    prediction_time: datetime | None = None


class RiskForecastResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    current: RiskPredictionResponse | None = None
    forecast: list[RiskPredictionResponse] = []
