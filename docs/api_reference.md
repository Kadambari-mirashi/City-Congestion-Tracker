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

### POST /ai/summary

Request an AI-generated congestion summary for a time window.

**Body (JSON):**
- `start` (required): Start of window, ISO format
- `end` (required): End of window, ISO format
- `query_type` (optional): e.g. `current_hotspots`, `time_of_day_pattern`, `current_vs_historical`
- `zone` (optional): Filter locations by zone
- `location_ids` (optional): List of location IDs to include
- `min_level` (optional): Minimum congestion level 0–100

**Response:** `{"summary": "..."}` — plain-language report string.

**Example:** `curl -X POST http://localhost:8000/ai/summary -H "Content-Type: application/json" -d '{"start":"2025-02-24T00:00:00","end":"2025-03-02T23:59:59","query_type":"current_hotspots"}'`

---

## Key functions (pipeline)

One-line reference for the main functions that define the pipeline. See source for full signatures.

| Where | Function | Purpose | Inputs | Returns |
|-------|----------|---------|--------|---------|
| `backend/supabase_client.py` | `get_supabase_client()` | Create or return shared Supabase client | None (uses env) | `Client` |
| `backend/supabase_client.py` | `get_all_locations(zone)` | Fetch locations from DB, optional zone filter | `zone`: str or None | `list[dict]` |
| `backend/supabase_client.py` | `get_congestion_raw(start, end, location_ids, min_level)` | Fetch raw readings in time window | `start`/`end` ISO strings; optional location list and min level | `list[dict]` |
| `backend/ai_client.py` | `generate_congestion_summary(stats, query_context)` | Call Ollama or OpenAI to produce narrative summary | `stats`: aggregated metrics dict; `query_context`: time range, type, etc. | `str` |
| `scripts/generate_synthetic_data.py` | `main()` | Write locations.csv and congestion_readings.csv to data/generated/ | None (fixed seed) | None |
| `scripts/load_to_supabase.py` | `main()` | Read CSVs from data/generated/, upsert into Supabase | CLI: optional `--clear` | None |
| `dashboard/api_client.py` | `get_locations(zone)` | GET /locations/ from backend | `zone`: str or None | `list[dict]` |
| `dashboard/api_client.py` | `get_congestion_raw(start, end, location_ids, min_level)` | GET /congestion/raw from backend | Same as API params | `list[dict]` |
| `dashboard/api_client.py` | `get_ai_summary(start, end, summary_type, ...)` | POST /ai/summary, return summary text | Time range, type, optional zone/location_ids/min_level | `str` |
