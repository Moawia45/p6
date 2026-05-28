"""
ConstructMind AI - Activities API Router
Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744

Provides endpoints for Activity CRUD operations, bulk creation,
AI activity generation, and AI duration estimation.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.project import Activity, Project, WBS, Relationship, BOQItem
from app.schemas.project import (
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
    ActivityBulkCreate,
    AIActivityGenerationRequest,
    AIActivityGenerationResponse,
    AIDurationEstimationRequest,
    AIDurationEstimationResponse,
    MessageResponse,
    WBSCreate,
    RelationshipCreate,
)
from app.services.ai.gemini_service import gemini_service
from app.services.ai.duration_engine import duration_engine

router = APIRouter()
logger = logging.getLogger("constructmind.routers.activities")


@router.get("/", response_model=List[ActivityResponse])
async def list_activities(
    project_id: str,
    db: AsyncSession = Depends(get_db)
) -> List[ActivityResponse]:
    """Retrieve all activities for a project, sorted by early start / planned start."""
    query = select(Activity).where(Activity.project_id == project_id)
    query = query.order_by(Activity.planned_start.asc(), Activity.sort_order.asc())
    result = await db.execute(query)
    activities = result.scalars().all()
    return [ActivityResponse.model_validate(act) for act in activities]


@router.post("/", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    project_id: str,
    activity_in: ActivityCreate,
    db: AsyncSession = Depends(get_db)
) -> ActivityResponse:
    """Create a single new activity in a project."""
    logger.info(f"Creating activity '{activity_in.activity_id}' in project '{project_id}'")
    
    # Check if project exists
    proj_check = await db.execute(select(Project).where(Project.id == project_id))
    if not proj_check.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found."
        )
        
    # Check if activity_id is already taken in this project
    act_check = await db.execute(
        select(Activity).where(
            Activity.project_id == project_id,
            Activity.activity_id == activity_in.activity_id
        )
    )
    if act_check.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Activity ID '{activity_in.activity_id}' is already in use in this project."
        )

    # Validate WBS if provided
    if activity_in.wbs_id:
        wbs_check = await db.execute(select(WBS).where(WBS.id == activity_in.wbs_id))
        if not wbs_check.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"WBS Node with ID '{activity_in.wbs_id}' not found."
            )

    db_activity = Activity(
        project_id=project_id,
        wbs_id=activity_in.wbs_id,
        activity_id=activity_in.activity_id,
        name=activity_in.name,
        description=activity_in.description,
        activity_type=activity_in.activity_type,
        original_duration=activity_in.original_duration,
        remaining_duration=activity_in.remaining_duration if activity_in.remaining_duration is not None else activity_in.original_duration,
        duration_unit=activity_in.duration_unit,
        planned_start=activity_in.planned_start,
        planned_finish=activity_in.planned_finish,
        budgeted_cost=activity_in.budgeted_cost,
        quantity=activity_in.quantity,
        unit=activity_in.unit,
        productivity_rate_id=activity_in.productivity_rate_id,
        sort_order=activity_in.sort_order,
    )
    
    db.add(db_activity)
    await db.commit()
    await db.refresh(db_activity)
    
    return ActivityResponse.model_validate(db_activity)


@router.post("/bulk", response_model=List[ActivityResponse], status_code=status.HTTP_201_CREATED)
async def bulk_create_activities(
    project_id: str,
    bulk_in: ActivityBulkCreate,
    db: AsyncSession = Depends(get_db)
) -> List[ActivityResponse]:
    """Bulk create activities for a project."""
    logger.info(f"Bulk creating {len(bulk_in.activities)} activities in project '{project_id}'")
    
    proj_check = await db.execute(select(Project).where(Project.id == project_id))
    if not proj_check.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found."
        )

    db_activities = []
    for act_in in bulk_in.activities:
        db_act = Activity(
            project_id=project_id,
            wbs_id=act_in.wbs_id,
            activity_id=act_in.activity_id,
            name=act_in.name,
            description=act_in.description,
            activity_type=act_in.activity_type,
            original_duration=act_in.original_duration,
            remaining_duration=act_in.remaining_duration if act_in.remaining_duration is not None else act_in.original_duration,
            duration_unit=act_in.duration_unit,
            planned_start=act_in.planned_start,
            planned_finish=act_in.planned_finish,
            budgeted_cost=act_in.budgeted_cost,
            quantity=act_in.quantity,
            unit=act_in.unit,
            productivity_rate_id=act_in.productivity_rate_id,
            sort_order=act_in.sort_order,
        )
        db.add(db_act)
        db_activities.append(db_act)
        
    await db.commit()
    for db_act in db_activities:
        await db.refresh(db_act)
        
    return [ActivityResponse.model_validate(act) for act in db_activities]


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    project_id: str,
    activity_id: str,
    db: AsyncSession = Depends(get_db)
) -> ActivityResponse:
    """Retrieve a single activity by its DB ID."""
    query = select(Activity).where(Activity.project_id == project_id, Activity.id == activity_id)
    result = await db.execute(query)
    activity = result.scalars().first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with ID '{activity_id}' not found in project '{project_id}'."
        )
    return ActivityResponse.model_validate(activity)


@router.put("/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    project_id: str,
    activity_id: str,
    activity_in: ActivityUpdate,
    db: AsyncSession = Depends(get_db)
) -> ActivityResponse:
    """Update details of an activity."""
    logger.info(f"Updating activity '{activity_id}' in project '{project_id}'")
    
    query = select(Activity).where(Activity.project_id == project_id, Activity.id == activity_id)
    result = await db.execute(query)
    activity = result.scalars().first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with ID '{activity_id}' not found in project '{project_id}'."
        )

    # Validate WBS if changing
    if activity_in.wbs_id and activity_in.wbs_id != activity.wbs_id:
        wbs_check = await db.execute(select(WBS).where(WBS.id == activity_in.wbs_id))
        if not wbs_check.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"WBS Node with ID '{activity_in.wbs_id}' not found."
            )

    update_data = activity_in.model_dump(exclude_unset=True)
    
    # Special handle for duration remaining
    if "original_duration" in update_data and "remaining_duration" not in update_data:
        # If remaining duration was not explicitly updated, align it with the new original duration if not started
        if activity.status == "not_started":
            activity.remaining_duration = update_data["original_duration"]
            
    for field, value in update_data.items():
        setattr(activity, field, value)
        
    await db.commit()
    await db.refresh(activity)
    
    return ActivityResponse.model_validate(activity)


@router.delete("/{activity_id}", response_model=MessageResponse)
async def delete_activity(
    project_id: str,
    activity_id: str,
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Delete an activity from a project."""
    logger.warning(f"Deleting activity '{activity_id}' from project '{project_id}'")
    
    query = select(Activity).where(Activity.project_id == project_id, Activity.id == activity_id)
    result = await db.execute(query)
    activity = result.scalars().first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with ID '{activity_id}' not found in project '{project_id}'."
        )
        
    await db.delete(activity)
    await db.commit()
    
    return MessageResponse(message=f"Activity '{activity_id}' deleted successfully.")


