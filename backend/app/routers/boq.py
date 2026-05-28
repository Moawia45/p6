"""
ConstructMind AI - Bill of Quantities (BOQ) API Router
Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744

Provides endpoints for BOQ uploading, parsing, AI analysis, 
and converting BOQ items into scheduled project activities.
"""

from __future__ import annotations

import logging
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.project import BOQItem, Project, Activity, WBS
from app.schemas.project import BOQItemResponse, BOQUploadResponse, MessageResponse
from app.utils.file_parser import parse_excel_boq, parse_pdf_boq
from app.services.ai.gemini_service import gemini_service

router = APIRouter()
logger = logging.getLogger("constructmind.routers.boq")


@router.post("/upload", response_model=BOQUploadResponse)
async def upload_boq(
    project_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
) -> BOQUploadResponse:
    """Upload and parse an Excel or PDF BOQ file, saving items to the database."""
    logger.info(f"Uploading BOQ file '{file.filename}' for project '{project_id}'")
    
    # Verify project exists
    proj_check = await db.execute(select(Project).where(Project.id == project_id))
    if not proj_check.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found."
        )

    # Read bytes
    try:
        contents = await file.read()
    except Exception as e:
        logger.error(f"Failed to read uploaded file: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read file contents."
        )

    # Parse based on extension
    filename = file.filename or "boq.xlsx"
    ext = filename.split(".")[-1].lower()
    
    parsed_items = []
    try:
        if ext in ["xlsx", "xls"]:
            parsed_items = parse_excel_boq(contents, filename)
        elif ext == "pdf":
            parsed_items = parse_pdf_boq(contents, filename)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format. Please upload an Excel (.xlsx/.xls) or PDF file."
            )
    except Exception as e:
        logger.error(f"Error parsing file: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse file: {str(e)}"
        )

    if not parsed_items:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No valid BOQ items could be extracted from this file."
        )

    # Clear any existing BOQ items for this project
    await db.execute(delete(BOQItem).where(BOQItem.project_id == project_id))

    # Add items to DB
    db_items = []
    for item in parsed_items:
        db_item = BOQItem(
            project_id=project_id,
            item_no=item["item_no"],
            description=item["description"],
            quantity=item["quantity"],
            unit=item["unit"],
            unit_rate=item["unit_rate"],
            total_amount=item["total_amount"],
            source_file=item["source_file"],
            source_row=item.get("source_row")
        )
        db.add(db_item)
        db_items.append(db_item)
        
    await db.commit()
    for db_item in db_items:
        await db.refresh(db_item)

    # Calculate total budget update for project
    total_amount = sum(item.total_amount for item in db_items)
    await db.execute(
        update(Project)
        .where(Project.id == project_id)
        .values(budget=total_amount)
    )
    await db.commit()

    return BOQUploadResponse(
        message=f"Successfully uploaded and parsed '{filename}'.",
        items_parsed=len(parsed_items),
        items_created=len(db_items),
        file_name=filename,
        items=[BOQItemResponse.model_validate(i) for i in db_items]
    )


@router.get("/", response_model=List[BOQItemResponse])
async def list_boq_items(
    project_id: str,
    db: AsyncSession = Depends(get_db)
) -> List[BOQItemResponse]:
    """Retrieve all BOQ items for a project."""
    query = select(BOQItem).where(BOQItem.project_id == project_id).order_by(BOQItem.item_no.asc())
    result = await db.execute(query)
    items = result.scalars().all()
    return [BOQItemResponse.model_validate(item) for item in items]


@router.post("/analyze", response_model=List[BOQItemResponse])
async def analyze_boq_items(
    project_id: str,
    db: AsyncSession = Depends(get_db)
) -> List[BOQItemResponse]:
    """Analyze BOQ items using Gemini AI and update categories/codes in database."""
    logger.info(f"Triggering AI BOQ analysis for project '{project_id}'")
    
    query = select(BOQItem).where(BOQItem.project_id == project_id)
    result = await db.execute(query)
    boq_items = result.scalars().all()
    
    if not boq_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No BOQ items exist for this project. Please upload a BOQ first."
        )

    # Map items to dictionaries for AI analysis
    items_payload = [
        {
            "id": item.id,
            "item_no": item.item_no,
            "description": item.description,
            "quantity": item.quantity,
            "unit": item.unit,
            "unit_rate": item.unit_rate,
            "total_amount": item.total_amount
        }
        for item in boq_items
    ]

    # Rule-based fallback classifier
    def fallback_classification(desc: str) -> dict:
        d = desc.lower()
        if any(w in d for w in ["excavation", "digging", "earthwork", "backfill", "compaction"]):
            return {"code": "02 30 00", "cat": "Earthwork / Excavation", "note": "Classified automatically: Substructure Earthwork."}
        if any(w in d for w in ["concrete", "lean", "pour", "rcc", "pcc", "foundation", "slab", "beam", "column"]):
            return {"code": "03 30 00", "cat": "Concrete & Formwork", "note": "Classified automatically: Cast-in-Place Concrete structure."}
        if any(w in d for w in ["brick", "block", "masonry", "mortar"]):
            return {"code": "04 20 00", "cat": "Masonry Works", "note": "Classified automatically: Brick/Block Masonry walls."}
        if any(w in d for w in ["paint", "plaster", "tile", "marble", "ceiling", "gypsum", "flooring", "wood"]):
            return {"code": "09 00 00", "cat": "Finishing & Tiling", "note": "Classified automatically: Surface finishes & architectural works."}
        if any(w in d for w in ["electrical", "conduit", "wiring", "plumbing", "pipe", "hvac", "duct", "drainage"]):
            return {"code": "21 00 00", "cat": "MEP Works", "note": "Classified automatically: Mechanical, Electrical, Plumbing services."}
        if any(w in d for w in ["steel", "rebar", "reinforcement", "structure", "fabrication"]):
            return {"code": "05 12 00", "cat": "Structural Metals", "note": "Classified automatically: Metal reinforcements / structural steel."}
        return {"code": "01 00 00", "cat": "General Requirements", "note": "Classified automatically: General project provisions."}

    categorized_map = {}
    
    if gemini_service.is_available:
        try:
            # We call Gemini in batches if there are many items to prevent timeouts,
            # but for MVP a single call up to 50 items is fine.
            analysis_results = await gemini_service.analyze_boq(items_payload[:60])
            for res_item in analysis_results.get("categorized_items", []):
                # Search by item_no
                categorized_map[res_item.get("item_no")] = {
                    "code": res_item.get("csi_code", "01 00 00"),
                    "cat": res_item.get("csi_category", "General Requirements"),
                    "note": res_item.get("validation_notes", "Verified by Gemini AI.")
                }
        except Exception as e:
            logger.error(f"Gemini BOQ analysis failed: {e}", exc_info=True)

    # Update items in database (using either AI results or fallback)
    for item in boq_items:
        ai_data = categorized_map.get(item.item_no)
        if not ai_data:
            ai_data = fallback_classification(item.description)
            
        item.csi_code = ai_data["code"]
        item.csi_category = ai_data["cat"]
        item.ai_category = ai_data["cat"]
        item.ai_notes = ai_data["note"]
        item.ai_parsed = True
        item.ai_confidence = 0.9 if gemini_service.is_available else 0.7
        db.add(item)
        
    await db.commit()
    for item in boq_items:
        await db.refresh(item)
        
    return [BOQItemResponse.model_validate(item) for item in boq_items]


