import math


def calculate_route(start_lat: float, start_lng: float, end_lat: float, end_lng: float):
    # Simulated route planning using haversine distance
    r_earth = 6371  # Earth radius in km
    dlat = math.radians(end_lat - start_lat)
    dlng = math.radians(end_lng - start_lng)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(start_lat)) * math.cos(math.radians(end_lat)) * math.sin(dlng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = r_earth * c

    # Simulate a few waypoints
    waypoints = [
        {"lat": start_lat, "lng": start_lng},
        {"lat": (start_lat + end_lat) / 2, "lng": (start_lng + end_lng) / 2},
        {"lat": end_lat, "lng": end_lng},
    ]

    return {
        "status": "SUCCESS",
        "distance_km": round(distance, 2),
        "estimated_time_mins": round(distance / 0.5, 2),  # 0.5 km/min speed
        "waypoints": waypoints,
    }
