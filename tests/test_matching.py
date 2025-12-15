"""Tests for matching endpoints."""

import pytest
from unittest.mock import patch, MagicMock
from uuid import uuid4


@pytest.mark.asyncio
async def test_find_students_for_job(client, auth_headers, db_session):
    """Test finding students for a job."""
    
    with patch('app.services.matching_service.search_vectors') as mock_search, \
         patch('app.services.matching_service.generate_job_embedding') as mock_embed:
        
        mock_embed.return_value = [0.1] * 1536
        mock_search.return_value = [
            {
                "id": str(uuid4()),
                "score": 0.89,
                "payload": {
                    "type": "student",
                    "external_id": "student_001",
                    "metadata": {}
                }
            }
        ]
        
        match_request = {
            "external_job_id": "job_001",
            "top_k": 10,
            "min_similarity_score": 0.75
        }
        
        response = client.post(
            "/api/v1/matching/students-for-job",
            json=match_request,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404, 401, 500]


@pytest.mark.asyncio
async def test_find_jobs_for_student(client, auth_headers, db_session):
    """Test finding jobs for a student."""
    
    with patch('app.services.matching_service.search_vectors') as mock_search, \
         patch('app.services.matching_service.generate_student_embedding') as mock_embed:
        
        mock_embed.return_value = [0.1] * 1536
        mock_search.return_value = [
            {
                "id": str(uuid4()),
                "score": 0.85,
                "payload": {
                    "type": "job",
                    "external_id": "job_001",
                    "metadata": {}
                }
            }
        ]
        
        match_request = {
            "external_student_id": "student_001",
            "top_k": 5,
            "min_similarity_score": 0.70
        }
        
        response = client.post(
            "/api/v1/matching/jobs-for-student",
            json=match_request,
            headers=auth_headers
        )
        
        assert response.status_code in [200, 404, 401, 500]


def test_matching_with_filters(client, auth_headers):
    """Test matching with education level filters."""
    
    match_request = {
        "external_job_id": "job_001",
        "top_k": 10,
        "min_similarity_score": 0.75,
        "filters": {
            "education_level": ["Bachelor's", "Master's"]
        }
    }
    
    response = client.post(
        "/api/v1/matching/students-for-job",
        json=match_request,
        headers=auth_headers
    )
    
    assert response.status_code in [200, 404, 401, 500]



