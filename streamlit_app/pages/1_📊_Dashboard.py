"""Dashboard page - System overview and configuration."""

import streamlit as st
import asyncio
import os
from utils.api_client import health_check

st.set_page_config(page_title="System Status — TalentMatch AI", page_icon="📊", layout="wide")

st.title("System Status")
st.markdown("Monitor system health and configure API settings.")

# Health Status Section
st.markdown("### Service Health")

async def check_health():
    return await health_check()

# Run health check
try:
    health_data = asyncio.run(check_health())
    
    if health_data.get("status") == "healthy":
        st.success("All services are operational.")
    elif health_data.get("status") == "degraded":
        st.warning("System is running in degraded mode. Some features may be unavailable.")
    else:
        st.error(f"System error: {health_data.get('error', 'Unknown')}")
    
    # Health metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        connected = health_data.get("postgres_connected", False)
        st.metric("Database", "Connected" if connected else "Disconnected")
    
    with col2:
        connected = health_data.get("qdrant_connected", False)
        st.metric("Vector Store", "Connected" if connected else "Disconnected")
    
    with col3:
        available = health_data.get("gemini_api_available", False)
        st.metric("AI Service", "Available" if available else "Unavailable")
    
    with col4:
        st.metric("Version", health_data.get("version", "Unknown"))

except Exception as e:
    error_msg = str(e)
    st.error(f"Could not connect to API: {error_msg}")
    
    if "Connection refused" in error_msg or "connect" in error_msg.lower():
        st.info("""
**Troubleshooting:**
1. Ensure the backend is running: `docker-compose up`
2. Check API logs: `docker-compose logs fastapi`
3. If running in Docker, API URL should be: `http://fastapi:8000/api/v1`
4. If running locally, use: `http://localhost:8000/api/v1`
        """)
    else:
        st.info("Check the API configuration below and ensure all services are running.")

st.markdown("---")

# Data Statistics
st.markdown("### Data Overview")

col1, col2, col3 = st.columns(3)

# Calculate counts including session-added items
sample_jobs = 5
sample_candidates = 8
session_jobs = len(st.session_state.get("jobs", []))
session_candidates = len(st.session_state.get("candidates", []))

with col1:
    st.metric("Job Postings", f"{sample_jobs + session_jobs}", 
              delta=f"+{session_jobs} this session" if session_jobs > 0 else None)

with col2:
    st.metric("Candidates", f"{sample_candidates + session_candidates}",
              delta=f"+{session_candidates} this session" if session_candidates > 0 else None)

with col3:
    st.metric("Embedding Dimensions", "768")

st.caption("Sample data (5 jobs, 8 candidates) is pre-loaded for testing.")

st.markdown("---")

# API Configuration
st.markdown("### API Configuration")

with st.expander("Connection Settings", expanded=True):
    env_api_url = os.getenv("API_URL")
    
    if env_api_url:
        st.info(f"**Running in Docker:** API URL is set to `{env_api_url}` from environment.")
        st.text_input(
            "API Base URL",
            value=env_api_url,
            disabled=True,
            help="This is configured automatically in Docker"
        )
        # Clear any cached localhost URL
        if "api_url" in st.session_state and "localhost" in st.session_state.get("api_url", ""):
            del st.session_state["api_url"]
    else:
        api_url = st.text_input(
            "API Base URL",
            value=st.session_state.get("api_url", "http://localhost:8000/api/v1"),
            help="The base URL of the TalentMatch AI backend"
        )
        if st.button("Save API URL"):
            st.session_state["api_url"] = api_url
            st.success("API URL saved.")
    
    st.markdown("---")
    
    jwt_token = st.text_input(
        "API Token",
        value=st.session_state.get("jwt_token", ""),
        type="password",
        help="JWT token for API authentication. Required for matching and data operations."
    )
    
    if st.button("Save Token", type="primary"):
        st.session_state["jwt_token"] = jwt_token
        st.success("Token saved. You can now use the Matching and data pages.")

st.markdown("---")

# Technology Stack
st.markdown("### Technology Stack")

tech_col1, tech_col2 = st.columns(2)

with tech_col1:
    st.markdown("""
**AI & Matching:**
- Google Gemini 2.5 Flash-Lite (parsing)
- text-embedding-004 (768 dimensions)
- Cosine similarity matching

**Backend:**
- FastAPI (Python 3.11)
- SQLAlchemy ORM
- Pydantic validation
    """)

with tech_col2:
    st.markdown("""
**Data Storage:**
- SQLite (demo) / PostgreSQL (production)
- Qdrant vector database

**Frontend:**
- Streamlit
    """)
