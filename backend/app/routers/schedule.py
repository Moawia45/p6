"""
ConstructMind AI - Schedule and CPM API Router
Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744

Provides endpoints for running CPM schedule calculations, retrieving 
Gantt-chart formatted data, and managing activity relationships.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.project import Activity, Relationship, Project, WBS
from app.schemas.project import (
    CPMRequest,
    CPMResult,
    GanttData,
    GanttItem,
    RelationshipCreate,
    RelationshipResponse,
    MessageResponse
)
from app.services.ai.cpm_engine import CPMEngine

router = APIRouter()
logger = logging.getLogger("constructmind.routers.schedule")


@router.post("/cpm", response_model=CPMResult)
async def calculate_critical_path(
    project_id: str,
    request: CPMRequest,
    db: AsyncSession = Depends(get_db)
) -> CPMResult:
    """
    Run CPM forward/backward pass calculations over all project activities,
    update activity dates and floats in the database, and return results.
    """
    logger.info(f"Running CPM calculation for project '{project_id}' starting '{request.project_start}'")
    
    # 1. Fetch project
    proj_query = select(Project).where(Project.id == project_id)
    proj_result = await db.execute(proj_query)
    proj = proj_result.scalars().first()
    if not proj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found."
        )

    # 2. Fetch all activities
    act_query = select(Activity).where(Activity.project_id == project_id)
    act_result = await db.execute(act_query)
    activities = act_result.scalars().all()
    
    if not activities:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No activities exist in the project. Cannot run CPM calculations."
        )

    # 3. Fetch all relationships
    rel_query = select(Relationship).where(Relationship.project_id == project_id)
    rel_result = await db.execute(rel_query)
    relationships = rel_result.scalars().all()

    # 4. Initialize CPMEngine
    engine = CPMEngine(calendar_type=request.calendar_type)
    
    # Map from database UUID to activity node info
    for act in activities:
        engine.add_activity(
            activity_db_id=act.id,
            activity_id=act.activity_id,
            name=act.name,
            duration=act.original_duration,
            activity_type=act.activity_type.value if hasattr(act.activity_type, "value") else str(act.activity_type)
        )
        
    for rel in relationships:
        engine.add_relationship(
            predecessor_id=rel.predecessor_id,
            successor_id=rel.successor_id,
            relationship_type=rel.relationship_type.value if hasattr(rel.relationship_type, "value") else str(rel.relationship_type),
            lag_days=rel.lag_days
        )

    # 5. Execute CPM calculation
    cpm_data = engine.calculate(request.project_start)
    
    if cpm_data.get("has_circular_dependency"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Circular dependency detected in relationships! CPM calculation failed."
        )

    # 6. Update database with calculated CPM values
    for act_res in cpm_data["activities"]:
        db_act_id = act_res["activity_db_id"]
        
        # Find activity in DB list
        db_act = next((a for a in activities if a.id == db_act_id), None)
        if db_act:
            db_act.early_start = act_res["early_start"]
            db_act.early_finish = act_res["early_finish"]
            db_act.late_start = act_res["late_start"]
            db_act.late_finish = act_res["late_finish"]
            db_act.total_float = act_res["total_float"]
            db_act.free_float = act_res["free_float"]
            db_act.is_critical = act_res["is_critical"]
            
            # Align planned dates with early start/finish for Gantt display
            db_act.planned_start = act_res["early_start"]
            db_act.planned_finish = act_res["early_finish"]
            
            db.add(db_act)

    # Update project end date & status
    proj.planned_start = request.project_start
    proj.planned_finish = cpm_data["project_finish"]
    proj.data_date = request.project_start
    db.add(proj)
    
    await db.commit()

    return CPMResult(
        project_id=project_id,
        project_start=cpm_data["project_start"],
        project_finish=cpm_data["project_finish"],
        total_duration_days=cpm_data["total_duration_days"],
        critical_path=cpm_data["critical_path"],
        critical_path_duration=cpm_data["critical_path_duration"],
        activities=cpm_data["activities"],
        num_critical_activities=cpm_data["num_critical_activities"],
        num_total_activities=cpm_data["num_total_activities"],
        has_circular_dependency=False,
        warnings=cpm_data["warnings"]
    )


@router.get("/gantt", response_model=GanttData)
async def get_gantt_data(
    project_id: str,
    db: AsyncSession = Depends(get_db)
) -> GanttData:
    """Retrieve Gantt chart formatted data for all project activities and dependencies."""
    # 1. Fetch project
    proj_query = select(Project).where(Project.id == project_id)
    proj_result = await db.execute(proj_query)
    proj = proj_result.scalars().first()
    if not proj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found."
        )

    # 2. Fetch WBS
    wbs_query = select(WBS).where(WBS.project_id == project_id)
    wbs_result = await db.execute(wbs_query)
    wbs_list = wbs_result.scalars().all()
    wbs_map = {w.id: w.name for w in wbs_list}

    # 3. Fetch activities
    act_query = select(Activity).where(Activity.project_id == project_id)
    act_result = await db.execute(act_query)
    activities = act_result.scalars().all()

    # 4. Fetch relationships
    rel_query = select(Relationship).where(Relationship.project_id == project_id)
    rel_result = await db.execute(rel_query)
    relationships = rel_result.scalars().all()

    # 5. Build predecessor mapping
    # Map predecessor DB IDs to list of activity_ids (e.g. A1010)
    pred_map = {}
    for rel in relationships:
        if rel.successor_id not in pred_map:
            pred_map[rel.successor_id] = []
        # Find predecessor activity_id code
        pred_act = next((a for a in activities if a.id == rel.predecessor_id), None)
        if pred_act:
            pred_map[rel.successor_id].append(
                f"{pred_act.activity_id}{rel.relationship_type.value if hasattr(rel.relationship_type, 'value') else str(rel.relationship_type)}"
            )

    gantt_items = []
    critical_path = []
    
    for act in activities:
        if act.is_critical:
            critical_path.append(act.activity_id)
            
        gantt_items.append(
            GanttItem(
                id=act.id,
                activity_id=act.activity_id,
                name=act.name,
                start=act.planned_start or act.early_start or date.today(),
                end=act.planned_finish or act.early_finish or date.today(),
                duration=act.original_duration,
                percent_complete=act.percent_complete,
                is_critical=act.is_critical,
                is_milestone=(act.activity_type.value == "milestone" if hasattr(act.activity_type, "value") else act.activity_type == "milestone"),
                wbs_id=act.wbs_id,
                wbs_name=wbs_map.get(act.wbs_id) if act.wbs_id else None,
                predecessors=pred_map.get(act.id, []),
                total_float=act.total_float,
                status=act.status.value if hasattr(act.status, "value") else str(act.status)
            )
        )

    return GanttData(
        project_id=project_id,
        project_name=proj.name,
        items=gantt_items,
        critical_path=critical_path,
        project_start=proj.planned_start,
        project_finish=proj.planned_finish
    )


@router.post("/relationships", response_model=RelationshipResponse, status_code=status.HTTP_201_CREATED)
async def create_relationship(
    project_id: str,
    rel_in: RelationshipCreate,
    db: AsyncSession = Depends(get_db)
) -> RelationshipResponse:
    """Create a new logic dependency relationship between two activities."""
    # Check if activities exist
    pred_check = await db.execute(select(Activity).where(Activity.project_id == project_id, Activity.id == rel_in.predecessor_id))
    pred = pred_check.scalars().first()
    if not pred:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Predecessor activity '{rel_in.predecessor_id}' not found."
        )
        
    succ_check = await db.execute(select(Activity).where(Activity.project_id == project_id, Activity.id == rel_in.successor_id))
    succ = succ_check.scalars().first()
    if not succ:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Successor activity '{rel_in.successor_id}' not found."
        )

    # Check for existing relationship
    rel_check = await db.execute(
        select(Relationship).where(
            Relationship.predecessor_id == rel_in.predecessor_id,
            Relationship.successor_id == rel_in.successor_id
        )
    )
    if rel_check.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A relationship already exists between these activities."
        )

    db_rel = Relationship(
        project_id=project_id,
        predecessor_id=rel_in.predecessor_id,
        successor_id=rel_in.successor_id,
        relationship_type=rel_in.relationship_type,
        lag_days=rel_in.lag_days
    )
    db.add(db_rel)
    await db.commit()
    await db.refresh(db_rel)
    
    return RelationshipResponse.model_validate(db_rel)


@router.delete("/relationships/{relationship_id}", response_model=MessageResponse)
async def delete_relationship(
    project_id: str,
    relationship_id: str,
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Delete a logic dependency relationship."""
    query = select(Relationship).where(Relationship.project_id == project_id, Relationship.id == relationship_id)
    result = await db.execute(query)
    rel = result.scalars().first()
    
    if not rel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relationship with ID '{relationship_id}' not found in project '{project_id}'."
        )
        
    await db.delete(rel)
    await db.commit()
    
    return MessageResponse(message=f"Relationship '{relationship_id}' deleted successfully.")
