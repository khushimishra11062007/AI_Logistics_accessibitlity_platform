# NER-SAFE API Documentation

## Base URL

```text
http://localhost:8000
```

Interactive documentation:

- Swagger UI: `GET /docs`
- OpenAPI schema: `GET /openapi.json`
- ReDoc: `GET /redoc`

The current API does not require authentication.

## Common response format

Successful responses return JSON. Validation and application errors use:

```json
{
  "detail": "Error message"
}
```

Validation errors return HTTP `422` and include a list under `detail`.

---

## 1. System endpoints

### `GET /`

Returns the backend status.

Response `200 OK`:

```json
{
  "message": "NER-SAFE Backend is running",
  "status": "online"
}
```

### `GET /health`

Checks service health.

Response `200 OK`:

```json
{
  "status": "healthy"
}
```

---

## 2. Incident APIs

### `GET /api/incidents`

Returns incident reports. All query parameters are optional.

Query parameters:

| Parameter | Type | Allowed values | Description |
| --- | --- | --- | --- |
| `type` | string | `landslide`, `flood`, `road_blockage`, `slope_failure`, `infrastructure_damage`, `other` | Filter by incident type |
| `severity` | string | `low`, `medium`, `high`, `critical` | Filter by severity |
| `status` | string | `active`, `open`, `in_progress`, `resolved`, `closed` | Filter by incident status |
| `district` | string | Any text | Searches the incident description |

Example:

```text
GET /api/incidents?type=landslide&severity=high&status=active
```

Response `200 OK`:

```json
[
  {
    "id": 1,
    "type": "landslide",
    "latitude": 27.123,
    "longitude": 93.456,
    "severity": "high",
    "description": "Large crack observed near a road cut.",
    "image_url": "https://example.com/incident.jpg",
    "status": "active",
    "reported_by": null,
    "created_at": "2026-09-06T10:30:00Z",
    "updated_at": "2026-09-06T10:30:00Z",
    "ai_classification": null,
    "ai_confidence": null
  }
]
```

### `GET /api/incidents/{incident_id}`

Returns one incident.

Response `200 OK`: same object shape as the list response.

Response `404 Not Found`:

```json
{
  "detail": "Incident not found"
}
```

### `POST /api/incidents`

Creates an incident report.

Request body:

```json
{
  "type": "landslide",
  "latitude": 27.123,
  "longitude": 93.456,
  "severity": "high",
  "description": "Large crack observed near a road cut.",
  "image_url": "https://example.com/incident.jpg",
  "status": "active"
}
```

Required fields: `type`, `latitude`, `longitude`, `severity`, `description`.

Optional fields:

- `image_url`: maximum 500 characters
- `status`: defaults to `active`

Response `201 Created`: returns the created incident object.

### `PUT /api/incidents/{incident_id}`

Updates an incident. Every field is optional; only supplied fields are changed.

Request body example:

```json
{
  "status": "in_progress",
  "description": "Road-clearing team has been dispatched.",
  "ai_classification": "landslide",
  "ai_confidence": 0.87
}
```

Response `200 OK`: returns the updated incident object.

---

## 3. Risk management APIs

Risk prediction currently uses a replaceable placeholder calculation. It is not scientifically
validated and can later be replaced by the AI/ML implementation without changing the API contract.

Risk levels:

- `low`: score `0-30`
- `moderate`: score `31-60`
- `high`: score `61-80`
- `critical`: score `81-100`

### `POST /api/risk/predict`

Creates and stores a risk prediction.

Request body:

```json
{
  "latitude": 27.12,
  "longitude": 93.52,
  "rainfall_1h": 25,
  "rainfall_6h": 90,
  "rainfall_24h": 160,
  "soil_moisture": 72,
  "slope": 42,
  "elevation": 1800,
  "historical_landslides": 5
}
```

Validation:

