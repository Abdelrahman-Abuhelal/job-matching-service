"""Custom exceptions for the IPSI AI Matching Service."""

from enum import Enum
from typing import Dict, Any, Optional


class ErrorCode(str, Enum):
    """Error codes for API responses."""
    
    # General errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    
    # External service errors
    OPENAI_ERROR = "OPENAI_ERROR"
    OPENAI_RATE_LIMIT = "OPENAI_RATE_LIMIT"
    OPENAI_TIMEOUT = "OPENAI_TIMEOUT"
    
    QDRANT_ERROR = "QDRANT_ERROR"
    QDRANT_TIMEOUT = "QDRANT_TIMEOUT"
    QDRANT_CONNECTION_ERROR = "QDRANT_CONNECTION_ERROR"
    
    # Business logic errors
    JOB_NOT_FOUND = "JOB_NOT_FOUND"
    STUDENT_NOT_FOUND = "STUDENT_NOT_FOUND"
    COMPANY_NOT_FOUND = "COMPANY_NOT_FOUND"
    COLLECTION_NOT_FOUND = "COLLECTION_NOT_FOUND"
    
    # Processing errors
    EMBEDDING_GENERATION_FAILED = "EMBEDDING_GENERATION_FAILED"
    JOB_PARSING_FAILED = "JOB_PARSING_FAILED"
    MATCHING_FAILED = "MATCHING_FAILED"


class APIException(Exception):
    """Base exception for API errors."""
    
    def __init__(
        self,
        code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 500
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


class ValidationException(APIException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=ErrorCode.VALIDATION_ERROR,
            message=message,
            details=details,
            status_code=422
        )


class NotFoundException(APIException):
    """Exception for not found errors."""
    
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            code=ErrorCode.NOT_FOUND,
            message=f"{resource} not found",
            details={"resource": resource, "identifier": identifier},
            status_code=404
        )


class ExternalServiceException(APIException):
    """Exception for external service errors."""
    
    def __init__(
        self,
        service: str,
        code: ErrorCode,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details["service"] = service
        super().__init__(
            code=code,
            message=message,
            details=details,
            status_code=503  # Service Unavailable
        )


class OpenAIException(ExternalServiceException):
    """Exception for OpenAI API errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            service="openai",
            code=ErrorCode.OPENAI_ERROR,
            message=message,
            details=details
        )


class QdrantException(ExternalServiceException):
    """Exception for Qdrant errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            service="qdrant",
            code=ErrorCode.QDRANT_ERROR,
            message=message,
            details=details
        )


class BusinessLogicException(APIException):
    """Exception for business logic errors."""
    
    def __init__(self, code: ErrorCode, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=code,
            message=message,
            details=details,
            status_code=400
        )
