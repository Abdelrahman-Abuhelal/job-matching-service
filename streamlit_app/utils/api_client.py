"""API client for TalentMatch AI backend."""

import httpx
import os
from typing import Dict, Any, Optional, List
import streamlit as st

# Default API base URL - check environment variable first (for Docker), then use localhost
DEFAULT_API_URL = os.getenv("API_URL", "http://localhost:8000/api/v1")


def get_api_url() -> str:
    """Get API URL from environment variable (Docker), session state, or default."""
    # Priority 1: Environment variable (for Docker - always use this if set)
    # This ensures Docker containers use the service name, not localhost
    env_url = os.getenv("API_URL")
    if env_url:
        return env_url
    
    # Priority 2: Session state (user override in UI - only when not in Docker)
    if "api_url" in st.session_state:
        return st.session_state.get("api_url")
    
    # Priority 3: Default (localhost for local development)
    return DEFAULT_API_URL


def get_token() -> Optional[str]:
    """Get JWT token from session state."""
    return st.session_state.get("jwt_token")


def get_headers() -> Dict[str, str]:
    """Build request headers with authentication."""
    headers = {"Content-Type": "application/json"}
    token = get_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


async def health_check() -> Dict[str, Any]:
    """Check API health status."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{get_api_url()}/health", timeout=10.0)
            return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}


async def parse_job(
    external_job_id: str,
    external_company_id: str,
    company_name: str,
    raw_description: str
) -> Dict[str, Any]:
    """Parse a job description."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{get_api_url()}/jobs/parse",
                headers=get_headers(),
                json={
                    "external_job_id": external_job_id,
                    "external_company_id": external_company_id,
                    "company_name": company_name,
                    "raw_description": raw_description
                },
                timeout=30.0
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


async def update_candidate(
    external_student_id: str,
    profile_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Create or update a candidate profile."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{get_api_url()}/students/update",
                headers=get_headers(),
                json={
                    "external_student_id": external_student_id,
                    "profile_data": profile_data
                },
                timeout=30.0
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            return {"success": False, "error": f"HTTP {e.response.status_code}: {e.response.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}


async def find_candidates_for_job(
    external_job_id: str,
    top_k: int = 10,
    min_score: float = 0.70,
    ranking_weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """Find matching candidates for a job."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            payload = {
                "external_job_id": external_job_id,
                "top_k": top_k,
                "min_similarity_score": min_score
            }
            if ranking_weights:
                payload["ranking_weights"] = ranking_weights
            
            api_url = get_api_url()
            headers = get_headers()
            
            # Check if token is missing
            if not headers.get("Authorization"):
                return {
                    "success": False,
                    "error": "JWT token required. Please add it in Dashboard > API Configuration"
                }
            
            response = await client.post(
                f"{api_url}/matching/students-for-job",
                headers=headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text[:200] if e.response.text else "No details"
            if e.response.status_code == 401:
                return {
                    "success": False,
                    "error": f"Authentication failed (401). Please check your JWT token in Dashboard settings. Details: {error_detail}"
                }
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {error_detail}"
            }
        except httpx.ConnectError as e:
            return {
                "success": False,
                "error": f"Connection failed. Check if API is running at {get_api_url()}. Error: {str(e)}"
            }
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request timed out after 60 seconds. The matching operation may be taking too long."
            }
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}


async def find_jobs_for_candidate(
    external_student_id: str,
    top_k: int = 5,
    min_score: float = 0.70,
    company_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Find matching jobs for a candidate."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            payload = {
                "external_student_id": external_student_id,
                "top_k": top_k,
                "min_similarity_score": min_score
            }
            if company_ids:
                payload["company_ids"] = company_ids
            
            api_url = get_api_url()
            headers = get_headers()
            
            # Check if token is missing
            if not headers.get("Authorization"):
                return {
                    "success": False,
                    "error": "JWT token required. Please add it in Dashboard > API Configuration"
                }
            
            response = await client.post(
                f"{api_url}/matching/jobs-for-student",
                headers=headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text[:200] if e.response.text else "No details"
            if e.response.status_code == 401:
                return {
                    "success": False,
                    "error": f"Authentication failed (401). Please check your JWT token in Dashboard settings. Details: {error_detail}"
                }
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {error_detail}"
            }
        except httpx.ConnectError as e:
            return {
                "success": False,
                "error": f"Connection failed. Check if API is running at {get_api_url()}. Error: {str(e)}"
            }
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request timed out after 60 seconds. The matching operation may be taking too long."
            }
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}


async def get_match_history(
    job_id: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """Get match history for past matching sessions."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            api_url = get_api_url()
            headers = get_headers()
            
            if not headers.get("Authorization"):
                return {
                    "success": False,
                    "error": "API token required. Configure it in Dashboard → API Configuration."
                }
            
            params = {"limit": limit}
            if job_id:
                params["job_id"] = job_id
            
            response = await client.get(
                f"{api_url}/matching/history",
                headers=headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except httpx.HTTPStatusError as e:
            error_detail = e.response.text[:200] if e.response.text else "No details"
            return {"success": False, "error": f"HTTP {e.response.status_code}: {error_detail}"}
        except httpx.ConnectError as e:
            return {"success": False, "error": f"Connection failed: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
