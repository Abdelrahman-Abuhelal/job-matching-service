"""Job parsing service using LLM."""

import uuid
from typing import Dict, Any
from sqlalchemy.orm import Session
import structlog

from app.core.openai_client import parse_job_description
from app.core.embeddings import generate_job_embedding
from app.core.qdrant_client import create_collection, upsert_vector
from app.models.database import Company, JobPosting
from app.models.schemas import StructuredJobData
from app.core.exceptions import (
    BusinessLogicException,
    ErrorCode,
    OpenAIException,
    QdrantException
)

logger = structlog.get_logger()


async def parse_and_store_job(
    db: Session,
    external_job_id: str,
    external_company_id: str,
    company_name: str,
    raw_description: str
) -> Dict[str, Any]:
    """
    Parse job description and store in database and Qdrant.
    
    Args:
        db: Database session
        external_job_id: Job ID from IPSI system
        external_company_id: Company ID from IPSI system
        company_name: Company name
        raw_description: Raw job description text
        
    Returns:
        Dictionary with job_id, structured_data, embedding_created, qdrant_point_id
        
    Raises:
        BusinessLogicException: If job parsing or storage fails
        OpenAIException: If OpenAI API fails
        QdrantException: If Qdrant operations fail
    """
    logger.info("job_parser.parse_and_store.start", 
               job_id=external_job_id, 
               company_id=external_company_id,
               description_length=len(raw_description))
    
    try:
        # Ensure global jobs collection exists
        await create_collection("jobs_global")
        
        # Get or create company
        company = db.query(Company).filter(
            Company.external_company_id == external_company_id
        ).first()
        
        if not company:
            logger.info("job_parser.creating_company", 
                       company_id=external_company_id, name=company_name)
            company = Company(
                external_company_id=external_company_id,
                name=company_name,
                qdrant_collection_name="jobs_global"  # All jobs in one collection
            )
            db.add(company)
            db.commit()
            db.refresh(company)
        
        # Parse job description using LLM
        logger.info("job_parser.parsing_description", job_id=external_job_id)
        structured_data = await parse_job_description(raw_description)
        
        # Generate embedding
        logger.info("job_parser.generating_embedding", job_id=external_job_id)
        embedding = await generate_job_embedding(structured_data)
        
        # Generate unique point ID for Qdrant
        qdrant_point_id = uuid.uuid4()
        
        # Store in Qdrant global jobs collection
        payload = {
            "type": "job",
            "external_id": external_job_id,
            "company_id": external_company_id,  # IMPORTANT: Track which company owns this job
            "company_name": company_name,
            "metadata": {
                "title": structured_data.get("title", ""),
                "skills": structured_data.get("required_skills", []) + structured_data.get("preferred_skills", []),
                "location": structured_data.get("location", ""),
                "education_level": structured_data.get("education_level", ""),
                "job_type": structured_data.get("job_type", "")
            }
        }
        
        logger.info("job_parser.storing_vector", 
                   job_id=external_job_id, 
                   collection="jobs_global",
                   company_id=external_company_id)
        await upsert_vector(
            collection_name="jobs_global",  # Single global collection for all jobs
            point_id=str(qdrant_point_id),
            vector=embedding,
            payload=payload
        )
        
        # Store in PostgreSQL
        job_posting = JobPosting(
            external_job_id=external_job_id,
            company_id=company.id,
            title=structured_data.get("title", ""),
            structured_data=structured_data,
            raw_description=raw_description,
            qdrant_point_id=qdrant_point_id
        )
        db.add(job_posting)
        db.commit()
        db.refresh(job_posting)
        
        logger.info("job_parser.parse_and_store.success", 
                   job_id=external_job_id, 
                   db_id=job_posting.id,
                   title=structured_data.get("title", "Unknown"))
        
        return {
            "job_id": job_posting.id,
            "structured_data": StructuredJobData(**structured_data),
            "embedding_created": True,
            "qdrant_point_id": qdrant_point_id
        }
        
    except (OpenAIException, QdrantException) as e:
        logger.error("job_parser.external_service_error", 
                    job_id=external_job_id, error=str(e))
        db.rollback()
        raise
        
    except Exception as e:
        logger.error("job_parser.unexpected_error", 
                    job_id=external_job_id, error=str(e))
        db.rollback()
        raise BusinessLogicException(
            ErrorCode.JOB_PARSING_FAILED,
            f"Failed to parse and store job: {external_job_id}",
            details={"job_id": external_job_id, "error": str(e)}
        ) from e



