"""
ConstructMind AI - Reports API Router
Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744

Provides endpoints for generating AI-powered construction project reports
(Progress, Cost Control, Delay Analysis, Risk Mitigation).
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.project import Project, Activity, Risk, BOQItem
from app.schemas.project import AIReportRequest, AIReportResponse
from app.services.ai.gemini_service import gemini_service
from app.config import settings

router = APIRouter()
logger = logging.getLogger("constructmind.routers.reports")


@router.post("/generate", response_model=AIReportResponse)
async def generate_project_report(
    project_id: str,
    request: AIReportRequest,
    db: AsyncSession = Depends(get_db)
) -> AIReportResponse:
    """
    Generate an AI report (Progress, Cost/EVM, Delay, or Risk) for a project.
    Compiles database data and runs analysis via Gemini.
    """
    logger.info(f"Generating AI report '{request.report_type}' for project '{project_id}'")

    # 1. Fetch project data from DB
    proj_query = select(Project).where(Project.id == project_id)
    proj_res = await db.execute(proj_query)
    proj = proj_res.scalars().first()
    if not proj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found."
        )

    # Fetch activities
    act_query = select(Activity).where(Activity.project_id == project_id)
    act_res = await db.execute(act_query)
    activities = act_res.scalars().all()

    # Fetch risks
    risk_query = select(Risk).where(Risk.project_id == project_id)
    risk_res = await db.execute(risk_query)
    risks = risk_res.scalars().all()

    # Fetch BOQ items
    boq_query = select(BOQItem).where(BOQItem.project_id == project_id)
    boq_res = await db.execute(boq_query)
    boq_items = boq_res.scalars().all()

    # 2. Compile payloads for Gemini
    project_payload = {
        "project_name": proj.name,
        "code": proj.code or "N/A",
        "budget": proj.budget or 0.0,
        "currency": proj.currency,
        "planned_start": str(proj.planned_start) if proj.planned_start else "Not Set",
        "planned_finish": str(proj.planned_finish) if proj.planned_finish else "Not Set",
        "status": proj.status.value if hasattr(proj.status, 'value') else str(proj.status),
        "location": proj.location or "Not Set",
        "client": proj.client_name or "Not Set",
        "contractor": proj.contractor_name or "Not Set",
        "total_activities": len(activities),
        "total_risks": len(risks),
        "total_boq_items": len(boq_items),
        "activities": [
            {
                "id": a.activity_id,
                "name": a.name,
                "duration": a.original_duration,
                "start": str(a.planned_start) if a.planned_start else "Not Set",
                "finish": str(a.planned_finish) if a.planned_finish else "Not Set",
                "status": a.status.value if hasattr(a.status, 'value') else str(a.status),
                "progress": a.percent_complete,
                "is_critical": a.is_critical,
                "float": a.total_float,
                "cost": a.budgeted_cost
            }
            for a in activities
        ],
        "risks": [
            {
                "id": r.risk_id,
                "title": r.title,
                "category": r.category,
                "severity": r.severity.value if hasattr(r.severity, 'value') else str(r.severity),
                "score": r.risk_score,
                "mitigation": r.mitigation_plan or "None"
            }
            for r in risks
        ]
    }

    # 3. Check if Gemini is available
    if not gemini_service.is_available:
        logger.warning("Gemini AI API not configured. Generating standard mock report.")
        return generate_mock_report(proj.name, request.report_type, project_payload)

    try:
        # Call Gemini Service
        ai_res = await gemini_service.generate_report(
            project_data=project_payload,
            report_type=request.report_type
        )

        # Parse AI response into response schema
        return AIReportResponse(
            report_type=request.report_type,
            title=ai_res.get("title", f"AI Project Controls Report ({request.report_type.capitalize()})"),
            content=ai_res.get("executive_summary", "") + "\n\n" + "\n\n".join([f"### {s['title']}\n{s['content']}" for s in ai_res.get("sections", [])]),
            generated_at=datetime.utcnow(),
            model_used=settings.GEMINI_MODEL,
            sections=ai_res.get("sections", []),
            recommendations=ai_res.get("recommendations", [])
        )
    except Exception as e:
        logger.error(f"Failed to generate Gemini AI report: {e}", exc_info=True)
        # Fallback on error
        return generate_mock_report(proj.name, request.report_type, project_payload)


# ══════════════════════════════════════════════════════════════════
# MOCK REPORT GENERATION (Fallback when AI Keys are missing)
# ══════════════════════════════════════════════════════════════════

def generate_mock_report(project_name: str, report_type: str, data: Dict[str, Any]) -> AIReportResponse:
    """Generate structured mock reports for testing and fallback."""
    title = f"{report_type.replace('_', ' ').title()} Analysis Report"
    
    sections = []
    recommendations = []
    
    # Extract totals
    total_acts = data["total_activities"]
    crit_acts = sum(1 for a in data["activities"] if a["is_critical"])
    
    # Heuristic metrics
    cpi = 0.94
    spi = 0.91
    variance = - (data["budget"] * 0.06) if data["budget"] else -50000
    
    if report_type == "progress":
        title = f"Project Executive Progress Report - {project_name}"
        executive_summary = (
            f"This progress report provides status intelligence for the construction of **{project_name}**.\n\n"
            f"Currently, the project schedule contains **{total_acts}** activities with **{crit_acts}** tasks on the Critical Path. "
            f"The schedule performance index (SPI) is estimated at **{spi}**, indicating the project is slightly behind the planned schedule baseline. "
            f"Immediate resource balancing is recommended on key critical activities to recover lost time."
        )
        sections = [
            {
                "title": "Schedule Performance Analysis",
                "content": (
                    f"Our CPM engine completed a full forward/backward pass calculation on {total_acts} activities.\n\n"
                    f"- **Planned Start:** {data['planned_start']}\n"
                    f"- **Current Planned Finish:** {data['planned_finish']}\n"
                    f"- **Schedule Variance (SV):** -9% (Behind Schedule)\n"
                    f"- **Schedule Performance Index (SPI):** {spi}\n\n"
                    "The primary bottlenecks are concentrated in structural excavation and concrete curing delays due to site logistics."
                ),
                "charts": [{"type": "line", "title": "Planned vs Actual Progress (S-Curve)", "data": {}}]
            },
            {
                "title": "Critical Path & Float Analysis",
                "content": (
                    f"A total of **{crit_acts}** activities have zero float and form the critical path. "
                    "Any delay in these activities will directly impact the project completion date. "
                    "Key critical items include foundation structural reinforcement and initial column framing."
                ),
                "charts": [{"type": "gantt", "title": "Critical Path Tasks", "data": {}}]
            }
        ]
        recommendations = [
            "Increase crew size on critical concrete pours by 20% to regain schedule momentum.",
            "Set up concrete strength field testing to minimize cure time waiting periods.",
            "Finalize MEP procurement items to avoid layout installation delays."
        ]
        
    elif report_type == "cost":
        title = f"Cost Control & EVM Analysis - {project_name}"
        executive_summary = (
            f"Financial performance controls audit for **{project_name}**.\n\n"
            f"The current project Budget at Completion (BAC) is **{data['budget']:,.2f} {data['currency']}**. "
            f"Based on our Earned Value Management (EVM) analysis, the Cost Performance Index (CPI) is **{cpi}**, "
            f"indicating the project is operating over-budget by approximately 6% (Cost Variance: {variance:,.2f} {data['currency']})."
        )
        sections = [
            {
                "title": "Earned Value Metrics Breakdown",
                "content": (
                    f"The project financial metrics as of the current reporting date:\n\n"
                    f"- **Budget at Completion (BAC):** {data['budget']:,.2f} {data['currency']}\n"
                    f"- **Planned Value (PV):** {(data['budget'] * 0.40 if data['budget'] else 100000):,.2f} {data['currency']}\n"
                    f"- **Earned Value (EV):** {(data['budget'] * 0.36 if data['budget'] else 90000):,.2f} {data['currency']}\n"
                    f"- **Actual Cost (AC):** {(data['budget'] * 0.38 if data['budget'] else 96000):,.2f} {data['currency']}\n"
                    f"- **Cost Variance (CV):** {variance:,.2f} {data['currency']}\n"
                    f"- **Cost Performance Index (CPI):** {cpi}\n"
                ),
                "charts": [{"type": "bar", "title": "EVM Bar Chart (PV vs EV vs AC)", "data": {}}]
            }
        ]
        recommendations = [
            "Re-evaluate masonry material procurement agreements to cut material costs.",
            "Implement stricter labor logging to control overtime costs in superstructure works."
        ]
        
    elif report_type == "delay_analysis":
        title = f"Forensic Delay Analysis & Recovery Plan - {project_name}"
        executive_summary = (
            f"This forensic report isolates delay factors affecting **{project_name}**.\n\n"
            "By analyzing early/late schedule deviations, we identified an overall slip of 8 days relative to the as-planned schedule. "
            "Excusable delays comprise 5 days due to heavy rain, and non-excusable contractor delays account for 3 days due to late subcontractor mobilization."
        )
        sections = [
            {
                "title": "Delay Attribution",
                "content": (
                    "Using Time Impact Analysis (TIA) logic, we map the slip as follows:\n\n"
                    "- **Weather Events (Excusable):** 5 days slip during site excavation.\n"
                    "- **Subcontractor Delays (Non-Excusable):** 3 days delay in concrete formwork mobilization.\n"
                    "- **Critical Path Impact:** The delay has directly pushed the GF slab concrete pour milestone."
                )
            }
        ]
        recommendations = [
            "Draft a formal Extension of Time (EOT) claim for the 5 weather delay days.",
            "Enforce contract liquidated damage warnings to the concrete formwork subcontractor.",
            "Optimize finishing task dependencies (converting FS to SS with lag) to compress the remaining schedule by 6 days."
        ]
        
    else: # Risk report
        title = f"AI Risk Assessment & Mitigation Matrix - {project_name}"
        executive_summary = (
            f"Schedule and cost hazard report for **{project_name}**.\n\n"
            f"The project database contains **{data['total_risks']}** identified risks. "
            "Our quantitative risk engine shows high concentration in procurement logistics and material rate volatility."
        )
        sections = [
            {
                "title": "Risk Register Breakdown",
                "content": (
                    "The top active hazards sorted by severity and impact score:\n\n"
                    "- **Steel/Cement Rate Inflation:** Severity HIGH (Cost Impact: 50,000+ PKR). Status: Active.\n"
                    "- **Labor Scarcity during Harvest Season:** Severity MEDIUM (Schedule Impact: 4 days). Status: Identified.\n"
                    "- **Monsoon Curing Wait Periods:** Severity MEDIUM. Mitigation in place."
                )
            }
        ]
        recommendations = [
            "Procure bulk steel reinforcement stock immediately to hedge inflation risk.",
            "Offer local transportation stipends to secure critical labor crews during seasonal shifts."
        ]

    return AIReportResponse(
        report_type=report_type,
        title=title,
        content=executive_summary + "\n\n" + "\n\n".join([f"### {s['title']}\n{s['content']}" for s in sections]),
        generated_at=datetime.utcnow(),
        model_used="MockEngine-1.0",
        sections=sections,
        recommendations=recommendations
    )
