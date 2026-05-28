"""
ConstructMind AI - AI Copilot API Router
Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744

Provides endpoints for streaming and non-streaming construction intelligence 
copilot chat using the Groq Llama 4 Scout model.
"""

from __future__ import annotations

import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.project import Project, Activity, Risk
from app.schemas.project import CopilotRequest, CopilotResponse
from app.services.ai.groq_service import groq_service

router = APIRouter()
logger = logging.getLogger("constructmind.routers.copilot")


@router.post("/chat")
async def copilot_chat(
    request: CopilotRequest,
    db: AsyncSession = Depends(get_db)
) -> StreamingResponse | JSONResponse:
    """
    Handle chat interactions with the AI Copilot.
    Supports regular JSON responses or SSE streaming.
    """
    logger.info(f"Copilot chat requested. Stream={request.stream}, project_id={request.project_id}")

    if not groq_service.is_available:
        logger.warning("Groq service is not configured. Returning static fallback.")
        fallback_msg = (
            "Hello! I am ConstructMind AI, your construction copilot. "
            "However, the Groq API key is currently not configured in the environment. "
            "Please check your `.env` configuration file.\n\n"
            "This project is created by **Moawia Husnain**, Civil Engineer from UET Taxila (+923266915744)."
        )
        if request.stream:
            async def fallback_stream():
                yield f"data: {json.dumps({'content': fallback_msg})}\n\n"
                yield "data: [DONE]\n\n"
            return StreamingResponse(fallback_stream(), media_type="text/event-stream")
        else:
            return JSONResponse(
                content={
                    "message": fallback_msg,
                    "model": "MockEngine-1.0",
                    "usage": None
                }
            )

    # 1. Fetch project context if project_id is provided
    project_context = ""
    if request.project_id:
        try:
            # Fetch project details
            proj_query = select(Project).where(Project.id == request.project_id)
            proj_res = await db.execute(proj_query)
            proj = proj_res.scalars().first()
            if proj:
                project_context += (
                    f"Active Project: {proj.name} (Code: {proj.code or 'N/A'})\n"
                    f"Budget: {proj.budget or 0:,.2f} {proj.currency}\n"
                    f"Start Date: {proj.planned_start or 'Not Set'}, Finish Date: {proj.planned_finish or 'Not Set'}\n"
                    f"Current Status: {proj.status.value if hasattr(proj.status, 'value') else str(proj.status)}\n"
                    f"Location: {proj.location or 'Not Set'}\n"
                )

                # Fetch activity summaries
                act_query = select(Activity).where(Activity.project_id == request.project_id)
                act_res = await db.execute(act_query)
                activities = act_res.scalars().all()
                total_acts = len(activities)
                critical_acts = sum(1 for a in activities if a.is_critical)
                completed_acts = sum(1 for a in activities if (a.status.value == "completed" if hasattr(a.status, "value") else a.status == "completed"))
                delayed_acts = sum(1 for a in activities if (a.status.value == "delayed" if hasattr(a.status, "value") else a.status == "delayed"))
                
                project_context += (
                    f"Total Activities in Schedule: {total_acts}\n"
                    f"Critical Path Tasks: {critical_acts}\n"
                    f"Completed Tasks: {completed_acts}\n"
                    f"Delayed Tasks: {delayed_acts}\n"
                )
                
                # Fetch top critical activities
                crit_names = [f"- {a.activity_id}: {a.name} (Float: {a.total_float}d, Finish: {a.planned_finish})" 
                              for a in activities if a.is_critical][:5]
                if crit_names:
                    project_context += "Top Critical Tasks:\n" + "\n".join(crit_names) + "\n"

                # Fetch risks
                risk_query = select(Risk).where(Risk.project_id == request.project_id)
                risk_res = await db.execute(risk_query)
                risks = risk_res.scalars().all()
                total_risks = len(risks)
                open_risks = sum(1 for r in risks if (r.status.value == "identified" or r.status.value == "occurred" if hasattr(r.status, "value") else r.status in ["identified", "occurred"]))
                
                project_context += f"Total Project Risks: {total_risks} ({open_risks} open)\n"
        except Exception as e:
            logger.error(f"Error gathering project context for AI: {e}", exc_info=True)

    # 2. Return SSE streaming response or JSON response
    if request.stream:
        # Define the synchronous generator function
        def sse_event_generator():
            try:
                # Get OpenAI streaming iterator
                stream_res = groq_service.stream_chat(
                    message=request.message,
                    conversation_history=[{"role": m.role, "content": m.content} for m in request.conversation_history],
                    project_context=project_context if project_context else None
                )
                for chunk in stream_res:
                    if chunk.choices and chunk.choices[0].delta.content:
                        text = chunk.choices[0].delta.content
                        yield f"data: {json.dumps({'content': text})}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as ex:
                logger.error(f"Error in copilot stream: {ex}")
                yield f"data: {json.dumps({'error': str(ex)})}\n\n"

        return StreamingResponse(sse_event_generator(), media_type="text/event-stream")
    else:
        try:
            res = groq_service.chat(
                message=request.message,
                conversation_history=[{"role": m.role, "content": m.content} for m in request.conversation_history],
                project_context=project_context if project_context else None
            )
            return JSONResponse(content=res)
        except Exception as e:
            logger.error(f"Error in copilot chat: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"AI Chat failed: {str(e)}"
            )
