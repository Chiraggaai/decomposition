from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date

router = APIRouter()

# In-memory storage
checklist_db = {
    1: {
        "item1": False,
        "item2": False,
        "item3": False
    }
}

# Mock SOW & Plan dates
plan_dates = {
    1: {
        "sow_start": date(2026, 4, 1),
        "sow_end": date(2026, 4, 10),
        "plan_start": date(2026, 4, 1),
        "plan_end": date(2026, 4, 12)
    }
}

# Request model
class ChecklistUpdate(BaseModel):
    item1: bool
    item2: bool
    item3: bool


# 1️⃣ GET CHECKLIST
@router.get("/{plan_id}/checklist")
def get_checklist(plan_id: int):
    return checklist_db.get(plan_id, {})


# 2️⃣ UPDATE CHECKLIST
@router.post("/{plan_id}/checklist")
def update_checklist(plan_id: int, data: ChecklistUpdate):
    checklist_db[plan_id] = data.dict()
    return {"message": "Checklist updated"}


# 3️⃣ VALIDATE CHECKLIST (ALL CHECKED)
@router.get("/{plan_id}/checklist/validate")
def validate_checklist(plan_id: int):
    checklist = checklist_db.get(plan_id)

    if not checklist:
        raise HTTPException(status_code=404, detail="Checklist not found")

    all_checked = all(checklist.values())

    return {
        "all_checked": all_checked,
        "can_confirm": all_checked
    }


# 4️⃣ DATE VALIDATION (SOW vs PLAN)
@router.get("/{plan_id}/checklist/date-validation")
def validate_dates(plan_id: int):
    dates = plan_dates.get(plan_id)

    if not dates:
        raise HTTPException(status_code=404, detail="Plan not found")

    diff = (dates["plan_end"] - dates["sow_end"]).days

    warning = None
    if diff > 0:
        warning = f"Plan exceeds SOW by {diff} days"

    return {
        "sow_start":
        dates["sow_start"],
        "sow_end": dates["sow_end"],
        "plan_start": dates["plan_start"],
        "plan_end": dates["plan_end"],
        "warning": warning
    }