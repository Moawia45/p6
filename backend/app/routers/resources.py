"""
ConstructMind AI - Resources API Router
Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744

Provides endpoints for Resource CRUD operations and Resource Assignments 
to schedule activities.
"""

from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.project import Resource, ResourceAssignment, Activity, Project
from app.schemas.project import (
    ResourceCreate,
    ResourceUpdate,
    ResourceResponse,
    ResourceAssignmentCreate,
    ResourceAssignmentResponse,
    MessageResponse,
)

router = APIRouter()
logger = logging.getLogger("constructmind.routers.resources")


@router.get("/", response_model=List[ResourceResponse])
async def list_resources(
    project_id: str,
    db: AsyncSession = Depends(get_db)
) -> List[ResourceResponse]:
    """Retrieve all resources available to a project."""
    query = select(Resource).where(Resource.project_id == project_id)
    result = await db.execute(query)
    resources = result.scalars().all()
    return [ResourceResponse.model_validate(r) for r in resources]


@router.post("/", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    project_id: str,
    resource_in: ResourceCreate,
    db: AsyncSession = Depends(get_db)
) -> ResourceResponse:
    """Create a new resource for a project."""
    logger.info(f"Creating resource '{resource_in.resource_id}' in project '{project_id}'")
    
    # Check if project exists
    proj_check = await db.execute(select(Project).where(Project.id == project_id))
    if not proj_check.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found."
        )

    # Check if resource_id is already in use for this project
    res_check = await db.execute(
        select(Resource).where(
            Resource.project_id == project_id,
            Resource.resource_id == resource_in.resource_id
        )
    )
    if res_check.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Resource ID '{resource_in.resource_id}' is already in use for this project."
        )

    db_resource = Resource(
        project_id=project_id,
        resource_id=resource_in.resource_id,
        name=resource_in.name,
        resource_type=resource_in.resource_type,
        max_units=resource_in.max_units,
        unit_of_measure=resource_in.unit_of_measure,
        standard_rate=resource_in.standard_rate,
        overtime_rate=resource_in.overtime_rate,
        cost_per_use=resource_in.cost_per_use,
        email=resource_in.email,
        phone=resource_in.phone,
        notes=resource_in.notes,
        is_active=resource_in.is_active,
    )
    db.add(db_resource)
    await db.commit()
    await db.refresh(db_resource)
    
    return ResourceResponse.model_validate(db_resource)


@router.get("/{resource_db_id}", response_model=ResourceResponse)
async def get_resource(
    project_id: str,
    resource_db_id: str,
    db: AsyncSession = Depends(get_db)
) -> ResourceResponse:
    """Retrieve details of a single resource by its database UUID."""
    query = select(Resource).where(Resource.project_id == project_id, Resource.id == resource_db_id)
    result = await db.execute(query)
    resource = result.scalars().first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource with ID '{resource_db_id}' not found."
        )
    return ResourceResponse.model_validate(resource)


@router.put("/{resource_db_id}", response_model=ResourceResponse)
async def update_resource(
    project_id: str,
    resource_db_id: str,
    resource_in: ResourceUpdate,
    db: AsyncSession = Depends(get_db)
) -> ResourceResponse:
    """Update details of an existing resource."""
    logger.info(f"Updating resource '{resource_db_id}' in project '{project_id}'")
    
    query = select(Resource).where(Resource.project_id == project_id, Resource.id == resource_db_id)
    result = await db.execute(query)
    resource = result.scalars().first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource with ID '{resource_db_id}' not found."
        )

    # Check resource_id uniqueness if modifying
    if resource_in.resource_id and resource_in.resource_id != resource.resource_id:
        res_check = await db.execute(
            select(Resource).where(
                Resource.project_id == project_id,
                Resource.resource_id == resource_in.resource_id,
                Resource.id != resource_db_id
            )
        )
        if res_check.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Resource ID '{resource_in.resource_id}' is already in use."
            )

    update_data = resource_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resource, field, value)
        
    await db.commit()
    await db.refresh(resource)
    
    return ResourceResponse.model_validate(resource)


