# routes/actions.py

from fastapi import APIRouter

router = APIRouter(
    prefix="/plans/actions",
    tags=["Plan Actions"]
)

@router.post("/kickoff")
def kickoff(plan_id: str):
    # 1. Generate plan using AI
    # 2. Save to DB
    # 3. Set status = PLAN_REVIEW_REQUIRED

    return {
        "message": "Plan generated successfully",
        "status": "PLAN_REVIEW_REQUIRED"
    }

@router.delete(
    "/{plan_id}/withdraw",
    operation_id="withdraw_plan"
)
def withdraw_plan(plan_id: str):
    # TODO: delete from DB

    return {
        "message": f"Plan {plan_id} withdrawn successfully",
        "status": "WITHDRAWN"
    }