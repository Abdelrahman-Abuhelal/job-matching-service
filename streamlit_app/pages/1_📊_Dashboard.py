"""Dashboard page - System overview and health status."""

import streamlit as st
import asyncio
from utils.api_client import health_check

st.set_page_config(page_title="Dashboard - TalentMatch AI", page_icon="📊", layout="wide")

st.title("📊 Dashboard")
st.markdown("System overview and health monitoring")

# Health Status Section
st.markdown("### 🏥 System Health")

async def check_health():
    return await health_check()

# Run health check
try:
    health_data = asyncio.run(check_health())
    
    if health_data.get("status") == "healthy":
        st.success("✅ All systems operational")
    elif health_data.get("status") == "degraded":
        st.warning("⚠️ System running in degraded mode")
    else:
        st.error(f"❌ System error: {health_data.get('error', 'Unknown')}")
    
    # Health metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = "🟢" if health_data.get("postgres_connected", False) else "🔴"
        st.metric("Database", f"{status} {'Connected' if health_data.get('postgres_connected', False) else 'Disconnected'}")
    
    with col2:
        status = "🟢" if health_data.get("qdrant_connected", False) else "🔴"
        st.metric("Qdrant", f"{status} {'Connected' if health_data.get('qdrant_connected', False) else 'Disconnected'}")
    
    with col3:
        status = "🟢" if health_data.get("gemini_api_available", False) else "🔴"
        st.metric("Gemini AI", f"{status} {'Available' if health_data.get('gemini_api_available', False) else 'Unavailable'}")
    
    with col4:
        st.metric("Version", health_data.get("version", "Unknown"))

except Exception as e:
    st.error(f"Could not connect to API: {str(e)}")
    st.info("Make sure the FastAPI backend is running on http://localhost:8000")

st.markdown("---")

# System Statistics
st.markdown("### 📈 System Statistics")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1e3a5f, #2d5a87); padding: 1.5rem; border-radius: 12px; text-align: center;">
        <h2 style="color: #ff6b6b; margin: 0;">5</h2>
        <p style="color: #b0c4de; margin: 0.5rem 0 0 0;">Jobs in System</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1e3a5f, #2d5a87); padding: 1.5rem; border-radius: 12px; text-align: center;">
        <h2 style="color: #ff6b6b; margin: 0;">8</h2>
        <p style="color: #b0c4de; margin: 0.5rem 0 0 0;">Candidates</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1e3a5f, #2d5a87); padding: 1.5rem; border-radius: 12px; text-align: center;">
        <h2 style="color: #ff6b6b; margin: 0;">768</h2>
        <p style="color: #b0c4de; margin: 0.5rem 0 0 0;">Vector Dimensions</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Configuration
st.markdown("### ⚙️ Configuration")

with st.expander("API Configuration"):
    api_url = st.text_input(
        "API Base URL",
        value=st.session_state.get("api_url", "http://localhost:8000/api/v1"),
        help="The base URL of the TalentMatch AI backend"
    )
    
    jwt_token = st.text_input(
        "JWT Token",
        value=st.session_state.get("jwt_token", ""),
        type="password",
        help="JWT authentication token for API access"
    )
    
    if st.button("Save Configuration"):
        st.session_state["api_url"] = api_url
        st.session_state["jwt_token"] = jwt_token
        st.success("Configuration saved!")

# Technology Info
st.markdown("---")
st.markdown("### 🛠️ Technology Stack")

tech_col1, tech_col2 = st.columns(2)

with tech_col1:
    st.markdown("""
    **AI & ML:**
    - Google Gemini 2.5 Flash-Lite
    - text-embedding-004 (768 dimensions)
    - Semantic similarity matching
    
    **Backend:**
    - FastAPI (Python 3.11)
    - SQLAlchemy ORM
    - Pydantic validation
    """)

with tech_col2:
    st.markdown("""
    **Databases:**
    - SQLite (demo) / PostgreSQL (production)
    - Qdrant vector database
    
    **Frontend:**
    - Streamlit
    - Interactive visualizations
    """)

