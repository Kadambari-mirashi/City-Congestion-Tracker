"""
Generate synthetic congestion datasets for the City Congestion Tracker.

Creates locations.csv and congestion_readings.csv under data/generated/.
Uses a fixed random seed for reproducibility.
"""

from pathlib import Path
from datetime import datetime, timedelta

import pandas as pd
import numpy as np

RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)

# 10 locations with realistic names and zones
LOCATIONS = [
    (1, "5th Ave & Main", "Downtown"),
    (2, "River Rd & Pine", "Riverside"),
    (3, "College Ave & Oak", "University District"),
    (4, "Market St & 3rd", "Downtown"),
    (5, "Broadway & Elm", "Midtown"),
    (6, "Park Blvd & Cedar", "University District"),
    (7, "Harbor Dr & Bay", "Riverside"),
    (8, "Central Ave & 1st", "Downtown"),
    (9, "Lake Dr & Maple", "Riverside"),
    (10, "Campus Way & Ivy", "University District"),
]

ZONES = ["Downtown", "Midtown", "Riverside", "University District"]


def _base_congestion(hour: int, day_of_week: int, zone: str) -> float:
    """
    Base congestion level (0-100) before adding noise.
    - Rush hours (7-9, 17-19): higher in Downtown/Midtown
    - Weekends (5, 6): lighter overall
    - Riverside/University: moderate peaks
    """
    is_weekend = day_of_week >= 5
    is_rush_morning = 7 <= hour <= 9
    is_rush_evening = 17 <= hour <= 19
    is_rush = is_rush_morning or is_rush_evening

    if is_weekend:
        base = 25.0
        if is_rush:
            base += 15
    else:
        base = 35.0
        if is_rush and zone in ("Downtown", "Midtown"):
            base += 35
        elif is_rush and zone in ("Riverside", "University District"):
            base += 20
        elif zone in ("Downtown", "Midtown"):
            base += 10

    return min(95, max(5, base))


def _derive_speed_and_delay(congestion: float) -> tuple[float, float]:
    """Derive avg_speed_kph and delay_minutes from congestion_level (0-100)."""
    # Higher congestion -> lower speed, higher delay
    avg_speed_kph = 60 - (congestion * 0.45) + np.random.uniform(-3, 3)
    delay_minutes = (congestion * 0.22) + np.random.uniform(-1, 2)
    avg_speed_kph = max(5, min(65, avg_speed_kph))
    delay_minutes = max(0, min(30, delay_minutes))
    return round(avg_speed_kph, 1), round(delay_minutes, 1)


def main() -> None:
    output_dir = Path(__file__).resolve().parent.parent / "data" / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. locations.csv
    locations_df = pd.DataFrame(
        LOCATIONS,
        columns=["id", "name", "zone"],
    )
    locations_path = output_dir / "locations.csv"
    locations_df.to_csv(locations_path, index=False)
    print(f"Wrote {len(locations_df)} rows to {locations_path}")

    # 2. congestion_readings.csv - 7 days, hourly, 10 locations
    start_dt = datetime(2025, 2, 24, 0, 0, 0)  # Monday 00:00
    readings = []
    reading_id = 1

    for loc_id, name, zone in LOCATIONS:
        for day_offset in range(7):
            for hour in range(24):
                ts = start_dt + timedelta(days=day_offset, hours=hour)
                day_of_week = ts.weekday()

                base = _base_congestion(hour, day_of_week, zone)
                noise = np.random.normal(0, 8)
                congestion_level = int(min(100, max(0, base + noise)))

                avg_speed_kph, delay_minutes = _derive_speed_and_delay(congestion_level)

                readings.append({
                    "id": reading_id,
                    "location_id": loc_id,
                    "timestamp": ts.isoformat(),
                    "congestion_level": congestion_level,
                    "avg_speed_kph": avg_speed_kph,
                    "delay_minutes": delay_minutes,
                })
                reading_id += 1

    readings_df = pd.DataFrame(readings)
    readings_path = output_dir / "congestion_readings.csv"
    readings_df.to_csv(readings_path, index=False)
    print(f"Wrote {len(readings_df)} rows to {readings_path}")


if __name__ == "__main__":
    main()
