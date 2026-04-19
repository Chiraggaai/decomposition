# routes/plans_v1.py
"""
AI Draft Review
POST /api/v1/plans

Returns the full AI-generated SOW draft review for a given wizard session,
including document sections, quality metrics, and anti-hallucination layer results.
All data is loaded from mock_db.json at startup via mock_db.py.
"""

from __future__ import annotations

from fastapi import APIRouter, Body, HTTPException

from mock_db import wizard_store as _DRAFT_STORE
from models import (
    AiDraftReviewData,
    AiDraftReviewRequest,
    AiDraftReviewResponse,
    DraftSection,
    GeneratedContent,
    HallucinationLayer,
    QualityMetrics,
)

router = APIRouter(prefix="/api/v1", tags=["AI Draft Review"])


def _build_response(raw: dict) -> AiDraftReviewData:
    gc_raw = raw["generated_content"]
    return AiDraftReviewData(
        id=raw["id"],
        wizard_id=raw["wizard_id"],
        enterprise_id=raw["enterprise_id"],
        created_by_user_id=raw["created_by_user_id"],
        status=raw["status"],
        business_owner_approver_id=raw["business_owner_approver_id"],
        final_approver_id=raw["final_approver_id"],
        legal_compliance_reviewer_id=raw["legal_compliance_reviewer_id"],
        security_reviewer_id=raw["security_reviewer_id"],
        generated_content=GeneratedContent(
            document_title=gc_raw["document_title"],
            client=gc_raw["client"],
            generated_date=gc_raw["generated_date"],
            section_count=gc_raw["section_count"],
            sections=[DraftSection(**s) for s in gc_raw["sections"]],
        ),
        quality_metrics=QualityMetrics(**raw["quality_metrics"]),
        hallucination_layers=[HallucinationLayer(**h) for h in raw["hallucination_layers"]],
        prohibited_clause_flags=raw["prohibited_clause_flags"],
        has_unresolved_prohibited_clauses=raw["has_unresolved_prohibited_clauses"],
        created_at=raw["created_at"],
        updated_at=raw["updated_at"],
        submitted_at=raw["submitted_at"],
        approved_at=raw.get("approved_at"),
    )


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/v1/plans
# Get full AI draft review for a wizard session
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/plans",
    response_model=AiDraftReviewResponse,
    operation_id="get_ai_draft_review",
    summary="Get full AI draft review",
    description=(
        "**Returns the complete AI-generated SOW draft review for a given wizard session.**\n\n"
        "### Available test wizard_ids (from mock_db.json):\n"
        "| wizard_id | enterprise_id | Status | Scenario |\n"
        "|-----------|---------------|--------|----------|\n"
        "| `69e36e960a1dd5877b9873ff` | `69d7465a2c5abe973ac687d5` | approved | All 8 layers green |\n"
        "| `WIZARD-DRAFT-001` | `ENT-BETA-999` | draft | Medium risk, timeline missing |\n"
        "| `WIZARD-REJECTED-001` | `ENT-GAMMA-555` | rejected | 2 prohibited clause flags |\n\n"
        "### Response includes:\n"
        "| Field | Description |\n"
        "|-------|-------------|\n"
        "| `generated_content` | Full AI-generated document with numbered sections |\n"
        "| `quality_metrics` | Overall confidence, risk score, completeness % |\n"
        "| `hallucination_layers` | Anti-hallucination pipeline (green / amber / red / grey) |\n"
        "| `prohibited_clause_flags` | Any flagged prohibited clauses |\n"
        "| `status` | draft · submitted · approved · rejected |\n\n"
        "### Confidence colour guide:\n"
        "| Range | Meaning |\n"
        "|-------|---------|\n"
        "| 85–100 | High — ready to approve |\n"
        "| 50–84  | Medium — review recommended |\n"
        "| < 50   | Low — section needs human input |\n\n"
        "### Error codes:\n"
        "| Code | Reason |\n"
        "|------|--------|\n"
        "| 403 | enterprise_id does not match wizard record |\n"
        "| 404 | wizard_id not found |"
    ),
)
def get_ai_draft_review(
    body: AiDraftReviewRequest = Body(
        ...,
        example={
            "wizard_id":     "69e36e960a1dd5877b9873ff",
            "enterprise_id": "69d7465a2c5abe973ac687d5",
        },
    ),
):
    raw = _DRAFT_STORE.get(body.wizard_id)
    if raw is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error": f"Wizard '{body.wizard_id}' not found.",
                "available_wizard_ids": list(_DRAFT_STORE.keys()),
            },
        )

    if raw["enterprise_id"] != body.enterprise_id:
        raise HTTPException(
            status_code=403,
            detail="enterprise_id does not match the wizard record.",
        )

    return AiDraftReviewResponse(
        success=True,
        message=None,
        data=_build_response(raw),
    )
