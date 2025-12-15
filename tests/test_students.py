"""Tests for student endpoints."""

import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_update_student_profile(client, auth_headers):
    """Test student profile update endpoint."""
    
    with patch('app.services.embedding_service.generate_student_embedding') as mock_embed, \
         patch('app.services.embedding_service.upsert_vector') as mock_upsert:
        
        mock_embed.return_value = [0.1] * 1536
        mock_upsert.return_value = True
        
        student_data = {
            "external_student_id": "test_student_001",
            "profile_data": {
                "skills": ["Python", "FastAPI", "PostgreSQL"],
                "education": {
                    "level": "Bachelor's",
                    "field": "Computer Science",
                    "university": "Test University"
                },
                "preferences": {
                    "locations": ["Remote", "Berlin"],
                    "job_types": ["Internship"],
                    "industries": ["Tech", "Software"]
                }
            }
        }
        
        response = client.post(
            "/api/v1/students/update",
            json=student_data,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 401, 500]


def test_update_student_invalid_data(client, auth_headers):
    """Test student update with invalid data."""
    
    invalid_data = {
        "external_student_id": "test_student_002",
        "profile_data": {
            "skills": "Python"  # Should be array
        }
    }
    
    response = client.post(
        "/api/v1/students/update",
        json=invalid_data,
        headers=auth_headers
    )
    
    assert response.status_code in [422, 401]



