from fastapi import APIRouter, HTTPException
from datetime import date

router = APIRouter()

# Mock Data (replace later with DB)
tasks_db = [
    {"id": 1, "milestone": "M1", "effort": 5, "skills": ["Python"], "critical": True},
    {"id": 2, "milestone": "M1", "effort": 3, "skills": ["React"], "critical": False},
    {"id": 3, "milestone": "M2", "effort": 4, "skills": ["SQL"], "critical": True},
]

plan_dates = {
    1: {
        "sow_start": date(2026, 4, 1),
        "sow_end": date(2026, 4, 10),
        "plan_start": date(2026, 4, 1),
        "plan_end": date(2026, 4, 12)
    }
}


# ✅ SUMMARY PANEL API
@router.get("/{plan_id}/summary-panel")
def get_summary_panel(plan_id: int):

    if plan_id not in plan_dates:
        raise HTTPException(status_code=404, detail="Plan not found")

    # 🔹 Total milestones
    milestones = set(task["milestone"] for task in tasks_db)
    total_milestones = len(milestones)

    # 🔹 Total tasks
    total_tasks = len(tasks_db)

    # 🔹 Total effort
    total_effort = sum(task["effort"] for task in tasks_db)

    # 🔹 Critical path
    critical_tasks = [t for t in tasks_db if t["critical"]]
    critical_path_days = sum(t["effort"] for t in critical_tasks)
    critical_tasks_count = len(critical_tasks)

    # 🔹 Skill coverage
    skills = set()
    for task in tasks_db:
        skills.update(task["skills"])

    # 🔹 Date validation
    dates = plan_dates[plan_id]
    diff = (dates["plan_end"] - dates["sow_end"]).days

    warning = None
    if diff > 0:
        warning = f"Plan exceeds SOW by {diff} days"

    return {
        "total_milestones": total_milestones,
        "total_tasks": total_tasks,
        "total_effort_days": total_effort,
        "critical_path_days": critical_path_days,
        "critical_tasks_count": critical_tasks_count,
        "skills": list(skills),
        "sow_start": dates["sow_start"],
        "sow_end": dates["sow_end"],
        "plan_start": dates["plan_start"],
        "plan_end": dates["plan_end"],
        "date_warning": warning
    }