@router.post("/generate", response_model=AIActivityGenerationResponse)
async def generate_activities_ai(
    project_id: str,
    request: AIActivityGenerationRequest,
    db: AsyncSession = Depends(get_db)
) -> AIActivityGenerationResponse:
    """
    Generate WBS, activities, and relationship suggestions using Gemini AI
    based on the project description or selected BOQ items.
    """
    logger.info(f"Generating AI plan for project '{project_id}' with type '{request.project_type}'")
    
    # Check project exists
    proj_check = await db.execute(select(Project).where(Project.id == project_id))
    proj = proj_check.scalars().first()
    if not proj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found."
        )

    # 1. Gather BOQ items if requested
    boq_items = []
    if request.boq_item_ids:
        boq_query = select(BOQItem).where(BOQItem.project_id == project_id, BOQItem.id.in_(request.boq_item_ids))
        boq_result = await db.execute(boq_query)
        boq_items = [
            {
                "item_no": b.item_no,
                "description": b.description,
                "quantity": b.quantity,
                "unit": b.unit,
                "unit_rate": b.unit_rate,
                "total_amount": b.total_amount
            }
            for b in boq_result.scalars().all()
        ]

    desc = request.project_description or proj.description or f"A standard {request.project_type} construction project."

    # 2. Check if AI is available
    if not gemini_service.is_available:
        logger.warning("Gemini API not configured, returning realistic mock schedule structure.")
        return get_mock_activity_generation(project_id, request.project_type, request.detail_level)

    try:
        raw_res = await gemini_service.generate_activities(
            project_description=desc,
            project_type=request.project_type,
            detail_level=request.detail_level,
            boq_items=boq_items if boq_items else None
        )
        
        # Parse result into schema
        # We need to construct WBSCreate, ActivityCreate, and RelationshipCreate lists
        wbs_suggestions = [
            WBSCreate(
                code=w.get("code", "1.0"),
                name=w.get("name", "Section"),
                level=w.get("level", 1),
                parent_id=None, # To be linked by code hierarchically
                description=w.get("description", "")
            )
            for w in raw_res.get("wbs", [])
        ]
        
        activities_suggestions = [
            ActivityCreate(
                activity_id=a.get("activity_id", f"A{i*10+1000}"),
                name=a.get("name", f"Activity {i}"),
                description=a.get("description", ""),
                activity_type=a.get("activity_type", "task"),
                original_duration=a.get("original_duration", 5.0),
                remaining_duration=a.get("original_duration", 5.0),
                duration_unit=a.get("duration_unit", "days"),
                quantity=a.get("quantity", 0.0),
                unit=a.get("unit", "LS"),
                sort_order=i * 10
            )
            for i, a in enumerate(raw_res.get("activities", []))
        ]
        
        relationship_suggestions = [
            RelationshipCreate(
                predecessor_id=r.get("predecessor_activity_id", ""),
                successor_id=r.get("successor_activity_id", ""),
                relationship_type=r.get("relationship_type", "FS"),
                lag_days=r.get("lag_days", 0.0)
            )
            for r in raw_res.get("relationships", [])
        ]
        
        return AIActivityGenerationResponse(
            activities=activities_suggestions,
            relationships=relationship_suggestions,
            wbs_suggestions=wbs_suggestions,
            ai_notes=raw_res.get("ai_notes", "Activities generated successfully."),
            model_used=settings.GEMINI_MODEL
        )
        
    except Exception as e:
        logger.error(f"Failed to generate activities via Gemini: {e}", exc_info=True)
        # Fallback to mock data on error so the application functions
        return get_mock_activity_generation(project_id, request.project_type, request.detail_level)


