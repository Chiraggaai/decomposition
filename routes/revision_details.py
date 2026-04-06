from fastapi import APIRouter, HTTPException

router = APIRouter()

# 🔹 Same shared mock DB (keep consistent)
plans_db = {
    1: [
        {
            "revision_id": 1,
            "tasks": [
                {"id": 1, "name": "Setup Project", "effort": 2},
                {"id": 2, "name": "Design DB", "effort": 3}
            ],
            "notes": "Initial plan"
        },
        {
            "revision_id": 2,
            "tasks": [
                {"id": 1, "name": "Setup Project", "effort": 3},
                {"id": 3, "name": "API Development", "effort": 5}
            ],
            "notes": "Updated effort and added API task"
        }
    ]
}


# 2️⃣ GET REVISION DETAIL
@router.get("/{plan_id}/revisions/{revision_id}")
def get_revision_detail(plan_id: int, revision_id: int):

    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail="Plan not found")

    versions = plans_db[plan_id]

    for version in versions:
        if version["revision_id"] == revision_id:
            return {
                "revision_id": revision_id,
                "notes": version["notes"],
                "tasks": version["tasks"]
            }

    raise HTTPException(status_code=404, detail="Revision not found")