from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    RESPONDER = "responder"
    CITIZEN = "citizen"
    ANALYST = "analyst"


class IncidentType(str, Enum):
    LANDSLIDE = "landslide"
    FLOOD = "flood"
    ROAD_BLOCKAGE = "road_blockage"
    SLOPE_FAILURE = "slope_failure"
    INFRASTRUCTURE_DAMAGE = "infrastructure_damage"
    OTHER = "other"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    ACTIVE = "active"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class AlertTarget(str, Enum):
    DISTRICT = "district"
    VILLAGE = "village"
    ROAD = "road"
    ALL = "all"


class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class SensorType(str, Enum):
    RAIN_GAUGE = "rain_gauge"
    SOIL_MOISTURE = "soil_moisture"
    SLOPE = "slope"
    WATER_LEVEL = "water_level"
    OTHER = "other"


class SensorStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class RoadStatus(str, Enum):
    OPEN = "open"
    BLOCKED = "blocked"
    PARTIALLY_BLOCKED = "partially_blocked"
    CLOSED = "closed"