@router.post("/estimate-durations", response_model=AIDurationEstimationResponse)
async def estimate_durations_ai(
    project_id: str,
    request: AIDurationEstimationRequest,
    db: AsyncSession = Depends(get_db)
) -> AIDurationEstimationResponse:
    """
    Estimate or refine activity durations using AI and the local productivity database.
    """
    logger.info(f"Estimating durations for {len(request.activity_ids)} activities in project '{project_id}'")
    
    if not request.activity_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must provide a list of activity IDs."
        )

    # Retrieve activities from DB
    query = select(Activity).where(Activity.project_id == project_id, Activity.id.in_(request.activity_ids))
    result = await db.execute(query)
    activities = result.scalars().all()
    
    if not activities:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching activities found."
        )

    results = []
    
    # Perform calculations
    for act in activities:
        # Check if we have a quantity and activity name to calculate
        calc = duration_engine.calculate_duration_auto(
            activity_name=act.name,
            quantity=act.quantity if act.quantity > 0 else 100.0, # Default quantity if none set
            unit=act.unit or "m²",
            mode=request.mode,
            weather_factor=request.weather_factor,
            overtime_hours=request.overtime_hours,
            site_constraint_factor=request.site_constraint_factor,
        )
        
        results.append({
            "activity_db_id": act.id,
            "activity_id": act.activity_id,
            "name": act.name,
            "estimated_duration_days": calc["duration_days"],
            "productivity_rate": calc.get("rate_description", "Standard planning estimation"),
            "crew_size": str(calc.get("crew_composition", {"labor": 2, "mason": 1})),
            "assumptions": calc.get("notes", "Calculated using local productivity rates database."),
            "confidence": calc.get("match_confidence", 0.8),
            "rate_id": calc.get("rate_id"),
        })

    return AIDurationEstimationResponse(
        estimations=results,
        mode=request.mode,
        notes=f"Successfully estimated durations for {len(results)} activities using the local engineering database."
    )


