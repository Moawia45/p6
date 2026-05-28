"""
ConstructMind AI - Projects API Router
Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744

Provides endpoints for Project CRUD operations.
"""

from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.project import Project, Activity, BOQItem
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectSummary, MessageResponse

router = APIRouter()
logger = logging.getLogger("constructmind.routers.projects")


@router.get("/", response_model=List[ProjectSummary])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    owner_id: str | None = None
) -> List[ProjectSummary]:
    """Retrieve a list of all projects, optionally filtered by owner_id."""
    query = select(Project)
    if owner_id:
        query = query.where(Project.owner_id == owner_id)
    
    query = query.order_by(Project.created_at.desc())
    result = await db.execute(query)
    projects_list = result.scalars().all()
    
    return [ProjectSummary.model_validate(p) for p in projects_list]


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """Create a new construction project."""
    logger.info(f"Creating project: {project_in.name}")
    
    # Check if code is already used
    if project_in.code:
        code_check = await db.execute(select(Project).where(Project.code == project_in.code))
        if code_check.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project code '{project_in.code}' is already in use."
            )
            
    db_project = Project(
        name=project_in.name,
        description=project_in.description,
        code=project_in.code,
        status=project_in.status,
        planned_start=project_in.planned_start,
        planned_finish=project_in.planned_finish,
        budget=project_in.budget,
        currency=project_in.currency,
        calendar_type=project_in.calendar_type,
        hours_per_day=project_in.hours_per_day,
        location=project_in.location,
        client_name=project_in.client_name,
        contractor_name=project_in.contractor_name,
        owner_id=project_in.owner_id,
    )
    
    db.add(db_project)
    await db.commit()
    await db.refresh(db_project)
    
    # Empty project starts with 0 activities/boqs
    response_data = ProjectResponse.model_validate(db_project)
    response_data.activity_count = 0
    response_data.boq_count = 0
    
    return response_data


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """Get a detailed project by ID, including activity and BOQ counts."""
    # Query project
    query = select(Project).where(Project.id == project_id)
    result = await db.execute(query)
    db_project = result.scalars().first()
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found."
        )
        
    # Count activities
    act_query = select(func.count(Activity.id)).where(Activity.project_id == project_id)
    act_result = await db.execute(act_query)
    activity_count = act_result.scalar_one()
    
    # Count BOQ items
    boq_query = select(func.count(BOQItem.id)).where(BOQItem.project_id == project_id)
    boq_result = await db.execute(boq_query)
    boq_count = boq_result.scalar_one()
    
    response_data = ProjectResponse.model_validate(db_project)
    response_data.activity_count = activity_count
    response_data.boq_count = boq_count
    
    return response_data


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db)
) -> ProjectResponse:
    """Update project details."""
    logger.info(f"Updating project: {project_id}")
    
    query = select(Project).where(Project.id == project_id)
    result = await db.execute(query)
    db_project = result.scalars().first()
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found."
        )
        
    # Check project code uniqueness if updating
    if project_in.code and project_in.code != db_project.code:
        code_check = await db.execute(
            select(Project).where(Project.code == project_in.code, Project.id != project_id)
        )
        if code_check.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project code '{project_in.code}' is already in use."
            )

    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
        
    await db.commit()
    await db.refresh(db_project)
    
    # Get counts
    act_query = select(func.count(Activity.id)).where(Activity.project_id == project_id)
    act_result = await db.execute(act_query)
    activity_count = act_result.scalar_one()
    
    boq_query = select(func.count(BOQItem.id)).where(BOQItem.project_id == project_id)
    boq_result = await db.execute(boq_query)
    boq_count = boq_result.scalar_one()
    
    response_data = ProjectResponse.model_validate(db_project)
    response_data.activity_count = activity_count
    response_data.boq_count = boq_count
    
    return response_data


@router.delete("/{project_id}", response_model=MessageResponse)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Delete a project and all associated data."""
    logger.warning(f"Deleting project: {project_id}")
    
    query = select(Project).where(Project.id == project_id)
    result = await db.execute(query)
    db_project = result.scalars().first()
    
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found."
        )
        
    await db.delete(db_project)
    await db.commit()
    
    return MessageResponse(message=f"Project '{project_id}' deleted successfully.")
