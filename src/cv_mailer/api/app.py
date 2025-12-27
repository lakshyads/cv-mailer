"""
FastAPI application for CV Mailer API.
This provides a RESTful API for the CV Mailer system.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from cv_mailer import __version__
from cv_mailer.api.routers import applications, emails, recruiters, stats
from cv_mailer.utils import init_database

# Initialize database
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


def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the API server."""
    uvicorn.run("cv_mailer.api.app:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    run_server(reload=True)
