"""
FastAPI application for CV Mailer API.

This file contains ONLY infrastructure setup:
- Logging configuration
- Database initialization
- CORS middleware
- Router registration

NO BUSINESS LOGIC HERE - all business logic is in services/.
API routers are thin controllers that call service methods.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from cv_mailer import __version__
from cv_mailer.api.routers import applications, emails, recruiters, stats, sync
from cv_mailer.utils import init_database, close_database
from cv_mailer.utils.logging_utils import setup_logging

# Setup logging with rotation support
setup_logging()
logger = logging.getLogger(__name__)

# Initialize database (infrastructure setup - not business logic)
init_database()

# Create FastAPI app
app = FastAPI(
    title="CV Mailer API",
    description="Automated Resume Email System API",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(applications.router, prefix="/api/v1", tags=["applications"])
app.include_router(emails.router, prefix="/api/v1", tags=["emails"])
app.include_router(recruiters.router, prefix="/api/v1", tags=["recruiters"])
app.include_router(stats.router, prefix="/api/v1", tags=["statistics"])
app.include_router(sync.router, prefix="/api/v1", tags=["sync"])

logger.info("CV Mailer API initialized")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "CV Mailer API",
        "version": __version__,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": __version__}


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on application shutdown.
    Checkpoints WAL file to ensure all changes are persisted.
    """
    logger.info("Shutting down API server...")
    try:
        close_database()
        logger.info("Shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}", exc_info=True)


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the API server."""
    uvicorn.run("cv_mailer.api.app:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    run_server(reload=True)
