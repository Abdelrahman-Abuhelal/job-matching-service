"""Health check endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.schemas import HealthCheckResponse
from app.dependencies import get_database
from app.core.qdrant_client import test_qdrant_connection
from app.core.gemini_client import test_gemini_connection
from app import __version__

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_database)):
    """
    Check the health status of the service and its dependencies.
    
    Returns:
        Health status including connectivity to Qdrant, PostgreSQL, and Gemini AI
    """
    # Test PostgreSQL/SQLite connection
    postgres_connected = False
    try:
        db.execute(text("SELECT 1"))
        postgres_connected = True
    except Exception:
        pass
    
    # Test Qdrant connection
    qdrant_connected = await test_qdrant_connection()
    
    # Test Gemini connection
    gemini_available = await test_gemini_connection()
    
    # Determine overall status
    status = "healthy" if (postgres_connected and qdrant_connected and gemini_available) else "degraded"
    
    return HealthCheckResponse(
        status=status,
        qdrant_connected=qdrant_connected,
        postgres_connected=postgres_connected,
        gemini_api_available=gemini_available,
        version=__version__
    )
