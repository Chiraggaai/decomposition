# routes/enterprise_decomposition.py
"""
Enterprise Decomposition — Submit AI Review
POST /enterprise/decomposition/{plan_id}/edit

Called when the user clicks the "Submit AI Review" button after editing tasks.
Applies user edits, sends to AI for re-review, and returns the updated task list.
"""

from __future__ import annotations

import copy
from datetime import datetime, timezone

from fastapi import APIRouter, Body, HTTPException, Path

from models import (
    BreakdownTask,
    EditAiPlanRequest,
    EditAiPlanResponse,
    EditableTask,
    MilestoneSection,
    TaskBreakdownResponse,
)

router = APIRouter(
    prefix="/enterprise/decomposition",
    tags=["Enterprise Decomposition — Edit AI Plan"],
)

_PLAN_ID = Path(..., description="Plan / project identifier", example="PLAN-001")


# ── Store — pre-seeded from mock_db.json ─────────────────────────────────────
from mock_db import edit_store as _edit_store  # noqa: E402

_MOCK_TASKS: list[dict] = [
    {
        "task_id": 1, "milestone": "M1", "task_name": "Discovery & requirements",
        "skills": "Analysis", "seniority": "Senior", "effort": 5,
        "start_date": "2026-04-01", "end_date": "2026-04-05", "critical": True,
    },
    {
        "task_id": 2, "milestone": "M1", "task_name": "Implementation",
        "skills": "Engineering", "seniority": "Mid", "effort": 10,
        "start_date": "2026-04-06", "end_date": "2026-04-20", "critical": True,
    },
    {
        "task_id": 3, "milestone": "M2", "task_name": "QA & handover",
        "skills": "QA", "seniority": "Junior", "effort": 4,
        "start_date": "2026-04-21", "end_date": "2026-04-25", "critical": False,
    },
]


def _get_or_init(plan_id: str) -> dict:
    if plan_id not in _edit_store:
        _edit_store[plan_id] = {
            "status": "PENDING",
            "tasks": copy.deepcopy(_MOCK_TASKS),
            "edit_history": [],
        }
    return _edit_store[plan_id]


def _apply_task_edits(tasks: list[dict], edits: list) -> tuple[list[dict], int]:
    """Apply user-supplied field overrides to the task list before AI re-review."""
    updated = copy.deepcopy(tasks)
    applied = 0
    for edit in edits:
        for task in updated:
            if task["task_id"] == edit.task_id and edit.field in task:
                task[edit.field] = int(edit.new_value) if edit.field == "effort" else edit.new_value
                applied += 1
    return updated, applied


def _ai_review(tasks: list[dict], notes: str) -> list[dict]:
    """
    AI decomposition re-review stub.
    Replace this body with your real LLM / decomposition service call.
    """
    reviewed = copy.deepcopy(tasks)
    for t in reviewed:
        if "(AI-reviewed)" not in t["task_name"]:
            t["task_name"] += " (AI-reviewed)"
    return reviewed


# ─────────────────────────────────────────────────────────────────────────────
# POST /enterprise/decomposition/{plan_id}/edit
# "Submit AI Review" button
# ─────────────────────────────────────────────────────────────────────────────

