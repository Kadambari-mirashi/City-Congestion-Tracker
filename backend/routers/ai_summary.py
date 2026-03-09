"""
Router for AI-generated congestion summaries.
"""

import logging

from fastapi import APIRouter, HTTPException

from ai_client import generate_congestion_summary
from schemas import AISummaryRequest, AISummaryResponse
from supabase_client import get_all_locations, get_congestion_raw

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/ai", tags=["ai"])


def _compute_stats(readings: list[dict], locations: list[dict]) -> dict:
    """Compute summary statistics from raw readings for the AI prompt."""
    if not readings:
        return {"message": "No congestion data in the selected time window."}

    loc_by_id = {loc["id"]: loc for loc in locations}
    congestion = [r["congestion_level"] for r in readings]
    speeds = [r["avg_speed_kph"] for r in readings if r.get("avg_speed_kph") is not None]
    delays = [r["delay_minutes"] for r in readings if r.get("delay_minutes") is not None]

    # Per-location aggregates
    from collections import defaultdict
    by_loc = defaultdict(list)
    for r in readings:
        by_loc[r["location_id"]].append(r["congestion_level"])

    top_locations = []
    for loc_id, levels in sorted(by_loc.items(), key=lambda x: -sum(x[1]) / len(x[1]))[:5]:
        name = loc_by_id.get(loc_id, {}).get("name", f"Location {loc_id}")
        avg = sum(levels) / len(levels)
        top_locations.append({"name": name, "avg_congestion": round(avg, 1)})

    stats = {
        "overall_avg_congestion": round(sum(congestion) / len(congestion), 1),
        "worst_location": top_locations[0]["name"] if top_locations else "N/A",
        "high_congestion_count": sum(1 for c in congestion if c >= 70),
        "top_5_locations": top_locations,
    }
    if speeds:
        stats["avg_speed_kph"] = round(sum(speeds) / len(speeds), 1)
    if delays:
        stats["avg_delay_minutes"] = round(sum(delays) / len(delays), 1)

    return stats


@router.post("/summary", response_model=AISummaryResponse)
def get_ai_summary(request: AISummaryRequest) -> AISummaryResponse:
    """Generate an AI summary from congestion data in the requested time window."""
    if not request.start or not request.end:
        raise HTTPException(status_code=400, detail="start and end are required")

    # Resolve location filter
    location_ids = request.location_ids
    if request.zone:
        locations = get_all_locations(zone=request.zone)
        if not location_ids:
            location_ids = [loc["id"] for loc in locations]
    else:
        locations = get_all_locations()

    # Fetch readings
    readings = get_congestion_raw(
        start=request.start,
        end=request.end,
        location_ids=location_ids,
        min_level=request.min_level,
    )

    stats = _compute_stats(readings, locations)
    query_context = request.model_dump()

    try:
        summary_text = generate_congestion_summary(stats=stats, query_context=query_context)
    except Exception as e:
        logger.exception("AI summary failed: %s", e)
        raise HTTPException(status_code=500, detail=f"AI summary failed: {str(e)}")

    return AISummaryResponse(summary=summary_text)
