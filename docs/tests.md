# Test Executions

Run these with the **backend** and **Supabase** set up and data loaded. Start the backend first: `uvicorn backend.main:app --reload`.

---

## Demonstration (how the tests show the tool working)

Running the tests below in order demonstrates the full pipeline:

1. **API tests (Test 1–3)** show that the **database → API** part works: the backend is up (Test 1), it reads locations from Supabase (Test 2), and it returns congestion readings for a time window (Test 3). Together they prove the API serves real data from the database.
2. **UI tests (UI Test 1–3)** show that the **dashboard** delivers results to the user: the default view loads KPIs, charts, and a table from the API (UI Test 1); filters correctly change the data shown (UI Test 2); and **Generate AI Summary** produces a plain-language report from the same data via the API and AI (UI Test 3).

To demonstrate the tool end-to-end: run Test 1–3 in a terminal (with the backend running), then run the dashboard and follow UI Test 1 → UI Test 2 → UI Test 3. That sequence shows database → API → dashboard → AI in use.

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

---

# UI (dashboard) test cases

Run the dashboard first: `streamlit run dashboard/app.py`, then open http://localhost:8501 in a browser.

---

## UI Test 1: Default view loads (KPIs and charts)

**Steps:**

1. Open http://localhost:8501.
2. Leave sidebar filters at defaults (e.g. **Time range:** Last 7 days, **Zone:** All zones).

**Expected:** Main area shows four KPI cards (Avg Congestion, Worst Location, High Congestion #, Avg Delay) with numeric values. Below, a time-series line chart and a horizontal bar chart of top congested locations. A data table lists Location, Zone, Avg Congestion, Avg Speed, Avg Delay. No error messages; charts and table are populated from the database.

---

## UI Test 2: Filters change the data

**Steps:**

1. In the sidebar, set **Time range** to **Last 1 hour**.
2. Set **Zone** to **Downtown**.

**Expected:** KPIs, charts, and table update to reflect only Downtown locations and only the last hour of data. Fewer rows in the table; charts show a shorter time span and fewer bars. Worst Location and other metrics may change.

---

## UI Test 3: AI summary generation

**Steps:**

1. Choose a time range (e.g. **Last 7 days**) and optionally a zone.
2. Click the **Generate AI Summary** button.
3. Wait for the request to complete.

**Expected:** A short loading state (e.g. “Generating summary…”), then an info box appears with a plain-language congestion report (2–3 paragraphs). The text mentions locations or zones, congestion levels or trends, and short-term advice (e.g. what to avoid or watch). No error message; if the backend or AI is misconfigured, an error message appears in red instead.
