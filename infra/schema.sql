-- City Congestion Tracker - Supabase schema
-- Run this in the Supabase SQL Editor to create the tables.

-- Locations (intersections, segments, or zones)
CREATE TABLE IF NOT EXISTS locations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    zone TEXT NOT NULL
);

-- If /locations returns empty, RLS may be blocking. Run infra/rls_fix.sql in SQL Editor.

-- Congestion readings (one per location per time interval)
-- congestion_level: 0-100 scale (0=free flow, 100=gridlock)
CREATE TABLE IF NOT EXISTS congestion_readings (
    id INTEGER PRIMARY KEY,
    location_id INTEGER NOT NULL REFERENCES locations(id),
    timestamp TIMESTAMPTZ NOT NULL,
    congestion_level INTEGER NOT NULL,
    avg_speed_kph FLOAT,
    delay_minutes FLOAT
);

-- Indexes for efficient time-window and location queries
CREATE INDEX IF NOT EXISTS idx_congestion_location_timestamp
    ON congestion_readings(location_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_congestion_timestamp
    ON congestion_readings(timestamp);
