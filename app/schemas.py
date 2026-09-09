from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


ReferenceCategory = Literal[
    "person_publicity",
    "brand_organization",
    "quoted_adapted_text",
    "historical_factual_claim",
    "location_property",
    "unverifiable_fictional_reference",
]
ReviewStatus = Literal[
    "clear_signal", "review", "high_attention", "insufficient_evidence"
]
Confidence = Literal["high", "medium", "low"]


class ReferenceCandidate(BaseModel):
    reference_text: str = Field(min_length=1, max_length=300)
    categories: list[ReferenceCategory] = Field(min_length=1)
    scene_or_page: str = Field(default="Unknown", max_length=100)
    script_context: str = Field(min_length=1, max_length=1200)
    why_research: str = Field(min_length=1, max_length=500)
    search_query: str = Field(min_length=3, max_length=400)


class ExtractedReferences(BaseModel):
    screenplay_title: str = Field(default="Untitled screenplay", max_length=200)
    references: list[ReferenceCandidate] = Field(default_factory=list)


class SourceEvidence(BaseModel):
    title: str
    url: HttpUrl
    excerpt: str = ""
    publish_date: str | None = None


class Finding(BaseModel):
    reference_text: str
    categories: list[ReferenceCategory]
    scene_or_page: str
    script_context: str
    status: ReviewStatus
    confidence: Confidence
    rationale: str
    recommended_action: str
    search_query: str
    sources: list[SourceEvidence] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


class ClearanceReport(BaseModel):
    screenplay_title: str
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    findings: list[Finding]
    tool_calls: int
    disclaimer: str = (
        "Script Sentinel provides research triage, not legal advice or a clearance "
        "decision. A qualified reviewer must verify sources and make final legal "
        "and production decisions."
    )

