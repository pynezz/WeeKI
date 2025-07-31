"""FastAPI server for WeeKI agent orchestration system."""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings
from .agents import AgentOrchestrator


# Request/Response models
class TaskRequest(BaseModel):
    """Task request model."""
    directive: str
    context: Dict[str, Any] = {}


class TaskResponse(BaseModel):
    """Task response model."""
    task_id: str
    status: str
    message: str
    result: Dict[str, Any] = {}


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    version: str
    agents_active: int


# Global orchestrator instance
orchestrator: AgentOrchestrator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global orchestrator
    
    # Startup
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=settings.log_format
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting WeeKI agent orchestration system...")
    
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()
    
    yield
    
    # Shutdown
    logger.info("Shutting down WeeKI agent orchestration system...")
    if orchestrator:
        await orchestrator.shutdown()


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    debug=settings.debug,
    lifespan=lifespan
)

# Add CORS middleware for self-hosting scenarios
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["http://localhost", "http://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    active_agents = 0
    if orchestrator:
        active_agents = orchestrator.get_active_agent_count()
    
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        agents_active=active_agents
    )


@app.post("/tasks", response_model=TaskResponse)
async def create_task(request: TaskRequest):
    """Create a new task for the agent orchestrator."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        task_id = await orchestrator.create_task(request.directive, request.context)
        return TaskResponse(
            task_id=task_id,
            status="created",
            message="Task created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create task: {str(e)}")


@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """Get the status of a specific task."""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    
    try:
        task_status = await orchestrator.get_task_status(task_id)
        if not task_status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskResponse(
            task_id=task_id,
            status=task_status["status"],
            message=task_status.get("message", ""),
            result=task_status.get("result", {})
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "WeeKI - Wee, Kunstig Intelligens",
        "description": "AI Agent Orchestration System",
        "version": settings.api_version,
        "docs_url": "/docs",
        "health_url": "/health"
    }