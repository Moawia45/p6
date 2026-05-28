"""
ConstructMind AI - FastAPI Application Entry Point
Created by Moawia Husnain | Civil Engineer | UET Taxila | +923266915744

Initializes the FastAPI application, registers middleware (CORS), 
wires up routers, and defines startup/shutdown lifespan behavior.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import create_tables
from app.schemas.project import HealthResponse
from app.routers import projects, activities, boq, schedule, copilot, reports, resources

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("constructmind")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """ Lifespan event handler to create database tables on startup. """
    logger.info("Initializing ConstructMind AI Database Tables...")
    try:
        await create_tables()
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.critical(f"Failed to initialize database tables: {e}", exc_info=True)
    yield
    logger.info("Shutting down ConstructMind AI Application...")

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Futuristic AI-powered Construction Planning, Scheduling, BOQ Analysis, "
        "and Project Controls Automation API.\n\n"
        "Created by Moawia Husnain (Civil Engineer, UET Taxila, UET Phone: +923266915744)"
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(activities.router, prefix="/api/projects/{project_id}/activities", tags=["Activities"])
app.include_router(boq.router, prefix="/api/projects/{project_id}/boq", tags=["Bill of Quantities"])
app.include_router(schedule.router, prefix="/api/projects/{project_id}/schedule", tags=["Scheduling"])
app.include_router(resources.router, prefix="/api/projects/{project_id}/resources", tags=["Resources"])
app.include_router(reports.router, prefix="/api/projects/{project_id}/reports", tags=["Reports & Analytics"])
app.include_router(copilot.router, prefix="/api/copilot", tags=["AI Copilot"])

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check() -> JSONResponse:
    """System health check endpoint."""
    return JSONResponse(
        content={
            "status": "ok",
            "version": settings.APP_VERSION,
            "app": settings.APP_NAME,
            "creator": "Moawia Husnain | Civil Engineer | UET Taxila | +923266915744"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
