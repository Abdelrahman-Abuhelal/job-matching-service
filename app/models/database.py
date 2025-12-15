"""SQLAlchemy database models."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, Integer, ForeignKey, DateTime, Index, JSON
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class UUID(TypeDecorator):
    """Platform-independent UUID type.
    
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36).
    """
    impl = CHAR
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            else:
                return str(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if isinstance(value, uuid.UUID):
                return value
            else:
                return uuid.UUID(value)


class Company(Base):
    """Company table for storing company information."""
    
    __tablename__ = "companies"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    external_company_id = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    qdrant_collection_name = Column(String(255), nullable=False)  # Removed UNIQUE - multiple companies share global collections
    scoring_weights = Column(JSON)  # Company-specific scoring weights configuration
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job_postings = relationship("JobPosting", back_populates="company")
    applications = relationship("Application", back_populates="company")


class JobPosting(Base):
    """Job posting table for storing job information and metadata."""
    
    __tablename__ = "job_postings"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    external_job_id = Column(String(255), unique=True, nullable=False, index=True)
    company_id = Column(UUID, ForeignKey("companies.id"), nullable=False)
    title = Column(String(500), nullable=False)
    structured_data = Column(JSON, nullable=False)
    raw_description = Column(Text)
    qdrant_point_id = Column(UUID, nullable=False)
    embedding_version = Column(String(50), default="text-embedding-3-large")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship("Company", back_populates="job_postings")
    match_history = relationship("MatchHistory", back_populates="job_posting")
    applications = relationship("Application", back_populates="job_posting")
    
    # Indexes
    __table_args__ = (
        Index("idx_job_company", "company_id"),
        Index("idx_job_external", "external_job_id"),
    )


class StudentProfile(Base):
    """Student profile table for storing student information and embeddings."""
    
    __tablename__ = "student_profiles"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    external_student_id = Column(String(255), unique=True, nullable=False, index=True)
    profile_summary = Column(Text, nullable=False)
    structured_data = Column(JSON)
    qdrant_point_id = Column(UUID, nullable=False)
    embedding_version = Column(String(50), default="text-embedding-3-large")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    match_history = relationship("MatchHistory", back_populates="student_profile")
    applications = relationship("Application", back_populates="student_profile")
    
    # Indexes
    __table_args__ = (
        Index("idx_student_external", "external_student_id"),
    )


class Application(Base):
    """Track which students have applied to which companies/jobs."""
    
    __tablename__ = "applications"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    student_profile_id = Column(UUID, ForeignKey("student_profiles.id"), nullable=False)
    company_id = Column(UUID, ForeignKey("companies.id"), nullable=False)
    job_posting_id = Column(UUID, ForeignKey("job_postings.id"), nullable=True)  # Optional: specific job
    status = Column(String(50), default="applied")  # applied, reviewed, interviewed, rejected, accepted
    application_date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    student_profile = relationship("StudentProfile", back_populates="applications")
    company = relationship("Company", back_populates="applications")
    job_posting = relationship("JobPosting", back_populates="applications")
    
    # Indexes
    __table_args__ = (
        Index("idx_app_student", "student_profile_id"),
        Index("idx_app_company", "company_id"),
        Index("idx_app_job", "job_posting_id"),
        Index("idx_app_date", "application_date"),
    )


class MatchHistory(Base):
    """Match history table for storing matching results and analytics."""
    
    __tablename__ = "match_history"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    job_posting_id = Column(UUID, ForeignKey("job_postings.id"), nullable=False)
    student_profile_id = Column(UUID, ForeignKey("student_profiles.id"), nullable=False)
    similarity_score = Column(Float, nullable=False)
    rank_position = Column(Integer)
    match_explanation = Column(JSON)
    requested_by = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    job_posting = relationship("JobPosting", back_populates="match_history")
    student_profile = relationship("StudentProfile", back_populates="match_history")
    
    # Indexes
    __table_args__ = (
        Index("idx_match_job", "job_posting_id"),
        Index("idx_match_student", "student_profile_id"),
        Index("idx_match_created", "created_at"),
    )