@router.post(
    "/{plan_id}/edit",
    response_model=EditAiPlanResponse,
    operation_id="submit_ai_review",
    summary="Submit AI Review — send edited tasks back to AI",
    description=(
        "**Mapped to the `Submit AI Review` button.**\n\n"
        "### Flow:\n"
        "1. User edits task fields on the frontend\n"
        "2. User clicks **Submit AI Review** → this endpoint is called\n"
        "3. `task_edits` field overrides are applied to the current task list\n"
        "4. AI re-reviews the plan against the `notes` and returns an updated breakdown\n"
        "5. Updated tasks are returned for the user to review before Approving\n\n"
        "### Request fields:\n"
        "| Field | Required | Description |\n"
        "|-------|----------|-------------|\n"
        "| `notes` | ✅ | What should change and why (sent to AI) |\n"
        "| `task_edits` | ❌ | Per-task field overrides — `task_id`, `field`, `new_value` |\n\n"
        "### Editable task fields:\n"
        "`task_name` · `effort` · `skills` · `seniority` · `start_date` · `end_date`\n\n"
        "### Error codes:\n"
        "| Code | Reason |\n"
        "|------|--------|\n"
        "| 409 | Plan already approved |\n"
        "| 409 | Plan has been withdrawn |"
    ),
)
def submit_ai_review(
    plan_id: str = _PLAN_ID,
    body: EditAiPlanRequest = Body(
        ...,
        example={
            "notes": "Split the implementation task into frontend and backend, and increase QA effort.",
            "task_edits": [
                {"task_id": 2, "field": "effort",    "new_value": "14"},
                {"task_id": 3, "field": "seniority", "new_value": "Senior"},
            ],
        },
    ),
):
    rec = _get_or_init(plan_id)

    if rec["status"] == "WITHDRAWN":
        raise HTTPException(
            status_code=409,
            detail="This plan has been withdrawn and cannot be submitted for AI review.",
        )
    if rec["status"] == "APPROVED":
        raise HTTPException(
            status_code=409,
            detail="Plan is already approved. Withdraw it first to make further changes.",
        )

    # Step 1 — apply user field overrides
    tasks_with_edits, edits_applied = _apply_task_edits(rec["tasks"], body.task_edits)

    # Step 2 — AI re-review  (swap _ai_review() with real LLM call)
    ai_tasks = _ai_review(tasks_with_edits, body.notes)

    # Step 3 — persist result
    now = datetime.now(timezone.utc).isoformat()
    rec["tasks"] = ai_tasks
    rec["status"] = "AI_REVIEW_SUBMITTED"
    rec["edit_history"].append({
        "submitted_at":  now,
        "notes":         body.notes,
        "task_edits":    [e.model_dump() for e in body.task_edits],
        "edits_applied": edits_applied,
    })

    return EditAiPlanResponse(
        message="AI has reviewed your edits and updated the task breakdown. Review the updated list and Approve.",
        plan_id=plan_id,
        status=rec["status"],
        notes_submitted=body.notes,
        task_edits_applied=edits_applied,
        updated_tasks=[EditableTask(**t) for t in ai_tasks],
        edited_at=now,
    )


# ─────────────────────────────────────────────────────────────────────────────
# Mock AI data — milestone-based breakdown (matches the UI screenshot)
# Replace _MOCK_MILESTONES with real DB / LLM data when ready.
# ─────────────────────────────────────────────────────────────────────────────

