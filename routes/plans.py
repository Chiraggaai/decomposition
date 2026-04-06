# routes/plans.py

from fastapi import APIRouter, HTTPException, Path, Body
from models import (
    PlanResponse,
    PlanStatusResponse,
    ConfirmPlanRequest,
    RevisionRequest,
    LockPlanRequest,
    PlanStatus,
)

router = APIRouter(prefix="/plans", tags=["Plans"])

@router.get(
    "",
    summary="List all plans (dashboard overview)",
    response_model=list[PlanStatusResponse],
)
def list_plans():
    """
    Returns a lightweight summary of all plans.
    Used by the frontend to populate the sidebar and
    'Needs Your Attention' section.
    """
    # TODO: query your DB
    # Example (SQLAlchemy):
    #   plans = db.query(Plan).all()
    #   return [PlanStatusResponse(**p.__dict__) for p in plans]
    #
    # Example (MongoDB):
    #   plans = await db["plans"].find({}, {"phases": 0, "risks": 0, "budget": 0}).to_list()
    #   return [PlanStatusResponse(**p) for p in plans]
    return []


# ─────────────────────────────────────────────────────────────
# GET /plans/{plan_id}
# Fetch full plan — populates the dashboard card
# ─────────────────────────────────────────────────────────────
@router.get(
    "/{plan_id}",
    response_model=PlanResponse,
    summary="Fetch full plan for dashboard review",
    description=(
        "Fetches the AGI-generated plan so the enterprise can read it "
        "inside the **'Plan review required'** dashboard card.\n\n"
        "### Status meanings\n"
        "| Status | Meaning |\n"
        "|---|---|\n"
        "| `PLAN_REVIEW_REQUIRED` | AGI generated the plan. Enterprise must review & confirm. |\n"
        "| `REVISION_IN_PROGRESS` | Enterprise requested changes. AGI is re-generating. Read-only. |\n"
        "| `PLAN_CONFIRMED` | Enterprise confirmed. Contributor matching is running. |\n"
        "| `PLAN_LOCKED` | A contributor accepted. Plan is now the contractual delivery structure. |"
    ),
)
def get_plan(
    plan_id: str = Path(..., description="Unique plan ID, e.g. PLAN-001"),
):
    """
    Returns the full plan that populates the dashboard review card.

    Frontend field mapping:
    - dashboard_message              → card title
    - status                         → badge colour
    - is_read_only                   → disable Confirm / Edit buttons
    - is_urgent                      → show 'Needs Attention' badge
    - revision_estimated_minutes     → show when REVISION_IN_PROGRESS
    - locked_at                      → show lock info when PLAN_LOCKED
    """
    # TODO: query your DB
    # Example (SQLAlchemy):
    #   plan = db.query(Plan).filter(Plan.plan_id == plan_id).first()
    #
    # Example (MongoDB):
    #   plan = await db["plans"].find_one({"plan_id": plan_id})

    plan = None  # ← replace with real DB query

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail={
                "error":   "Plan not found",
                "plan_id": plan_id,
                "message": f"No plan with ID '{plan_id}' exists.",
            },
        )

    # TODO: return PlanResponse(**plan) or PlanResponse.model_validate(plan)


# ─────────────────────────────────────────────────────────────
# GET /plans/{plan_id}/status
# Lightweight status-only check — for polling while revision runs
# ─────────────────────────────────────────────────────────────
@router.get(
    "/{plan_id}/status",
    response_model=PlanStatusResponse,
    summary="Get current status of a plan",
    description=(
        "Lightweight endpoint — returns only the status fields.\n\n"
        "**Use case:** Frontend polls this every 30–60 seconds while "
        "`REVISION_IN_PROGRESS` to know when AGI has finished re-generating. "
        "When status changes back to `PLAN_REVIEW_REQUIRED`, the frontend "
        "re-fetches the full plan via `GET /plans/{plan_id}`."
    ),
)
def get_plan_status(
    plan_id: str = Path(..., description="Unique plan ID"),
):
    # TODO: query your DB (select only status fields, not full plan)
    # Example (SQLAlchemy):
    #   plan = db.query(
    #       Plan.plan_id, Plan.project_name, Plan.status,
    #       Plan.dashboard_message, Plan.is_read_only,
    #       Plan.is_urgent, Plan.revision_estimated_minutes
    #   ).filter(Plan.plan_id == plan_id).first()
    #
    # Example (MongoDB):
    #   plan = await db["plans"].find_one(
    #       {"plan_id": plan_id},
    #       {"plan_id":1, "project_name":1, "status":1,
    #        "dashboard_message":1, "is_read_only":1,
    #        "is_urgent":1, "revision_estimated_minutes":1}
    #   )

    plan = None  # ← replace with real DB query

    if plan is None:
        raise HTTPException(
            status_code=404,
            detail=f"Plan '{plan_id}' not found.",
        )

    # TODO: return PlanStatusResponse(**plan)


