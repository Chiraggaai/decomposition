from fastapi import APIRouter, HTTPException

router = APIRouter()

# 🔹 Mock storage (should align with other modules)
plan_status_db = {
    1: "PLAN REVIEW REQUIRED"  # other states: REVISION IN PROGRESS, CONFIRMED
}

checklist_db = {
    1: {
        "item1": True,
        "item2": True,
        "item3": True
    }
}


# 1️⃣ CONFIRM PLAN API
@router.post("/{plan_id}/confirm", operation_id="confirm_plan_action")
def confirm_plan(plan_id: int):

    # 🔴 Check plan exists
    if plan_id not in plan_status_db:
        raise HTTPException(status_code=404, detail="Plan not found")

    status = plan_status_db[plan_id]

    # 🔴 Prevent re-confirmation
    if status == "CONFIRMED":
        raise HTTPException(status_code=400, detail="Plan already confirmed")

    # 🔴 Prevent confirmation during revision
    if status == "REVISION IN PROGRESS":
        raise HTTPException(
            status_code=400,
            detail="Cannot confirm while revision is in progress"
        )

    # 🔴 Validate checklist
    checklist = checklist_db.get(plan_id)

    if not checklist or not all(checklist.values()):
        raise HTTPException(
            status_code=400,
            detail="Checklist not completed"
        )

    # 🔹 Update status
    plan_status_db[plan_id] = "CONFIRMED"

    # 🔹 (Future) trigger contributor matching
    # trigger_matching(plan_id)

    return {
        "message": "Plan confirmed successfully",
        "status": plan_status_db[plan_id]
    }