"""
ConstructMind AI - Pydantic v2 Schemas
Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744

Request/Response schemas for all API endpoints.
Uses Pydantic v2 with model_config for ORM mode.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


# ══════════════════════════════════════════════════════════════════
# COMMON
# ══════════════════════════════════════════════════════════════════

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str = "1.0.0"
    app: str = "ConstructMind AI"


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    detail: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Wrapper for paginated list responses."""
    items: List[Any]
    total: int
    page: int = 1
    page_size: int = 50


# ══════════════════════════════════════════════════════════════════
# PROJECT SCHEMAS
# ══════════════════════════════════════════════════════════════════

class ProjectCreate(BaseModel):
    """Schema for creating a new project."""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    code: Optional[str] = Field(None, max_length=50, description="Project code")
    status: str = Field("planning", description="Project status")
    planned_start: Optional[date] = Field(None, description="Planned start date")
    planned_finish: Optional[date] = Field(None, description="Planned finish date")
    budget: Optional[float] = Field(None, ge=0, description="Project budget")
    currency: str = Field("PKR", max_length=10, description="Currency code")
    calendar_type: str = Field("6_day", description="Calendar type")
    hours_per_day: float = Field(8.0, gt=0, le=24, description="Working hours per day")
    location: Optional[str] = Field(None, max_length=255, description="Project location")
    client_name: Optional[str] = Field(None, max_length=255, description="Client name")
    contractor_name: Optional[str] = Field(None, max_length=255, description="Contractor name")
    owner_id: Optional[str] = Field(None, description="Owner user ID")

    @field_validator("planned_finish")
    @classmethod
    def validate_finish_after_start(cls, v: Optional[date], info) -> Optional[date]:
        start = info.data.get("planned_start")
        if v and start and v < start:
            raise ValueError("planned_finish must be after planned_start")
        return v


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project. All fields optional."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    code: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = None
    planned_start: Optional[date] = None
    planned_finish: Optional[date] = None
    actual_start: Optional[date] = None
    actual_finish: Optional[date] = None
    data_date: Optional[date] = None
    budget: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = Field(None, max_length=10)
    calendar_type: Optional[str] = None
    hours_per_day: Optional[float] = Field(None, gt=0, le=24)
    location: Optional[str] = Field(None, max_length=255)
    client_name: Optional[str] = Field(None, max_length=255)
    contractor_name: Optional[str] = Field(None, max_length=255)


class ProjectResponse(BaseModel):
    """Full project response with computed fields."""
    model_config = {"from_attributes": True}

    id: str
    name: str
    description: Optional[str] = None
    code: Optional[str] = None
    status: str
    planned_start: Optional[date] = None
    planned_finish: Optional[date] = None
    actual_start: Optional[date] = None
    actual_finish: Optional[date] = None
    data_date: Optional[date] = None
    budget: Optional[float] = None
    currency: str = "PKR"
    calendar_type: str = "6_day"
    hours_per_day: float = 8.0
    location: Optional[str] = None
    client_name: Optional[str] = None
    contractor_name: Optional[str] = None
    owner_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    activity_count: int = 0
    boq_count: int = 0


class ProjectSummary(BaseModel):
    """Lightweight project list item."""
    model_config = {"from_attributes": True}

    id: str
    name: str
    code: Optional[str] = None
    status: str
    planned_start: Optional[date] = None
    planned_finish: Optional[date] = None
    budget: Optional[float] = None
    currency: str = "PKR"
    created_at: datetime


# ══════════════════════════════════════════════════════════════════
# WBS SCHEMAS
# ══════════════════════════════════════════════════════════════════

class WBSCreate(BaseModel):
    """Schema for creating a WBS node."""
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[str] = None
    level: int = Field(1, ge=1)
    sort_order: int = Field(0, ge=0)


class WBSUpdate(BaseModel):
    """Schema for updating a WBS node."""
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[str] = None
    level: Optional[int] = Field(None, ge=1)
    sort_order: Optional[int] = Field(None, ge=0)


class WBSResponse(BaseModel):
    """WBS node response."""
    model_config = {"from_attributes": True}

    id: str
    project_id: str
    parent_id: Optional[str] = None
    code: str
    name: str
    description: Optional[str] = None
    level: int = 1
    sort_order: int = 0
    created_at: datetime
    updated_at: datetime


