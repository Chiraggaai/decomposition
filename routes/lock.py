from fastapi import APIRouter, HTTPException

router = APIRouter()

# 🔹 Mock DB (keep consistent across modules)
plan_status_db = {
    1: "CONFIRMED"   # possible: PLAN REVIEW REQUIRED, REVISION IN PROGRESS, CONFIRMED, PLAN LOCKED
}

project_started_db = {
    1: True   # simulate kickoff access control
}


# 1️⃣ LOCK PLAN API (Triggered by contributor acceptance)
@router.post("/{plan_id}/lock")
def lock_plan(plan_id: int):

    # 🔴 Check plan exists
    if plan_id not in plan_status_db:
        raise HTTPException(status_code=404, detail="Plan not found")

    # 🔴 Check project access (Rule DCP-005)
    if not project_started_db.get(plan_id, False):
        raise HTTPException(
            status_code=403,
            detail="This project has not been kicked off yet"
        )

    status = plan_status_db[plan_id]

    # 🔴 Only CONFIRMED plans can be locked
    if status != "CONFIRMED":
        raise HTTPException(
            status_code=400,
            detail="Plan must be CONFIRMED before locking"
        )

    # 🔴 Prevent re-lock
    if status == "PLAN LOCKED":
        raise HTTPException(
            status_code=400,
            detail="Plan is already locked"
        )

    # 🔹 Update status
    plan_status_db[plan_id] = "PLAN LOCKED"

    return {
        "message": "Plan locked successfully. Delivery has started.",
        "status": plan_status_db[plan_id]
    }


# 2️⃣ GET PLAN STATUS API (for UI control)
@router.get("/{plan_id}/status")
def get_plan_status(plan_id: int):

    # 🔴 Check plan exists
    if plan_id not in plan_status_db:
        raise HTTPException(status_code=404, detail="Plan not found")

    # 🔴 Access control before kickoff (Rule DCP-005)
    if not project_started_db.get(plan_id, False):
        raise HTTPException(
            status_code=403,
            detail="This project has not been kicked off yet"
        )

    status = plan_status_db[plan_id]

    return {
        "plan_id": plan_id,
        "status": status,
        "is_locked": status == "PLAN LOCKED",
        "can_request_revision": status not in ["PLAN LOCKED"],
        "can_confirm": status == "PLAN REVIEW REQUIRED"
    }