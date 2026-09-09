const API_BASE_URL = "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const detail = Array.isArray(payload?.detail)
      ? payload.detail.map((error) => error.msg).join(", ")
      : payload?.detail;
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  return payload;
}

export function checkBackend() {
  return request("/health");
}

export function getBackendStatus() {
  return request("/");
}

export function listIncidents(filters = {}) {
  const query = new URLSearchParams();
  const supportedFilters = ["type", "severity", "status", "district"];

  for (const filter of supportedFilters) {
    if (filters[filter] !== undefined && filters[filter] !== null && filters[filter] !== "") {
      query.set(filter, filters[filter]);
    }
  }

  const queryString = query.toString();
  return request(`/api/incidents${queryString ? `?${queryString}` : ""}`);
}

export function getIncident(incidentId) {
  return request(`/api/incidents/${incidentId}`);
}

export function createIncident(incident) {
  return request("/api/incidents", {
    method: "POST",
    body: JSON.stringify(incident),
  });
}

export function updateIncident(incidentId, updates) {
  return request(`/api/incidents/${incidentId}`, {
    method: "PUT",
    body: JSON.stringify(updates),
  });
}

export function predictRisk(input) {
  return request("/api/risk/predict", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function getCurrentRisk() {
  return request("/api/risk/current");
}

export function getRiskForecast(limit = 5) {
  const query = new URLSearchParams({ limit: String(limit) });
  return request(`/api/risk/forecast?${query.toString()}`);
}

export function listRoads() {
  return request("/api/roads");
}

export function getRoad(roadId) {
  return request(`/api/roads/${roadId}`);
}

export function updateRoadStatus(roadId, status) {
  return request(`/api/roads/${roadId}/status`, {
    method: "PUT",
    body: JSON.stringify({ status }),
  });
}

export function listVillages(filters = {}) {
  const query = new URLSearchParams();
  const supportedFilters = ["state", "district", "risk_level"];

  for (const filter of supportedFilters) {
    if (filters[filter] !== undefined && filters[filter] !== null && filters[filter] !== "") {
      query.set(filter, filters[filter]);
    }
  }

  const queryString = query.toString();
  return request(`/api/villages${queryString ? `?${queryString}` : ""}`);
}

export function getVillage(villageId) {
  return request(`/api/villages/${villageId}`);
}

export function listAlerts() {
  return request("/api/alerts");
}

export function createAlert(alert) {
  return request("/api/alerts", {
    method: "POST",
    body: JSON.stringify(alert),
  });
}

export function generateAlert(input) {
  return request("/api/alerts/generate", {
    method: "POST",
    body: JSON.stringify(input),
  });
}