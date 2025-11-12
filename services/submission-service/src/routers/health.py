"""
Health check router
"""
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    service: str
    timestamp: datetime


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    Returns service health status
    """
    return HealthResponse(
        status="healthy",
        service="submission-service",
        timestamp=datetime.utcnow(),
    )


@router.get("/health/live")
async def liveness_check():
    """
    Liveness probe endpoint
    Returns 200 if service is alive
    """
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_check():
    """
    Readiness probe endpoint
    Returns 200 if service is ready to accept traffic
    """
    return {"status": "ready"}
