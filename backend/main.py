"""FastAPI main application for OEM Research Dashboard."""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.models.database import create_tables
from backend.routers import research, review, trends, factories, simulator
from backend.scheduler import setup_scheduler, shutdown_scheduler

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    create_tables()
    setup_scheduler()
    yield
    # Shutdown
    shutdown_scheduler()


app = FastAPI(
    title="OEM Research Dashboard API",
    description="API for OEM product development research tool",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(research.router)
app.include_router(review.router)
app.include_router(trends.router)
app.include_router(factories.router)
app.include_router(simulator.router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "services": {
            "keepa_api": bool(os.getenv("KEEPA_API_KEY")),
            "sp_api": bool(os.getenv("SP_API_REFRESH_TOKEN")),
            "claude_api": bool(os.getenv("ANTHROPIC_API_KEY")),
        },
    }
