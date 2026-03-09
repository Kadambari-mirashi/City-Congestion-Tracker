import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import ai_summary, congestion, locations

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="City Congestion Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(locations.router)
app.include_router(congestion.router)
app.include_router(ai_summary.router)


@app.get("/health")
def health_check():
    """Basic health-check endpoint."""
    return {"status": "ok", "service": "city-congestion-tracker-backend"}


@app.get("/debug/locations-count")
def debug_locations_count():
    """Temporary debug endpoint: total rows in locations table."""
    from .supabase_client import get_all_locations
    rows = get_all_locations(zone=None)
    return {"count": len(rows), "table": "locations"}


@app.get("/debug/ai-provider")
def debug_ai_provider():
    """Temporary debug: which AI provider is configured."""
    from config import settings
    if settings.ollama_host:
        return {
            "provider": "ollama",
            "host": settings.ollama_host,
            "model": settings.ollama_model,
            "api_key_set": bool(settings.ollama_api_key),
        }
    if settings.openai_api_key:
        return {"provider": "openai", "key_set": True}
    return {"provider": "none", "message": "Set OLLAMA_HOST+OLLAMA_API_KEY or OPENAI_API_KEY"}


