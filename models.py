# models.py

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class PlanStatus(str, Enum):
    NEW = "NEW"
    PLAN_REVIEW_REQUIRED = "PLAN_REVIEW_REQUIRED"
    REVISION_IN_PROGRESS = "REVISION_IN_PROGRESS"
    PLAN_CONFIRMED = "PLAN_CONFIRMED"
    PLAN_LOCKED = "PLAN_LOCKED"


# ── Shared sub-models ─────────────────────────────────────────

class PlanPhase(BaseModel):
    phase_number:    int
    phase_name:      str
    duration_weeks:  int
    deliverables:    list[str]
    assigned_team:   str


class PlanRisk(BaseModel):
    risk_id:     str
    description: str
    severity:    str        # LOW | MEDIUM | HIGH
    mitigation:  str


class BudgetBreakdown(BaseModel):
    total_estimated_cost: str
    currency:             str
    breakdown:            dict


# ── Plan summary stats (header strip) ────────────────────────

class PlanSummaryStats(BaseModel):
    total_milestones:          int
    total_tasks:               int
    estimated_total_effort_days: int
    project_start:             str       # DD Mon YYYY
    project_end:               str       # DD Mon YYYY
    critical_path_task_count:  int


# ── Main plan response ────────────────────────────────────────

class PlanResponse(BaseModel):
    plan_id:             str
    project_name:        str
    project_description: str
    sow_reference:       str           # SOW reference shown in page header sublabel
    plan_version:        int           # version number shown in page header sublabel

    # Status
    status:              PlanStatus
    dashboard_message:   str        # e.g. "Plan review required: [project name]"
    is_read_only:        bool       # True when REVISION_IN_PROGRESS or PLAN_LOCKED
    is_urgent:           bool       # True when PLAN_REVIEW_REQUIRED

    # Revision tracking
    revision_count:             int  = 0   # current revision round (0–3)
    max_revisions:              int  = 3   # hard cap
    revision_limit_reached:     bool = False

    # Status-specific fields (None when not applicable)
    revision_estimated_minutes: Optional[str]   = None  # shown when REVISION_IN_PROGRESS
    revision_requested_at:      Optional[str]   = None  # when enterprise submitted revision
    confirmed_at:               Optional[str]   = None  # when enterprise confirmed
    locked_at:                  Optional[str]   = None  # when first contributor accepted
    locked_by_contributor_id:   Optional[str]   = None  # who triggered the lock

    # Plan summary strip
    summary:                PlanSummaryStats

    # Plan content
    objective:              str
    scope:                  str
    total_duration_weeks:   int
    phases:                 list[PlanPhase]
    risks:                  list[PlanRisk]
    budget:                 BudgetBreakdown
    success_metrics:        list[str]
    assumptions:            list[str]
    agi_confidence_score:   float

    # Meta
    generated_by:                      str
    generated_at:                      str
    enterprise_deadline_to_confirm:    str


# ── Request bodies ────────────────────────────────────────────

class ConfirmPlanRequest(BaseModel):
    confirmed_by: str               # user ID or name of the enterprise user confirming


class RevisionRequest(BaseModel):
    requested_by:   str             # user ID
    revision_notes: str             # what the enterprise wants changed


class LockPlanRequest(BaseModel):
    contributor_id:      str        # first contributor who accepted an assignment
    assignment_offer_id: str        # the offer that triggered the lock


# ── Status-only response (lightweight) ───────────────────────

class PlanStatusResponse(BaseModel):
    plan_id:           str
    project_name:      str
    status:            PlanStatus
    dashboard_message: str
    is_read_only:      bool
    is_urgent:         bool
    revision_estimated_minutes: Optional[str] = None


# ── Empty state responses ────────────────────────────────────

class EmptyStateLink(BaseModel):
    label: str
    url:   str


class EmptyStateResponse(BaseModel):
    empty:   bool = True
    reason:  str            # machine-readable key
    message: str            # user-facing text
    cta:     Optional[EmptyStateLink] = None
    links:   Optional[list[EmptyStateLink]] = None

# ─────────────────────────────────────────────────────────────
# PLAN REVIEW PAGE MODELS
# ─────────────────────────────────────────────────────────────

class RevisionRound(str, Enum):
    ROUND_0 = "ROUND_0"   # no revisions yet  → green
    ROUND_1 = "ROUND_1"   # 1 revision used   → amber
    ROUND_2 = "ROUND_2"   # 2 revisions used  → orange
    ROUND_3 = "ROUND_3"   # max reached       → red


class PlanSummaryStrip(BaseModel):
    total_milestones:       int
    total_tasks:            int
    estimated_effort_days:  int
    project_start:          str     # DD Mon YYYY
    project_end:            str     # DD Mon YYYY
    critical_path_tasks:    int


class ReviewChecklistItem(BaseModel):
    item_id:     str
    label:       str
    is_checked:  bool


