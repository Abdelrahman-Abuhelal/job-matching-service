"""AI-powered insights generator using GPT-4.1."""

from typing import Dict, Any
import structlog

from app.core.openai_client import get_openai_service
from app.config import settings
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

logger = structlog.get_logger()


@retry(
    retry=retry_if_exception_type((Exception,)),
    stop=stop_after_attempt(2),  # Only 2 attempts for insights (not critical)
    wait=wait_exponential(multiplier=1, min=2, max=6),
    before_sleep=before_sleep_log(logger, "WARNING")
)
async def generate_ai_student_insights(
    job_data: Dict[str, Any],
    student_data: Dict[str, Any],
    similarity_score: float
) -> Dict[str, Any]:
    """
    Generate AI-powered insights for student-job match using GPT-4.1.
    
    Args:
        job_data: Job structured data
        student_data: Student profile data
        similarity_score: Vector similarity score (0-1)
        
    Returns:
        AI-generated match insights with detailed explanations
    """
    try:
        service = await get_openai_service()
        client = await service.get_client()
        
        # Build comprehensive context for GPT-4.1
        student_skills = student_data.get("skills", [])
        student_edu = student_data.get("education", {})
        student_prefs = student_data.get("preferences", {})
        
        job_title = job_data.get("title", "")
        job_required = job_data.get("required_skills", [])
        job_preferred = job_data.get("preferred_skills", [])
        job_edu = job_data.get("education_level", "")
        job_location = job_data.get("location", "")
        job_type = job_data.get("job_type", "")
        
        prompt = f"""You are an expert HR consultant analyzing a student-job match for an internship platform.

STUDENT PROFILE:
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

Be specific, actionable, and focus on why this is a good match. Highlight transferable skills and growth opportunities."""

        logger.info("ai_insights.generating",
                   model=settings.AI_INSIGHTS_MODEL,
                   similarity_score=similarity_score)
        
        response = await client.chat.completions.create(
            model=settings.AI_INSIGHTS_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert HR consultant specializing in student-internship matching. Provide detailed, actionable insights in valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        import json
        content = response.choices[0].message.content
        ai_insights = json.loads(content)
        
        logger.info("ai_insights.generated",
                   match_quality=ai_insights.get("match_quality", "Unknown"),
                   reasons_count=len(ai_insights.get("recommended_because", [])))
        
        return ai_insights
        
    except Exception as e:
        logger.error("ai_insights.generation_failed",
                    error=str(e),
                    similarity_score=similarity_score)
        # Return empty insights if AI fails (will be handled gracefully)
        return None


@retry(
    retry=retry_if_exception_type((Exception,)),
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=2, max=6),
    before_sleep=before_sleep_log(logger, "WARNING")
)
async def generate_ai_job_insights(
    student_data: Dict[str, Any],
    job_data: Dict[str, Any],
    similarity_score: float
) -> Dict[str, Any]:
    """
    Generate AI-powered insights for job match (for student searching jobs).
    
    Args:
        student_data: Student profile data
        job_data: Job structured data
        similarity_score: Vector similarity score (0-1)
        
    Returns:
        AI-generated match insights
    """
    try:
        service = await get_openai_service()
        client = await service.get_client()
        
        student_skills = student_data.get("skills", [])
        student_edu = student_data.get("education", {})
        
        job_title = job_data.get("title", "")
        job_required = job_data.get("required_skills", [])
        job_preferred = job_data.get("preferred_skills", [])
        job_responsibilities = job_data.get("responsibilities", [])
        job_benefits = job_data.get("benefits", [])
        
        prompt = f"""You are a career advisor helping a student find the perfect internship/job match.

STUDENT BACKGROUND:
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
        "Compelling reason why this opportunity fits the student (be specific)",
        "Second strong reason highlighting alignment",
        "Third reason focusing on growth potential"
    ],
    "skill_strengths": [
        "Student's skill 1 that directly applies",
        "Student's skill 2 that gives them an advantage"
    ],
    "growth_opportunities": [
        "Specific skill they'll develop in this role",
        "Career growth opportunity this provides"
    ],
    "next_steps": "One-sentence actionable advice for applying",
    "match_score_explanation": "Brief explanation of why the {similarity_score:.0%} match score makes sense"
}}

Be encouraging, specific, and help the student see why this is a good opportunity for their career growth."""

        logger.info("ai_insights.job_match.generating",
                   model=settings.AI_INSIGHTS_MODEL,
                   job_title=job_title,
                   similarity_score=similarity_score)
        
        response = await client.chat.completions.create(
            model=settings.AI_INSIGHTS_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a supportive career advisor helping students find their ideal opportunities. Provide personalized, encouraging insights in valid JSON format."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,  # Slightly higher for more personalized responses
            response_format={"type": "json_object"}
        )
        
        import json
        content = response.choices[0].message.content
        ai_insights = json.loads(content)
        
        logger.info("ai_insights.job_match.generated",
                   assessment=ai_insights.get("match_assessment", "Unknown"))
        
        return ai_insights
        
    except Exception as e:
        logger.error("ai_insights.job_match.generation_failed",
                    error=str(e),
                    similarity_score=similarity_score)
        return None

