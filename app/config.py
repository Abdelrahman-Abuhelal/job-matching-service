"""Application configuration using Pydantic settings."""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    DATABASE_URL: str = "sqlite:///./talentmatch.db"
    
    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: str = ""
    
    # Gemini AI
    GEMINI_API_KEY: str
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"
    GEMINI_CHAT_MODEL: str = "gemini-2.5-flash-lite"
    EMBEDDING_DIMENSIONS: int = 768  # Gemini text-embedding-004 dimensions
    
    # AI Insights Configuration
    AI_INSIGHTS_ENABLED: bool = True
    AI_INSIGHTS_TOP_N: int = 5  # Generate AI insights for top N matches
    
    # Security
    JWT_SECRET_KEY: str = "change-this-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8501"
    
    # Service
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    API_V1_PREFIX: str = "/api/v1"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string into list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
