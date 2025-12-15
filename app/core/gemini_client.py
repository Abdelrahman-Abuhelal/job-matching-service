"""Gemini client for embeddings and chat completions."""

import json
import asyncio
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import structlog

from app.config import settings
from app.core.exceptions import AIException, ErrorCode

logger = structlog.get_logger()


class GeminiService:
    """Async Gemini service with connection management and retry logic."""
    
    def __init__(self):
        self._configured = False
        self._chat_model = None
        self._embedding_model = None
    
    def configure(self):
        """Configure Gemini API."""
        if not self._configured:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self._configured = True
    
    def get_chat_model(self):
        """Get Gemini chat model."""
        self.configure()
        if self._chat_model is None:
            self._chat_model = genai.GenerativeModel(settings.GEMINI_CHAT_MODEL)
        return self._chat_model
    
    def get_embedding_model(self) -> str:
        """Get embedding model name."""
        self.configure()
        return f"models/{settings.GEMINI_EMBEDDING_MODEL}"


# Global service instance
_gemini_service = GeminiService()


def get_gemini_service() -> GeminiService:
    """Get the global Gemini service instance."""
    return _gemini_service


@retry(
    retry=retry_if_exception_type((Exception,)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    before_sleep=before_sleep_log(logger, "WARNING")
)
async def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding vector for text using Gemini with retry logic.
    
    Args:
        text: Input text to embed
        
    Returns:
        Embedding vector (768 dimensions for text-embedding-004)
        
    Raises:
        AIException: If embedding generation fails after retries
    """
    try:
        service = get_gemini_service()
        service.configure()
        
        logger.info("gemini.embedding.request", text_length=len(text))
        
        # Run embedding generation in executor (sync API)
        loop = asyncio.get_event_loop()
        
        def _generate():
            result = genai.embed_content(
                model=service.get_embedding_model(),
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        
        embedding = await loop.run_in_executor(None, _generate)
        
        logger.info("gemini.embedding.success", dimensions=len(embedding))
        
        return embedding
        
    except Exception as e:
        logger.error("gemini.embedding.failed", error=str(e), text_length=len(text))
        raise AIException(
            message="Failed to generate embedding",
            details={"text_length": len(text), "error": str(e)}
        ) from e


@retry(
    retry=retry_if_exception_type((Exception,)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    before_sleep=before_sleep_log(logger, "WARNING")
)
async def parse_job_description(raw_description: str) -> Dict[str, Any]:
    """
    Parse job description into structured JSON using Gemini with retry logic.
    
    Args:
        raw_description: Raw job description text
        
    Returns:
        Structured job data as dictionary
        
    Raises:
        AIException: If job parsing fails after retries
    """
    prompt = f"""Parse the following job description into structured JSON:

Job Description:
{raw_description}

Return ONLY valid JSON with this exact structure (no additional text, no markdown):
{{
    "title": "string",
    "required_skills": ["skill1", "skill2"],
    "preferred_skills": ["skill1"],
    "education_level": "string",
    "experience_years": "string",
    "location": "string",
    "job_type": "Internship|Full-time|Part-time|Working Student",
    "responsibilities": ["resp1", "resp2"],
    "benefits": ["benefit1"]
}}

Important: Return ONLY the JSON object, no markdown code blocks or additional text."""
    
    try:
        service = get_gemini_service()
        model = service.get_chat_model()
        
        logger.info("gemini.job_parsing.request", description_length=len(raw_description))
        
        # Run in executor (sync API)
        loop = asyncio.get_event_loop()
        
        def _generate():
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )
            return response.text
        
        content = await loop.run_in_executor(None, _generate)
        
        if not content:
            raise ValueError("Empty response from Gemini")
        
        # Clean up response if needed
        content = content.strip()
        if content.startswith("```"):
            # Remove markdown code blocks if present
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])
        
        structured_data = json.loads(content)
        logger.info("gemini.job_parsing.success", title=structured_data.get("title", "Unknown"))
        
        return structured_data
        
    except json.JSONDecodeError as e:
        logger.error("gemini.job_parsing.json_error", error=str(e))
        raise AIException(
            message="Failed to parse job description - invalid JSON response",
            details={"json_error": str(e), "description_length": len(raw_description)}
        ) from e
        
    except Exception as e:
        logger.error("gemini.job_parsing.failed", error=str(e), description_length=len(raw_description))
        raise AIException(
            message="Failed to parse job description",
            details={"description_length": len(raw_description), "error": str(e)}
        ) from e


@retry(
    retry=retry_if_exception_type((Exception,)),
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=2, max=6),
    before_sleep=before_sleep_log(logger, "WARNING")
)
async def generate_student_insights(
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
    try:
        service = get_gemini_service()
        model = service.get_chat_model()
        
        # Build comprehensive context
        student_skills = student_data.get("skills", [])
        student_edu = student_data.get("education", {})
        student_prefs = student_data.get("preferences", {})
        
        job_title = job_data.get("title", "")
        job_required = job_data.get("required_skills", [])
        job_preferred = job_data.get("preferred_skills", [])
        job_edu = job_data.get("education_level", "")
        job_location = job_data.get("location", "")
        job_type = job_data.get("job_type", "")
        
        prompt = f"""You are an expert HR consultant analyzing a candidate-job match.

CANDIDATE PROFILE:
• Skills: {', '.join(student_skills)}
• Education: {student_edu.get('level', '')} in {student_edu.get('field', '')} from {student_edu.get('university', '')}
• Location Preferences: {', '.join(student_prefs.get('locations', []))}
• Job Type Preferences: {', '.join(student_prefs.get('job_types', []))}
• Industry Interests: {', '.join(student_prefs.get('industries', []))}

JOB POSTING:
• Title: {job_title}
• Required Skills: {', '.join(job_required[:10])}
• Preferred Skills: {', '.join(job_preferred[:5])}
• Education Requirement: {job_edu}
• Location: {job_location}
• Type: {job_type}

VECTOR SIMILARITY SCORE: {similarity_score:.2%} (semantic match based on AI embeddings)

Provide a detailed match analysis in JSON format:
{{
    "match_quality": "Excellent|Strong|Good|Fair",
    "recommended_because": [
        "Primary reason 1 (be specific and detailed)",
        "Secondary reason 2",
        "Additional reason 3"
    ],
    "skill_analysis": {{
        "strong_matches": ["skill1", "skill2"],
        "transferable_skills": ["skill that applies even if not exact match"],
        "skill_gaps": ["skill1", "skill2"]
    }},
    "development_recommendations": [
        "Specific actionable recommendation 1",
        "Specific actionable recommendation 2"
    ],
    "cultural_fit_notes": "Brief note on location/type/preference alignment",
    "confidence_assessment": "Why this match score makes sense given the profiles"
}}

Return ONLY the JSON object, no markdown code blocks."""

        logger.info("gemini.insights.generating",
                   model=settings.GEMINI_CHAT_MODEL,
                   similarity_score=similarity_score)
        
        # Run in executor
        loop = asyncio.get_event_loop()
        
        def _generate():
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.3,
                    response_mime_type="application/json"
                )
            )
            return response.text
        
        content = await loop.run_in_executor(None, _generate)
        
        # Clean up response
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])
        
        ai_insights = json.loads(content)
        
        logger.info("gemini.insights.generated",
                   match_quality=ai_insights.get("match_quality", "Unknown"),
                   reasons_count=len(ai_insights.get("recommended_because", [])))
        
        return ai_insights
        
    except Exception as e:
        logger.error("gemini.insights.generation_failed",
                    error=str(e),
                    similarity_score=similarity_score)
        return None


@retry(
    retry=retry_if_exception_type((Exception,)),
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=2, max=6),
    before_sleep=before_sleep_log(logger, "WARNING")
)
async def generate_job_insights(
    student_data: Dict[str, Any],
    job_data: Dict[str, Any],
    similarity_score: float
) -> Optional[Dict[str, Any]]:
    """
    Generate AI-powered insights for job match (for candidate searching jobs).
    
    Args:
        student_data: Candidate profile data
        job_data: Job structured data
        similarity_score: Vector similarity score (0-1)
        
    Returns:
        AI-generated match insights
    """
    try:
        service = get_gemini_service()
        model = service.get_chat_model()
        
        student_skills = student_data.get("skills", [])
        student_edu = student_data.get("education", {})
        
        job_title = job_data.get("title", "")
        job_required = job_data.get("required_skills", [])
        job_preferred = job_data.get("preferred_skills", [])
        job_responsibilities = job_data.get("responsibilities", [])
        job_benefits = job_data.get("benefits", [])
        
        prompt = f"""You are a career advisor helping a candidate find the perfect job match.

CANDIDATE BACKGROUND:
• Skills: {', '.join(student_skills)}
• Education: {student_edu.get('level', '')} in {student_edu.get('field', '')}
• University: {student_edu.get('university', '')}

JOB OPPORTUNITY:
• Position: {job_title}
• Key Requirements: {', '.join(job_required[:10])}
• Preferred Qualifications: {', '.join(job_preferred[:5])}
• Responsibilities: {', '.join(job_responsibilities[:3])}
• Benefits: {', '.join(job_benefits[:3])}

AI MATCH SCORE: {similarity_score:.2%} (based on semantic similarity analysis)

Provide a personalized match analysis in JSON format:
{{
    "match_assessment": "Excellent Fit|Strong Fit|Good Fit|Potential Fit",
    "why_recommended": [
        "Compelling reason why this opportunity fits the candidate (be specific)",
        "Second strong reason highlighting alignment",
        "Third reason focusing on growth potential"
    ],
    "skill_strengths": [
        "Candidate's skill 1 that directly applies",
        "Candidate's skill 2 that gives them an advantage"
    ],
    "growth_opportunities": [
        "Specific skill they'll develop in this role",
        "Career growth opportunity this provides"
    ],
    "next_steps": "One-sentence actionable advice for applying",
    "match_score_explanation": "Brief explanation of why the {similarity_score:.0%} match score makes sense"
}}

Return ONLY the JSON object, no markdown code blocks."""

        logger.info("gemini.job_insights.generating",
                   model=settings.GEMINI_CHAT_MODEL,
                   job_title=job_title,
                   similarity_score=similarity_score)
        
        # Run in executor
        loop = asyncio.get_event_loop()
        
        def _generate():
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    temperature=0.4,
                    response_mime_type="application/json"
                )
            )
            return response.text
        
        content = await loop.run_in_executor(None, _generate)
        
        # Clean up response
        content = content.strip()
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])
        
        ai_insights = json.loads(content)
        
        logger.info("gemini.job_insights.generated",
                   assessment=ai_insights.get("match_assessment", "Unknown"))
        
        return ai_insights
        
    except Exception as e:
        logger.error("gemini.job_insights.generation_failed",
                    error=str(e),
                    similarity_score=similarity_score)
        return None


async def test_gemini_connection() -> bool:
    """
    Test if Gemini API is accessible.
    
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        service = get_gemini_service()
        service.configure()
        
        # Simple test embedding
        loop = asyncio.get_event_loop()
        
        def _test():
            result = genai.embed_content(
                model=service.get_embedding_model(),
                content="test",
                task_type="retrieval_document"
            )
            return len(result['embedding']) > 0
        
        success = await loop.run_in_executor(None, _test)
        return success
        
    except Exception as e:
        logger.warning("gemini.connection_test.failed", error=str(e))
        return False

