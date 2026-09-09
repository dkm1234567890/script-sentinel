import json
import re
import uuid
from typing import Any

from google import genai
from google.genai import types

from app.config import get_settings
from app.parallel_tool import search_web_for_clearance
from app.prompts import ASSESSMENT_INSTRUCTION, EXTRACTION_PROMPT
from app.schemas import (
    ClearanceReport,
    ExtractedReferences,
    Finding,
    ReferenceCandidate,
    SourceEvidence,
)


def _gemini_client() -> genai.Client:
    settings = get_settings()
    # The hackathon targets Gemini Enterprise Agent Platform. The explicit client
    # arguments keep this visible to judges and avoid API-key-based AI providers.
    try:
        return genai.Client(
            enterprise=True,
            project=settings.google_cloud_project,
            location=settings.google_cloud_location,
        )
    except TypeError:
        # Compatibility with SDK releases that still use the Vertex AI flag.
        return genai.Client(
            vertexai=True,
            project=settings.google_cloud_project,
            location=settings.google_cloud_location,
        )


def _json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


def extract_references(pdf_bytes: bytes) -> ExtractedReferences:
    settings = get_settings()
    client = _gemini_client()
    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=[
                types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf"),
                types.Part.from_text(text=EXTRACTION_PROMPT),
            ],
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
                response_schema=ExtractedReferences,
            ),
        )
        extracted = response.parsed
        if not isinstance(extracted, ExtractedReferences):
            extracted = ExtractedReferences.model_validate_json(response.text)
        extracted.references = extracted.references[: settings.max_references]
        return extracted
    finally:
        client.close()


async def _assess_with_adk(reference: ReferenceCandidate) -> tuple[dict[str, Any], list[SourceEvidence]]:
    """Run a real ADK agent whose required function tool calls Parallel Search."""
    from google.adk.agents import Agent
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService

    settings = get_settings()
    evidence_capture: dict[str, Any] = {}

    def captured_search(
        query: str, objective: str, max_results: int = 5
    ) -> dict[str, Any]:
        """Search the live web for current, source-linked clearance evidence."""
        result = search_web_for_clearance(query, objective, max_results)
        evidence_capture.update(result)
        return result

    agent = Agent(
        name="script_sentinel_clearance_agent",
        model=settings.gemini_model,
        instruction=ASSESSMENT_INSTRUCTION,
        tools=[captured_search],
    )
    app_name = "script_sentinel"
    user_id = "web_user"
    session_id = uuid.uuid4().hex
    sessions = InMemorySessionService()
    await sessions.create_session(
        app_name=app_name, user_id=user_id, session_id=session_id
    )
    runner = Runner(agent=agent, app_name=app_name, session_service=sessions)

    prompt = (
        "Research and assess this screenplay reference.\n"
        f"Reference: {reference.reference_text}\n"
        f"Categories: {', '.join(reference.categories)}\n"
        f"Scene/page: {reference.scene_or_page}\n"
        f"Context: {reference.script_context}\n"
        f"Research reason: {reference.why_research}\n"
        f"Required query: {reference.search_query}\n"
        "Use this objective: Find current, traceable evidence relevant to whether "
        "this screenplay reference needs human factual or clearance review."
    )
    final_text = ""
    message = types.Content(role="user", parts=[types.Part.from_text(text=prompt)])
    async for event in runner.run_async(
        user_id=user_id, session_id=session_id, new_message=message
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = "".join(
                part.text or "" for part in event.content.parts if part.text
            )
    if not final_text:
        raise RuntimeError("The ADK agent returned no final assessment.")

    assessment = _json_object(final_text)
    sources = [
        SourceEvidence.model_validate(item)
        for item in evidence_capture.get("results", [])
    ]
    return assessment, sources


async def analyze_screenplay(pdf_bytes: bytes) -> ClearanceReport:
    extracted = extract_references(pdf_bytes)
    findings: list[Finding] = []
    tool_calls = 0

    for reference in extracted.references:
        try:
            assessment, sources = await _assess_with_adk(reference)
            tool_calls += 1
            findings.append(
                Finding(
                    reference_text=reference.reference_text,
                    categories=reference.categories,
                    scene_or_page=reference.scene_or_page,
                    script_context=reference.script_context,
                    status=assessment.get("status", "insufficient_evidence"),
                    confidence=assessment.get("confidence", "low"),
                    rationale=assessment.get(
                        "rationale", "The agent could not produce a complete rationale."
                    ),
                    recommended_action=assessment.get(
                        "recommended_action", "Review this item manually."
                    ),
                    search_query=reference.search_query,
                    sources=sources,
                    limitations=assessment.get("limitations", []),
                )
            )
        except Exception as exc:
            findings.append(
                Finding(
                    reference_text=reference.reference_text,
                    categories=reference.categories,
                    scene_or_page=reference.scene_or_page,
                    script_context=reference.script_context,
                    status="insufficient_evidence",
                    confidence="low",
                    rationale="The research step did not complete reliably.",
                    recommended_action="Retry the search or review this item manually.",
                    search_query=reference.search_query,
                    limitations=[f"Tool error: {type(exc).__name__}"],
                )
            )

    return ClearanceReport(
        screenplay_title=extracted.screenplay_title,
        findings=findings,
        tool_calls=tool_calls,
    )
