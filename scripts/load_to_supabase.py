"""
Load generated CSV congestion data into Supabase.

Reads locations.csv and congestion_readings.csv from data/generated/,
optionally clears existing rows, and inserts the data.
Run from project root: python scripts/load_to_supabase.py [--clear]
"""

import argparse
import sys
from pathlib import Path

# Ensure project root is on path when running as script
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import pandas as pd

from backend.supabase_client import get_supabase_client


def main() -> None:
    parser = argparse.ArgumentParser(description="Load synthetic data into Supabase")
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing rows before insert (correct dependency order)",
    )
    args = parser.parse_args()

    data_dir = _project_root / "data" / "generated"
    locations_path = data_dir / "locations.csv"
    readings_path = data_dir / "congestion_readings.csv"

    if not locations_path.exists() or not readings_path.exists():
        print("Error: Run generate_synthetic_data.py first to create locations.csv and congestion_readings.csv")
        sys.exit(1)

    print("Connecting to Supabase...")
    client = get_supabase_client()

    if args.clear:
        print("Clearing existing data (congestion_readings first, then locations)...")
        client.table("congestion_readings").delete().neq("id", 0).execute()
        client.table("locations").delete().neq("id", 0).execute()
        print("Cleared.")

    # Load locations
    locations_df = pd.read_csv(locations_path)
    locations_records = locations_df.to_dict(orient="records")
    print(f"Loading {len(locations_records)} rows into table 'locations'...")
    try:
        result = client.table("locations").upsert(locations_records, on_conflict="id").execute()
        print(f"Inserted {len(locations_records)} rows into locations.")
        # Verify: fetch and count
        verify = client.table("locations").select("*").execute()
        print(f"Verification: locations table now has {len(verify.data or [])} rows.")
    except Exception as e:
        print(f"ERROR inserting locations: {e}")
        raise

    # Load congestion_readings
    readings_df = pd.read_csv(readings_path)
    readings_df["congestion_level"] = readings_df["congestion_level"].astype(int)
    readings_records = readings_df.to_dict(orient="records")
    for r in readings_records:
        for k, v in r.items():
            if pd.isna(v):
                r[k] = None
    result = client.table("congestion_readings").upsert(readings_records, on_conflict="id").execute()
    print(f"Inserted {len(readings_records)} rows into congestion_readings.")

    print("Done.")


if __name__ == "__main__":
    main()
