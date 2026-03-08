"""
Pydantic models for API request and response payloads.

These schemas allow the FastAPI backend to validate inputs and structure
responses for locations, congestion readings, and AI summaries.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Location(BaseModel):
    """Basic representation of a traffic location or intersection."""

    id: int
    name: str
    zone: str


class CongestionReading(BaseModel):
    """Single congestion reading for a location at a specific timestamp."""

    id: int
    location_id: int
    timestamp: datetime
    congestion_level: int
    avg_speed_kph: Optional[float] = None
    delay_minutes: Optional[float] = None


class HealthResponse(BaseModel):
    """Response model for the /health endpoint."""

    status: str
    service: str


class AISummaryRequest(BaseModel):
    """Input for requesting an AI-generated congestion summary."""

    start: Optional[str] = None
    end: Optional[str] = None
    query_type: Optional[str] = None
    zone: Optional[str] = None
    location_ids: Optional[list[int]] = None
    min_level: Optional[int] = None


class AISummaryResponse(BaseModel):
    """Response containing the generated congestion summary text."""

    summary: str
