"""Embedding generation utilities."""

from typing import List, Dict, Any
from app.core.openai_client import generate_embedding


async def create_job_embedding_text(structured_data: Dict[str, Any]) -> str:
    """
    Create text representation of job for embedding.
    
    Args:
        structured_data: Structured job data
        
    Returns:
        Combined text for embedding
    """
    parts = []
    
    # Title
    if "title" in structured_data:
        parts.append(f"Job Title: {structured_data['title']}")
    
    # Required skills
    if "required_skills" in structured_data and structured_data["required_skills"]:
        skills = ", ".join(structured_data["required_skills"])
        parts.append(f"Required Skills: {skills}")
    
    # Preferred skills
    if "preferred_skills" in structured_data and structured_data["preferred_skills"]:
        skills = ", ".join(structured_data["preferred_skills"])
        parts.append(f"Preferred Skills: {skills}")
    
    # Education
    if "education_level" in structured_data:
        parts.append(f"Education: {structured_data['education_level']}")
    
    # Experience
    if "experience_years" in structured_data:
        parts.append(f"Experience: {structured_data['experience_years']}")
    
    # Location
    if "location" in structured_data:
        parts.append(f"Location: {structured_data['location']}")
    
    # Job type
    if "job_type" in structured_data:
        parts.append(f"Type: {structured_data['job_type']}")
    
    # Responsibilities
    if "responsibilities" in structured_data and structured_data["responsibilities"]:
        resp = ". ".join(structured_data["responsibilities"])
        parts.append(f"Responsibilities: {resp}")
    
    return ". ".join(parts)


async def create_student_embedding_text(profile_data: Dict[str, Any]) -> str:
    """
    Create text representation of student profile for embedding.
    
    Args:
        profile_data: Student profile data
        
    Returns:
        Combined text for embedding
    """
    parts = []
    
    # Skills
    if "skills" in profile_data and profile_data["skills"]:
        skills = ", ".join(profile_data["skills"])
        parts.append(f"Skills: {skills}")
    
    # Education
    if "education" in profile_data:
        edu = profile_data["education"]
        edu_text = f"{edu.get('level', '')} in {edu.get('field', '')} from {edu.get('university', '')}"
        parts.append(f"Education: {edu_text}")
    
    # Preferences
    if "preferences" in profile_data:
        prefs = profile_data["preferences"]
        
        if prefs.get("locations"):
            locs = ", ".join(prefs["locations"])
            parts.append(f"Preferred Locations: {locs}")
        
        if prefs.get("job_types"):
            types = ", ".join(prefs["job_types"])
            parts.append(f"Preferred Job Types: {types}")
        
        if prefs.get("industries"):
            industries = ", ".join(prefs["industries"])
            parts.append(f"Interested in: {industries}")
    
    return ". ".join(parts)


async def generate_job_embedding(structured_data: Dict[str, Any]) -> List[float]:
    """
    Generate embedding for a job posting.
    
    Args:
        structured_data: Structured job data
        
    Returns:
        Embedding vector
    """
    text = await create_job_embedding_text(structured_data)
    return await generate_embedding(text)


async def generate_student_embedding(profile_data: Dict[str, Any]) -> List[float]:
    """
    Generate embedding for a student profile.
    
    Args:
        profile_data: Student profile data
        
    Returns:
        Embedding vector
    """
    text = await create_student_embedding_text(profile_data)
    return await generate_embedding(text)



