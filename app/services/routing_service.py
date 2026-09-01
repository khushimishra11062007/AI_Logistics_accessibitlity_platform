from __future__ import annotations

import networkx as nx


def _build_mock_road_network():
    """Build a small controlled road network for safe-routing tests.

    Edge format: (from, to, distance, status)
    Statuses: open, blocked, high_risk.
    """
    edges = [
        ("A", "B", 2.0, "blocked"),
        ("B", "D", 2.0, "open"),
        ("A", "C", 3.0, "high_risk"),
        ("C", "D", 2.0, "open"),
        ("A", "D", 6.0, "open"),
    ]
    return edges


def _edge_penalty(status: str) -> float:
    status_map = {
        "open": 0,
        "high_risk": 150,
        "blocked": 100000,
    }
    return status_map.get(status, 0)


def optimize_route(origin: str, destination: str, avoid_blocked: bool = True) -> dict:
    """Choose the lowest-cost safe route from a simple controlled road graph.

    Blocked roads are removed when avoid_blocked is True. High-risk roads are heavily penalized
    but still available if no safer route exists. This keeps the logic simple while making the
    safer path choice visible and testable.
    """
    graph = nx.Graph()
    for from_node, to_node, distance, status in _build_mock_road_network():
        if status == "blocked" and avoid_blocked:
            continue
        risk_cost = distance + _edge_penalty(status)
        graph.add_edge(from_node, to_node, weight=distance, risk_cost=risk_cost, status=status)

    if origin not in graph or destination not in graph:
        raise ValueError(f"Unknown route nodes: {origin} -> {destination}")

    if not nx.has_path(graph, origin, destination):
        raise ValueError(f"No valid route exists from {origin} to {destination}.")

    path = nx.shortest_path(graph, source=origin, target=destination, weight="risk_cost")
    distance = nx.shortest_path_length(graph, source=origin, target=destination, weight="weight")
    risky_segments = []
    for start, end in zip(path, path[1:]):
        edge_data = graph.get_edge_data(start, end)
        if edge_data and edge_data.get("status") in {"high_risk", "blocked"}:
            risky_segments.append(f"{start}-{end}")

    safety_score = 100
    for start, end in zip(path, path[1:]):
        status = graph.get_edge_data(start, end, {}).get("status", "open")
        if status == "high_risk":
            safety_score -= 35
        elif status == "blocked":
            safety_score -= 70
    safety_score = max(0, min(100, safety_score))

    return {
        "origin": origin,
        "destination": destination,
        "optimized_route": path,
        "total_distance_km": float(distance),
        "estimated_duration_minutes": int(round(distance * 6)),
        "safety_score": safety_score,
        "blocked_segments": risky_segments,
        "message": "Safe route selection based on road status and distance.",
    }