- `latitude`: `-90` to `90`
- `longitude`: `-180` to `180`
- rainfall values: minimum `0`
- `soil_moisture`: `0` to `100`
- `slope`: `0` to `90`
- `elevation`: minimum `-500`
- `historical_landslides`: minimum `0`

Response `201 Created`:

```json
{
  "id": 1,
  "latitude": 27.12,
  "longitude": 93.52,
  "rainfall_1h": 25,
  "rainfall_6h": 90,
  "rainfall_24h": 160,
  "soil_moisture": 72,
  "slope": 42,
  "elevation": 1800,
  "historical_landslides": 5,
  "risk_score": 68.42,
  "risk_level": "high",
  "model_confidence": 0.5,
  "prediction_time": "2026-09-06T10:35:00Z"
}
```

### `GET /api/risk/current`

Returns the most recent stored prediction.

Response `200 OK`: returns one risk prediction object.

Response `404 Not Found`:

```json
{
  "detail": "No risk prediction found"
}
```

### `GET /api/risk/forecast`

Returns recent stored predictions, newest first.

Query parameters:

| Parameter | Type | Default | Allowed values |
| --- | --- | --- | --- |
| `limit` | integer | `5` | `1` to `20` |

Example:

```text
GET /api/risk/forecast?limit=10
```

Response `200 OK`:

```json
[
  {
    "id": 1,
    "latitude": 27.12,
    "longitude": 93.52,
    "rainfall_1h": 25,
    "rainfall_6h": 90,
    "rainfall_24h": 160,
    "soil_moisture": 72,
    "slope": 42,
    "elevation": 1800,
    "historical_landslides": 5,
    "risk_score": 68.42,
    "risk_level": "high",
    "model_confidence": 0.5,
    "prediction_time": "2026-09-06T10:35:00Z"
  }
]
```

---

## 4. Road APIs

Road status values:

- `open`
- `partially_blocked`
- `high_risk`
- `blocked`

### `GET /api/roads`

Returns all roads ordered by name.

Response `200 OK`:

```json
[
  {
    "id": 1,
    "name": "Mountain Link",
    "start_lat": 27.1,
    "start_lon": 93.4,
    "end_lat": 27.2,
    "end_lon": 93.5,
    "status": "open",
    "risk_score": 12.5,
    "last_updated": "2026-09-06T10:40:00Z"
  }
]
```

### `GET /api/roads/{road_id}`

Returns one road.

Response `200 OK`: returns one road object.

Response `404 Not Found`:

```json
{
  "detail": "Road not found"
}
```

### `PUT /api/roads/{road_id}/status`

Updates only the status of a road.

Request body:

```json
{
  "status": "high_risk"
}
```

Response `200 OK`: returns the updated road object.

Invalid status values return `422 Unprocessable Entity`.

---

## 5. Village APIs

Village risk-level values:

- `low`
- `moderate`
- `high`
- `critical`

### `GET /api/villages`

Returns villages ordered by name. All filters are optional and can be combined.

Query parameters:

| Parameter | Type | Description |
| --- | --- | --- |
| `state` | string | Filter by exact state name |
| `district` | string | Filter by exact district name |
| `risk_level` | string | Filter by `low`, `moderate`, `high`, or `critical` |

Example:

```text
GET /api/villages?state=Arunachal%20Pradesh&district=Papum%20Pare&risk_level=high
```

Response `200 OK`:

```json
[
  {
    "id": 1,
    "name": "Hill Village",
    "district": "Papum Pare",
    "state": "Arunachal Pradesh",
    "latitude": 27.2,
    "longitude": 93.6,
    "population": 1200,
    "risk_level": "high"
  }
]
```

### `GET /api/villages/{village_id}`

Returns one village.

Response `200 OK`: returns one village object.

Response `404 Not Found`:

```json
{
  "detail": "Village not found"
}
```

---

## HTTP status codes

| Status | Meaning |
| --- | --- |
| `200` | Request completed successfully |
| `201` | Resource created successfully |
| `404` | Requested record does not exist |
| `422` | Request validation failed |
| `500` | Unexpected server error |
