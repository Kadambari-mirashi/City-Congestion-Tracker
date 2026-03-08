"""
AI client for generating congestion summaries.
Supports OpenAI, Ollama Cloud (OLLAMA_HOST + OLLAMA_API_KEY), or local Ollama.
"""

from typing import Any

from .config import settings


def _format_stats(stats: dict[str, Any]) -> str:
    """Format stats dict as readable text for the prompt."""
    import json
    lines = []
    for k, v in stats.items():
        if isinstance(v, (list, dict)):
            lines.append(f"{k}: {json.dumps(v, indent=2)}")
        else:
            lines.append(f"{k}: {v}")
    return "\n".join(lines) if lines else "No statistics available."


def _build_prompt(stats: dict[str, Any], query_context: dict[str, Any]) -> tuple[str, str]:
    """Build system and user prompts for the AI."""
    summary_type = query_context.get("query_type") or "current_hotspots"
    start = query_context.get("start", "")
    end = query_context.get("end", "")

    system_prompt = (
        "You are a transportation analytics assistant. Given congestion statistics from a traffic database, "
        "write a clear, detailed report (2–3 paragraphs, about 10–15 sentences total). "
        "First paragraph: describe which areas or intersections are most congested, how levels compare to usual, "
        "and how congestion varies by time or location. "
        "Second paragraph: give short-term, practical advice for drivers and traffic managers—which roads or "
        "intersections to avoid now, when to expect the worst delays, and what to watch in the next hour or day. "
        "Do NOT recommend infrastructure projects, signal upgrades, or policy pilots; only advise on routes and "
        "timing based on the data. Use plain language."
    )

    user_content = f"""Time window: {start} to {end}
Summary type: {summary_type}

Statistics:
{_format_stats(stats)}

Write a longer, detailed congestion report as described above."""

    return system_prompt, user_content


def generate_congestion_summary(stats: dict[str, Any], query_context: dict[str, Any]) -> str:
    """
    Generate a congestion summary using Ollama (if OLLAMA_HOST set) or OpenAI.
    """
    system_prompt, user_content = _build_prompt(stats, query_context)

    if settings.ollama_host:
        if "ollama.com" in settings.ollama_host and not settings.ollama_api_key:
            raise RuntimeError("OLLAMA_API_KEY is required for Ollama Cloud. Add it to .env")
        return _generate_with_ollama(system_prompt, user_content)
    if settings.openai_api_key:
        return _generate_with_openai(system_prompt, user_content)
    raise RuntimeError(
        "Set OLLAMA_HOST + OLLAMA_API_KEY (Cloud) or OLLAMA_HOST (local) or OPENAI_API_KEY in .env"
    )


def _generate_with_ollama(system_prompt: str, user_content: str) -> str:
    """Use Ollama (Cloud or local) for chat completion."""
    from ollama import Client

    kwargs = {"host": settings.ollama_host}
    if settings.ollama_api_key:
        kwargs["headers"] = {"Authorization": f"Bearer {settings.ollama_api_key}"}
    client = Client(**kwargs)
    response = client.chat(
        model=settings.ollama_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
    )
    return response.message.content or "Unable to generate summary."


def _generate_with_openai(system_prompt: str, user_content: str) -> str:
    """Use OpenAI for chat completion."""
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        max_tokens=600,
    )
    return response.choices[0].message.content or "Unable to generate summary."
