"""TalentMatch AI - Streamlit Demo Application."""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="TalentMatch AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Main theme colors - Deep blue and coral accent */
    :root {
        --primary-color: #1e3a5f;
        --secondary-color: #ff6b6b;
        --background-dark: #0d1b2a;
        --text-light: #e0e0e0;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        font-family: 'Segoe UI', sans-serif;
    }
    
    .main-header p {
        color: #b0c4de;
        font-size: 1.1rem;
        margin-top: 0.5rem;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(145deg, #1e3a5f, #2d5a87);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        border-left: 4px solid #ff6b6b;
    }
    
    .metric-card h3 {
        color: #ff6b6b;
        font-size: 2rem;
        margin: 0;
    }
    
    .metric-card p {
        color: #b0c4de;
        margin: 0.5rem 0 0 0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #0d1b2a 0%, #1e3a5f 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.4);
    }
    
    /* Info boxes */
    .info-box {
        background: rgba(30, 58, 95, 0.5);
        border: 1px solid #2d5a87;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* Feature list */
    .feature-item {
        display: flex;
        align-items: center;
        padding: 0.75rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .feature-icon {
        font-size: 1.5rem;
        margin-right: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Main content
st.markdown("""
<div class="main-header">
    <h1>🎯 TalentMatch AI</h1>
    <p>AI-powered talent matching using Gemini 2.5 Flash-Lite and semantic search</p>
</div>
""", unsafe_allow_html=True)

# Welcome section
st.markdown("## Welcome to TalentMatch AI")

st.markdown("""
TalentMatch AI is a proof-of-concept demonstration of an intelligent talent matching system. 
It uses **Google Gemini AI** for natural language understanding and **Qdrant** vector database 
for semantic similarity search.
""")

# Features section
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🚀 Key Features")
    st.markdown("""
    - **Intelligent Job Parsing**: AI extracts structured data from job descriptions
    - **Semantic Matching**: Vector-based similarity for accurate matches
    - **AI Insights**: Detailed explanations for each match
    - **Customizable Ranking**: Adjust weights for skills, experience, etc.
    """)

with col2:
    st.markdown("### 🛠️ Technology Stack")
    st.markdown("""
    - **AI Engine**: Google Gemini 2.5 Flash-Lite
    - **Embeddings**: text-embedding-004 (768 dimensions)
    - **Vector DB**: Qdrant
    - **Backend**: FastAPI + Python
    - **Frontend**: Streamlit
    """)

# Navigation guide
st.markdown("---")
st.markdown("### 📍 Getting Started")

st.markdown("""
Use the sidebar to navigate between different sections:

1. **📊 Dashboard** - View system statistics and health status
2. **💼 Jobs** - Add and manage job postings
3. **👥 Candidates** - Add and manage candidate profiles
4. **🎯 Matching** - Run AI-powered matching and view results

Each section provides a complete workflow for demonstrating the matching capabilities.
""")

# Quick stats
st.markdown("---")
st.markdown("### 📈 Quick Stats")

# These would come from the API in a real implementation
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Jobs", value="5", delta="Demo data")
with col2:
    st.metric(label="Total Candidates", value="8", delta="Demo data")
with col3:
    st.metric(label="AI Model", value="Gemini 2.5")
with col4:
    st.metric(label="Vector Dim", value="768")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>TalentMatch AI - Proof of Concept Demo</p>
    <p style="font-size: 0.8rem;">Powered by Google Gemini AI and Qdrant Vector Database</p>
</div>
""", unsafe_allow_html=True)

