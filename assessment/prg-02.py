import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
from datetime import datetime
from typing import Dict, List


def create_zones_gdf(zones: Dict[str, List[tuple]]) -> gpd.GeoDataFrame:
    """Convert a zone dictionary to a GeoDataFrame."""
    data = [{"zone_name": name, "geometry": Polygon(coords)} for name, coords in zones.items()]
    return gpd.GeoDataFrame(data)


def track_zone_transitions_geopandas(bird_df: pd.DataFrame, zones_gdf: gpd.GeoDataFrame, timestamp_col: str | None = None):
    """Track zone transitions using GeoPandas geometry operations."""
    geometry = [Point(xy) for xy in zip(bird_df["longitude"], bird_df["latitude"])]
    bird_gdf = gpd.GeoDataFrame(bird_df.copy(), geometry=geometry)

    transitions: List[dict] = []
    for _, zone_row in zones_gdf.iterrows():
        name = zone_row["zone_name"]
        bird_gdf[f"in_{name}"] = bird_gdf["geometry"].within(zone_row["geometry"])
        bird_gdf[f"prev_in_{name}"] = bird_gdf[f"in_{name}"].shift(1).fillna(False)

        entries = bird_gdf[(bird_gdf[f"in_{name}"]) & (~bird_gdf[f"prev_in_{name}"])]
        exits = bird_gdf[(~bird_gdf[f"in_{name}"]) & (bird_gdf[f"prev_in_{name}"])]

        for idx, row in entries.iterrows():
            ev = {"index": idx, "zone": name, "event": "entry"}
            if timestamp_col:
                ev["timestamp"] = row[timestamp_col]
            transitions.append(ev)
        for idx, row in exits.iterrows():
            ev = {"index": idx, "zone": name, "event": "exit"}
            if timestamp_col:
                ev["timestamp"] = row[timestamp_col]
            transitions.append(ev)

    transitions.sort(key=lambda x: x.get("timestamp", x["index"]))
    return transitions


if __name__ == "__main__":
    bird_data = {
        "latitude": [40.7128, 41.8781, 34.0522, 37.7749, 29.7604],
        "longitude": [-74.0060, -87.6298, -118.2437, -122.4194, -95.3698],
        "timestamp": [
            datetime(2023, 1, 1, 8, 0, 0),
            datetime(2023, 1, 2, 9, 30, 0),
            datetime(2023, 1, 3, 14, 15, 0),
            datetime(2023, 1, 4, 11, 45, 0),
            datetime(2023, 1, 5, 16, 20, 0),
        ],
    }
    bird_df = pd.DataFrame(bird_data)

    zones = {
        "west_coast": [
            (-125.0, 33.0),
            (-115.0, 33.0),
            (-115.0, 42.0),
            (-125.0, 42.0),
        ],
        "east_coast": [
            (-82.0, 37.0),
            (-70.0, 37.0),
            (-70.0, 45.0),
            (-82.0, 45.0),
        ],
    }
    zones_gdf = create_zones_gdf(zones)

    for evt in track_zone_transitions_geopandas(bird_df, zones_gdf, "timestamp"):
        ts = evt.get("timestamp", "")
        print(f"{ts} {evt['event']} {evt['zone']} index={evt['index']}")
