"""Student profile endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.schemas import StudentUpdateRequest, StudentUpdateResponse
from app.dependencies import get_database, get_current_user
from app.services.embedding_service import create_or_update_student_embedding

router = APIRouter()


@router.post("/students/update", response_model=StudentUpdateResponse)
async def update_student_profile(
    request: StudentUpdateRequest,
    db: Session = Depends(get_database),
    current_user: dict = Depends(get_current_user)
):
    """
    Create or update a student profile and generate embeddings.
    
    This endpoint:
    1. Creates or updates student profile in PostgreSQL
    2. Generates an embedding vector from student skills, education, and preferences
    3. Stores/updates the vector in all company collections in Qdrant
    4. Returns the student profile summary
    
    Args:
        request: Student update request with profile data
        db: Database session
        current_user: Authenticated user
        
    Returns:
        Student profile with embedding confirmation
    """
    # Convert Pydantic model to dict for processing
    profile_data = request.profile_data.model_dump()
    
    result = await create_or_update_student_embedding(
        db=db,
        external_student_id=request.external_student_id,
        profile_data=profile_data
    )
    
    return StudentUpdateResponse(**result)



