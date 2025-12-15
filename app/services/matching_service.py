"""Matching service for finding students and jobs."""

from typing import List, Dict, Any, Optional, Set
from sqlalchemy.orm import Session
import structlog

from app.core.qdrant_client import search_vectors
from app.core.embeddings import (
    generate_job_embedding,
    generate_student_embedding
)
from app.models.database import JobPosting, StudentProfile, Company, MatchHistory
from app.services.ai_insights_generator import (
    generate_ai_student_insights,
    generate_ai_job_insights
)
from app.config import settings
from app.core.exceptions import (
    NotFoundException,
    BusinessLogicException,
    ErrorCode,
    QdrantException,
    AIException
)

logger = structlog.get_logger()

# Default ranking weights (if not provided in request)
DEFAULT_WEIGHTS = {
    "similarity": 0.6,
    "required_skills": 0.3,
    "preferred_skills": 0.1
}


def normalize_skill(skill: str) -> str:
    """Normalize a skill string for comparison."""
    return skill.lower().strip()


def is_valid_skill(skill: str) -> bool:
    """
    Check if a string is a valid skill (not a requirement sentence).
    Filters out long sentences and requirement-like phrases.
    """
    if len(skill) > 50:
        return False

    skip_prefixes = (
        "bachelor", "master", "phd", "currently", "experience with",
        "knowledge of", "understanding of", "strong", "excellent",
        "proficiency in", "familiarity", "ability to", "minimum",
        "years of", "degree in"
    )
    return not skill.lower().startswith(skip_prefixes)


def extract_skills_set(skills_list: List[str]) -> Set[str]:
    """Extract normalized skills from a list, filtering invalid entries."""
    return {
        normalize_skill(s) for s in skills_list
        if is_valid_skill(s)
    }


def compute_skills_breakdown(
    student_skills: List[str],
    required_skills: List[str],
    preferred_skills: List[str]
) -> Dict[str, Any]:
    """
    Compute detailed skills breakdown for a student vs job requirements.

    Returns a dictionary with:
    - Lists of matched/missing skills for both required and preferred
    - Counts for display
    - Coverage scores (0-1) for scoring
    """
    # Normalize all skills
    student_set = extract_skills_set(student_skills)
    required_set = extract_skills_set(required_skills)
    preferred_set = extract_skills_set(preferred_skills)

    # Compute overlaps
    required_matched = list(student_set & required_set)
    required_missing = list(required_set - student_set)
    preferred_matched = list(student_set & preferred_set)
    preferred_missing = list(preferred_set - student_set)

    # Compute coverage scores
    required_coverage = (
        len(required_matched) / len(required_set)
        if required_set else 0.0
    )
    preferred_coverage = (
        len(preferred_matched) / len(preferred_set)
        if preferred_set else 0.0
    )

    return {
        "required_skills_matched": required_matched,
        "required_skills_missing": required_missing,
        "preferred_skills_matched": preferred_matched,
        "preferred_skills_missing": preferred_missing,
        "required_matched_count": len(required_matched),
        "required_total_count": len(required_set),
        "preferred_matched_count": len(preferred_matched),
        "preferred_total_count": len(preferred_set),
        "required_coverage": required_coverage,
        "preferred_coverage": preferred_coverage
    }


def compute_final_score(
    similarity: float,
    required_coverage: float,
    preferred_coverage: float,
    weights: Dict[str, float]
) -> float:
    """
    Compute the final composite score using weighted combination.

    Args:
        similarity: Raw similarity score from Qdrant (0-1)
        required_coverage: Required skills coverage (0-1)
        preferred_coverage: Preferred skills coverage (0-1)
        weights: Dictionary with keys 'similarity', 'required_skills',
                 'preferred_skills'

    Returns:
        Weighted composite score (0-1)
    """
    return (
        weights.get("similarity", DEFAULT_WEIGHTS["similarity"]) * similarity +
        weights.get("required_skills", DEFAULT_WEIGHTS["required_skills"])
        * required_coverage +
        weights.get("preferred_skills", DEFAULT_WEIGHTS["preferred_skills"])
        * preferred_coverage
    )


