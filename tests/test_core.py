import json

from app.pipeline import _json_object
from app.schemas import ClearanceReport, Finding


def test_json_object_accepts_fenced_json():
    assert _json_object('```json\n{"status":"review"}\n```')["status"] == "review"


def test_report_schema_serializes():
    report = ClearanceReport(
        screenplay_title="Test",
        tool_calls=0,
        findings=[
            Finding(
                reference_text="Example",
                categories=["historical_factual_claim"],
                scene_or_page="1",
                script_context="A test claim.",
                status="insufficient_evidence",
                confidence="low",
                rationale="No evidence yet.",
                recommended_action="Review manually.",
                search_query="test claim evidence",
            )
        ],
    )
    payload = json.loads(report.model_dump_json())
    assert payload["screenplay_title"] == "Test"
    assert payload["findings"][0]["status"] == "insufficient_evidence"