@router.post("/convert", response_model=MessageResponse)
async def convert_boq_to_activities(
    project_id: str,
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Convert categorized BOQ items to schedule WBS sections and activities.
    """
    logger.info(f"Converting BOQ items to schedule for project '{project_id}'")
    
    # 1. Fetch analyzed BOQ items
    query = select(BOQItem).where(BOQItem.project_id == project_id)
    result = await db.execute(query)
    boq_items = result.scalars().all()
    
    if not boq_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No BOQ items to convert. Upload and analyze a BOQ first."
        )

    # 2. Extract unique CSI categories to create WBS structure
    categories = sorted(list({item.csi_category or "General Requirements" for item in boq_items}))
    
    # Clear existing WBS and Activities for a clean conversion
    await db.execute(delete(Activity).where(Activity.project_id == project_id))
    await db.execute(delete(WBS).where(WBS.project_id == project_id))
    await db.commit()

    # 3. Create WBS nodes
    wbs_map = {}
    for idx, cat in enumerate(categories):
        wbs_code = f"{idx + 1}.0"
        db_wbs = WBS(
            project_id=project_id,
            code=wbs_code,
            name=cat,
            level=1,
            sort_order=idx * 10
        )
        db.add(db_wbs)
        wbs_map[cat] = db_wbs

    await db.commit()
    for cat in wbs_map:
        await db.refresh(wbs_map[cat])

    # 4. Create Activities from BOQ items
    activities_created = 0
    for idx, item in enumerate(boq_items):
        cat = item.csi_category or "General Requirements"
        wbs_node = wbs_map.get(cat)
        
        # Determine duration: use simple quantity-based heuristics if no duration engine match
        dur_days = 5.0
        if item.quantity > 0:
            # simple quantity heuristic mapping
            if "m³" in item.unit or "cft" in item.unit.lower():
                dur_days = max(2.0, round(item.quantity / 50.0, 1))
            elif "m²" in item.unit or "sft" in item.unit.lower():
                dur_days = max(2.0, round(item.quantity / 150.0, 1))
            elif "ton" in item.unit.lower() or "kg" in item.unit.lower():
                dur_days = max(3.0, round(item.quantity / 2.0, 1))
            else:
                dur_days = max(2.0, round(item.quantity / 20.0, 1))
                
        # Limit max duration to 30 days for scheduling grain
        dur_days = min(30.0, dur_days)

        act_id = f"A{1000 + idx*10}"
        
        # Name: Truncate description for activity name
        short_name = item.description[:80] + "..." if len(item.description) > 80 else item.description

        db_act = Activity(
            project_id=project_id,
            wbs_id=wbs_node.id if wbs_node else None,
            activity_id=act_id,
            name=short_name,
            description=item.description,
            activity_type="task",
            original_duration=dur_days,
            remaining_duration=dur_days,
            quantity=item.quantity,
            unit=item.unit,
            budgeted_cost=item.total_amount,
            sort_order=idx * 10
        )
        db.add(db_act)
        activities_created += 1

    await db.commit()
    
    # 5. Connect activities in simple linear sequence within each WBS for basic schedule baseline
    # Fetch activities back
    act_query = select(Activity).where(Activity.project_id == project_id).order_by(Activity.sort_order.asc())
    act_result = await db.execute(act_query)
    all_acts = act_result.scalars().all()
    
    if len(all_acts) > 1:
        for idx in range(len(all_acts) - 1):
            pred = all_acts[idx]
            succ = all_acts[idx + 1]
            db_rel = Relationship(
                project_id=project_id,
                predecessor_id=pred.id,
                successor_id=succ.id,
                relationship_type="FS",
                lag_days=0
            )
            db.add(db_rel)
        await db.commit()

    return MessageResponse(
        message=f"Converted {len(boq_items)} BOQ items into {activities_created} activities and {len(wbs_map)} WBS nodes."
    )
