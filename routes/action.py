# routes/action.py — Plan Actions

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Body, HTTPException, Path, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/plans/actions", tags=["Plan Actions"])

_PLAN_ID = Path(..., description="Plan identifier", example="PLAN-001")

# ── Store — pre-seeded from mock_db.json ─────────────────────────────────────
from mock_db import action_store as _store  # noqa: E402


def _get_or_init(plan_id: str) -> dict:
    if plan_id not in _store:
        _store[plan_id] = {
            "status":      "PENDING",
            "approved_by": None,
            "approved_at": None,
        }
    return _store[plan_id]


# ── Request schema ────────────────────────────────────────────────────────────

class ApproveRequest(BaseModel):
    approved_by: str = Field(
        ...,
        min_length=1,
        description="User ID or display name of the approver.",
    )
    model_config = {"json_schema_extra": {"example": {"approved_by": "enterprise_user_001"}}}


# ─────────────────────────────────────────────────────────────────────────────
# POST /plans/actions/{plan_id}/approve
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/{plan_id}/approve",
    operation_id="action_approve_plan",
    summary="Approve the plan",
    description=(
        "**Frontend Approve button handler.**\n\n"
        "### On success:\n"
        "- `status` → `APPROVED`\n\n"
        "### Error codes:\n"
        "| Code | Reason |\n"
        "|------|--------|\n"
        "| 404 | Plan not found |\n"
        "| 409 | Plan is already approved |"
    ),
)
def approve_plan(
    plan_id: str = _PLAN_ID,
    body: ApproveRequest = Body(...),
):
    rec = _store.get(plan_id)
    if rec is None:
        raise HTTPException(status_code=404, detail=f"Plan '{plan_id}' not found.")
    if rec["status"] == "APPROVED":
        raise HTTPException(status_code=409, detail="Plan is already approved.")

    rec["status"]      = "APPROVED"
    rec["approved_by"] = body.approved_by
    rec["approved_at"] = datetime.now(timezone.utc).isoformat()

    return {
        "success":     True,
        "message":     "Plan approved successfully.",
        "plan_id":     plan_id,
        "status":      rec["status"],
        "approved_by": rec["approved_by"],
        "approved_at": rec["approved_at"],
    }


# ─────────────────────────────────────────────────────────────────────────────
# DELETE /plans/actions/{plan_id}/withdraw
# ─────────────────────────────────────────────────────────────────────────────

@router.delete(
    "/{plan_id}/withdraw",
    operation_id="action_withdraw_plan",
    summary="Withdraw — permanently delete the project",
    description=(
        "**Mapped to the Withdraw button.**\n\n"
        "Permanently deletes all plan data from every backend store "
        "(action store + AI-edit store).\n\n"
        "### What happens on success:\n"
        "- Plan record is hard-deleted from the action store\n"
        "- AI-edit history and tasks are hard-deleted from the edit store\n"
        "- `deleted_at` timestamp is returned\n"
        "- Frontend should remove the plan from its state and navigate away\n\n"
        "### Error codes:\n"
        "| Code | Reason |\n"
        "|------|--------|\n"
        "| 404 | Plan not found in any store |"
    ),
    responses={
        200: {"description": "Plan deleted successfully."},
        404: {"description": "Plan not found."},
    },
)
def withdraw_plan(plan_id: str = _PLAN_ID):
    from routes.enterprise_decomposition import _edit_store

    in_action_store = plan_id in _store
    in_edit_store   = plan_id in _edit_store

    if not in_action_store and not in_edit_store:
        raise HTTPException(
            status_code=404,
            detail=f"Plan '{plan_id}' not found. Nothing to withdraw.",
        )

    _store.pop(plan_id, None)
    _edit_store.pop(plan_id, None)

    return {
        "success":      True,
        "message":      f"Plan '{plan_id}' has been permanently deleted from the backend.",
        "plan_id":      plan_id,
        "deleted_from": {
            "action_store": in_action_store,
            "edit_store":   in_edit_store,
        },
        "deleted_at": datetime.now(timezone.utc).isoformat(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# POST /plans/actions/kickoff
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/kickoff",
    operation_id="action_kickoff",
    summary="Kick-off a plan",
    description=(
        "Initialises the plan record and returns its current status. "
        "Call this when the user clicks the Kick-off button."
    ),
)
def kickoff(
    plan_id: str = Query(..., description="Plan identifier", example="PLAN-001"),
):
    rec = _get_or_init(plan_id)
    return {
        "success": True,
        "message": "Plan initialised." if rec["status"] == "PENDING" else f"Plan is already {rec['status']}.",
        "plan_id": plan_id,
        "status":  rec["status"],
    }
