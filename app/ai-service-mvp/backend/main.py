"""
AI Service Marketplace - Main API Application
FastAPI backend orchestrator for the entire system
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator

from app.core.config import settings
from app.core.database import database_manager
from app.api import ai
from app.api import master
from app.api import terminal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager"""
    # Startup
    logger.info("Starting AI Service Marketplace API...")
    await database_manager.connect()
    logger.info("Database connected")
    
    yield
    
    # Shutdown
    logger.info("Shutting down AI Service Marketplace API...")
    await database_manager.disconnect()
    logger.info("Database disconnected")


# Create FastAPI application
app = FastAPI(
    title="AI Service Marketplace API",
    description="Autonomous AI platform connecting service masters with clients",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI Services"])
app.include_router(master.router, prefix="/api/v1/masters", tags=["Master Onboarding"])
app.include_router(terminal.router, prefix="/api/v1/terminal", tags=["Master Terminal"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI Service Marketplace",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db_status = await database_manager.check_connection()
        
        return {
            "status": "healthy",
            "database": "connected" if db_status else "disconnected"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
