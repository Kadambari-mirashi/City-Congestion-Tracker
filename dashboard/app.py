"""
City Congestion Tracker - Interactive dashboard.
"""

from datetime import datetime, timedelta

import pandas as pd
import requests
import streamlit as st

from api_client import get_ai_summary, get_congestion_raw, get_locations

# Synthetic data spans 2025-02-24 to 2025-03-02; use end as reference "now"
REFERENCE_NOW = datetime(2025, 3, 2, 23, 0, 0)


def _time_range_to_iso(choice: str, custom_start=None, custom_end=None) -> tuple[str, str]:
    """Convert time range choice to (start, end) ISO strings."""
    if choice == "Custom" and custom_start and custom_end:
        return custom_start.strftime("%Y-%m-%dT%H:%M:%S"), custom_end.strftime("%Y-%m-%dT%H:%M:%S")
    now = REFERENCE_NOW
    if choice == "Last 1 hour":
        start = now - timedelta(hours=1)
    elif choice == "Today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif choice == "Last 24 hours":
        start = now - timedelta(hours=24)
    elif choice == "Last 7 days":
        start = now - timedelta(days=7)
    else:
        start = now - timedelta(days=7)
    end = now
    return start.strftime("%Y-%m-%dT%H:%M:%S"), end.strftime("%Y-%m-%dT%H:%M:%S")


st.set_page_config(page_title="City Congestion Tracker", layout="wide")
# Hide deploy button (also .streamlit/config.toml: client.toolbarMode = "viewer")
st.markdown("""
    <style>
        [data-testid="stDeployButton"] { display: none !important; }
        .stDeployButton { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- Title bar ---
st.title("City Congestion Tracker")
st.caption("Monitor congestion trends and generate AI-powered traffic summaries")

# --- Sidebar filters ---
with st.sidebar:
    st.header("Filters")

    time_choice = st.selectbox(
        "Time range",
        ["Last 1 hour", "Today", "Last 24 hours", "Last 7 days", "Custom"],
        index=3,
    )
    custom_start, custom_end = None, None
    if time_choice == "Custom":
        custom_start = st.datetime_input("Start", value=datetime(2025, 2, 24, 0, 0))
        custom_end = st.datetime_input("End", value=datetime(2025, 3, 2, 23, 0))

    start_iso, end_iso = _time_range_to_iso(time_choice, custom_start, custom_end)

    zone_filter = st.selectbox(
        "Zone",
        ["All zones", "Downtown", "Midtown", "Riverside", "University District"],
        index=0,
    )
    zone = None if zone_filter == "All zones" else zone_filter

    locations = get_locations(zone=zone)
    location_options = {f"{loc['name']} ({loc['zone']})": loc["id"] for loc in locations}
    selected_names = st.multiselect(
        "Location",
        options=list(location_options.keys()),
        default=[],
        help="Leave empty for all locations in selected zone",
    )
    location_ids = [location_options[n] for n in selected_names] if selected_names else None
    if location_ids is None and zone:
        location_ids = [loc["id"] for loc in locations]

    min_threshold = st.slider("Minimum congestion threshold", 0, 100, 0, help="Filter readings below this level")

    summary_type = st.selectbox(
        "AI summary type",
        ["Current hotspots", "Time-of-day pattern", "Current vs historical"],
        index=0,
    )
    summary_type_map = {
        "Current hotspots": "current_hotspots",
        "Time-of-day pattern": "time_of_day_pattern",
        "Current vs historical": "current_vs_historical",
    }
    query_type = summary_type_map[summary_type]

# --- Fetch data ---
readings = get_congestion_raw(
    start=start_iso,
    end=end_iso,
    location_ids=location_ids,
    min_level=min_threshold if min_threshold > 0 else None,
)

if not readings:
    st.warning("No congestion data for the selected filters. Try a wider time range or fewer filters.")
    st.stop()

df = pd.DataFrame(readings)
df["timestamp"] = pd.to_datetime(df["timestamp"])
loc_list = get_locations(zone=zone)
loc_map = {loc["id"]: loc for loc in loc_list}
df["location_name"] = df["location_id"].map(lambda x: loc_map.get(x, {}).get("name", str(x)))
df["zone_name"] = df["location_id"].map(lambda x: loc_map.get(x, {}).get("zone", ""))

# --- Row 1: KPI cards ---
avg_cong = round(df["congestion_level"].mean(), 1)
worst_loc = df.loc[df["congestion_level"].idxmax(), "location_name"] if len(df) > 0 else "N/A"
high_count = (df["congestion_level"] >= 70).sum()
avg_delay = round(df["delay_minutes"].mean(), 1) if "delay_minutes" in df and df["delay_minutes"].notna().any() else 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Avg Congestion", f"{avg_cong}")
with col2:
    st.metric("Worst Location", worst_loc)
with col3:
    st.metric("High Congestion #", high_count)
with col4:
    st.metric("Avg Delay", f"{avg_delay} min")

# --- Row 2: Charts ---
col_left, col_right = st.columns(2)

with col_left:
    ts_df = df.groupby(df["timestamp"].dt.floor("h"))["congestion_level"].mean()
    ts_df = ts_df.to_frame("avg_congestion")
    st.subheader("Time-Series Trend Chart")
    st.caption("Avg congestion over time")
    st.line_chart(ts_df)

with col_right:
    bar_df = df.groupby("location_name")["congestion_level"].mean().sort_values(ascending=False)
    bar_df = bar_df.to_frame("avg_congestion")
    st.subheader("Top Congested Locations")
    st.caption("Bar chart by location")
    st.bar_chart(bar_df)

# --- Row 3: Data table ---
table_df = df.groupby(["location_name", "zone_name"]).agg(
    avg_congestion=("congestion_level", "mean"),
    avg_speed=("avg_speed_kph", "mean"),
    avg_delay=("delay_minutes", "mean"),
).round(1).reset_index()
table_df.columns = ["Location", "Zone", "Avg Congestion", "Avg Speed", "Avg Delay"]
st.subheader("Congestion Data Table")
st.dataframe(table_df, use_container_width=True, hide_index=True)

# --- Row 4: AI Summary panel ---
st.subheader("AI Summary")
if st.button("Generate AI Summary", type="primary"):
    with st.spinner("Generating summary..."):
        try:
            summary = get_ai_summary(
                start=start_iso,
                end=end_iso,
                summary_type=query_type,
                zone=zone,
                location_ids=location_ids,
                min_level=min_threshold if min_threshold > 0 else None,
            )
            st.info(summary)
        except Exception as e:
            err_msg = str(e)
            if hasattr(e, "response") and e.response is not None:
                try:
                    body = e.response.json()
                    if "detail" in body:
                        err_msg = body["detail"]
                except Exception:
                    pass
            st.error(f"Failed to generate summary: {err_msg}")
else:
    st.markdown(
        "_Click **Generate AI Summary** to get an actionable narrative based on the current filters._"
    )
