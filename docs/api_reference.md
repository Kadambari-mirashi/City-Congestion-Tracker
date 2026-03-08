# City Congestion Tracker API Reference

Base URL: `http://localhost:8000` (or your deployed backend URL)

## Endpoints

### GET /health

Health check. Returns `{"status": "ok", "service": "city-congestion-tracker-backend"}`.

### GET /locations/

List all locations.

**Query params:**
- `zone` (optional): Filter by zone (e.g., `Downtown`, `Midtown`)

**Example:** `GET /locations/?zone=Downtown`

### GET /congestion/raw

Fetch raw congestion readings in a time window.

**Query params:**
- `start` (required): Start of window, ISO format (e.g., `2025-02-24T00:00:00`)
- `end` (required): End of window, ISO format
- `location_ids` (optional): Comma-separated IDs (e.g., `1,2,3`)
- `min_level` (optional): Minimum congestion level 0–100

**Example:** `GET /congestion/raw?start=2025-02-24T00:00:00&end=2025-02-24T23:59:59&location_ids=1,2&min_level=50`
