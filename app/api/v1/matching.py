"""Matching endpoints for finding students and jobs."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.schemas import (
    StudentsForJobRequest,
    StudentsForJobResponse,
    JobsForStudentRequest,
    JobsForStudentResponse
)
from app.dependencies import get_database, get_current_user
from app.services.matching_service import find_students_for_job, find_jobs_for_student

router = APIRouter()


@router.post("/matching/students-for-job", response_model=StudentsForJobResponse)
async def get_students_for_job(
    request: StudentsForJobRequest,
    db: Session = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """
    Find the best matching students for a job posting.
    
    This endpoint:
    1. Retrieves the job posting from the database
    2. Generates job embedding
    3. Searches for similar student vectors in Qdrant
    4. Applies filters (education level, location, etc.)
    5. Generates match insights (skill overlap, missing skills, etc.)
    6. Stores match history for analytics
    
    Args:
        request: Search request with job ID and filters
        db: Database session
        current_user: Authenticated user (typically HR)
        
    Returns:
        List of matching students with scores and insights
    """
    # Convert filters to dict if present
    filters_dict = None
    if request.filters:
        filters_dict = request.filters.model_dump(exclude_none=True)

    # Convert ranking weights to dict if present
    weights_dict = None
    if request.ranking_weights:
        weights_dict = request.ranking_weights.model_dump()

    result = await find_students_for_job(
        db=db,
        external_job_id=request.external_job_id,
        top_k=request.top_k,
        min_similarity_score=request.min_similarity_score,
        filters=filters_dict,
        ranking_weights=weights_dict
    )

    return StudentsForJobResponse(**result)


@router.post("/matching/jobs-for-student", response_model=JobsForStudentResponse)
async def get_jobs_for_student(
    request: JobsForStudentRequest,
    db: Session = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """
    Find the best matching jobs for a student.
    
    This endpoint:
    1. Retrieves the student profile from the database
    2. Generates student embedding
    3. Searches across company collections in Qdrant
    4. Optionally filters by specific companies
    5. Generates match insights (why recommended, development areas)
    6. Returns top matching jobs sorted by similarity
    
    Args:
        request: Search request with student ID and filters
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of matching jobs with scores and insights
    """
    # Convert ranking weights to dict if present
    weights_dict = None
    if request.ranking_weights:
        weights_dict = request.ranking_weights.model_dump()

    result = await find_jobs_for_student(
        db=db,
        external_student_id=request.external_student_id,
        company_ids=request.company_ids,
        top_k=request.top_k,
        min_similarity_score=request.min_similarity_score,
        ranking_weights=weights_dict
    )

    return JobsForStudentResponse(**result)