# ══════════════════════════════════════════════════════════════════
# ACTIVITY SCHEMAS
# ══════════════════════════════════════════════════════════════════

class ActivityCreate(BaseModel):
    """Schema for creating an activity."""
    activity_id: str = Field(..., min_length=1, max_length=50, description="Activity ID code")
    name: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    activity_type: str = Field("task", description="task, milestone, summary, level_of_effort")
    wbs_id: Optional[str] = None

    # Duration
    original_duration: float = Field(0, ge=0)
    remaining_duration: Optional[float] = Field(None, ge=0)
    duration_unit: str = Field("days", description="days, hours, weeks")

    # Dates
    planned_start: Optional[date] = None
    planned_finish: Optional[date] = None

    # Cost
    budgeted_cost: float = Field(0, ge=0)

    # Quantity
    quantity: float = Field(0, ge=0)
    unit: Optional[str] = None
    productivity_rate_id: Optional[str] = None

    # Sort
    sort_order: int = Field(0, ge=0)

    @model_validator(mode="after")
    def set_remaining_duration(self):
        if self.remaining_duration is None:
            self.remaining_duration = self.original_duration
        return self


class ActivityUpdate(BaseModel):
    """Schema for updating an activity."""
    activity_id: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    activity_type: Optional[str] = None
    wbs_id: Optional[str] = None
    original_duration: Optional[float] = Field(None, ge=0)
    remaining_duration: Optional[float] = Field(None, ge=0)
    actual_duration: Optional[float] = Field(None, ge=0)
    duration_unit: Optional[str] = None
    planned_start: Optional[date] = None
    planned_finish: Optional[date] = None
    actual_start: Optional[date] = None
    actual_finish: Optional[date] = None
    percent_complete: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[str] = None
    budgeted_cost: Optional[float] = Field(None, ge=0)
    actual_cost: Optional[float] = Field(None, ge=0)
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = None
    productivity_rate_id: Optional[str] = None
    sort_order: Optional[int] = Field(None, ge=0)


class ActivityResponse(BaseModel):
    """Full activity response with CPM fields."""
    model_config = {"from_attributes": True}

    id: str
    project_id: str
    wbs_id: Optional[str] = None
    activity_id: str
    name: str
    description: Optional[str] = None
    activity_type: str = "task"

    # Duration
    original_duration: float = 0
    remaining_duration: float = 0
    actual_duration: float = 0
    duration_unit: str = "days"

    # Dates
    planned_start: Optional[date] = None
    planned_finish: Optional[date] = None
    actual_start: Optional[date] = None
    actual_finish: Optional[date] = None

    # CPM
    early_start: Optional[date] = None
    early_finish: Optional[date] = None
    late_start: Optional[date] = None
    late_finish: Optional[date] = None
    total_float: float = 0
    free_float: float = 0
    is_critical: bool = False

    # Progress
    percent_complete: float = 0
    status: str = "not_started"

    # Cost
    budgeted_cost: float = 0
    actual_cost: float = 0

    # Quantity
    quantity: float = 0
    unit: Optional[str] = None
    productivity_rate_id: Optional[str] = None

    # AI
    ai_generated: bool = False
    ai_confidence: Optional[float] = None

    sort_order: int = 0
    created_at: datetime
    updated_at: datetime


class ActivityBulkCreate(BaseModel):
    """Schema for bulk-creating activities (AI generation)."""
    activities: List[ActivityCreate]


# ══════════════════════════════════════════════════════════════════
# RELATIONSHIP SCHEMAS
# ══════════════════════════════════════════════════════════════════

class RelationshipCreate(BaseModel):
    """Schema for creating an activity dependency."""
    predecessor_id: str = Field(..., description="Predecessor activity DB ID")
    successor_id: str = Field(..., description="Successor activity DB ID")
    relationship_type: str = Field("FS", description="FS, FF, SS, SF")
    lag_days: float = Field(0, description="Lag (positive) or lead (negative) in days")

    @field_validator("relationship_type")
    @classmethod
    def validate_relationship_type(cls, v: str) -> str:
        valid = {"FS", "FF", "SS", "SF"}
        v = v.upper()
        if v not in valid:
            raise ValueError(f"relationship_type must be one of {valid}")
        return v


