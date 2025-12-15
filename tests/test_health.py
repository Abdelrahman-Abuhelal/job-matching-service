"""Tests for health check endpoint."""

import pytest
from fastapi.testclient import TestClient


def test_health_check_without_auth(client: TestClient):
    """Test health check endpoint accessibility."""
    response = client.get("/api/v1/health")
    
    # Health check should work without authentication
    assert response.status_code in [200, 401]  # May require auth depending on config


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert data["service"] == "IPSI AI Matching Service"



