"""
Lightweight client for calling the FastAPI backend from the Streamlit dashboard.
"""

import json
import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")


def _parse_json(response: requests.Response) -> Any:
    """Parse response as JSON or raise a clear error with status and body snippet."""
    try:
        return response.json()
    except json.JSONDecodeError as e:
        body = (response.text or "").strip()
        snippet = body[:200] + ("..." if len(body) > 200 else "") if body else "(empty)"
        raise RuntimeError(
            f"Backend returned non-JSON (status={response.status_code}). "
            f"First 200 chars: {snippet!r}"
        ) from e


def get_health() -> dict[str, Any]:
    """Call the backend /health endpoint."""
    response = requests.get(f"{BACKEND_BASE_URL}/health", timeout=5)
    response.raise_for_status()
    return _parse_json(response)


def get_locations(zone: str | None = None) -> list[dict[str, Any]]:
    """Fetch locations, optionally filtered by zone."""
    url = f"{BACKEND_BASE_URL}/locations/"
    params = {} if not zone else {"zone": zone}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return _parse_json(response)


def get_congestion_raw(
    start: str,
    end: str,
    location_ids: list[int] | None = None,
    min_level: int | None = None,
) -> list[dict[str, Any]]:
    """Fetch raw congestion readings for the given time window and filters."""
    url = f"{BACKEND_BASE_URL}/congestion/raw"
    params = {"start": start, "end": end}
    if location_ids:
        params["location_ids"] = ",".join(str(x) for x in location_ids)
    if min_level is not None:
        params["min_level"] = min_level
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return _parse_json(response)


def get_ai_summary(
    start: str,
    end: str,
    summary_type: str,
    zone: str | None = None,
    location_ids: list[int] | None = None,
    min_level: int | None = None,
) -> str:
    """Request an AI-generated congestion summary from the backend."""
    url = f"{BACKEND_BASE_URL}/ai/summary"
    payload = {
        "start": start,
        "end": end,
        "query_type": summary_type,
        "zone": zone,
        "location_ids": location_ids,
        "min_level": min_level,
    }
    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    data = _parse_json(response)
    return data.get("summary", "")