class RelationshipUpdate(BaseModel):
    """Schema for updating a relationship."""
    relationship_type: Optional[str] = None
    lag_days: Optional[float] = None


class RelationshipResponse(BaseModel):
    """Relationship response."""
    model_config = {"from_attributes": True}

    id: str
    project_id: str
    predecessor_id: str
    successor_id: str
    relationship_type: str
    lag_days: float = 0
    created_at: datetime


# ══════════════════════════════════════════════════════════════════
# RESOURCE SCHEMAS
# ══════════════════════════════════════════════════════════════════

class ResourceCreate(BaseModel):
    """Schema for creating a resource."""
    resource_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    resource_type: str = Field("labor", description="labor, equipment, material, subcontractor")
    max_units: float = Field(1.0, gt=0)
    unit_of_measure: str = Field("hours", max_length=50)
    standard_rate: float = Field(0, ge=0)
    overtime_rate: float = Field(0, ge=0)
    cost_per_use: float = Field(0, ge=0)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    is_active: bool = True


class ResourceUpdate(BaseModel):
    """Schema for updating a resource."""
    resource_id: Optional[str] = Field(None, min_length=1, max_length=50)
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    resource_type: Optional[str] = None
    max_units: Optional[float] = Field(None, gt=0)
    unit_of_measure: Optional[str] = Field(None, max_length=50)
    standard_rate: Optional[float] = Field(None, ge=0)
    overtime_rate: Optional[float] = Field(None, ge=0)
    cost_per_use: Optional[float] = Field(None, ge=0)
    email: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ResourceResponse(BaseModel):
    """Resource response."""
    model_config = {"from_attributes": True}

    id: str
    project_id: str
    resource_id: str
    name: str
    resource_type: str
    max_units: float = 1.0
    unit_of_measure: str = "hours"
    standard_rate: float = 0
    overtime_rate: float = 0
    cost_per_use: float = 0
    email: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime


# ══════════════════════════════════════════════════════════════════
# RESOURCE ASSIGNMENT SCHEMAS
# ══════════════════════════════════════════════════════════════════

class ResourceAssignmentCreate(BaseModel):
    """Schema for assigning a resource to an activity."""
    activity_id: str
    resource_id: str
    units: float = Field(1.0, gt=0)
    planned_units: float = Field(0, ge=0)
    planned_cost: float = Field(0, ge=0)


class ResourceAssignmentResponse(BaseModel):
    """Resource assignment response."""
    model_config = {"from_attributes": True}

    id: str
    activity_id: str
    resource_id: str
    units: float = 1.0
    planned_units: float = 0
    actual_units: float = 0
    remaining_units: float = 0
    planned_cost: float = 0
    actual_cost: float = 0
    created_at: datetime


# ══════════════════════════════════════════════════════════════════
# BOQ SCHEMAS
# ══════════════════════════════════════════════════════════════════

class BOQItemCreate(BaseModel):
    """Schema for creating a BOQ item."""
    item_no: str = Field(..., min_length=1, max_length=50)
    description: str = Field(..., min_length=1)
    csi_code: Optional[str] = Field(None, max_length=20)
    csi_category: Optional[str] = Field(None, max_length=100)
    quantity: float = Field(0, ge=0)
    unit: str = Field("LS", max_length=50)
    unit_rate: float = Field(0, ge=0)
    total_amount: Optional[float] = Field(None, ge=0)

    @model_validator(mode="after")
    def compute_total(self):
        if self.total_amount is None or self.total_amount == 0:
            self.total_amount = self.quantity * self.unit_rate
        return self


class BOQItemUpdate(BaseModel):
    """Schema for updating a BOQ item."""
    item_no: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = None
    csi_code: Optional[str] = Field(None, max_length=20)
    csi_category: Optional[str] = Field(None, max_length=100)
    quantity: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = Field(None, max_length=50)
    unit_rate: Optional[float] = Field(None, ge=0)
    total_amount: Optional[float] = Field(None, ge=0)