# ══════════════════════════════════════════════════════════════════
# MOCK PLAN GENERATION (Fallback when AI Keys are missing)
# ══════════════════════════════════════════════════════════════════

def get_mock_activity_generation(project_id: str, project_type: str, detail_level: str) -> AIActivityGenerationResponse:
    """Return a realistic set of activities and WBS based on project type."""
    
    wbs_list = []
    activities = []
    relationships = []
    
    # Common WBS
    wbs_list.append(WBSCreate(code="1.0", name="Engineering & Procurement", level=1))
    wbs_list.append(WBSCreate(code="2.0", name="Substructure Works", level=1))
    wbs_list.append(WBSCreate(code="3.0", name="Superstructure Works", level=1))
    wbs_list.append(WBSCreate(code="4.0", name="Finishing & MEP", level=1))
    wbs_list.append(WBSCreate(code="5.0", name="Testing & Commissioning", level=1))
    
    if project_type.lower() in ["building", "residential", "high-rise"]:
        activities = [
            # WBS 1.0
            ActivityCreate(activity_id="A1010", name="Project Mobilization", activity_type="milestone", original_duration=0, wbs_id=None, quantity=0, unit="LS", sort_order=10),
            ActivityCreate(activity_id="A1020", name="Submit Structural Drawings for Approval", activity_type="task", original_duration=10, wbs_id=None, quantity=1, unit="LS", sort_order=20),
            ActivityCreate(activity_id="A1030", name="Procure Construction Materials (Cement, Rebar)", activity_type="task", original_duration=15, wbs_id=None, quantity=1, unit="LS", sort_order=30),
            # WBS 2.0
            ActivityCreate(activity_id="A2010", name="Site Excavation and Earthwork", activity_type="task", original_duration=8, wbs_id=None, quantity=800, unit="m³", sort_order=40),
            ActivityCreate(activity_id="A2020", name="Pour Lean Concrete", activity_type="task", original_duration=4, wbs_id=None, quantity=120, unit="m³", sort_order=50),
            ActivityCreate(activity_id="A2030", name="Foundation Rebar Fixing and Formwork", activity_type="task", original_duration=10, wbs_id=None, quantity=15, unit="ton", sort_order=60),
            ActivityCreate(activity_id="A2040", name="Pour Foundation Concrete", activity_type="task", original_duration=5, wbs_id=None, quantity=250, unit="m³", sort_order=70),
            ActivityCreate(activity_id="A2050", name="Backfilling and Compaction", activity_type="task", original_duration=6, wbs_id=None, quantity=400, unit="m³", sort_order=80),
            # WBS 3.0
            ActivityCreate(activity_id="A3010", name="GF Columns Rebar and Formwork", activity_type="task", original_duration=8, wbs_id=None, quantity=45, unit="m²", sort_order=90),
            ActivityCreate(activity_id="A3020", name="GFRC Concrete Pouring for GF Columns", activity_type="task", original_duration=3, wbs_id=None, quantity=30, unit="m³", sort_order=100),
            ActivityCreate(activity_id="A3030", name="GF Slab Shuttering and Rebar Binding", activity_type="task", original_duration=12, wbs_id=None, quantity=350, unit="m²", sort_order=110),
            ActivityCreate(activity_id="A3040", name="GF Slab Concrete Pouring", activity_type="task", original_duration=2, wbs_id=None, quantity=90, unit="m³", sort_order=120),
            ActivityCreate(activity_id="A3050", name="Concrete Curing Period (GF Slab)", activity_type="task", original_duration=7, wbs_id=None, quantity=7, unit="days", sort_order=130),
            # WBS 4.0
            ActivityCreate(activity_id="A4010", name="Masonry Work (GF Brickwork)", activity_type="task", original_duration=12, wbs_id=None, quantity=120, unit="m³", sort_order=140),
            ActivityCreate(activity_id="A4020", name="MEP Conduit Laying & Piping Rough-in", activity_type="task", original_duration=10, wbs_id=None, quantity=200, unit="m", sort_order=150),
            ActivityCreate(activity_id="A4030", name="GF Internal Plastering", activity_type="task", original_duration=14, wbs_id=None, quantity=1200, unit="m²", sort_order=160),
            ActivityCreate(activity_id="A4040", name="Floor Tiling Work", activity_type="task", original_duration=10, wbs_id=None, quantity=300, unit="m²", sort_order=170),
            ActivityCreate(activity_id="A4050", name="GF Painting - Primer and Putty", activity_type="task", original_duration=8, wbs_id=None, quantity=1200, unit="m²", sort_order=180),
            # WBS 5.0
            ActivityCreate(activity_id="A5010", name="Installation of Fixtures & Switches", activity_type="task", original_duration=6, wbs_id=None, quantity=50, unit="nos", sort_order=190),
            ActivityCreate(activity_id="A5020", name="Final Handover", activity_type="milestone", original_duration=0, wbs_id=None, quantity=0, unit="LS", sort_order=200),
        ]
        
        relationships = [
            RelationshipCreate(predecessor_id="A1010", successor_id="A1020", relationship_type="FS", lag_days=0),
            RelationshipCreate(predecessor_id="A1020", successor_id="A1030", relationship_type="FS", lag_days=2),
            RelationshipCreate(predecessor_id="A1010", successor_id="A2010", relationship_type="FS", lag_days=0),
            RelationshipCreate(predecessor_id="A2010", successor_id="A2020", relationship_type="FS", lag_days=0),
            RelationshipCreate(predecessor_id="A2020", successor_id="A2030", relationship_type="FS", lag_days=0),
            RelationshipCreate(predecessor_id="A1030", successor_id="A2040", relationship_type="FF", lag_days=0), # Material must arrive
            RelationshipCreate(predecessor_id="A2030", successor_id="A2040", relationship_type="FS", lag_days=0),
            RelationshipCreate(predecessor_id="A2040", successor_id="A2050", relationship_type="FS", lag_days=3), # Wait 3 days to dry
            RelationshipCreate(predecessor_id="A2040", successor_id="A3010", relationship_type="FS", lag_days=3),
            RelationshipCreate(predecessor_id="A3010", successor_id="A3020", relationship_type="FS", lag_days=0),
            RelationshipCreate(predecessor_id="A3020", successor_id="A3030", relationship_type="FS", lag_days=2), # Allow column to set
            RelationshipCreate(predecessor_id="A3030", successor_id="A3040", relationship_type="FS", lag_days=0),
            RelationshipCreate(predecessor_id="A3040", successor_id="A3050", relationship_type="FS", lag_days=0),
            RelationshipCreate(predecessor_id="A3050", successor_id="A4010", relationship_type="FS", lag_days=0),
            RelationshipCreate(predecessor_id="A4010", successor_id="A4020", relationship_type="SS", lag_days=3), # Parallel MEP
            RelationshipCreate(predecessor_id="A4020", successor_id="A4030", relationship_type="FS", lag_days=0),
            RelationshipCreate(predecessor_id="A4030", successor_id="A4040", relationship_type="FS", lag_days=5), # Let plaster cure
            RelationshipCreate(predecessor_id="A4040", successor_id="A4050", relationship_type="FS", lag_days=2),
            RelationshipCreate(predecessor_id="A4050", successor_id="A5010", relationship_type="FS", lag_days=0),
            RelationshipCreate(predecessor_id="A5010", successor_id="A5020", relationship_type="FS", lag_days=0),
        ]
    else:
        # Default mock for roads/infrastructure
        activities = [
            ActivityCreate(activity_id="A1010", name="Mobilization & Site Survey", activity_type="task", original_duration=5, wbs_id=None, quantity=1, unit="LS", sort_order=10),
            ActivityCreate(activity_id="A1020", name="Clearing and Grubbing", activity_type="task", original_duration=10, wbs_id=None, quantity=2, unit="km", sort_order=20),
            ActivityCreate(activity_id="A1030", name="Subgrade Excavation", activity_type="task", original_duration=12, wbs_id=None, quantity=4500, unit="m³", sort_order=30),
            ActivityCreate(activity_id="A1040", name="Subgrade Preparation & Compaction", activity_type="task", original_duration=8, wbs_id=None, quantity=10000, unit="m²", sort_order=40),
            ActivityCreate(activity_id="A1050", name="Sub-base Course Laying", activity_type="task", original_duration=10, wbs_id=None, quantity=2500, unit="m³", sort_order=50),
            ActivityCreate(activity_id="A1060", name="Base Course Laying & Compaction", activity_type="task", original_duration=12, wbs_id=None, quantity=2000, unit="m³", sort_order=60),
            ActivityCreate(activity_id="A1070", name="Prime Coat Spraying", activity_type="task", original_duration=3, wbs_id=None, quantity=10000, unit="m²", sort_order=70),
            ActivityCreate(activity_id="A1080", name="Asphalt Concrete Wearing Course", activity_type="task", original_duration=6, wbs_id=None, quantity=800, unit="ton", sort_order=80),
            ActivityCreate(activity_id="A1090", name="Road Marking & Signage", activity_type="task", original_duration=4, wbs_id=None, quantity=1, unit="LS", sort_order=90),
            ActivityCreate(activity_id="A1100", name="Project Completion", activity_type="milestone", original_duration=0, wbs_id=None, quantity=0, unit="LS", sort_order=100),
        ]
        relationships = [
            RelationshipCreate(predecessor_id="A1010", successor_id="A1020", relationship_type="FS", lag_days=0),
            RelationshipCreate(predecessor_id="A1020", successor_id="A1030", relationship_type="FS", lag_days=0),
            RelationshipCreate(predecessor_id="A1030", successor_id="A1040", relationship_type="FS", lag_days=0),
            RelationshipCreate(predecessor_id="A1040", successor_id="A1050", relationship_type="FS", lag_days=0),
            RelationshipCreate(predecessor_id="A1050", successor_id="A1060", relationship_type="FS", lag_days=0),
            RelationshipCreate(predecessor_id="A1060", successor_id="A1070", relationship_type="FS", lag_days=1), # Curing base
            RelationshipCreate(predecessor_id="A1070", successor_id="A1080", relationship_type="FS", lag_days=1), # Tack/prime break
            RelationshipCreate(predecessor_id="A1080", successor_id="A1090", relationship_type="FS", lag_days=2), # Cool down
            RelationshipCreate(predecessor_id="A1090", successor_id="A1100", relationship_type="FS", lag_days=0),
        ]

    # Handle detail levels
    if detail_level.lower() == "summary":
        # Keep only milestone + high-level tasks
        activities = [a for a in activities if a.activity_type == "milestone" or "GF" not in a.name]
        
    return AIActivityGenerationResponse(
        activities=activities,
        relationships=relationships,
        wbs_suggestions=wbs_list,
        ai_notes="Generated realistic construction sequence (Mock Fallback). Please check your Gemini API keys for actual AI generation.",
        model_used="MockEngine-1.0"
    )
