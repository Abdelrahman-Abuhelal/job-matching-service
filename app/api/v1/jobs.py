"""Job endpoints for parsing and managing job postings."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.schemas import JobParseRequest, JobParseResponse
from app.dependencies import get_database, get_current_user
from app.services.job_parser import parse_and_store_job

router = APIRouter()


@router.post("/jobs/parse", response_model=JobParseResponse)
async def parse_job_description(
    request: JobParseRequest,
    db: Session = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """
    Parse a job description and store it in the database.
    
    This endpoint:
    1. Uses GPT-4 to parse the raw job description into structured JSON
    2. Generates an embedding vector for the job
    3. Stores the job in PostgreSQL and Qdrant
    4. Creates a company collection in Qdrant if it doesn't exist
    
    Args:
        request: Job parsing request containing job details
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Parsed job data with embedding confirmation
    """
    # Custom exceptions will be automatically handled by the global exception handler
    result = await parse_and_store_job(
        db=db,
        external_job_id=request.external_job_id,
        external_company_id=request.external_company_id,
        company_name=request.company_name,
        raw_description=request.raw_description
    )
    
    return JobParseResponse(**result)