@router.delete("/{resource_db_id}", response_model=MessageResponse)
async def delete_resource(
    project_id: str,
    resource_db_id: str,
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Delete a resource from a project."""
    logger.warning(f"Deleting resource '{resource_db_id}' from project '{project_id}'")
    
    query = select(Resource).where(Resource.project_id == project_id, Resource.id == resource_db_id)
    result = await db.execute(query)
    resource = result.scalars().first()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource with ID '{resource_db_id}' not found."
        )
        
    await db.delete(resource)
    await db.commit()
    
    return MessageResponse(message=f"Resource '{resource_db_id}' deleted successfully.")


# ══════════════════════════════════════════════════════════════════
# RESOURCE ASSIGNMENT ENDPOINTS
# ══════════════════════════════════════════════════════════════════

@router.post("/assignments", response_model=ResourceAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_resource_to_activity(
    project_id: str,
    assignment_in: ResourceAssignmentCreate,
    db: AsyncSession = Depends(get_db)
) -> ResourceAssignmentResponse:
    """Assign an existing project resource to an activity."""
    logger.info(f"Assigning resource '{assignment_in.resource_id}' to activity '{assignment_in.activity_id}'")
    
    # Verify activity exists in this project
    act_check = await db.execute(
        select(Activity).where(Activity.project_id == project_id, Activity.id == assignment_in.activity_id)
    )
    activity = act_check.scalars().first()
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with ID '{assignment_in.activity_id}' not found in project '{project_id}'."
        )

    # Verify resource exists in this project
    res_check = await db.execute(
        select(Resource).where(Resource.project_id == project_id, Resource.id == assignment_in.resource_id)
    )
    resource = res_check.scalars().first()
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource with ID '{assignment_in.resource_id}' not found in project '{project_id}'."
        )

    # Check if already assigned
    assign_check = await db.execute(
        select(ResourceAssignment).where(
            ResourceAssignment.activity_id == assignment_in.activity_id,
            ResourceAssignment.resource_id == assignment_in.resource_id
        )
    )
    if assign_check.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resource is already assigned to this activity."
        )

    # Calculate planned cost: standard rate * planned units
    planned_units = assignment_in.planned_units if assignment_in.planned_units > 0 else (activity.original_duration * 8.0 * assignment_in.units)
    planned_cost = assignment_in.planned_cost if assignment_in.planned_cost > 0 else (planned_units * resource.standard_rate)

    db_assignment = ResourceAssignment(
        activity_id=assignment_in.activity_id,
        resource_id=assignment_in.resource_id,
        units=assignment_in.units,
        planned_units=planned_units,
        remaining_units=planned_units,
        planned_cost=planned_cost,
    )
    
    db.add(db_assignment)
    
    # Add cost to activity budgeted cost
    activity.budgeted_cost += planned_cost
    db.add(activity)
    
    await db.commit()
    await db.refresh(db_assignment)
    
    return ResourceAssignmentResponse.model_validate(db_assignment)


@router.get("/assignments", response_model=List[ResourceAssignmentResponse])
async def list_resource_assignments(
    project_id: str,
    db: AsyncSession = Depends(get_db)
) -> List[ResourceAssignmentResponse]:
    """Retrieve all resource assignments inside a project."""
    query = (
        select(ResourceAssignment)
        .join(Activity)
        .where(Activity.project_id == project_id)
    )
    result = await db.execute(query)
    assignments = result.scalars().all()
    
    return [ResourceAssignmentResponse.model_validate(a) for a in assignments]


@router.delete("/assignments/{assignment_id}", response_model=MessageResponse)
async def remove_resource_assignment(
    project_id: str,
    assignment_id: str,
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """Remove a resource assignment from an activity."""
    # Verify assignment exists
    query = (
        select(ResourceAssignment)
        .join(Activity)
        .where(Activity.project_id == project_id, ResourceAssignment.id == assignment_id)
    )
    result = await db.execute(query)
    assignment = result.scalars().first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with ID '{assignment_id}' not found in project '{project_id}'."
        )

    # Fetch activity to deduct budgeted cost
    act_query = select(Activity).where(Activity.id == assignment.activity_id)
    act_res = await db.execute(act_query)
    activity = act_res.scalars().first()
    if activity:
        activity.budgeted_cost = max(0.0, activity.budgeted_cost - assignment.planned_cost)
        db.add(activity)

    await db.delete(assignment)
    await db.commit()
    
    return MessageResponse(message=f"Resource assignment '{assignment_id}' removed successfully.")
