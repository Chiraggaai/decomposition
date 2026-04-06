from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter()

# 🔹 Mock storage (shared conceptually with other modules)
revision_db = {
    1: {
        "revision_count": 0,
        "max_revisions": 3,
        "status": "PLAN REVIEW REQUIRED"
    }
}

# This should match your flag API storage
flagged_tasks_db = {
    1: [1, 2]  # task IDs
}

# Mock task names (for display)
tasks_lookup = {
    1: "Design API",
    2: "Build UI",
    3: "Testing"
}


# 🔹 Request model
class RevisionRequest(BaseModel):
    notes: str = Field(..., min_length=30, max_length=2000)


# 1️⃣ GET REVISION MODAL DATA
@router.get("/{plan_id}/revision-modal")
def get_revision_modal(plan_id: int):

    if plan_id not in revision_db:
        raise HTTPException(status_code=404, detail="Plan not found")

    revision_data = revision_db[plan_id]
    flagged_ids = flagged_tasks_db.get(plan_id, [])

    flagged_tasks = [
        {"id": tid, "name": tasks_lookup.get(tid, "Unknown")}
        for tid in flagged_ids
    ]

    return {
        "revision_count": revision_data["revision_count"],
        "max_revisions": revision_data["max_revisions"],
        "status": revision_data["status"],
        "flagged_tasks": flagged_tasks
    }


# 2️⃣ SUBMIT REVISION REQUEST (MAIN ACTION)
@router.post("/{plan_id}/request-revision", operation_id="request_revision_plan")
def request_revision(plan_id: int, data: RevisionRequest):

    if plan_id not in revision_db:
        raise HTTPException(status_code=404, detail="Plan not found")

    revision_data = revision_db[plan_id]

    # 🔴 Check revision limit
    if revision_data["revision_count"] >= revision_data["max_revisions"]:
        raise HTTPException(
            status_code=400,
            detail="Maximum revision limit reached"
        )

    # 🔴 Notes validation handled by Pydantic (min 30 chars)

    # 🔹 Increment revision
    revision_data["revision_count"] += 1

    # 🔹 Change status
    revision_data["status"] = "REVISION IN PROGRESS"

    # 🔹 Clear flagged tasks
    flagged_tasks_db[plan_id] = []

    return {
        "message": "Revision request submitted",
        "revision_count": revision_data["revision_count"],
        "status": revision_data["status"]
    }