"""
Router for congestion query endpoints.
"""

from typing import Optional

from fastapi import APIRouter, Query

from ..schemas import CongestionReading
from ..supabase_client import get_congestion_raw


router = APIRouter(prefix="/congestion", tags=["congestion"])


def _parse_location_ids(value: Optional[str]) -> Optional[list[int]]:
    """Parse comma-separated location_ids string into list of ints."""
    if not value or not value.strip():
        return None
    try:
        return [int(x.strip()) for x in value.split(",") if x.strip()]
    except ValueError:
        return None


@router.get("/raw", response_model=list[CongestionReading])
def get_raw_congestion(
    start: str = Query(..., description="Start of time window (ISO format, e.g. 2025-02-24T00:00:00)"),
    end: str = Query(..., description="End of time window (ISO format)"),
    location_ids: Optional[str] = Query(
        default=None,
        description="Comma-separated location IDs, e.g. 1,2,3",
    ),
    min_level: Optional[int] = Query(default=None, ge=0, le=100),
):
    """Fetch raw congestion readings in the given time window."""
    loc_ids = _parse_location_ids(location_ids)
    rows = get_congestion_raw(
        start=start,
        end=end,
        location_ids=loc_ids,
        min_level=min_level,
    )
    return [CongestionReading(**r) for r in rows]