class BOQItemResponse(BaseModel):
    """BOQ item response."""
    model_config = {"from_attributes": True}

    id: str
    project_id: str
    item_no: str
    description: str
    csi_code: Optional[str] = None
    csi_category: Optional[str] = None
    quantity: float = 0
    unit: str = "LS"
    unit_rate: float = 0
    total_amount: float = 0
    source_file: Optional[str] = None
    source_sheet: Optional[str] = None
    source_row: Optional[int] = None
    ai_parsed: bool = False
    ai_category: Optional[str] = None
    ai_confidence: Optional[float] = None
    ai_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class BOQUploadResponse(BaseModel):
    """Response after BOQ file upload and parsing."""
    message: str
    items_parsed: int
    items_created: int
    file_name: str
    warnings: List[str] = []
    items: List[BOQItemResponse] = []


# ══════════════════════════════════════════════════════════════════
# BASELINE SCHEMAS
# ══════════════════════════════════════════════════════════════════

class BaselineCreate(BaseModel):
    """Schema for creating a baseline snapshot."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    is_primary: bool = False


class BaselineResponse(BaseModel):
    """Baseline response."""
    model_config = {"from_attributes": True}

    id: str
    project_id: str
    name: str
    description: Optional[str] = None
    baseline_number: int = 1
    is_primary: bool = False
    total_activities: int = 0
    total_duration_days: float = 0
    project_start: Optional[date] = None
    project_finish: Optional[date] = None
    total_cost: float = 0
    created_at: datetime


# ══════════════════════════════════════════════════════════════════
# RISK SCHEMAS
# ══════════════════════════════════════════════════════════════════

class RiskCreate(BaseModel):
    """Schema for creating a risk entry."""
    risk_id: str = Field(..., min_length=1, max_length=50)
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=100)
    probability: float = Field(0.5, ge=0, le=1)
    impact: float = Field(0.5, ge=0, le=1)
    severity: str = Field("medium", description="low, medium, high, critical")
    mitigation_plan: Optional[str] = None
    contingency_plan: Optional[str] = None
    owner: Optional[str] = Field(None, max_length=255)
    schedule_impact_days: float = Field(0, ge=0)
    cost_impact: float = Field(0, ge=0)
    affected_activity_ids: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def compute_risk_score(self):
        self._risk_score = self.probability * self.impact * 100
        return self


class RiskUpdate(BaseModel):
    """Schema for updating a risk entry."""
    risk_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    probability: Optional[float] = Field(None, ge=0, le=1)
    impact: Optional[float] = Field(None, ge=0, le=1)
    severity: Optional[str] = None
    status: Optional[str] = None
    mitigation_plan: Optional[str] = None
    contingency_plan: Optional[str] = None
    owner: Optional[str] = None
    schedule_impact_days: Optional[float] = Field(None, ge=0)
    cost_impact: Optional[float] = Field(None, ge=0)
    affected_activity_ids: Optional[Dict[str, Any]] = None


class RiskResponse(BaseModel):
    """Risk response."""
    model_config = {"from_attributes": True}

    id: str
    project_id: str
    risk_id: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    probability: float = 0.5
    impact: float = 0.5
    severity: str = "medium"
    risk_score: float = 0
    mitigation_plan: Optional[str] = None
    contingency_plan: Optional[str] = None
    owner: Optional[str] = None
    status: str = "identified"
    schedule_impact_days: float = 0
    cost_impact: float = 0
    affected_activity_ids: Optional[Dict[str, Any]] = None
    ai_generated: bool = False
    ai_recommendations: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ══════════════════════════════════════════════════════════════════
# SCHEDULE / CPM SCHEMAS
# ══════════════════════════════════════════════════════════════════

class CPMRequest(BaseModel):
    """Request body for CPM calculation."""
    project_start: date = Field(..., description="Project start date for scheduling")
    calendar_type: str = Field("6_day", description="5_day, 6_day, 7_day, custom")
    hours_per_day: float = Field(8.0, gt=0, le=24)


class CPMActivityResult(BaseModel):
    """CPM result for a single activity."""
    activity_id: str
    activity_db_id: str
    name: str
    duration: float
    early_start: Optional[date] = None
    early_finish: Optional[date] = None
    late_start: Optional[date] = None
    late_finish: Optional[date] = None
    total_float: float = 0
    free_float: float = 0
    is_critical: bool = False


class CPMResult(BaseModel):
    """Full CPM calculation result."""
    project_id: str
    project_start: date
    project_finish: Optional[date] = None
    total_duration_days: float = 0
    critical_path: List[str] = []
    critical_path_duration: float = 0
    activities: List[CPMActivityResult] = []
    num_critical_activities: int = 0
    num_total_activities: int = 0
    has_circular_dependency: bool = False
    warnings: List[str] = []


class GanttItem(BaseModel):
    """Single item for Gantt chart rendering."""
    id: str
    activity_id: str
    name: str
    start: Optional[date] = None
    end: Optional[date] = None
    duration: float = 0
    percent_complete: float = 0
    is_critical: bool = False
    is_milestone: bool = False
    wbs_id: Optional[str] = None
    wbs_name: Optional[str] = None
    predecessors: List[str] = []
    total_float: float = 0
    status: str = "not_started"


class GanttData(BaseModel):
    """Complete Gantt chart data payload."""
    project_id: str
    project_name: str
    items: List[GanttItem] = []
    critical_path: List[str] = []
    project_start: Optional[date] = None
    project_finish: Optional[date] = None


# ══════════════════════════════════════════════════════════════════
# AI COPILOT SCHEMAS
# ══════════════════════════════════════════════════════════════════

class CopilotMessage(BaseModel):
    """A single message in the copilot chat."""
    role: str = Field(..., description="user, assistant, or system")
    content: str = Field(..., min_length=1)


class CopilotRequest(BaseModel):
    """Request to the AI copilot."""
    message: str = Field(..., min_length=1, max_length=10000, description="User message")
    conversation_history: List[CopilotMessage] = Field(
        default_factory=list, description="Previous messages for context"
    )
    project_id: Optional[str] = Field(None, description="Active project ID for context")
    stream: bool = Field(True, description="Whether to stream the response via SSE")


class CopilotResponse(BaseModel):
    """Non-streaming copilot response."""
    message: str
    model: str
    usage: Optional[Dict[str, int]] = None


# ══════════════════════════════════════════════════════════════════
# AI GENERATION SCHEMAS
# ══════════════════════════════════════════════════════════════════

class AIActivityGenerationRequest(BaseModel):
    """Request AI to generate activities from project description or BOQ."""
    project_description: Optional[str] = Field(None, description="Free-text project description")
    boq_item_ids: List[str] = Field(default_factory=list, description="BOQ item IDs to generate from")
    project_type: str = Field("building", description="building, road, bridge, industrial, etc.")
    detail_level: str = Field("detailed", description="summary, detailed, comprehensive")


class AIActivityGenerationResponse(BaseModel):
    """Response from AI activity generation."""
    activities: List[ActivityCreate]
    relationships: List[RelationshipCreate] = []
    wbs_suggestions: List[WBSCreate] = []
    ai_notes: str = ""
    model_used: str = ""


class AIDurationEstimationRequest(BaseModel):
    """Request AI to estimate durations for activities."""
    activity_ids: List[str] = Field(default_factory=list, description="Activity DB IDs")
    mode: str = Field("realistic", description="aggressive, realistic, conservative")
    weather_factor: float = Field(1.0, ge=0.5, le=1.5, description="Weather adjustment factor")
    overtime_hours: float = Field(0, ge=0, le=8, description="Daily overtime hours")
    site_constraint_factor: float = Field(1.0, ge=0.5, le=1.5, description="Site constraint factor")


class AIDurationEstimationResponse(BaseModel):
    """Response from AI duration estimation."""
    estimations: List[Dict[str, Any]]
    mode: str
    notes: str = ""


class AIReportRequest(BaseModel):
    """Request AI to generate a project report."""
    report_type: str = Field(
        "progress",
        description="progress, delay_analysis, cost, risk, executive_summary"
    )
    include_charts: bool = Field(False, description="Whether to include chart data")
    date_range_start: Optional[date] = None
    date_range_end: Optional[date] = None


class AIReportResponse(BaseModel):
    """Response from AI report generation."""
    report_type: str
    title: str
    content: str
    generated_at: datetime
    model_used: str
    sections: List[Dict[str, Any]] = []
    recommendations: List[str] = []
