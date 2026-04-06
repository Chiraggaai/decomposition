from fastapi import APIRouter, HTTPException

router = APIRouter()

# 🔹 Mock Task Data (extend as needed)
tasks_db = [
    {
        "id": 1,
        "task_id": "TSK-001-001",
        "task_name": "Design API",
        "milestone": "Backend",
        "skills": ["Python", "FastAPI"],
        "seniority": "Senior",
        "effort_days": 5,
        "start_date": "2026-04-01",
        "end_date": "2026-04-05",
        "critical": True,
        "acceptance_criteria": "API should handle 1000 req/sec",
        "data_sensitivity": "High",
        "evidence_types": ["code", "test report"]
    },
    {
        "id": 2,
        "task_id": "TSK-001-002",
        "task_name": "Build UI",
        "milestone": "Frontend",
        "skills": ["React"],
        "seniority": "Junior",
        "effort_days": 3,
        "start_date": "2026-04-06",
        "end_date": "2026-04-08",
        "critical": False,
        "acceptance_criteria": "Responsive UI with API integration",
        "data_sensitivity": "Low",
        "evidence_types": ["design files"]
    }
]

# 🔹 Store flagged tasks per plan
flagged_tasks_db = {
    1: []  # plan_id: [task_ids]
}


# 1️⃣ GET TASK DETAIL
@router.get("/{plan_id}/tasks/{task_id}/detail")
def get_task_detail(plan_id: int, task_id: int):

    for task in tasks_db:
        if task["id"] == task_id:
            return task

    raise HTTPException(status_code=404, detail="Task not found")


# 2️⃣ FLAG TASK FOR REVISION
@router.post("/{plan_id}/tasks/{task_id}/flag")
def flag_task(plan_id: int, task_id: int):

    # Check task exists
    task_exists = any(task["id"] == task_id for task in tasks_db)
    if not task_exists:
        raise HTTPException(status_code=404, detail="Task not found")

    # Initialize if not present
    if plan_id not in flagged_tasks_db:
        flagged_tasks_db[plan_id] = []

    # Avoid duplicate flag
    if task_id not in flagged_tasks_db[plan_id]:
        flagged_tasks_db[plan_id].append(task_id)

    return {
        "message": "Task flagged for revision",
        "total_flagged": len(flagged_tasks_db[plan_id]),
        "flagged_tasks": flagged_tasks_db[plan_id]
    }