def generate_match_summary(
    similarity: float,
    skills_breakdown: Dict[str, Any],
    final_score: float
) -> str:
    """
    Generate a human-friendly summary of the match.

    Args:
        similarity: Raw similarity score
        skills_breakdown: Skills analysis dictionary
        final_score: Computed final score

    Returns:
        Human-readable summary string
    """
    req_matched = skills_breakdown["required_matched_count"]
    req_total = skills_breakdown["required_total_count"]
    pref_matched = skills_breakdown["preferred_matched_count"]
    pref_total = skills_breakdown["preferred_total_count"]

    parts = []

    # Skills summary
    if req_total > 0:
        parts.append(f"{req_matched}/{req_total} required skills")
    if pref_total > 0:
        parts.append(f"{pref_matched}/{pref_total} preferred skills")

    # Semantic similarity note
    if similarity >= 0.85:
        parts.append("strong semantic alignment")
    elif similarity >= 0.75:
        parts.append("good semantic fit")

    if parts:
        return "Matched " + ", ".join(parts) + "."
    else:
        return f"Match score: {final_score:.0%}"


async def find_students_for_job(
    db: Session,
    external_job_id: str,
    top_k: int = 10,
    min_similarity_score: float = 0.70,
    filters: Optional[Dict[str, Any]] = None,
    ranking_weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Find matching students for a job with customizable ranking.

    Args:
        db: Database session
        external_job_id: Job ID from IPSI system
        top_k: Number of top matches to return
        min_similarity_score: Minimum similarity score for retrieval
        filters: Optional filters (education_level, locations, job_types)
        ranking_weights: Optional weights for ranking customization
            - similarity: weight for semantic similarity (default 0.6)
            - required_skills: weight for required skills coverage (default 0.3)
            - preferred_skills: weight for preferred skills coverage (default 0.1)

    Returns:
        Dictionary with job info and list of matching students
    """
    # Use defaults if no weights provided
    weights = ranking_weights or DEFAULT_WEIGHTS

    logger.info(
        "matching.students_for_job.start",
        job_id=external_job_id,
        top_k=top_k,
        min_score=min_similarity_score,
        has_filters=bool(filters),
        weights=weights
    )

    try:
        # Get job posting
        job = db.query(JobPosting).filter(
            JobPosting.external_job_id == external_job_id
        ).first()

        if not job:
            logger.warning("matching.job_not_found", job_id=external_job_id)
            raise NotFoundException("Job", external_job_id)

        # Get company for logging/context
        company = db.query(Company).filter(Company.id == job.company_id).first()
        if not company:
            logger.error(
                "matching.company_not_found",
                job_id=external_job_id,
                company_id=job.company_id
            )
            raise BusinessLogicException(
                ErrorCode.COMPANY_NOT_FOUND,
                f"Company not found for job: {external_job_id}"
            )

        # Extract job skills for scoring
        job_data = job.structured_data or {}
        job_required_skills = job_data.get("required_skills", [])
        job_preferred_skills = job_data.get("preferred_skills", [])

        # Generate job embedding for search
        logger.info("matching.generating_job_embedding", job_id=external_job_id)
        job_embedding = await generate_job_embedding(job.structured_data)

        # Build filter conditions for Qdrant global collection
        filter_conditions = {"type": "student"}
        if filters:
            if filters.get("education_level"):
                filter_conditions["metadata.education_level"] = (
                    filters["education_level"]
                )

        # Search in global students collection
        # Fetch more than top_k since we'll re-rank
        fetch_k = min(top_k * 3, 100)
        logger.info(
            "matching.searching_global_students",
            collection="students_global",
            company=company.external_company_id,
            requested_top_k=top_k,
            fetch_k=fetch_k
        )

        results = await search_vectors(
            collection_name="students_global",
            query_vector=job_embedding,
            top_k=fetch_k,
            score_threshold=min_similarity_score,
            filter_conditions=filter_conditions
        )

        # Get student profiles from database with single query
        external_student_ids = [r["payload"]["external_id"] for r in results]
        students_dict = {}

        if external_student_ids:
            students = db.query(StudentProfile).filter(
                StudentProfile.external_student_id.in_(external_student_ids)
            ).all()
            students_dict = {s.external_student_id: s for s in students}

        # Compute scores and build candidate list
        candidates = []
        for result in results:
            external_student_id = result["payload"]["external_id"]
            student = students_dict.get(external_student_id)

            if not student:
                continue

            student_data = student.structured_data or {}
            student_skills = student_data.get("skills", [])
            similarity = result["score"]

            # Compute skills breakdown
            skills_breakdown = compute_skills_breakdown(
                student_skills=student_skills,
                required_skills=job_required_skills,
                preferred_skills=job_preferred_skills
            )

            # Compute final score
            final_score = compute_final_score(
                similarity=similarity,
                required_coverage=skills_breakdown["required_coverage"],
                preferred_coverage=skills_breakdown["preferred_coverage"],
                weights=weights
            )

            # Generate human-friendly summary
            summary = generate_match_summary(
                similarity=similarity,
                skills_breakdown=skills_breakdown,
                final_score=final_score
            )

            candidates.append({
                "student": student,
                "external_student_id": external_student_id,
                "similarity": similarity,
                "final_score": final_score,
                "skills_breakdown": skills_breakdown,
                "summary": summary,
                "student_data": student_data
            })

        # Sort by final_score descending
        candidates.sort(key=lambda x: x["final_score"], reverse=True)

        # Take top_k after re-ranking
        top_candidates = candidates[:top_k]

        matches = []
        match_histories = []

        for i, candidate in enumerate(top_candidates):
            rank = i + 1
            student = candidate["student"]
            external_student_id = candidate["external_student_id"]
            similarity = candidate["similarity"]
            final_score = candidate["final_score"]
            skills_breakdown = candidate["skills_breakdown"]
            summary = candidate["summary"]
            student_data = candidate["student_data"]

            # Build base insights with skills breakdown
            insights = {
                "ai_powered": False,
                "skills_breakdown": skills_breakdown,
                "final_score": final_score,
                "similarity_score_raw": similarity,
                "required_skill_score": skills_breakdown["required_coverage"],
                "preferred_skill_score": skills_breakdown["preferred_coverage"],
                "summary": summary,
                # Legacy fields for backward compatibility
                "skill_overlap": (
                    skills_breakdown["required_skills_matched"][:10] +
                    skills_breakdown["preferred_skills_matched"][:5]
                ),
                "missing_skills": skills_breakdown["required_skills_missing"][:5]
            }

            # Generate AI insights for top N matches if enabled
            if settings.AI_INSIGHTS_ENABLED and rank <= settings.AI_INSIGHTS_TOP_N:
                logger.info(
                    "matching.generating_ai_insights",
                    student_id=external_student_id,
                    rank=rank,
                    score=similarity
                )

                ai_insights = await generate_ai_student_insights(
                    job.structured_data,
                    student_data,
                    similarity
                )

                if ai_insights:
                    insights["ai_powered"] = True
                    insights["match_quality"] = ai_insights.get(
                        "match_quality", "Good"
                    )
                    insights["recommended_because"] = ai_insights.get(
                        "recommended_because", []
                    )
                    insights["skill_analysis"] = ai_insights.get(
                        "skill_analysis", {}
                    )
                    insights["development_recommendations"] = ai_insights.get(
                        "development_recommendations", []
                    )
                    insights["cultural_fit"] = ai_insights.get(
                        "cultural_fit_notes", ""
                    )
                    insights["confidence_note"] = ai_insights.get(
                        "confidence_assessment", ""
                    )
                    logger.info(
                        "matching.ai_insights_success",
                        student_id=external_student_id,
                        quality=insights["match_quality"]
                    )

            if not insights.get("ai_powered"):
                insights["note"] = (
                    f"Match based on {similarity:.1%} semantic similarity"
                )

            matches.append({
                "student_id": student.id,
                "external_student_id": external_student_id,
                "similarity_score": similarity,
                "rank": rank,
                "match_insights": insights
            })

            # Prepare match history for batch insert
            match_history = MatchHistory(
                job_posting_id=job.id,
                student_profile_id=student.id,
                similarity_score=similarity,
                rank_position=rank,
                match_explanation=insights
            )
            match_histories.append(match_history)

        # Batch insert all match histories
        if match_histories:
            db.add_all(match_histories)

        db.commit()

        logger.info(
            "matching.students_for_job.success",
            job_id=external_job_id,
            matches_found=len(matches),
            total_candidates=len(results)
        )

        return {
            "job_id": job.id,
            "job_title": job.title,
            "matches": matches,
            "total_candidates": len(results),
            "returned_count": len(matches)
        }

    except (AIException, QdrantException) as e:
        logger.error(
            "matching.students_for_job.external_service_error",
            job_id=external_job_id,
            error=str(e)
        )
        db.rollback()
        raise

    except Exception as e:
        logger.error(
            "matching.students_for_job.unexpected_error",
            job_id=external_job_id,
            error=str(e)
        )
        db.rollback()
        raise BusinessLogicException(
            ErrorCode.MATCHING_FAILED,
            f"Failed to find students for job: {external_job_id}",
            details={"job_id": external_job_id, "error": str(e)}
        ) from e


async def find_jobs_for_student(
    db: Session,
    external_student_id: str,
    company_ids: Optional[List[str]] = None,
    top_k: int = 5,
    min_similarity_score: float = 0.70,
    ranking_weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Find matching jobs for a student with customizable ranking.

    Args:
        db: Database session
        external_student_id: Student ID from IPSI system
        company_ids: Optional list of company IDs to search
        top_k: Number of top matches to return
        min_similarity_score: Minimum similarity score
        ranking_weights: Optional weights for ranking customization

    Returns:
        Dictionary with student info and list of matching jobs
    """
    # Use defaults if no weights provided
    weights = ranking_weights or DEFAULT_WEIGHTS

    logger.info(
        "matching.jobs_for_student.start",
        student_id=external_student_id,
        top_k=top_k,
        min_score=min_similarity_score,
        company_count=len(company_ids) if company_ids else "all",
        weights=weights
    )

    try:
        # Get student profile
        student = db.query(StudentProfile).filter(
            StudentProfile.external_student_id == external_student_id
        ).first()

        if not student:
            logger.warning(
                "matching.student_not_found",
                student_id=external_student_id
            )
            raise NotFoundException("Student", external_student_id)

        # Extract student skills for scoring
        student_data = student.structured_data or {}
        student_skills = student_data.get("skills", [])

        # Generate student embedding for search
        logger.info(
            "matching.generating_student_embedding",
            student_id=external_student_id
        )
        student_embedding = await generate_student_embedding(student_data)

        # Build filter for global jobs collection
        filter_conditions = {"type": "job"}

        # Fetch more candidates for re-ranking
        fetch_k = min(top_k * 3, 100) if company_ids else min(top_k * 2, 50)

        logger.info(
            "matching.searching_global_jobs",
            collection="jobs_global",
            student_id=external_student_id,
            requested_top_k=top_k,
            fetch_k=fetch_k
        )

        results = await search_vectors(
            collection_name="jobs_global",
            query_vector=student_embedding,
            top_k=fetch_k,
            score_threshold=min_similarity_score,
            filter_conditions=filter_conditions
        )

        # Filter by company_ids if specified
        if company_ids:
            company_ids_lower = [cid.lower() for cid in company_ids]
            results = [
                r for r in results
                if r["payload"].get("company_id", "").lower() in company_ids_lower
            ]

        # Collect all external job IDs
        external_job_ids = [r["payload"]["external_id"] for r in results]

        # Build candidates with scores
        candidates = []
        if external_job_ids:
            jobs = db.query(JobPosting).filter(
                JobPosting.external_job_id.in_(external_job_ids)
            ).all()
            jobs_dict = {job.external_job_id: job for job in jobs}

            # Get company info for display
            company_ids_in_results = list(set([
                r["payload"].get("company_id") for r in results
            ]))
            companies = db.query(Company).filter(
                Company.external_company_id.in_(company_ids_in_results)
            ).all()
            companies_dict = {c.external_company_id: c for c in companies}

            for result in results:
                external_job_id = result["payload"]["external_id"]
                company_id_from_payload = result["payload"].get("company_id")
                job = jobs_dict.get(external_job_id)
                company = companies_dict.get(company_id_from_payload)

                if not job or not company:
                    continue

                job_data = job.structured_data or {}
                job_required_skills = job_data.get("required_skills", [])
                job_preferred_skills = job_data.get("preferred_skills", [])
                similarity = result["score"]

                # Compute skills breakdown
                skills_breakdown = compute_skills_breakdown(
                    student_skills=student_skills,
                    required_skills=job_required_skills,
                    preferred_skills=job_preferred_skills
                )

                # Compute final score
                final_score = compute_final_score(
                    similarity=similarity,
                    required_coverage=skills_breakdown["required_coverage"],
                    preferred_coverage=skills_breakdown["preferred_coverage"],
                    weights=weights
                )

                # Generate summary
                summary = generate_match_summary(
                    similarity=similarity,
                    skills_breakdown=skills_breakdown,
                    final_score=final_score
                )

                candidates.append({
                    "job": job,
                    "company": company,
                    "external_job_id": external_job_id,
                    "similarity": similarity,
                    "final_score": final_score,
                    "skills_breakdown": skills_breakdown,
                    "summary": summary,
                    "job_data": job_data
                })

        # Sort by final_score descending
        candidates.sort(key=lambda x: x["final_score"], reverse=True)

        # Take top_k after re-ranking
        top_candidates = candidates[:top_k]

        matches = []
        for i, candidate in enumerate(top_candidates):
            rank = i + 1
            job = candidate["job"]
            company = candidate["company"]
            similarity = candidate["similarity"]
            final_score = candidate["final_score"]
            skills_breakdown = candidate["skills_breakdown"]
            summary = candidate["summary"]
            job_data = candidate["job_data"]

            # Build base insights with skills breakdown
            insights = {
                "ai_powered": False,
                "skills_breakdown": skills_breakdown,
                "final_score": final_score,
                "similarity_score_raw": similarity,
                "required_skill_score": skills_breakdown["required_coverage"],
                "preferred_skill_score": skills_breakdown["preferred_coverage"],
                "summary": summary,
                # Legacy fields
                "skill_strengths": skills_breakdown["required_skills_matched"][:5],
                "growth_opportunities": (
                    skills_breakdown["required_skills_missing"][:3]
                )
            }

            # Generate AI insights for top matches if enabled
            if settings.AI_INSIGHTS_ENABLED and rank <= settings.AI_INSIGHTS_TOP_N:
                logger.info(
                    "matching.generating_ai_job_insights",
                    job_id=candidate["external_job_id"],
                    rank=rank,
                    score=similarity
                )

                ai_insights = await generate_ai_job_insights(
                    student_data,
                    job_data,
                    similarity
                )

                if ai_insights:
                    insights["ai_powered"] = True
                    insights["match_assessment"] = ai_insights.get(
                        "match_assessment", "Good Fit"
                    )
                    insights["why_recommended"] = ai_insights.get(
                        "why_recommended", []
                    )
                    insights["skill_strengths"] = ai_insights.get(
                        "skill_strengths", []
                    )
                    insights["growth_opportunities"] = ai_insights.get(
                        "growth_opportunities", []
                    )
                    insights["next_steps"] = ai_insights.get("next_steps", "")
                    insights["match_explanation"] = ai_insights.get(
                        "match_score_explanation", ""
                    )
                    logger.info(
                        "matching.ai_job_insights_success",
                        job_id=candidate["external_job_id"],
                        assessment=insights["match_assessment"]
                    )
                else:
                    insights["note"] = (
                        f"Match based on {similarity:.1%} semantic similarity"
                    )
            else:
                insights["note"] = (
                    f"Match based on {similarity:.1%} semantic similarity"
                )

            matches.append({
                "job_id": job.id,
                "external_job_id": candidate["external_job_id"],
                "job_title": job.title,
                "company_name": company.name,
                "similarity_score": similarity,
                "rank": rank,
                "match_insights": insights
            })

        logger.info(
            "matching.jobs_for_student.success",
            student_id=external_student_id,
            matches_found=len(matches),
            total_candidates=len(candidates)
        )

        return {
            "student_id": student.id,
            "matches": matches
        }

    except (AIException, QdrantException) as e:
        logger.error(
            "matching.jobs_for_student.external_service_error",
            student_id=external_student_id,
            error=str(e)
        )
        raise

    except Exception as e:
        logger.error(
            "matching.jobs_for_student.unexpected_error",
            student_id=external_student_id,
            error=str(e)
        )
        raise BusinessLogicException(
            ErrorCode.MATCHING_FAILED,
            f"Failed to find jobs for student: {external_student_id}",
            details={"student_id": external_student_id, "error": str(e)}
        ) from e


def generate_student_match_insights(
    job_data: Dict[str, Any],
    student_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate detailed insights about student-job match.

    Args:
        job_data: Job structured data
        student_data: Student profile data

    Returns:
        Match insights dictionary with skill analysis
    """
    student_skills = student_data.get("skills", [])
    required_skills = job_data.get("required_skills", [])
    preferred_skills = job_data.get("preferred_skills", [])

    # Use the new skills breakdown function
    breakdown = compute_skills_breakdown(
        student_skills=student_skills,
        required_skills=required_skills,
        preferred_skills=preferred_skills
    )

    # Check education match
    job_edu = job_data.get("education_level", "").lower()
    student_edu = student_data.get("education", {}).get("level", "").lower()
    education_match = (
        (job_edu and student_edu and
         (job_edu in student_edu or student_edu in job_edu)) or
        not job_edu or
        ("bachelor" in job_edu and "master" in student_edu) or
        ("bachelor" in job_edu and "phd" in student_edu) or
        ("master" in job_edu and "phd" in student_edu)
    )

    # Check location match
    job_location = job_data.get("location", "").lower()
    student_locations = [
        loc.lower()
        for loc in student_data.get("preferences", {}).get("locations", [])
    ]
    location_match = (
        any(loc in job_location for loc in student_locations) or
        "remote" in job_location or
        not student_locations
    )

    return {
        "skill_overlap": (
            breakdown["required_skills_matched"][:10] +
            breakdown["preferred_skills_matched"][:5]
        ),
        "missing_skills": breakdown["required_skills_missing"][:5],
        "education_match": education_match,
        "location_match": location_match
    }


def generate_job_match_insights(
    student_data: Dict[str, Any],
    job_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate detailed insights about job match for student.

    Args:
        student_data: Student profile data
        job_data: Job structured data

    Returns:
        Match insights dictionary with detailed recommendations
    """
    student_skills = student_data.get("skills", [])
    required_skills = job_data.get("required_skills", [])
    preferred_skills = job_data.get("preferred_skills", [])

    # Use the new skills breakdown function
    breakdown = compute_skills_breakdown(
        student_skills=student_skills,
        required_skills=required_skills,
        preferred_skills=preferred_skills
    )

    # Build recommendations
    reasons = []

    # Skill matches
    if breakdown["required_skills_matched"]:
        skill_list = ', '.join(breakdown["required_skills_matched"][:5])
        reasons.append(f"Strong skill match: {skill_list}")
    elif (breakdown["required_skills_matched"] or
          breakdown["preferred_skills_matched"]):
        all_matched = (
            breakdown["required_skills_matched"] +
            breakdown["preferred_skills_matched"]
        )
        skill_list = ', '.join(all_matched[:5])
        reasons.append(f"Relevant skills: {skill_list}")

    # Education match
    job_edu = job_data.get("education_level", "").lower()
    student_edu = student_data.get("education", {}).get("level", "").lower()
    student_field = student_data.get("education", {}).get("field", "")

    if job_edu and student_edu:
        if "bachelor" in job_edu and "bachelor" in student_edu:
            reasons.append(
                f"Education match: {student_field} degree aligns with requirements"
            )
        elif "master" in job_edu and "master" in student_edu:
            reasons.append(
                f"Advanced degree: {student_field} Master's meets requirements"
            )
        elif "phd" in job_edu and "phd" in student_edu:
            reasons.append(
                f"Doctoral level: {student_field} PhD matches requirements"
            )

    # Location match
    job_location = job_data.get("location", "").lower()
    student_locations = [
        loc.lower()
        for loc in student_data.get("preferences", {}).get("locations", [])
    ]

    if job_location and student_locations:
        if any(loc in job_location for loc in student_locations):
            matching_loc = next(
                (loc for loc in student_locations if loc in job_location),
                ""
            )
            reasons.append(f"Location preference matches: {matching_loc.title()}")
        elif "remote" in job_location:
            reasons.append("Remote work option available")

    # Job type preference
    job_type = job_data.get("job_type", "").lower()
    preferred_job_types = [
        jt.lower()
        for jt in student_data.get("preferences", {}).get("job_types", [])
    ]

    if job_type and any(jt in job_type for jt in preferred_job_types):
        reasons.append(f"Job type matches preference: {job_type.title()}")

    # Coverage percentage
    if breakdown["required_total_count"] > 0:
        coverage = breakdown["required_coverage"] * 100
        if coverage >= 50:
            reasons.append(f"{int(coverage)}% required skill coverage")

    if not reasons:
        reasons.append("Profile aligns with position requirements")

    # Development areas
    development_areas = []
    missing = breakdown["required_skills_missing"]

    if missing:
        learnable = [s for s in missing if len(s) < 30]
        for skill in learnable[:3]:
            development_areas.append(f"Consider learning {skill.title()}")

    # Experience recommendations
    experience = job_data.get("experience_years", "")
    if experience and "0" not in experience and "junior" not in experience.lower():
        development_areas.append(f"Gain experience: {experience} may be required")

    return {
        "recommended_because": reasons if reasons else ["General profile fit"],
        "development_areas": (
            development_areas if development_areas
            else ["Strong match - minimal gaps"]
        )
    }