class PlanReviewPageResponse(BaseModel):
    # Header
    plan_id:          str
    project_name:     str
    sow_reference:    str           # shown as sublabel under project name
    plan_version:     str           # e.g. "v1", "v2"

    # Status & revision counter
    status:           PlanStatus
    revision_round:   RevisionRound
    revision_label:   str           # e.g. "Revision 1 of 3"
    max_revisions_reached: bool
    revision_warning: Optional[str] # set when round 3: "Maximum revisions reached — GlimmoraTeam Admin has been notified."

    # Button states (computed server-side so frontend just reads flags)
    can_request_revision: bool      # True only when PLAN_REVIEW_REQUIRED and round < 3
    can_confirm_plan:     bool      # True only when all checklist checked + PLAN_REVIEW_REQUIRED
    revision_in_progress: bool

    # Summary strip
    summary: PlanSummaryStrip

    # Review checklist (3 items — all must be checked to unlock confirm button)
    checklist: list[ReviewChecklistItem]
    checklist_complete: bool        # True when all 3 are checked


class ChecklistUpdateRequest(BaseModel):
    item_id:    str
    is_checked: bool
    updated_by: str     # user ID


class ChecklistUpdateResponse(BaseModel):
    plan_id:            str
    item_id:            str
    is_checked:         bool
    checklist_complete: bool        # True when all 3 items are now checked
    can_confirm_plan:   bool        # frontend uses this to enable/disable confirm button


# ─────────────────────────────────────────────────────────────────────────────
# ENTERPRISE DECOMPOSITION — Edit AI Plan
# /enterprise/decomposition/{plan_id}/edit
# ─────────────────────────────────────────────────────────────────────────────

class EditableTask(BaseModel):
    """A single task row the user can modify on the Edit page."""
    task_id:    int    = Field(..., example=1)
    milestone:  str    = Field(..., example="M1")
    task_name:  str    = Field(..., example="Design API")
    skills:     str    = Field(..., example="Python")
    seniority:  str    = Field(..., example="Senior")
    effort:     int    = Field(..., description="Effort in days", example=5)
    start_date: str    = Field(..., example="2026-04-01")
    end_date:   str    = Field(..., example="2026-04-05")
    critical:   bool   = Field(..., example=True)


class TaskEdit(BaseModel):
    """One field change submitted by the user for a specific task."""
    task_id:   int = Field(..., description="ID of the task to edit.", example=1)
    field:     str = Field(
        ...,
        description="Field to change: task_name | effort | skills | seniority | start_date | end_date",
        example="effort",
    )
    new_value: str = Field(..., description="New value for the field.", example="8")

    model_config = {
        "json_schema_extra": {"example": {"task_id": 1, "field": "effort", "new_value": "8"}}
    }


class EditAiPlanRequest(BaseModel):
    """
    Body for PUT /enterprise/decomposition/{plan_id}/edit.
    Submitted when the user clicks the Edit button and saves changes.
    """
    notes:      str        = Field(
        ...,
        min_length=5,
        description="What should change and why — sent to AI for review.",
        example="Split the implementation task into frontend and backend, and increase QA effort.",
    )
    task_edits: list[TaskEdit] = Field(
        default_factory=list,
        description="Per-task field overrides (optional). Applied before AI re-review.",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "notes": "Split the implementation task into frontend and backend, and increase QA effort.",
                "task_edits": [
                    {"task_id": 2, "field": "effort",   "new_value": "14"},
                    {"task_id": 3, "field": "seniority", "new_value": "Senior"},
                ],
            }
        }
    }


class EditAiPlanResponse(BaseModel):
    """Response for PUT — returns AI-reviewed updated task list."""
    success:                  bool              = True
    message:                  str
    plan_id:                  str
    status:                   str
    notes_submitted:          str
    task_edits_applied:       int
    updated_tasks:            list[EditableTask]
    edited_at:                str
    next:                     str               = (
        "Review the updated task list, check all checklist items, then Approve."
    )


# ─────────────────────────────────────────────────────────────────────────────
# ENTERPRISE DECOMPOSITION — Task Breakdown
# GET /enterprise/decomposition/{plan_id}/breakdown
# ─────────────────────────────────────────────────────────────────────────────

class BreakdownTask(BaseModel):
    """A single task row inside a milestone section (matches the list UI)."""
    task_id:          int        = Field(..., example=101)
    task_name:        str        = Field(..., example="Stakeholder interview synthesis")
    status:           str        = Field(
        ...,
        description="IN_PROGRESS | BACKLOG | DONE | PROPOSED",
        example="IN_PROGRESS",
    )
    priority:         str        = Field(
        ...,
        description="HIGH | MEDIUM | LOW",
        example="HIGH",
    )
    effort_hours:     int        = Field(..., description="Effort in hours", example=19)
    skills:           list[str]  = Field(
        default_factory=list,
        description="Skill / tech-stack tags shown on the task card.",
        example=["TypeScript", "React"],
    )
    progress:         int        = Field(
        ...,
        description="Completion percentage 0–100",
        example=88,
    )
    dependency_count: int        = Field(
        default=0,
        description="Number of tasks this task depends on.",
        example=1,
    )


