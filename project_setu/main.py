from fastapi import FastAPI
from api.terminology import router as terminology_router
from api.users import router as users_router
from database import engine
import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI application instance
app = FastAPI(
    title="Project Setu",
    description="Secure FastAPI application for NAMASTE terminology integration with user management",
    version="1.0.0"
)

# Include routers
app.include_router(terminology_router, prefix="/api", tags=["terminology"])
app.include_router(users_router, prefix="/api", tags=["users"])


@app.get("/")
async def health_check():
    """
    Health check endpoint for the Project Setu API.
    
    Returns:
        Simple health status response
    """
    return {
        "status": "healthy",
        "service": "Project Setu",
        "version": "1.0.0",
        "message": "NAMASTE terminology integration API is running"
    }


@app.get("/health")
async def detailed_health():
    """
    Detailed health check endpoint.
    
    Returns:
        Comprehensive health status information
    """
    return {
        "status": "healthy",
        "service": "Project Setu",
        "version": "1.0.0",
        "endpoints": {
            "health_check": "/",
            "detailed_health": "/health",
            "code_system_lookup": "/api/CodeSystem/$lookup",
            "concept_map_translate": "/api/ConceptMap/$translate",
            "create_bundle": "/api/Bundle",
            "register_doctor": "/api/doctors/register",
            "login": "/api/token",
            "profile": "/api/doctors/me"
        },
        "authentication": "JWT Bearer token required for API endpoints",
        "message": "All systems operational"
    }
