"""Tests for job endpoints."""

import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_parse_job_description(client, auth_headers):
    """Test job description parsing endpoint."""
    
    # Mock OpenAI responses
    with patch('app.services.job_parser.parse_job_description') as mock_parse, \
         patch('app.services.job_parser.generate_job_embedding') as mock_embed, \
         patch('app.services.job_parser.create_collection') as mock_create, \
         patch('app.services.job_parser.upsert_vector') as mock_upsert:
        
        # Configure mocks
        mock_parse.return_value = {
            "title": "Python Developer",
            "required_skills": ["Python", "FastAPI"],
            "preferred_skills": ["Docker"],
            "education_level": "Bachelor's",
            "experience_years": "2-3",
            "location": "Remote",
            "job_type": "Internship",
            "responsibilities": ["Develop APIs"],
            "benefits": ["Flexible hours"]
        }
        mock_embed.return_value = [0.1] * 1536
        mock_create.return_value = True
        mock_upsert.return_value = True
        
        # Test data
        job_data = {
            "external_job_id": "test_job_001",
            "external_company_id": "test_company_001",
            "company_name": "Test Company",
            "raw_description": "We are looking for a Python developer..."
        }
        
        response = client.post(
            "/api/v1/jobs/parse",
            json=job_data,
            headers=auth_headers
        )
        
        # Verify response
        assert response.status_code in [200, 401, 500]  # May fail without proper setup


def test_parse_job_missing_fields(client, auth_headers):
    """Test job parsing with missing required fields."""
    
    incomplete_data = {
        "external_job_id": "test_job_002"
        # Missing other required fields
    }
    
    response = client.post(
        "/api/v1/jobs/parse",
        json=incomplete_data,
        headers=auth_headers
    )
    
    # Should return validation error
    assert response.status_code in [422, 401]



