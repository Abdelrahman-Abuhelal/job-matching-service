"""Pydantic schemas for API request/response validation."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field, model_validator


# ============= Ranking Configuration =============

class RankingWeights(BaseModel):
    """
    Configurable weights for ranking customization.
    HR can adjust these sliders to control how matches are ranked.
    Weights are normalized server-side if they don't sum to 1.0.
    """

    similarity: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Weight for semantic similarity score (0-1)"
    )
    required_skills: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Weight for required skills coverage (0-1)"
    )
    preferred_skills: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
        description="Weight for preferred skills coverage (0-1)"
    )

    @model_validator(mode='after')
    def normalize_weights(self) -> 'RankingWeights':
        """Normalize weights to sum to 1.0 if they don't already."""
        total = self.similarity + self.required_skills + self.preferred_skills
        if total > 0 and abs(total - 1.0) > 0.001:
            self.similarity = self.similarity / total
            self.required_skills = self.required_skills / total
            self.preferred_skills = self.preferred_skills / total
        elif total == 0:
            # If all weights are 0, default to similarity only
            self.similarity = 1.0
            self.required_skills = 0.0
            self.preferred_skills = 0.0
        return self


class SkillsBreakdown(BaseModel):
    """
    Detailed breakdown of skill matching for transparency.
    Shows HR exactly which skills match and which are missing.
    """

    required_skills_matched: List[str] = Field(
        default_factory=list,
        description="Required skills the candidate has"
    )
    required_skills_missing: List[str] = Field(
        default_factory=list,
        description="Required skills the candidate is missing"
    )
    preferred_skills_matched: List[str] = Field(
        default_factory=list,
        description="Preferred skills the candidate has"
    )
    preferred_skills_missing: List[str] = Field(
        default_factory=list,
        description="Preferred skills the candidate is missing"
    )
    required_matched_count: int = Field(
        default=0,
        description="Number of required skills matched"
    )
    required_total_count: int = Field(
        default=0,
        description="Total number of required skills"
    )
    preferred_matched_count: int = Field(
        default=0,
        description="Number of preferred skills matched"
    )
    preferred_total_count: int = Field(
        default=0,
        description="Total number of preferred skills"
    )
    required_coverage: float = Field(
        default=0.0,
        description="Percentage of required skills matched (0-1)"
    )
    preferred_coverage: float = Field(
        default=0.0,
        description="Percentage of preferred skills matched (0-1)"
    )


# ============= Job Schemas =============

class JobParseRequest(BaseModel):
    """Request schema for parsing a job description."""

    external_job_id: str = Field(..., description="Job ID from IPSI")
    external_company_id: str = Field(..., description="Company ID from IPSI")
    company_name: str = Field(..., description="Company name")
    raw_description: str = Field(..., description="Raw job description")


class StructuredJobData(BaseModel):
    """Structured job data parsed from description."""

    title: str
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    education_level: str = ""
    experience_years: str = ""
    location: str = ""
    job_type: str = ""
    responsibilities: List[str] = []
    benefits: List[str] = []


class JobParseResponse(BaseModel):
    """Response schema for job parsing."""

    job_id: UUID
    structured_data: StructuredJobData
    embedding_created: bool
    qdrant_point_id: UUID


# ============= Student Schemas =============

class StudentEducation(BaseModel):
    """Student education information."""

    level: str
    field: str
    university: str
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None


class StudentProject(BaseModel):
    """Student project information."""

    title: str
    description: str
    technologies: List[str] = []
    duration_months: Optional[int] = None
    role: Optional[str] = None


class StudentExperience(BaseModel):
    """Student work experience."""

    title: str
    company: str
    duration_months: int
    description: str
    technologies: List[str] = []


class StudentPreferences(BaseModel):
    """Student job preferences."""

    locations: List[str] = []
    job_types: List[str] = []
    industries: List[str] = []
    min_salary: Optional[int] = None
    remote_preference: Optional[str] = None  # "required", "preferred", "no"


class StudentProfileData(BaseModel):
    """Student profile data."""

    skills: List[str]
    education: StudentEducation
    preferences: StudentPreferences
    experience_years: Optional[float] = 0.0
    experiences: List[StudentExperience] = []
    projects: List[StudentProject] = []
    certifications: List[str] = []
    languages: List[str] = []
    availability_date: Optional[str] = None


class StudentUpdateRequest(BaseModel):
    """Request schema for updating student profile."""

    external_student_id: str = Field(..., description="Student ID from IPSI")
    profile_data: StudentProfileData


class StudentUpdateResponse(BaseModel):
    """Response schema for student profile update."""

    student_id: UUID
    profile_summary: str
    embedding_created: bool
    qdrant_point_id: UUID


# ============= Matching Schemas =============

