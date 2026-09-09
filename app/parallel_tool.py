from typing import Any

from parallel import Parallel

from app.config import get_settings


def search_web_for_clearance(
    query: str,
    objective: str,
    max_results: int = 5,
) -> dict[str, Any]:
    """Search the live web with Parallel and return normalized source evidence."""
    settings = get_settings()
    if not settings.parallel_api_key:
        return {
            "ok": False,
            "error": "PARALLEL_API_KEY is not configured.",
            "query": query,
            "results": [],
        }

    client = Parallel(api_key=settings.parallel_api_key)
    response = client.search(
        objective=objective,
        search_queries=[query],
        mode="fast",
    )
    normalized = []
    for item in response.results[: min(max_results, settings.max_search_results)]:
        excerpts = list(item.excerpts or [])
        publish_date = getattr(item, "publish_date", None)
        normalized.append(
            {
                "title": item.title or item.url,
                "url": item.url,
                "excerpt": excerpts[0][:1200] if excerpts else "",
                "publish_date": str(publish_date) if publish_date else None,
            }
        )
    return {
        "ok": True,
        "query": query,
        "search_id": getattr(response, "search_id", None),
        "results": normalized,
    }
