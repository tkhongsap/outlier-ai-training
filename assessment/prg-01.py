from datetime import datetime
from typing import Dict, List, Tuple, Optional

Point = Tuple[float, float]
Polygon = List[Point]

def is_point_in_polygon(point: Point, polygon: Polygon) -> bool:
    """Return True if *point* is inside the given *polygon*."""
    x, y = point
    inside = False
    for i in range(len(polygon)):
        j = (i + 1) % len(polygon)
        x1, y1 = polygon[i]
        x2, y2 = polygon[j]
        if (y1 > y) != (y2 > y):
            xinters = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < xinters:
                inside = not inside
    return inside

def track_zone_transitions(path: List[Point], zones: Dict[str, Polygon], timestamps: Optional[List[datetime]] = None):
    """Detect entry and exit events for each zone along the *path*."""
    in_zone = {name: False for name in zones}
    transitions = []
    for idx, point in enumerate(path):
        for name, poly in zones.items():
            inside = is_point_in_polygon(point, poly)
            if inside and not in_zone[name]:
                event = {"index": idx, "zone": name, "event": "entry"}
                if timestamps:
                    event["timestamp"] = timestamps[idx]
                transitions.append(event)
            elif not inside and in_zone[name]:
                event = {"index": idx, "zone": name, "event": "exit"}
                if timestamps:
                    event["timestamp"] = timestamps[idx]
                transitions.append(event)
            in_zone[name] = inside
    return transitions

if __name__ == "__main__":
    path = [
        (40.7128, -74.0060),
        (41.8781, -87.6298),
        (34.0522, -118.2437),
        (37.7749, -122.4194),
        (29.7604, -95.3698),
    ]

    times = [
        datetime(2023, 1, 1, 8, 0, 0),
        datetime(2023, 1, 2, 9, 30, 0),
        datetime(2023, 1, 3, 14, 15, 0),
        datetime(2023, 1, 4, 11, 45, 0),
        datetime(2023, 1, 5, 16, 20, 0),
    ]

    zones = {
        "west_coast": [
            (33.0, -125.0),
            (33.0, -115.0),
            (42.0, -115.0),
            (42.0, -125.0),
        ],
        "east_coast": [
            (37.0, -82.0),
            (37.0, -70.0),
            (45.0, -70.0),
            (45.0, -82.0),
        ],
    }

    for evt in track_zone_transitions(path, zones, times):
        ts = evt.get("timestamp", "")
        print(f"{ts} {evt['event']} {evt['zone']} index={evt['index']}")