class MatchFilters(BaseModel):
    """Filters for matching queries."""

    education_level: Optional[List[str]] = None
    locations: Optional[List[str]] = None
    job_types: Optional[List[str]] = None


class StudentsForJobRequest(BaseModel):
    """Request schema for finding students for a job."""

    external_job_id: str
    top_k: int = Field(10, ge=1, le=50, description="Top matches count")
    min_similarity_score: float = Field(0.70, ge=0.0, le=1.0)
    filters: Optional[MatchFilters] = None
    ranking_weights: Optional[RankingWeights] = Field(
        default=None,
        description="Ranking weights for customizing match ordering"
    )


class MatchInsights(BaseModel):
    """Insights about a match - supports both AI and rule-based."""

    # AI-powered fields (when AI_INSIGHTS_ENABLED=true for top N matches)
    ai_powered: bool = False
    match_quality: Optional[str] = None
    recommended_because: List[str] = []
    skill_analysis: Optional[Dict[str, Any]] = None
    development_recommendations: List[str] = []
    cultural_fit: Optional[str] = None
    confidence_note: Optional[str] = None

    # Simple match note (for non-AI matches)
    note: Optional[str] = None

    # Skills breakdown for HR transparency (always populated)
    skills_breakdown: Optional[SkillsBreakdown] = None

    # Scoring breakdown for transparency
    final_score: Optional[float] = Field(
        default=None,
        description="Composite score used for ranking"
    )
    similarity_score_raw: Optional[float] = Field(
        default=None,
        description="Raw semantic similarity score from Qdrant"
    )
    required_skill_score: Optional[float] = Field(
        default=None,
        description="Required skills coverage score (0-1)"
    )
    preferred_skill_score: Optional[float] = Field(
        default=None,
        description="Preferred skills coverage score (0-1)"
    )

    # Human-friendly summary
    summary: Optional[str] = Field(
        default=None,
        description="Short human-readable summary of the match"
    )

    # Legacy fields (for backward compatibility)
    skill_overlap: List[str] = []
    missing_skills: List[str] = []
    education_match: Optional[bool] = None
    location_match: Optional[bool] = None

    class Config:
        extra = "allow"


class StudentMatch(BaseModel):
    """A single student match result."""

    student_id: UUID
    external_student_id: str
    similarity_score: float
    rank: int
    match_insights: MatchInsights


class StudentsForJobResponse(BaseModel):
    """Response schema for students-for-job matching."""

    job_id: UUID
    job_title: str
    matches: List[StudentMatch]
    total_candidates: int
    returned_count: int


class JobsForStudentRequest(BaseModel):
    """Request schema for finding jobs for a student."""

    external_student_id: str
    company_ids: Optional[List[str]] = None
    top_k: int = Field(5, ge=1, le=50, description="Top matches count")
    min_similarity_score: float = Field(0.70, ge=0.0, le=1.0)
    ranking_weights: Optional[RankingWeights] = Field(
        default=None,
        description="Ranking weights for customizing match ordering"
    )


class JobMatchInsights(BaseModel):
    """Insights about a job match for a student."""

    # AI-powered fields
    ai_powered: bool = False
    match_assessment: Optional[str] = None
    why_recommended: List[str] = []
    skill_strengths: List[str] = []
    growth_opportunities: List[str] = []
    next_steps: Optional[str] = None
    match_explanation: Optional[str] = None

    # Simple match note
    note: Optional[str] = None

    # Skills breakdown for transparency (always populated)
    skills_breakdown: Optional[SkillsBreakdown] = None

    # Scoring breakdown for transparency
    final_score: Optional[float] = Field(
        default=None,
        description="Composite score used for ranking"
    )
    similarity_score_raw: Optional[float] = Field(
        default=None,
        description="Raw semantic similarity score from Qdrant"
    )
    required_skill_score: Optional[float] = Field(
        default=None,
        description="Required skills coverage score (0-1)"
    )
    preferred_skill_score: Optional[float] = Field(
        default=None,
        description="Preferred skills coverage score (0-1)"
    )

    # Human-friendly summary
    summary: Optional[str] = Field(
        default=None,
        description="Short human-readable summary of the match"
    )

    # Legacy fields (for backward compatibility)
    recommended_because: List[str] = []
    development_areas: List[str] = []

    class Config:
        extra = "allow"


class JobMatch(BaseModel):
    """A single job match result."""

    job_id: UUID
    external_job_id: str
    job_title: str
    company_name: str
    similarity_score: float
    rank: int
    match_insights: JobMatchInsights


class JobsForStudentResponse(BaseModel):
    """Response schema for jobs-for-student matching."""

    student_id: UUID
    matches: List[JobMatch]


# ============= Health Check Schema =============

class HealthCheckResponse(BaseModel):
    """Health check response."""

    status: str
    qdrant_connected: bool
    postgres_connected: bool
    gemini_api_available: bool
    version: str
