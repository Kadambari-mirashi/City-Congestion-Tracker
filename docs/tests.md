# Test Executions

Run these with the **backend** and **Supabase** set up and data loaded. Start the backend first: `uvicorn backend.main:app --reload`.

---

## Test 1: Health check

**Command:**

```bash
curl http://localhost:8000/health
```

**Expected:** JSON indicating the API is running, e.g. `{"status":"ok","service":"city-congestion-tracker-backend"}`. HTTP status 200.

---

## Test 2: List locations (database connected)

**Command:**

```bash
curl "http://localhost:8000/locations/"
```

**Expected:** JSON array of location objects. With the default synthetic data you should see **10 locations**, each with `id`, `name`, and `zone`. Example snippet: `[{"id":1,"name":"5th Ave & Main","zone":"Downtown"},...]`. To test zone filtering: `curl "http://localhost:8000/locations/?zone=Downtown"` — expect a subset (e.g. 3 Downtown locations).

---

## Test 3: Raw congestion readings (time window)

**Command:**

```bash
curl "http://localhost:8000/congestion/raw?start=2025-02-24T00:00:00&end=2025-02-24T12:00:00"
```

**Expected:** JSON array of congestion readings. Each object has `id`, `location_id`, `timestamp`, `congestion_level`, and optionally `avg_speed_kph`, `delay_minutes`. For the 12-hour window across 10 locations (hourly data) you get **120 rows**. Times are in the requested range; ordering is by timestamp.
