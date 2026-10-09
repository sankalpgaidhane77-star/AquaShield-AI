import math
from typing import List, Dict, Any, Optional

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance in kilometers between two points on Earth.
    """
    R = 6371.0 # Earth's radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    distance = R * c
    return round(distance, 3)

def calculate_travel_time(distance_km: float, speed_kmh: float = 4.5) -> int:
    """
    Estimate walking travel time in minutes.
    """
    hours = distance_km / speed_kmh
    minutes = int(round(hours * 60))
    return max(1, minutes)

def generate_route_points(lat1: float, lon1: float, lat2: float, lon2: float, steps: int = 5) -> List[List[float]]:
    """
    Generates intermediate waypoints for visual pathing on map.
    """
    points = []
    for i in range(steps + 1):
        t = i / float(steps)
        # Add slight natural road curvature
        curve_offset = math.sin(t * math.pi) * 0.0012 if steps > 2 else 0.0
        lat = lat1 + (lat2 - lat1) * t + curve_offset
        lon = lon1 + (lon2 - lon1) * t - (curve_offset * 0.5)
        points.append([round(lat, 6), round(lon, 6)])
    return points
