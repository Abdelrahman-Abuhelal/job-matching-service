"""Matching endpoints for finding students and jobs."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.schemas import (
    StudentsForJobRequest,
    StudentsForJobResponse,
    JobsForStudentRequest,
    JobsForStudentResponse,
    MatchHistoryResponse,
    MatchHistorySession,
    MatchHistoryEntry
)
from app.models.database import MatchHistory, JobPosting, StudentProfile
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


@router.get("/matching/history", response_model=MatchHistoryResponse)
async def get_match_history(
    job_id: Optional[str] = Query(None, description="Filter by external job ID"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of sessions to return"),
    db: Session = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve match history for past matching sessions.
    
    Returns matching sessions grouped by job and timestamp, allowing HR to
    revisit and compare past matching results.
    
    Args:
        job_id: Optional filter by external job ID
        limit: Maximum sessions to return (default 20)
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List of matching sessions with their results
    """
    # Build base query - get distinct sessions by job and created_at
    query = db.query(
        MatchHistory.job_posting_id,
        MatchHistory.created_at,
        func.count(MatchHistory.id).label('match_count'),
        func.max(MatchHistory.similarity_score).label('top_score')
    ).group_by(
        MatchHistory.job_posting_id,
        func.date(MatchHistory.created_at),
        func.strftime('%H:%M', MatchHistory.created_at)  # Group by hour:minute for sessions
    ).order_by(
        MatchHistory.created_at.desc()
    )
    
    # Filter by job if specified
    if job_id:
        job = db.query(JobPosting).filter(
            JobPosting.external_job_id == job_id
        ).first()
        if job:
            query = query.filter(MatchHistory.job_posting_id == job.id)
    
    # Get sessions
    session_rows = query.limit(limit).all()
    
    sessions = []
    for row in session_rows:
        # Get job details
        job = db.query(JobPosting).filter(JobPosting.id == row.job_posting_id).first()
        if not job:
            continue
        
        # Get matches for this session (same job, same time window)
        matches_query = db.query(MatchHistory).filter(
            MatchHistory.job_posting_id == row.job_posting_id,
            func.date(MatchHistory.created_at) == func.date(row.created_at)
        ).order_by(MatchHistory.rank_position).limit(20)
        
        match_entries = []
        for match in matches_query.all():
            # Get student external ID
            student = db.query(StudentProfile).filter(
                StudentProfile.id == match.student_profile_id
            ).first()
            
            if student:
                match_entries.append(MatchHistoryEntry(
                    external_student_id=student.external_student_id,
                    similarity_score=match.similarity_score,
                    rank_position=match.rank_position or 0,
                    match_explanation=match.match_explanation,
                    created_at=match.created_at.isoformat()
                ))
        
        sessions.append(MatchHistorySession(
            session_id=f"{job.external_job_id}_{row.created_at.strftime('%Y%m%d_%H%M')}",
            job_id=job.id,
            external_job_id=job.external_job_id,
            job_title=job.title or job.external_job_id,
            created_at=row.created_at.isoformat(),
            candidates_matched=row.match_count,
            top_score=row.top_score or 0.0,
            matches=match_entries
        ))
    
    return MatchHistoryResponse(
        sessions=sessions,
        total_sessions=len(sessions)
    )