# ─────────────────────────────────────────────────────────────
# POST /plans/{plan_id}/confirm
# Enterprise confirms the plan → status becomes PLAN_CONFIRMED
# ─────────────────────────────────────────────────────────────
@router.post(
    "/{plan_id}/confirm",
    summary="Enterprise confirms the plan",
    description=(
        "Moves the plan from `PLAN_REVIEW_REQUIRED` → `PLAN_CONFIRMED`.\n\n"
        "**What happens after this:**\n"
        "- Contributor matching begins running in the background.\n"
        "- The Teams module starts populating with assignment offers.\n"
        "- Plan is confirmed but **not yet locked** — it locks when "
        "the first contributor accepts an offer."
    ),
)
def confirm_plan(
    plan_id: str = Path(..., description="Unique plan ID"),
    body: ConfirmPlanRequest = Body(...),
):
    """
    Only valid when current status is PLAN_REVIEW_REQUIRED.
    Returns 409 if plan is not in a confirmable state.
    """
    # TODO: fetch plan from DB
    # plan = db.query(Plan).filter(Plan.plan_id == plan_id).first()
    # if not plan:
    #     raise HTTPException(status_code=404, detail=f"Plan '{plan_id}' not found.")

    # TODO: guard — only allow confirm when status is PLAN_REVIEW_REQUIRED
    # if plan.status != PlanStatus.PLAN_REVIEW_REQUIRED:
    #     raise HTTPException(
    #         status_code=409,
    #         detail={
    #             "error":          "Invalid status transition",
    #             "current_status": plan.status,
    #             "message":        "Plan can only be confirmed when status is PLAN_REVIEW_REQUIRED.",
    #         },
    #     )

    # TODO: update plan in DB
    # plan.status            = PlanStatus.PLAN_CONFIRMED
    # plan.confirmed_at      = datetime.utcnow().isoformat()
    # plan.is_read_only      = False
    # plan.is_urgent         = False
    # plan.dashboard_message = f"Plan confirmed: {plan.project_name}"
    # db.commit()

    # TODO: trigger contributor matching background job / queue

    return {
        "message":    "Plan confirmed successfully.",
        "plan_id":    plan_id,
        "new_status": PlanStatus.PLAN_CONFIRMED,
        "next_step":  "Contributor matching is now running. Teams module will begin populating.",
    }


# ─────────────────────────────────────────────────────────────
# POST /plans/{plan_id}/request-revision
# Enterprise requests changes → status becomes REVISION_IN_PROGRESS
# ─────────────────────────────────────────────────────────────
@router.post(
    "/{plan_id}/request-revision",
    summary="Enterprise requests a plan revision",
    description=(
        "Moves the plan from `PLAN_REVIEW_REQUIRED` → `REVISION_IN_PROGRESS`.\n\n"
        "**What happens after this:**\n"
        "- Plan becomes **read-only** during revision.\n"
        "- AGI begins re-generating the plan.\n"
        "- Enterprise is notified when revision is complete.\n"
        "- Estimated revision time: **15–60 minutes**."
    ),
)
def request_revision(
    plan_id: str = Path(..., description="Unique plan ID"),
    body: RevisionRequest = Body(...),
):
    """
    Only valid when current status is PLAN_REVIEW_REQUIRED.
    Returns 409 if plan is already locked or in revision.
    """
    # TODO: fetch plan from DB
    # plan = db.query(Plan).filter(Plan.plan_id == plan_id).first()
    # if not plan:
    #     raise HTTPException(status_code=404, detail=f"Plan '{plan_id}' not found.")

    # TODO: guard — only allow revision when status is PLAN_REVIEW_REQUIRED
    # if plan.status != PlanStatus.PLAN_REVIEW_REQUIRED:
    #     raise HTTPException(
    #         status_code=409,
    #         detail={
    #             "error":          "Invalid status transition",
    #             "current_status": plan.status,
    #             "message":        "Revision can only be requested when status is PLAN_REVIEW_REQUIRED.",
    #         },
    #     )

    # TODO: update plan in DB
    # plan.status                     = PlanStatus.REVISION_IN_PROGRESS
    # plan.is_read_only               = True
    # plan.revision_requested_at      = datetime.utcnow().isoformat()
    # plan.revision_estimated_minutes = "15–60 min"
    # plan.dashboard_message          = f"Revision in progress: {plan.project_name}"
    # db.commit()

    # TODO: trigger AGI re-generation background job / queue

    return {
        "message":            "Revision request submitted.",
        "plan_id":            plan_id,
        "new_status":         PlanStatus.REVISION_IN_PROGRESS,
        "estimated_revision": "15–60 min",
        "next_step":          "Plan is read-only. Enterprise will be notified when revision is complete.",
    }


