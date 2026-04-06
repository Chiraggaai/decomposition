# models.py

from pydantic import BaseModel
from typing import Optional
from enum import Enum


class PlanStatus(str, Enum):
    PLAN_REVIEW_REQUIRED   = "PLAN_REVIEW_REQUIRED"
    REVISION_IN_PROGRESS   = "REVISION_IN_PROGRESS"
    PLAN_CONFIRMED         = "PLAN_CONFIRMED"
    PLAN_LOCKED            = "PLAN_LOCKED"


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

class PlanStatus(str, Enum):
    NEW = "NEW"  # ← ADD THIS
    PLAN_REVIEW_REQUIRED = "PLAN_REVIEW_REQUIRED"
    REVISION_IN_PROGRESS = "REVISION_IN_PROGRESS"
    PLAN_CONFIRMED = "PLAN_CONFIRMED"
    PLAN_LOCKED = "PLAN_LOCKED"