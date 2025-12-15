"""Health check endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.schemas import HealthCheckResponse
from app.dependencies import get_database
from app.core.qdrant_client import test_qdrant_connection
from app.core.openai_client import test_openai_connection
from app import __version__

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_database)):
    """
    Check the health status of the service and its dependencies.
    
    Returns:
        Health status including connectivity to Qdrant, PostgreSQL, and OpenAI
    """
    # Test PostgreSQL connection
    postgres_connected = False
    try:
        db.execute("SELECT 1")
        postgres_connected = True
    except Exception:
        pass
    
    # Test Qdrant connection
    qdrant_connected = await test_qdrant_connection()
    
    # Test OpenAI connection
    openai_available = await test_openai_connection()
    
    # Determine overall status
    status = "healthy" if (postgres_connected and qdrant_connected and openai_available) else "degraded"
    
    return HealthCheckResponse(
        status=status,
        qdrant_connected=qdrant_connected,
        postgres_connected=postgres_connected,
        openai_api_available=openai_available,
        version=__version__
    )