_MOCK_MILESTONES: list[dict] = [
    {
        "milestone_id": 1,
        "milestone_name": "Discovery & Requirements",
        "status": "PROPOSED",
        "tasks_completed": 0,
        "task_count": 6,
        "subtask_count": 8,
        "total_hours": 160,
        "tasks": [
            {
                "task_id": 101, "task_name": "Stakeholder interview synthesis",
                "status": "IN_PROGRESS", "priority": "HIGH", "effort_hours": 19,
                "skills": ["TypeScript", "React"], "progress": 88, "dependency_count": 0,
            },
            {
                "task_id": 102, "task_name": "Frontend scaffolding",
                "status": "BACKLOG", "priority": "HIGH", "effort_hours": 48,
                "skills": ["UX Research", "Figma"], "progress": 84, "dependency_count": 0,
            },
            {
                "task_id": 103, "task_name": "Integration test suite",
                "status": "BACKLOG", "priority": "HIGH", "effort_hours": 40,
                "skills": ["Python", "FastAPI"], "progress": 38, "dependency_count": 0,
            },
            {
                "task_id": 104, "task_name": "Security review gates",
                "status": "BACKLOG", "priority": "HIGH", "effort_hours": 32,
                "skills": ["TypeScript", "React"], "progress": 92, "dependency_count": 1,
            },
            {
                "task_id": 105, "task_name": "Data model ERD",
                "status": "BACKLOG", "priority": "HIGH", "effort_hours": 24,
                "skills": ["UX Research", "Figma"], "progress": 81, "dependency_count": 0,
            },
            {
                "task_id": 106, "task_name": "Backend service skeleton",
                "status": "IN_PROGRESS", "priority": "HIGH", "effort_hours": 19,
                "skills": ["Python", "FastAPI"], "progress": 85, "dependency_count": 0,
            },
        ],
    },
    {
        "milestone_id": 2,
        "milestone_name": "Architecture & Design",
        "status": "PROPOSED",
        "tasks_completed": 0,
        "task_count": 6,
        "subtask_count": 10,
        "total_hours": 200,
        "tasks": [
            {
                "task_id": 201, "task_name": "System architecture diagram",
                "status": "BACKLOG", "priority": "HIGH", "effort_hours": 24,
                "skills": ["Architecture", "Figma"], "progress": 0, "dependency_count": 0,
            },
            {
                "task_id": 202, "task_name": "API contract definition",
                "status": "BACKLOG", "priority": "HIGH", "effort_hours": 32,
                "skills": ["FastAPI", "OpenAPI"], "progress": 0, "dependency_count": 1,
            },
            {
                "task_id": 203, "task_name": "Database schema design",
                "status": "BACKLOG", "priority": "MEDIUM", "effort_hours": 40,
                "skills": ["PostgreSQL", "Python"], "progress": 0, "dependency_count": 0,
            },
            {
                "task_id": 204, "task_name": "CI/CD pipeline setup",
                "status": "BACKLOG", "priority": "MEDIUM", "effort_hours": 48,
                "skills": ["DevOps", "GitHub Actions"], "progress": 0, "dependency_count": 0,
            },
            {
                "task_id": 205, "task_name": "Component design system",
                "status": "BACKLOG", "priority": "HIGH", "effort_hours": 32,
                "skills": ["Figma", "React"], "progress": 0, "dependency_count": 0,
            },
            {
                "task_id": 206, "task_name": "Auth flow design",
                "status": "BACKLOG", "priority": "HIGH", "effort_hours": 24,
                "skills": ["TypeScript", "OAuth"], "progress": 0, "dependency_count": 1,
            },
        ],
    },
    {
        "milestone_id": 3,
        "milestone_name": "Core Implementation",
        "status": "PROPOSED",
        "tasks_completed": 0,
        "task_count": 6,
        "subtask_count": 12,
        "total_hours": 240,
        "tasks": [
            {
                "task_id": 301, "task_name": "User authentication module",
                "status": "BACKLOG", "priority": "HIGH", "effort_hours": 40,
                "skills": ["Python", "FastAPI", "JWT"], "progress": 0, "dependency_count": 1,
            },
            {
                "task_id": 302, "task_name": "Dashboard UI components",
                "status": "BACKLOG", "priority": "HIGH", "effort_hours": 48,
                "skills": ["React", "TypeScript"], "progress": 0, "dependency_count": 0,
            },
            {
                "task_id": 303, "task_name": "REST API endpoints",
                "status": "BACKLOG", "priority": "HIGH", "effort_hours": 56,
                "skills": ["FastAPI", "Python"], "progress": 0, "dependency_count": 2,
            },
            {
                "task_id": 304, "task_name": "Database migrations",
                "status": "BACKLOG", "priority": "MEDIUM", "effort_hours": 24,
                "skills": ["PostgreSQL", "Alembic"], "progress": 0, "dependency_count": 1,
            },
            {
                "task_id": 305, "task_name": "Third-party integrations",
                "status": "BACKLOG", "priority": "MEDIUM", "effort_hours": 40,
                "skills": ["Python", "REST"], "progress": 0, "dependency_count": 0,
            },
            {
                "task_id": 306, "task_name": "Error handling & logging",
                "status": "BACKLOG", "priority": "LOW", "effort_hours": 32,
                "skills": ["Python", "Sentry"], "progress": 0, "dependency_count": 0,
            },
        ],
    },
    {
        "milestone_id": 4,
        "milestone_name": "Testing & Deployment",
        "status": "PROPOSED",
        "tasks_completed": 0,
        "task_count": 6,
        "subtask_count": 8,
        "total_hours": 180,
        "tasks": [
            {
                "task_id": 401, "task_name": "End-to-end test suite",
                "status": "BACKLOG", "priority": "HIGH", "effort_hours": 48,
                "skills": ["Playwright", "TypeScript"], "progress": 0, "dependency_count": 2,
            },
            {
                "task_id": 402, "task_name": "Performance benchmarking",
                "status": "BACKLOG", "priority": "MEDIUM", "effort_hours": 24,
                "skills": ["Python", "k6"], "progress": 0, "dependency_count": 1,
            },
            {
                "task_id": 403, "task_name": "Security penetration test",
                "status": "BACKLOG", "priority": "HIGH", "effort_hours": 32,
                "skills": ["Security", "OWASP"], "progress": 0, "dependency_count": 0,
            },
            {
                "task_id": 404, "task_name": "Staging environment setup",
                "status": "BACKLOG", "priority": "MEDIUM", "effort_hours": 24,
                "skills": ["DevOps", "Docker"], "progress": 0, "dependency_count": 0,
            },
            {
                "task_id": 405, "task_name": "Production deployment",
                "status": "BACKLOG", "priority": "HIGH", "effort_hours": 32,
                "skills": ["DevOps", "Kubernetes"], "progress": 0, "dependency_count": 3,
            },
            {
                "task_id": 406, "task_name": "Post-launch monitoring setup",
                "status": "BACKLOG", "priority": "LOW", "effort_hours": 20,
                "skills": ["Datadog", "Python"], "progress": 0, "dependency_count": 0,
            },
        ],
    },
]


