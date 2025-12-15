"""FastAPI application entry point."""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from app.config import settings
from app.api.v1 import health, jobs, students, matching
from app.core.exceptions import APIException
from app.core.openai_client import get_openai_service
from app.core.qdrant_client import get_qdrant_service
from app import __version__

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()

class TimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware to add request timeouts."""
    
    async def dispatch(self, request: Request, call_next):
        try:
            return await asyncio.wait_for(
                call_next(request),
                timeout=60.0  # 60 second timeout
            )
        except asyncio.TimeoutError:
            logger.error("request.timeout", path=request.url.path)
            return JSONResponse(
                status_code=504,
                content={
                    "error": {
                        "code": "REQUEST_TIMEOUT",
                        "message": "Request timeout after 60 seconds"
                    }
                }
            )

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    # Startup
    logger.info("application.starting", version=__version__)
    yield
    # Shutdown
    logger.info("application.shutting_down")
    
    # Close connections
    openai_service = await get_openai_service()
    await openai_service.close()
    
    qdrant_service = get_qdrant_service()
    qdrant_service.close()
    
    logger.info("application.shutdown_complete")

# Create FastAPI application
app = FastAPI(
    title="IPSI AI Matching Service",
    description="AI-powered student-internship matching microservice for the IPSI platform",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Exception handlers
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    """Handle custom API exceptions."""
    logger.error("api.exception", 
                error_code=exc.code.value, 
                message=exc.message,
                path=request.url.path,
                details=exc.details)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code.value,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@app.exception_handler(Exception) 
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error("api.unexpected_exception", 
                error=str(exc), 
                path=request.url.path,
                exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        }
    )

# Add middleware
app.add_middleware(TimeoutMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=settings.API_V1_PREFIX, tags=["Health"])
app.include_router(jobs.router, prefix=settings.API_V1_PREFIX, tags=["Jobs"])
app.include_router(students.router, prefix=settings.API_V1_PREFIX, tags=["Students"])
app.include_router(matching.router, prefix=settings.API_V1_PREFIX, tags=["Matching"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "IPSI AI Matching Service",
        "version": __version__,
        "status": "running",
        "docs": "/docs"
    }



