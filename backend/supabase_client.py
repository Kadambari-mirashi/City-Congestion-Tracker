"""
Supabase client helpers for querying the congestion database.
"""

import logging
from typing import Any

from supabase import create_client, Client

from config import settings

logger = logging.getLogger(__name__)
_client: Client | None = None


def get_supabase_client() -> Client:
    """Create and return a Supabase client. Reuses a singleton if available."""
    global _client
    if _client is None:
        if not settings.supabase_url or not settings.supabase_key:
            raise RuntimeError(
                "Supabase configuration is missing. Check SUPABASE_URL and SUPABASE_KEY."
            )
        _client = create_client(settings.supabase_url, settings.supabase_key)
        logger.info("Supabase client created successfully (url=%s)", settings.supabase_url[:50] + "...")
    return _client


def get_all_locations(zone: str | None = None) -> list[dict[str, Any]]:
    """
    Fetch all locations, optionally filtered by zone.
    Table: locations. Column for zone filter: zone (exact match).
    """
    try:
        client = get_supabase_client()
        table_name = "locations"
        query = client.table(table_name).select("*")
        if zone:
            query = query.eq("zone", zone)
            logger.info("Querying table=%s with zone filter=%r", table_name, zone)
        else:
            logger.info("Querying table=%s (no zone filter)", table_name)
        result = query.execute()
        rows = result.data or []
        logger.info("Table=%s returned %d rows", table_name, len(rows))
        if not rows and result.count is not None:
            logger.warning("Supabase returned count=%s but data is empty", result.count)
        return rows
    except Exception as e:
        logger.exception("Supabase query failed for locations: %s", e)
        raise


def get_congestion_raw(
    start: str,
    end: str,
    location_ids: list[int] | None = None,
    min_level: int | None = None,
) -> list[dict[str, Any]]:
    """
    Fetch raw congestion readings in the given time window.
    start, end: ISO format datetime strings (e.g. "2025-02-24T00:00:00").
    """
    client = get_supabase_client()
    query = (
        client.table("congestion_readings")
        .select("*")
        .gte("timestamp", start)
        .lte("timestamp", end)
    )
    if location_ids:
        query = query.in_("location_id", location_ids)
    if min_level is not None:
        query = query.gte("congestion_level", min_level)
    result = query.order("timestamp").execute()
    return result.data or []
