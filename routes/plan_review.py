# routes/plan_review.py

from fastapi import APIRouter, HTTPException, Path, Body
from models import (
    PlanReviewPageResponse,
    ChecklistUpdateRequest,
    ChecklistUpdateResponse,
    PlanStatus,
    RevisionRound,
)

router = APIRouter(prefix="/plans", tags=["Plan Review Page"])


# ─────────────────────────────────────────────────────────────
# GET /plans/{plan_id}/review
# Full data for the Plan Review Page header + summary strip
# ─────────────────────────────────────────────────────────────
@router.get(
    "/{plan_id}/review",
    response_model=PlanReviewPageResponse,
    summary="Load full Plan Review Page",
    description=(
        "Returns everything needed to render the Plan Review Page:\n\n"
        "- Page header (project name, SOW ref, plan version)\n"
        "- Status badge + revision counter badge\n"
        "- Plan summary strip (milestones, tasks, effort, dates, critical path)\n"
        "- Button states: `can_request_revision`, `can_confirm_plan`\n"
        "- Review checklist with current checked state\n\n"
        "**Revision counter colour rules:**\n"
        "| Round | Label | Colour |\n"
        "|---|---|---|\n"
        "| ROUND_0 | Revision 0 of 3 | Green |\n"
        "| ROUND_1 | Revision 1 of 3 | Amber |\n"
        "| ROUND_2 | Revision 2 of 3 | Orange |\n"
        "| ROUND_3 | Revision 3 of 3 | Red — Admin notified |\n\n"
        "**`[Confirm & Activate Plan]` hard gate:**\n"
        "`can_confirm_plan` is only `true` when:\n"
        "- all 3 checklist items are checked, AND\n"
        "- status is `PLAN_REVIEW_REQUIRED`"
    ),
)
def get_plan_review_page(
    plan_id: str = Path(..., description="Unique plan ID"),
):
    """
    Called when enterprise clicks a project row in the Decomposition landing.
    This is the primary data load for the entire Plan Review Page.
    """
    # TODO: fetch plan + checklist from DB
    # plan      = db.query(Plan).filter(Plan.plan_id == plan_id).first()
    # checklist = db.query(Checklist).filter(Checklist.plan_id == plan_id).all()
    # if not plan:
    #     raise HTTPException(status_code=404, detail=f"Plan '{plan_id}' not found.")

    # TODO: compute button states
    # checklist_complete  = all(item.is_checked for item in checklist)
    # can_request_revision = (
    #     plan.status == PlanStatus.PLAN_REVIEW_REQUIRED and
    #     plan.revision_round != RevisionRound.ROUND_3
    # )
    # can_confirm_plan = (
    #     checklist_complete and
    #     plan.status == PlanStatus.PLAN_REVIEW_REQUIRED
    # )

    # TODO: build and return PlanReviewPageResponse(...)
    plan = None  # ← replace with real DB query
    if plan is None:
        raise HTTPException(status_code=404, detail=f"Plan '{plan_id}' not found.")


# ─────────────────────────────────────────────────────────────
# GET /plans/{plan_id}/review/checklist
# Return current checklist state
# ─────────────────────────────────────────────────────────────
@router.get(
    "/{plan_id}/review/checklist",
    summary="Get review checklist state",
    description=(
        "Returns the 3 checklist items and their current checked state.\n\n"
        "The `[Confirm & Activate Plan]` button is disabled until "
        "`checklist_complete` is `true`."
    ),
)
def get_checklist(
    plan_id: str = Path(..., description="Unique plan ID"),
):
    """
    Frontend uses this to re-sync checklist state after page reload
    without re-fetching the full plan review page.
    """
    # TODO: fetch checklist items from DB
    # checklist = db.query(Checklist).filter(Checklist.plan_id == plan_id).all()
    # if not checklist:
    #     raise HTTPException(status_code=404, detail=f"Checklist for plan '{plan_id}' not found.")

    # TODO: return:
    # {
    #     "plan_id": plan_id,
    #     "checklist": [ChecklistItem(**item) for item in checklist],
    #     "checklist_complete": all(i.is_checked for i in checklist),
    # }
    pass


