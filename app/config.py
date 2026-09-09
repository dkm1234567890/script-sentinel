from functools import lru_cache
from os import getenv

from pydantic import BaseModel


class Settings(BaseModel):
    google_cloud_project: str = getenv("GOOGLE_CLOUD_PROJECT", "")
    google_cloud_location: str = getenv("GOOGLE_CLOUD_LOCATION", "global")
    gemini_model: str = getenv("GEMINI_MODEL", "gemini-2.5-flash")
    parallel_api_key: str = getenv("PARALLEL_API_KEY", "")
    allow_parallel_demo_fallback: bool = getenv(
        "ALLOW_PARALLEL_DEMO_FALLBACK", "false"
    ).lower() in {"1", "true", "yes"}
    max_upload_mb: int = int(getenv("MAX_UPLOAD_MB", "20"))
    max_references: int = int(getenv("MAX_REFERENCES", "8"))
    max_search_results: int = int(getenv("MAX_SEARCH_RESULTS", "5"))

    def missing_credentials(self) -> list[str]:
        missing: list[str] = []
        if not self.google_cloud_project:
            missing.append("GOOGLE_CLOUD_PROJECT")
        if not self.parallel_api_key:
            missing.append("PARALLEL_API_KEY")
        return missing


@lru_cache
def get_settings() -> Settings:
    return Settings()
