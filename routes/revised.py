from fastapi import APIRouter, HTTPException

router = APIRouter()

# 🔹 Mock versioned plans (IMPORTANT STRUCTURE)
plans_db = {
    1: [
        {   # Revision 1
            "revision_id": 1,
            "tasks": [
                {"id": 1, "name": "Setup Project", "effort": 2},
                {"id": 2, "name": "Design DB", "effort": 3}
            ],
            "notes": "Initial plan"
        },
        {   # Revision 2 (latest)
            "revision_id": 2,
            "tasks": [
                {"id": 1, "name": "Setup Project", "effort": 3},  # modified
                {"id": 3, "name": "API Development", "effort": 5} # added
            ],
            "notes": "Updated effort and added API task"
        }
    ]
}


# 🔹 DIFF LOGIC FUNCTION
def calculate_diff(old_tasks, new_tasks):
    old_map = {t["id"]: t for t in old_tasks}
    new_map = {t["id"]: t for t in new_tasks}

    added = []
    modified = []
    removed = []

    # Added & Modified
    for task_id, task in new_map.items():
        if task_id not in old_map:
            added.append(task_id)
        elif task != old_map[task_id]:
            modified.append(task_id)

    # Removed
    for task_id in old_map:
        if task_id not in new_map:
            removed.append(task_id)

    return added, modified, removed


# 1️⃣ GET REVISED PLAN WITH DIFF
@router.get("/{plan_id}/revised")
def get_revised_plan(plan_id: int):

    if plan_id not in plans_db:
        raise HTTPException(status_code=404, detail="Plan not found")

    versions = plans_db[plan_id]

    # 🔴 Need at least 2 versions for diff
    if len(versions) < 2:
        raise HTTPException(status_code=400, detail="No revision available")

    latest = versions[-1]
    previous = versions[-2]

    added, modified, removed = calculate_diff(
        previous["tasks"],
        latest["tasks"]
    )

    return {
        "current_revision": latest["revision_id"],
        "tasks": latest["tasks"],
        "changes": {
            "added": added,
            "modified": modified,
            "removed": removed
        },
        "summary": {
            "added": len(added),
            "modified": len(modified),
            "removed": len(removed)
        }
    }