# ─────────────────────────────────────────────────────────────
# PATCH /plans/{plan_id}/review/checklist
# Enterprise checks/unchecks one checklist item
# ─────────────────────────────────────────────────────────────
@router.patch(
    "/{plan_id}/review/checklist",
    response_model=ChecklistUpdateResponse,
    summary="Check or uncheck a review checklist item",
    description=(
        "Updates a single checklist item's checked state.\n\n"
        "Returns `checklist_complete` and `can_confirm_plan` so the "
        "frontend can immediately enable/disable the `[Confirm & Activate Plan]` button "
        "without a full page reload.\n\n"
        "**Hard gate:** even if `can_confirm_plan` is `true` here, the confirm "
        "endpoint will re-validate checklist state server-side."
    ),
)
def update_checklist_item(
    plan_id: str = Path(..., description="Unique plan ID"),
    body: ChecklistUpdateRequest = Body(...),
):
    """
    Called every time the enterprise ticks or unticks a checklist item.
    The confirm button state is driven by the returned can_confirm_plan flag.
    """
    # TODO: fetch plan and checklist from DB
    # plan = db.query(Plan).filter(Plan.plan_id == plan_id).first()
    # if not plan:
    #     raise HTTPException(status_code=404, detail=f"Plan '{plan_id}' not found.")

    # TODO: guard — checklist is not editable when plan is read-only
    # if plan.is_read_only:
    #     raise HTTPException(
    #         status_code=409,
    #         detail={
    #             "error":   "Plan is read-only",
    #             "status":  plan.status,
    #             "message": "Checklist cannot be updated while plan is read-only.",
    #         },
    #     )

    # TODO: update the specific checklist item in DB
    # item = db.query(Checklist).filter(
    #     Checklist.plan_id == plan_id,
    #     Checklist.item_id == body.item_id,
    # ).first()
    # if not item:
    #     raise HTTPException(status_code=404, detail=f"Checklist item '{body.item_id}' not found.")
    # item.is_checked = body.is_checked
    # db.commit()

    # TODO: recompute checklist_complete and can_confirm_plan
    # all_items          = db.query(Checklist).filter(Checklist.plan_id == plan_id).all()
    # checklist_complete = all(i.is_checked for i in all_items)
    # can_confirm_plan   = checklist_complete and plan.status == PlanStatus.PLAN_REVIEW_REQUIRED

    # TODO: return ChecklistUpdateResponse(
    #     plan_id            = plan_id,
    #     item_id            = body.item_id,
    #     is_checked         = body.is_checked,
    #     checklist_complete = checklist_complete,
    #     can_confirm_plan   = can_confirm_plan,
    # )
    pass


# ─────────────────────────────────────────────────────────────
# GET /plans/{plan_id}/review/summary
# Summary strip only — lightweight re-fetch after revision completes
# ─────────────────────────────────────────────────────────────
@router.get(
    "/{plan_id}/review/summary",
    summary="Get plan summary strip data",
    description=(
        "Returns only the summary strip stats:\n"
        "total milestones, total tasks, estimated effort, "
        "project start/end dates, critical path task count.\n\n"
        "**Use case:** re-fetch the strip after a revision completes "
        "without reloading the entire review page."
    ),
)
def get_plan_summary(
    plan_id: str = Path(..., description="Unique plan ID"),
):
    # TODO: fetch summary stats from DB
    # plan = db.query(
    #     Plan.plan_id,
    #     Plan.total_milestones,
    #     Plan.total_tasks,
    #     Plan.estimated_effort_days,
    #     Plan.project_start,
    #     Plan.project_end,
    #     Plan.critical_path_tasks,
    # ).filter(Plan.plan_id == plan_id).first()
    # if not plan:
    #     raise HTTPException(status_code=404, detail=f"Plan '{plan_id}' not found.")
    # return PlanSummaryStrip(**plan)
    pass