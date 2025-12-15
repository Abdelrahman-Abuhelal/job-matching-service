"""FastAPI dependencies for dependency injection."""

from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import verify_token


async def get_current_user(token_payload: dict = Depends(verify_token)) -> dict:
    """
    Get current authenticated user from token.
    
    Args:
        token_payload: Decoded JWT token payload
        
    Returns:
        User information from token
    """
    return token_payload


def get_database():
    """
    Get database session dependency.
    
    Yields:
        Database session
    """
    yield from get_db()



