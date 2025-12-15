"""Embedding service for managing student and job vectors."""

import uuid
from typing import Dict, Any
from sqlalchemy.orm import Session
import structlog

from app.core.embeddings import generate_student_embedding, create_student_embedding_text
from app.core.qdrant_client import upsert_vector, create_collection
from app.models.database import StudentProfile
from app.core.exceptions import (
    BusinessLogicException,
    ErrorCode,
    AIException,
    QdrantException
)

logger = structlog.get_logger()


async def create_or_update_student_embedding(
    db: Session,
    external_student_id: str,
    profile_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create or update student profile embedding.
    
    Args:
        db: Database session
        external_student_id: Student ID from IPSI system
        profile_data: Student profile data (skills, education, preferences)
        
    Returns:
        Dictionary with student_id, profile_summary, embedding_created, qdrant_point_id
        
    Raises:
        BusinessLogicException: If student profile processing fails
        OpenAIException: If OpenAI API fails
        QdrantException: If Qdrant operations fail
    """
    logger.info("embedding_service.create_or_update.start", 
               student_id=external_student_id,
               skills_count=len(profile_data.get("skills", [])))
    
    try:
        # Check if student already exists
        student = db.query(StudentProfile).filter(
            StudentProfile.external_student_id == external_student_id
        ).first()
        
        is_update = student is not None
        logger.info("embedding_service.student_check", 
                   student_id=external_student_id, is_update=is_update)
        
        # Generate embedding
        logger.info("embedding_service.generating_embedding", 
                   student_id=external_student_id)
        embedding = await generate_student_embedding(profile_data)
        
        # Create profile summary text
        profile_summary = await create_student_embedding_text(profile_data)
        
        # Generate or reuse point ID
        if student:
            qdrant_point_id = student.qdrant_point_id
            # Update existing student
            student.profile_summary = profile_summary
            student.structured_data = profile_data
        else:
            qdrant_point_id = uuid.uuid4()
            # Create new student
            student = StudentProfile(
                external_student_id=external_student_id,
                profile_summary=profile_summary,
                structured_data=profile_data,
                qdrant_point_id=qdrant_point_id
            )
            db.add(student)
        
        db.commit()
        db.refresh(student)
        
        # Ensure global students collection exists
        await create_collection("students_global")
        
        # Store in single global students collection (NO REPLICATION!)
        logger.info("embedding_service.upserting_to_global_collection", 
                   student_id=external_student_id, 
                   collection="students_global")
        
        payload = {
            "type": "student",
            "external_id": external_student_id,
            "metadata": {
                "skills": profile_data.get("skills", []),
                "education_level": profile_data.get("education", {}).get("level", ""),
                "field": profile_data.get("education", {}).get("field", ""),
                "university": profile_data.get("education", {}).get("university", ""),
                "locations": profile_data.get("preferences", {}).get("locations", []),
                "job_types": profile_data.get("preferences", {}).get("job_types", []),
                "industries": profile_data.get("preferences", {}).get("industries", [])
            }
        }
        
        # Single upsert to global collection (efficient!)
        await upsert_vector(
            collection_name="students_global",
            point_id=str(qdrant_point_id),
            vector=embedding,
            payload=payload
        )
        
        logger.info("embedding_service.create_or_update.success", 
                   student_id=external_student_id, 
                   db_id=student.id,
                   is_update=is_update,
                   collection="students_global")
        
        return {
            "student_id": student.id,
            "profile_summary": profile_summary,
            "embedding_created": True,
            "qdrant_point_id": qdrant_point_id
        }
        
    except (AIException, QdrantException) as e:
        logger.error("embedding_service.external_service_error", 
                    student_id=external_student_id, error=str(e))
        db.rollback()
        raise
        
    except Exception as e:
        logger.error("embedding_service.unexpected_error", 
                    student_id=external_student_id, error=str(e))
        db.rollback()
        raise BusinessLogicException(
            ErrorCode.EMBEDDING_GENERATION_FAILED,
            f"Failed to create/update student embedding: {external_student_id}",
            details={"student_id": external_student_id, "error": str(e)}
        ) from e