def _build_milestone(m: dict, plan_tasks: dict[int, dict] | None = None) -> MilestoneSection:
    """
    Convert a raw milestone dict into the MilestoneSection schema.
    `plan_tasks` is a per-plan override map (task_id → task dict) for
    any edits the user has submitted via the edit endpoint.
    """
    tasks: list[BreakdownTask] = []
    for raw in m["tasks"]:
        # Merge any live edits stored under this plan
        t = {**raw, **(plan_tasks.get(raw["task_id"], {}) if plan_tasks else {})}
        tasks.append(BreakdownTask(
            task_id=t["task_id"],
            task_name=t["task_name"],
            status=t["status"],
            priority=t["priority"],
            effort_hours=t["effort_hours"],
            skills=t["skills"],
            progress=t["progress"],
            dependency_count=t["dependency_count"],
        ))

    return MilestoneSection(
        milestone_id=m["milestone_id"],
        milestone_name=m["milestone_name"],
        status=m["status"],
        tasks_completed=m["tasks_completed"],
        task_count=m["task_count"],
        subtask_count=m["subtask_count"],
        total_hours=m["total_hours"],
        tasks=tasks,
    )


# ─────────────────────────────────────────────────────────────────────────────
# GET /enterprise/decomposition/{plan_id}/breakdown
# Returns the AI plan broken down by milestone sections
# ─────────────────────────────────────────────────────────────────────────────

@router.get(
    "/{plan_id}/breakdown",
    response_model=TaskBreakdownResponse,
    operation_id="get_task_breakdown",
    summary="Get AI plan breakdown by milestone sections",
    description=(
        "**Returns the AI-generated task breakdown organised by milestone sections.**\n\n"
        "This powers the Task Breakdown list view (List / Gantt toggle).\n\n"
        "### Response structure:\n"
        "```\n"
        "milestones[]\n"
        "  ├─ milestone_name   (e.g. 'Discovery & Requirements')\n"
        "  ├─ status           PROPOSED | IN_PROGRESS | DONE\n"
        "  ├─ task_count       total tasks in the section\n"
        "  ├─ subtask_count    total subtasks across all tasks\n"
        "  ├─ total_hours      sum of effort hours in the section\n"
        "  └─ tasks[]\n"
        "       ├─ task_name\n"
        "       ├─ status      IN_PROGRESS | BACKLOG | DONE | PROPOSED\n"
        "       ├─ priority    HIGH | MEDIUM | LOW\n"
        "       ├─ effort_hours\n"
        "       ├─ skills      [ 'TypeScript', 'React', ... ]\n"
        "       ├─ progress    0–100 %\n"
        "       └─ dependency_count\n"
        "```\n\n"
        "### Error codes:\n"
        "| Code | Reason |\n"
        "|------|--------|\n"
        "| 404 | Plan not found |\n"
        "| 409 | Plan has been withdrawn |"
    ),
)
def get_task_breakdown(plan_id: str = _PLAN_ID):
    # Allow calling without a prior kickoff — auto-init read-only plan record
    rec = _get_or_init(plan_id)

    if rec["status"] == "WITHDRAWN":
        raise HTTPException(
            status_code=409,
            detail="This plan has been withdrawn.",
        )

    # Per-plan task overrides stored by the edit endpoint
    plan_task_overrides: dict[int, dict] = rec.get("task_overrides", {})

    milestones = [_build_milestone(m, plan_task_overrides) for m in _MOCK_MILESTONES]

    total_tasks = sum(m.task_count for m in milestones)
    total_hours = sum(m.total_hours for m in milestones)

    return TaskBreakdownResponse(
        plan_id=plan_id,
        total_milestones=len(milestones),
        total_tasks=total_tasks,
        total_hours=total_hours,
        milestones=milestones,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
