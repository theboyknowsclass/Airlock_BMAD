"""
API Key Service
API key generation, validation, and token issuance
"""
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .routers import health, api_keys
from .utils.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Get service configuration from environment
SERVICE_NAME = os.getenv("SERVICE_NAME", "api-key-service")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info(f"{SERVICE_NAME} service starting up")
    logger.info(f"Log level: {LOG_LEVEL}")
    yield
    # Shutdown
    logger.info(f"{SERVICE_NAME} service shutting down")


# Create FastAPI app
app = FastAPI(
    title="API Key Service",
    description="API key generation, validation, and token issuance",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(api_keys.router)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=LOG_LEVEL.lower(),
    )
