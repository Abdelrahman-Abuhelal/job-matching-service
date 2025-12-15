"""OpenAI client for embeddings and chat completions."""

import json
import asyncio
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from openai.types import CreateEmbeddingResponse
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import structlog

from app.config import settings
from app.core.exceptions import OpenAIException, ErrorCode

logger = structlog.get_logger()

class OpenAIService:
    """Async OpenAI service with connection management and retry logic."""
    
    def __init__(self):
        self._client: Optional[AsyncOpenAI] = None
    
    async def get_client(self) -> AsyncOpenAI:
        """Get or create async OpenAI client."""
        if self._client is None:
            # Simple initialization for compatibility
            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        return self._client
    
    async def close(self):
        """Close the OpenAI client."""
        if self._client:
            await self._client.close()
            self._client = None

# Global service instance
_openai_service = OpenAIService()

async def get_openai_service() -> OpenAIService:
    """Get the global OpenAI service instance."""
    return _openai_service


@retry(
    retry=retry_if_exception_type((Exception,)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    before_sleep=before_sleep_log(logger, "WARNING")
)
async def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding vector for text using OpenAI with retry logic.
    
    Args:
        text: Input text to embed
        
    Returns:
        Embedding vector (1536 dimensions for text-embedding-3-large)
        
    Raises:
        OpenAIException: If embedding generation fails after retries
    """
    try:
        service = await get_openai_service()
        client = await service.get_client()
        
        logger.info("openai.embedding.request", text_length=len(text))
        
        response = await client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=text,
            dimensions=1536  # Force 1536 dimensions for compatibility
        )
        
        embedding = response.data[0].embedding
        logger.info("openai.embedding.success", dimensions=len(embedding))
        
        return embedding
        
    except Exception as e:
        logger.error("openai.embedding.failed", error=str(e), text_length=len(text))
        raise OpenAIException(
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
    Parse job description into structured JSON using GPT-4 with retry logic.
    
    Args:
        raw_description: Raw job description text
        
    Returns:
        Structured job data as dictionary
        
    Raises:
        OpenAIException: If job parsing fails after retries
    """
    prompt = f"""
Parse the following job description into structured JSON:

Job Description:
{raw_description}

Return ONLY valid JSON with this exact structure (no additional text):
{{
    "title": "string",
    "required_skills": ["skill1", "skill2"],
    "preferred_skills": ["skill1"],
    "education_level": "string",
    "experience_years": "string",
    "location": "string",
    "job_type": "Internship|Full-time|Part-time",
    "responsibilities": ["resp1", "resp2"],
    "benefits": ["benefit1"]
}}
"""
    
    try:
        service = await get_openai_service()
        client = await service.get_client()
        
        logger.info("openai.job_parsing.request", description_length=len(raw_description))
        
        response = await client.chat.completions.create(
            model=settings.OPENAI_CHAT_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured data from job descriptions. Always return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        # Parse the JSON response
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty response from OpenAI")
            
        structured_data = json.loads(content)
        logger.info("openai.job_parsing.success", title=structured_data.get("title", "Unknown"))
        
        return structured_data
        
    except json.JSONDecodeError as e:
        logger.error("openai.job_parsing.json_error", error=str(e), content=content[:200])
        raise OpenAIException(
            message="Failed to parse job description - invalid JSON response",
            details={"json_error": str(e), "description_length": len(raw_description)}
        ) from e
        
    except Exception as e:
        logger.error("openai.job_parsing.failed", error=str(e), description_length=len(raw_description))
        raise OpenAIException(
            message="Failed to parse job description",
            details={"description_length": len(raw_description), "error": str(e)}
        ) from e


async def test_openai_connection() -> bool:
    """
    Test if OpenAI API is accessible.
    
    Returns:
        True if connection is successful, False otherwise
    """
    try:
        service = await get_openai_service()
        client = await service.get_client()
        
        # Simple test embedding with short text
        response = await client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input="test",
            dimensions=1536  # Force 1536 dimensions for compatibility
        )
        return len(response.data) > 0
    except Exception as e:
        logger.warning("openai.connection_test.failed", error=str(e))
        return False



