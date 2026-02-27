"""
FastAPI application entry point for OEM Product Research Dashboard.
Configures CORS, includes all routers, initializes database,
and sets up the background scheduler.
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.models.database import create_tables
from backend.routers import factories, research, review, simulator, trends
from backend.scheduler import get_scheduler_status, setup_scheduler

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    logger.info("Starting OEM Product Research Dashboard API...")

    # Create database tables
    create_tables()
    logger.info("Database tables created/verified.")

    # Setup and start the background scheduler
    sched = setup_scheduler()
    sched.start()
    logger.info("Background scheduler started.")

    yield

    # Shutdown
    sched.shutdown(wait=False)
    logger.info("Background scheduler shut down.")
    logger.info("Application shutdown complete.")


# Create FastAPI application
app = FastAPI(
    title="OEM Product Research Dashboard API",
    description=(
        "Backend API for OEM product research, market analysis, "
        "review analysis, ingredient trends, factory management, "
        "and profit simulation."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(research.router)
app.include_router(review.router)
app.include_router(trends.router)
app.include_router(factories.router)
app.include_router(simulator.router)


@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "OEM Product Research Dashboard API",
        "version": "1.0.0",
    }


@app.get("/api/scheduler/status")
async def scheduler_status() -> Dict[str, Any]:
    """Get background scheduler status."""
    return get_scheduler_status()