# ─────────────────────────────────────────────────────────────
# POST /plans/{plan_id}/lock
# First contributor accepts → status becomes PLAN_LOCKED
# ─────────────────────────────────────────────────────────────
@router.post(
    "/{plan_id}/lock",
    summary="Lock the plan when first contributor accepts",
    description=(
        "Moves the plan from `PLAN_CONFIRMED` → `PLAN_LOCKED`.\n\n"
        "**Triggered by:** the moment the first contributor accepts an assignment offer.\n\n"
        "**What this means:**\n"
        "- Plan is now the **contractual delivery structure**.\n"
        "- No further revisions allowed — changes require a formal **Change Request via Admin**.\n"
        "- Plan can still be viewed but not edited."
    ),
)
def lock_plan(
    plan_id: str = Path(..., description="Unique plan ID"),
    body: LockPlanRequest = Body(...),
):
    """
    Only valid when current status is PLAN_CONFIRMED.
    Called internally when a contributor accepts an offer — not directly by the enterprise.
    """
    # TODO: fetch plan from DB
    # plan = db.query(Plan).filter(Plan.plan_id == plan_id).first()
    # if not plan:
    #     raise HTTPException(status_code=404, detail=f"Plan '{plan_id}' not found.")

    # TODO: guard — only lock when status is PLAN_CONFIRMED
    # if plan.status != PlanStatus.PLAN_CONFIRMED:
    #     raise HTTPException(
    #         status_code=409,
    #         detail={
    #             "error":          "Invalid status transition",
    #             "current_status": plan.status,
    #             "message":        "Plan can only be locked from PLAN_CONFIRMED status.",
    #         },
    #     )

    # TODO: update plan in DB
    # plan.status                   = PlanStatus.PLAN_LOCKED
    # plan.is_read_only             = True
    # plan.locked_at                = datetime.utcnow().isoformat()
    # plan.locked_by_contributor_id = body.contributor_id
    # plan.dashboard_message        = f"Plan locked — Delivery started: {plan.project_name}"
    # db.commit()

    return {
        "message":    "Plan is now locked. Delivery has started.",
        "plan_id":    plan_id,
        "new_status": PlanStatus.PLAN_LOCKED,
        "locked_by":  body.contributor_id,
        "next_step":  "Changes require a formal Change Request via Admin.",
    }

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/plans", tags=["Plans"])

# Temporary DB
plans_db = {
    1: {
        "revision": 0,
        "status": "PLAN_REVIEW_REQUIRED",
        "checklist": {"item1": True, "item2": True, "item3": False}
    }
}

# 1. Get Revision
@router.get("/{plan_id}/revision")
def get_revision(plan_id: int):
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail="Plan not found")

    return {
        "plan_id": plan_id,
        "revision": plans_db[plan_id]["revision"]
    }

# 2. Increase Revision
@router.post("/{plan_id}/revision")
def increase_revision(plan_id: int):
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail="Plan not found")

    if plans_db[plan_id]["revision"] >= 3:
        return {"message": "Max revision reached"}

    plans_db[plan_id]["revision"] += 1
    return {"revision": plans_db[plan_id]["revision"]}

# 3. Plan Summary
@router.get("/{plan_id}/summary")
def get_summary(plan_id: int):
    return {
        "total_milestones": 5,
        "total_tasks": 20,
        "effort_days": 15
    }

# 4. Request Revision
@router.post("/{plan_id}/request-revision")
def request_revision(plan_id: int):
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail="Plan not found")

    if plans_db[plan_id]["status"] != "PLAN_REVIEW_REQUIRED":
        raise HTTPException(status_code=400, detail="Not allowed")

    return {"message": "Revision requested"}

# 5. Get Status
@router.get("/{plan_id}/status")
def get_status(plan_id: int):
    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail="Plan not found")

    return {"status": plans_db[plan_id]["status"]}

# 6. Checklist
@router.get("/{plan_id}/checklist-status")
def get_checklist(plan_id: int):
    return plans_db[plan_id]["checklist"]

# 7. Confirm Plan
@router.post("/{plan_id}/confirm")
def confirm_plan(plan_id: int):
    checklist = plans_db[plan_id]["checklist"]

    if not all(checklist.values()):
        raise HTTPException(status_code=400, detail="Checklist incomplete")

    plans_db[plan_id]["status"] = "PLAN_CONFIRMED"
    return {"message": "Plan confirmed"}
