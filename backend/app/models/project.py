"""
ConstructMind AI - SQLAlchemy Database Models
Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744

Complete data model for construction project planning, scheduling,
cost estimation, and resource management.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, date
from typing import List, Optional

from sqlalchemy import (
    Column,
    DateTime,
    Date,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Boolean,
    JSON,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# ── Helper ───────────────────────────────────────────────────────
def generate_uuid() -> str:
    """Generate a new UUID4 string for use as primary key."""
    return str(uuid.uuid4())


# ══════════════════════════════════════════════════════════════════
# ENUMS
# ══════════════════════════════════════════════════════════════════

class ProjectStatus(str, enum.Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ActivityStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    SUSPENDED = "suspended"


class ActivityType(str, enum.Enum):
    TASK = "task"
    MILESTONE = "milestone"
    SUMMARY = "summary"
    LOE = "level_of_effort"  # Level of Effort
    WBS_SUMMARY = "wbs_summary"


class RelationshipType(str, enum.Enum):
    FS = "FS"  # Finish-to-Start
    FF = "FF"  # Finish-to-Finish
    SS = "SS"  # Start-to-Start
    SF = "SF"  # Start-to-Finish


class ResourceType(str, enum.Enum):
    LABOR = "labor"
    EQUIPMENT = "equipment"
    MATERIAL = "material"
    SUBCONTRACTOR = "subcontractor"


class RiskSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskStatus(str, enum.Enum):
    IDENTIFIED = "identified"
    MITIGATED = "mitigated"
    OCCURRED = "occurred"
    CLOSED = "closed"


class CalendarType(str, enum.Enum):
    FIVE_DAY = "5_day"
    SIX_DAY = "6_day"
    SEVEN_DAY = "7_day"
    CUSTOM = "custom"


class DurationMode(str, enum.Enum):
    AGGRESSIVE = "aggressive"
    REALISTIC = "realistic"
    CONSERVATIVE = "conservative"


# ══════════════════════════════════════════════════════════════════
# PROJECT
# ══════════════════════════════════════════════════════════════════

class Project(Base):
    """
    Root entity representing a construction project.
    Contains all top-level metadata and links to WBS, activities,
    resources, BOQ items, baselines, and risks.
    """
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, unique=True)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus), default=ProjectStatus.PLANNING, nullable=False
    )

    # Dates
    planned_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    planned_finish: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_finish: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    data_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Budget
    budget: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="PKR", nullable=False)

    # Calendar
    calendar_type: Mapped[CalendarType] = mapped_column(
        Enum(CalendarType), default=CalendarType.SIX_DAY, nullable=False
    )
    hours_per_day: Mapped[float] = mapped_column(Float, default=8.0, nullable=False)

    # Location
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    client_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    contractor_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Owner / User
    owner_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # ── Relationships ────────────────────────────────────────────
    wbs_items: Mapped[List["WBS"]] = relationship(
        "WBS", back_populates="project", cascade="all, delete-orphan", lazy="selectin"
    )
    activities: Mapped[List["Activity"]] = relationship(
        "Activity", back_populates="project", cascade="all, delete-orphan", lazy="selectin"
    )
    resources: Mapped[List["Resource"]] = relationship(
        "Resource", back_populates="project", cascade="all, delete-orphan", lazy="selectin"
    )
    boq_items: Mapped[List["BOQItem"]] = relationship(
        "BOQItem", back_populates="project", cascade="all, delete-orphan", lazy="selectin"
    )
    baselines: Mapped[List["Baseline"]] = relationship(
        "Baseline", back_populates="project", cascade="all, delete-orphan", lazy="selectin"
    )
    risks: Mapped[List["Risk"]] = relationship(
        "Risk", back_populates="project", cascade="all, delete-orphan", lazy="selectin"
    )
    relationships: Mapped[List["Relationship"]] = relationship(
        "Relationship", back_populates="project", cascade="all, delete-orphan", lazy="selectin"
    )


# ══════════════════════════════════════════════════════════════════
# WBS (Work Breakdown Structure)
# ══════════════════════════════════════════════════════════════════

class WBS(Base):
    """
    Hierarchical work breakdown structure node.
    Supports multi-level nesting via parent_id self-reference.
    """
    __tablename__ = "wbs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    parent_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("wbs.id", ondelete="CASCADE"), nullable=True
    )

    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # ── Relationships ────────────────────────────────────────────
    project: Mapped["Project"] = relationship("Project", back_populates="wbs_items")
    parent: Mapped[Optional["WBS"]] = relationship(
        "WBS", remote_side="WBS.id", back_populates="children"
    )
    children: Mapped[List["WBS"]] = relationship(
        "WBS", back_populates="parent", cascade="all, delete-orphan", lazy="selectin"
    )
    activities: Mapped[List["Activity"]] = relationship(
        "Activity", back_populates="wbs", lazy="selectin"
    )

    __table_args__ = (
        UniqueConstraint("project_id", "code", name="uq_wbs_project_code"),
    )


# ══════════════════════════════════════════════════════════════════
# ACTIVITY
# ══════════════════════════════════════════════════════════════════

class Activity(Base):
    """
    Individual schedulable task or milestone within a project.
    Core entity for CPM scheduling with ES/EF/LS/LF/Float fields.
    """
    __tablename__ = "activities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    wbs_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("wbs.id", ondelete="SET NULL"), nullable=True
    )

    # Identity
    activity_id: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    activity_type: Mapped[ActivityType] = mapped_column(
        Enum(ActivityType), default=ActivityType.TASK, nullable=False
    )

    # Duration
    original_duration: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    remaining_duration: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    actual_duration: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    duration_unit: Mapped[str] = mapped_column(String(20), default="days", nullable=False)

    # Dates (Planned)
    planned_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    planned_finish: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Dates (Actual)
    actual_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_finish: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # CPM Calculated Fields
    early_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    early_finish: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    late_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    late_finish: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    total_float: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    free_float: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    is_critical: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Progress
    percent_complete: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    status: Mapped[ActivityStatus] = mapped_column(
        Enum(ActivityStatus), default=ActivityStatus.NOT_STARTED, nullable=False
    )

    # Cost
    budgeted_cost: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    actual_cost: Mapped[float] = mapped_column(Float, default=0, nullable=False)

    # Quantity (link to BOQ)
    quantity: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    productivity_rate_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Calendar
    calendar_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    # Sort / Display
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # AI metadata
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # ── Relationships ────────────────────────────────────────────
    project: Mapped["Project"] = relationship("Project", back_populates="activities")
    wbs: Mapped[Optional["WBS"]] = relationship("WBS", back_populates="activities")
    resource_assignments: Mapped[List["ResourceAssignment"]] = relationship(
        "ResourceAssignment", back_populates="activity", cascade="all, delete-orphan", lazy="selectin"
    )

    # Relationships where this activity is predecessor or successor
    predecessor_links: Mapped[List["Relationship"]] = relationship(
        "Relationship",
        foreign_keys="Relationship.successor_id",
        back_populates="successor",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    successor_links: Mapped[List["Relationship"]] = relationship(
        "Relationship",
        foreign_keys="Relationship.predecessor_id",
        back_populates="predecessor",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("project_id", "activity_id", name="uq_activity_project_actid"),
        Index("ix_activity_critical", "project_id", "is_critical"),
    )


# ══════════════════════════════════════════════════════════════════
# RELATIONSHIP (Activity Dependencies)
# ══════════════════════════════════════════════════════════════════

class Relationship(Base):
    """
    Dependency link between two activities.
    Supports FS, FF, SS, SF with lag/lead days.
    """
    __tablename__ = "relationships"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    predecessor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("activities.id", ondelete="CASCADE"), nullable=False
    )
    successor_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("activities.id", ondelete="CASCADE"), nullable=False
    )
    relationship_type: Mapped[RelationshipType] = mapped_column(
        Enum(RelationshipType), default=RelationshipType.FS, nullable=False
    )
    lag_days: Mapped[float] = mapped_column(Float, default=0, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # ── Relationships ────────────────────────────────────────────
    project: Mapped["Project"] = relationship("Project", back_populates="relationships")
    predecessor: Mapped["Activity"] = relationship(
        "Activity", foreign_keys=[predecessor_id], back_populates="successor_links"
    )
    successor: Mapped["Activity"] = relationship(
        "Activity", foreign_keys=[successor_id], back_populates="predecessor_links"
    )

    __table_args__ = (
        UniqueConstraint(
            "predecessor_id", "successor_id", "relationship_type",
            name="uq_relationship_pred_succ_type"
        ),
    )


# ══════════════════════════════════════════════════════════════════
# RESOURCE
# ══════════════════════════════════════════════════════════════════

class Resource(Base):
    """
    A labor, equipment, material, or subcontractor resource
    available to the project.
    """
    __tablename__ = "resources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )

    resource_id: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_type: Mapped[ResourceType] = mapped_column(
        Enum(ResourceType), default=ResourceType.LABOR, nullable=False
    )

    # Capacity & Availability
    max_units: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(50), default="hours", nullable=False)

    # Cost
    standard_rate: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    overtime_rate: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    cost_per_use: Mapped[float] = mapped_column(Float, default=0, nullable=False)

    # Contact / Details
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Active
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # ── Relationships ────────────────────────────────────────────
    project: Mapped["Project"] = relationship("Project", back_populates="resources")
    assignments: Mapped[List["ResourceAssignment"]] = relationship(
        "ResourceAssignment", back_populates="resource", cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        UniqueConstraint("project_id", "resource_id", name="uq_resource_project_resid"),
    )


# ══════════════════════════════════════════════════════════════════
# RESOURCE ASSIGNMENT
# ══════════════════════════════════════════════════════════════════

class ResourceAssignment(Base):
    """
    Links a resource to an activity with allocation details.
    """
    __tablename__ = "resource_assignments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    activity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("activities.id", ondelete="CASCADE"), nullable=False, index=True
    )
    resource_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("resources.id", ondelete="CASCADE"), nullable=False, index=True
    )

    units: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    planned_units: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    actual_units: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    remaining_units: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    planned_cost: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    actual_cost: Mapped[float] = mapped_column(Float, default=0, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # ── Relationships ────────────────────────────────────────────
    activity: Mapped["Activity"] = relationship("Activity", back_populates="resource_assignments")
    resource: Mapped["Resource"] = relationship("Resource", back_populates="assignments")

    __table_args__ = (
        UniqueConstraint("activity_id", "resource_id", name="uq_assignment_activity_resource"),
    )


# ══════════════════════════════════════════════════════════════════
# BOQ ITEM (Bill of Quantities)
# ══════════════════════════════════════════════════════════════════

class BOQItem(Base):
    """
    Individual line item from a Bill of Quantities.
    Can be AI-parsed from uploaded Excel/PDF files.
    """
    __tablename__ = "boq_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Item Identity
    item_no: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    csi_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    csi_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Quantities & Rates
    quantity: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), default="LS", nullable=False)
    unit_rate: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, default=0, nullable=False)

    # Source
    source_file: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    source_sheet: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_row: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # AI Analysis
    ai_parsed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ai_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ai_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # ── Relationships ────────────────────────────────────────────
    project: Mapped["Project"] = relationship("Project", back_populates="boq_items")


# ══════════════════════════════════════════════════════════════════
# BASELINE
# ══════════════════════════════════════════════════════════════════

class Baseline(Base):
    """
    Project schedule baseline snapshot.
    Stores a JSON snapshot of all activity dates/durations at baseline time.
    """
    __tablename__ = "baselines"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    baseline_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Snapshot data stored as JSON
    snapshot_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Summary metrics at baseline time
    total_activities: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_duration_days: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    project_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    project_finish: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    total_cost: Mapped[float] = mapped_column(Float, default=0, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # ── Relationships ────────────────────────────────────────────
    project: Mapped["Project"] = relationship("Project", back_populates="baselines")


# ══════════════════════════════════════════════════════════════════
# RISK
# ══════════════════════════════════════════════════════════════════

class Risk(Base):
    """
    Project risk register entry for risk management.
    """
    __tablename__ = "risks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Risk Identity
    risk_id: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Assessment
    probability: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    impact: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)
    severity: Mapped[RiskSeverity] = mapped_column(
        Enum(RiskSeverity), default=RiskSeverity.MEDIUM, nullable=False
    )
    risk_score: Mapped[float] = mapped_column(Float, default=0, nullable=False)

    # Response
    mitigation_plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contingency_plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    owner: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    status: Mapped[RiskStatus] = mapped_column(
        Enum(RiskStatus), default=RiskStatus.IDENTIFIED, nullable=False
    )

    # Impact on schedule / cost
    schedule_impact_days: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    cost_impact: Mapped[float] = mapped_column(Float, default=0, nullable=False)
    affected_activity_ids: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # AI analysis
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ai_recommendations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # ── Relationships ────────────────────────────────────────────
    project: Mapped["Project"] = relationship("Project", back_populates="risks")

    __table_args__ = (
        UniqueConstraint("project_id", "risk_id", name="uq_risk_project_riskid"),
    )
