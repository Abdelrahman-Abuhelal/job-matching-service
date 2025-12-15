"""AI-powered insights generator using Gemini."""

from typing import Dict, Any, Optional
import structlog

from app.core.gemini_client import generate_student_insights, generate_job_insights

logger = structlog.get_logger()


async def generate_ai_student_insights(
    job_data: Dict[str, Any],
    student_data: Dict[str, Any],
    similarity_score: float
) -> Optional[Dict[str, Any]]:
    """
    Generate AI-powered insights for student-job match using Gemini.
    
    Args:
        job_data: Job structured data
        student_data: Student profile data
        similarity_score: Vector similarity score (0-1)
        
    Returns:
        AI-generated match insights with detailed explanations
    """
    return await generate_student_insights(job_data, student_data, similarity_score)


async def generate_ai_job_insights(
    student_data: Dict[str, Any],
    job_data: Dict[str, Any],
    similarity_score: float
) -> Optional[Dict[str, Any]]:
    """
    Generate AI-powered insights for job match (for student searching jobs).
    
    Args:
        student_data: Student profile data
        job_data: Job structured data
        similarity_score: Vector similarity score (0-1)
        
    Returns:
        AI-generated match insights
    """
    return await generate_job_insights(student_data, job_data, similarity_score)
