"""Tests for security and authentication."""

import pytest
from app.core.security import create_access_token, decode_token
from datetime import timedelta


def test_create_and_decode_token():
    """Test JWT token creation and decoding."""
    
    user_data = {"sub": "test_user", "role": "admin"}
    token = create_access_token(data=user_data)
    
    assert token is not None
    assert isinstance(token, str)
    
    # Decode token
    decoded = decode_token(token)
    assert decoded["sub"] == "test_user"
    assert decoded["role"] == "admin"


def test_token_with_expiration():
    """Test token with custom expiration."""
    
    user_data = {"sub": "test_user"}
    token = create_access_token(
        data=user_data,
        expires_delta=timedelta(minutes=30)
    )
    
    assert token is not None
    decoded = decode_token(token)
    assert "exp" in decoded


def test_invalid_token():
    """Test decoding invalid token."""
    
    from fastapi import HTTPException
    
    invalid_token = "invalid.token.here"
    
    with pytest.raises(HTTPException) as exc_info:
        decode_token(invalid_token)
    
    assert exc_info.value.status_code == 401


def test_endpoint_without_auth(client):
    """Test accessing protected endpoint without authentication."""
    
    job_data = {
        "external_job_id": "test_job",
        "external_company_id": "test_company",
        "company_name": "Test",
        "raw_description": "Test description"
    }
    
    response = client.post("/api/v1/jobs/parse", json=job_data)
    
    # Should return 401 Unauthorized
    assert response.status_code == 401



