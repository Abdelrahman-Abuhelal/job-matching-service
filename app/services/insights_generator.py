"""Service for generating AI-powered insights about matches."""

from typing import Dict, Any, List


def generate_detailed_insights(
    job_data: Dict[str, Any],
    student_data: Dict[str, Any],
    similarity_score: float
) -> Dict[str, Any]:
    """
    Generate detailed insights about a student-job match.
    
    Args:
        job_data: Job structured data
        student_data: Student profile data
        similarity_score: Vector similarity score
        
    Returns:
        Detailed insights dictionary
    """
    insights = {
        "overall_match": _calculate_overall_match(similarity_score),
        "skill_analysis": _analyze_skills(job_data, student_data),
        "education_analysis": _analyze_education(job_data, student_data),
        "location_analysis": _analyze_location(job_data, student_data),
        "experience_analysis": _analyze_experience(job_data, student_data),
        "recommendations": _generate_recommendations(job_data, student_data)
    }
    
    return insights


def _calculate_overall_match(score: float) -> str:
    """Calculate overall match quality."""
    if score >= 0.90:
        return "Excellent Match"
    elif score >= 0.80:
        return "Strong Match"
    elif score >= 0.70:
        return "Good Match"
    else:
        return "Moderate Match"


def _analyze_skills(job_data: Dict[str, Any], student_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze skill match between job and student."""
    student_skills = set([s.lower() for s in student_data.get("skills", [])])
    required_skills = set([s.lower() for s in job_data.get("required_skills", [])])
    preferred_skills = set([s.lower() for s in job_data.get("preferred_skills", [])])
    
    matched_required = student_skills & required_skills
    matched_preferred = student_skills & preferred_skills
    missing_required = required_skills - student_skills
    
    return {
        "matched_required_skills": list(matched_required),
        "matched_preferred_skills": list(matched_preferred),
        "missing_required_skills": list(missing_required),
        "skill_match_percentage": round(len(matched_required) / len(required_skills) * 100, 1) if required_skills else 0
    }


def _analyze_education(job_data: Dict[str, Any], student_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze education match."""
    job_edu = job_data.get("education_level", "")
    student_edu = student_data.get("education", {})
    
    return {
        "required": job_edu,
        "student_level": student_edu.get("level", ""),
        "student_field": student_edu.get("field", ""),
        "matches": job_edu.lower() in student_edu.get("level", "").lower()
    }


def _analyze_location(job_data: Dict[str, Any], student_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze location match."""
    job_location = job_data.get("location", "")
    preferred_locations = student_data.get("preferences", {}).get("locations", [])
    
    matches = job_location.lower() in [loc.lower() for loc in preferred_locations] or "remote" in job_location.lower()
    
    return {
        "job_location": job_location,
        "preferred_locations": preferred_locations,
        "matches": matches
    }


def _analyze_experience(job_data: Dict[str, Any], student_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze experience requirements."""
    required_experience = job_data.get("experience_years", "")
    
    return {
        "required": required_experience,
        "note": "Internship positions typically welcome fresh graduates"
    }


def _generate_recommendations(job_data: Dict[str, Any], student_data: Dict[str, Any]) -> List[str]:
    """Generate recommendations for improving the match."""
    recommendations = []
    
    student_skills = set([s.lower() for s in student_data.get("skills", [])])
    required_skills = set([s.lower() for s in job_data.get("required_skills", [])])
    
    missing = required_skills - student_skills
    if missing:
        for skill in list(missing)[:3]:
            recommendations.append(f"Consider learning {skill} to strengthen your application")
    
    return recommendations



