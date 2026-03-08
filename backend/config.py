"""
Configuration and environment variable loading for the City Congestion Tracker backend.

This module will centralize settings such as Supabase credentials, OpenAI API keys,
and other runtime configuration using Pydantic or similar tools.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env files."""

    supabase_url: str | None = None
    supabase_key: str | None = None
    openai_api_key: str | None = None
    ollama_host: str | None = None  # https://ollama.com for Cloud, http://localhost:11434 for local
    ollama_api_key: str | None = None  # Required for Ollama Cloud
    ollama_model: str = "gpt-oss:20b-cloud"  # Cloud: gpt-oss:20b-cloud; local: llama3.2

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra env vars (e.g. BACKEND_BASE_URL used by dashboard)


settings = Settings()

