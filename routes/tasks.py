from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional

router = APIRouter()

# In-memory data (since no DB)
tasks_db = [
    {
        "id": 1,
        "milestone": "M1",
        "task_name": "Design API",
        "skills": "Python",
        "seniority": "Senior",
        "effort": 5,
        "start_date": "2026-04-01",
        "end_date": "2026-04-05",
        "critical": True
    },
    {
        "id": 2,
        "milestone": "M1",
        "task_name": "Build UI",
        "skills": "React",
        "seniority": "Junior",
        "effort": 3,
        "start_date": "2026-04-06",
        "end_date": "2026-04-08",
        "critical": False
    }
]

# 1️⃣ GET ALL TASKS (Gantt + List View)
@router.get("/{plan_id}/tasks")
def get_tasks(plan_id: int):
    return {"tasks": tasks_db}


# 2️⃣ FILTER + SORT TASKS
@router.get("/{plan_id}/tasks/query")
def query_tasks(
    plan_id: int,
    milestone: Optional[str] = None,
    sort_by: Optional[str] = "id"
):
    data = tasks_db

    if milestone:
        data = [t for t in data if t["milestone"] == milestone]

    try:
        data = sorted(data, key=lambda x: x.get(sort_by))
    except:
        raise HTTPException(status_code=400, detail="Invalid sort field")

    return {"tasks": data}


# 3️⃣ TASK DETAIL (CLICK ACTION)
@router.get("/{plan_id}/tasks/{task_id}")
def get_task(plan_id: int, task_id: int):
    for task in tasks_db:
        if task["id"] == task_id:
            return task

    raise HTTPException(status_code=404, detail="Task not found")


# 4️⃣ MILESTONE → TASK HIERARCHY
@router.get("/{plan_id}/milestones")
def get_milestones(plan_id: int):
    result = {}

    for task in tasks_db:
        key = task["milestone"]
        if key not in result:
            result[key] = []
        result[key].append(task)

    return {"milestones": result}


# 5️⃣ CRITICAL PATH TASKS
@router.get("/{plan_id}/critical-path")
def critical_tasks(plan_id: int):
    data = [t for t in tasks_db if t["critical"]]
    return {"critical_tasks": data}