class MilestoneSection(BaseModel):
    """
    One collapsible milestone section (e.g. 'Discovery & Requirements').
    Contains multiple tasks produced by the AI breakdown.
    """
    milestone_id:   int                 = Field(..., example=1)
    milestone_name: str                 = Field(..., example="Discovery & Requirements")
    status:         str                 = Field(
        ...,
        description="PROPOSED | IN_PROGRESS | DONE",
        example="PROPOSED",
    )
    tasks_completed: int                = Field(..., description="Number of completed tasks", example=0)
    task_count:      int                = Field(..., description="Total tasks in this milestone", example=6)
    subtask_count:   int                = Field(..., description="Total subtasks across all tasks", example=8)
    total_hours:     int                = Field(..., description="Sum of effort_hours across all tasks", example=160)
    tasks:           list[BreakdownTask]


class TaskBreakdownResponse(BaseModel):
    """Response for GET /enterprise/decomposition/{plan_id}/breakdown."""
    success:           bool                  = True
    plan_id:           str
    total_milestones:  int
    total_tasks:       int
    total_hours:       int                   = Field(..., description="Grand total effort hours across all milestones")
    milestones:        list[MilestoneSection]
    generated_at:      str


# ─────────────────────────────────────────────────────────────────────────────
# AI DRAFT REVIEW
# POST /api/v1/plans
# ─────────────────────────────────────────────────────────────────────────────

class AiDraftReviewRequest(BaseModel):
    """Request body — identify which wizard / enterprise plan to retrieve."""
    wizard_id:     str = Field(..., description="Wizard session identifier.", example="69e36e960a1dd5877b9873ff")
    enterprise_id: str = Field(..., description="Enterprise account identifier.",  example="69d7465a2c5abe973ac687d5")

    model_config = {
        "json_schema_extra": {
            "example": {
                "wizard_id":     "69e36e960a1dd5877b9873ff",
                "enterprise_id": "69d7465a2c5abe973ac687d5",
            }
        }
    }


class DraftSection(BaseModel):
    """One numbered section inside the AI-generated document."""
    section_id: str  = Field(..., example="S1")
    title:      str  = Field(..., example="1. Project Vision & Business Context")
    confidence: int  = Field(..., description="AI confidence score 0–100", example=95)
    content:    str  = Field(..., description="Markdown-formatted section body")


class GeneratedContent(BaseModel):
    """Full AI-generated SOW document."""
    document_title: str            = Field(..., example="Statement of Work — Customer Service /")
    client:         str            = Field(..., example="Microsoft")
    generated_date: str            = Field(..., example="18 April 2026")
    sections:       list[DraftSection]
    section_count:  int            = Field(..., example=8)


class QualityMetrics(BaseModel):
    """AI quality and risk scoring for the generated document."""
    overall_confidence:  float = Field(..., example=66.5)
    risk_score:          float = Field(..., example=15.7)
    risk_level:          str   = Field(..., description="Low | Medium | High", example="Low")
    hallucination_flags: int   = Field(..., example=0)
    completeness_pct:    float = Field(..., example=87.5)
    completeness_status: str   = Field(..., example="Near complete")


class HallucinationLayer(BaseModel):
    """One validation layer in the AI anti-hallucination pipeline."""
    layer_id: int  = Field(..., example=1)
    name:     str  = Field(..., example="Template Selection Validation")
    active:   bool = Field(..., example=True)
    status:   str  = Field(..., description="green | amber | red | grey", example="green")
    detail:   str  = Field(..., example="Platform: Web + Mobile, Category: System migration")


class AiDraftReviewData(BaseModel):
    """Full plan / SOW record returned by the AI draft review endpoint."""
    id:                              str
    wizard_id:                       str
    enterprise_id:                   str
    created_by_user_id:              str
    status:                          str = Field(..., description="draft | submitted | approved | rejected")
    business_owner_approver_id:      str
    final_approver_id:               str
    legal_compliance_reviewer_id:    str
    security_reviewer_id:            str
    generated_content:               GeneratedContent
    quality_metrics:                 QualityMetrics
    hallucination_layers:            list[HallucinationLayer]
    prohibited_clause_flags:         list[str] = Field(default_factory=list)
    has_unresolved_prohibited_clauses: bool    = False
    created_at:  str
    updated_at:  str
    submitted_at: str
    approved_at: Optional[str] = None


class AiDraftReviewResponse(BaseModel):
    """Envelope returned by POST /api/v1/plans."""
    success: bool                    = True
    message: Optional[str]           = None
    data:    AiDraftReviewData