"""
Router for endpoints related to traffic locations (intersections, zones, etc.).
"""

import logging
from typing import Optional

from fastapi import APIRouter, Query

from ..schemas import Location
from ..supabase_client import get_all_locations

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/locations", tags=["locations"])


@router.get("/", response_model=list[Location])
def list_locations(zone: Optional[str] = Query(default=None)):
    """List all locations, optionally filtered by zone."""
    try:
        rows = get_all_locations(zone=zone)
        logger.info("/locations zone=%r returned %d rows", zone, len(rows))
        return [Location(**r) for r in rows]
    except Exception as e:
        logger.exception("/locations failed: %s", e)
        raise
