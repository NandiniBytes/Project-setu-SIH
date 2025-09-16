from fastapi import FastAPI
from api.terminology import router as terminology_router

# Create FastAPI application instance
app = FastAPI(
    title="Project Setu",
    description="Secure FastAPI application for NAMASTE terminology integration",
    version="1.0.0"
)

# Include the terminology router
app.include_router(terminology_router, prefix="/api")


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
            "create_bundle": "/api/Bundle"
        },
        "authentication": "JWT Bearer token required for API endpoints",
        "message": "All systems operational"
    }
