"""Candidates page - Add and manage candidate profiles."""

import streamlit as st
import asyncio
import uuid
from utils.api_client import update_candidate

st.set_page_config(page_title="Candidates - TalentMatch AI", page_icon="👥", layout="wide")

st.title("👥 Candidate Management")
st.markdown("Add and manage candidate profiles for matching")

# Initialize session state
if "candidates" not in st.session_state:
    st.session_state.candidates = []

# Tabs
tab1, tab2 = st.tabs(["➕ Add New Candidate", "📋 View Candidates"])

with tab1:
    st.markdown("### Add a New Candidate Profile")
    
    with st.form("add_candidate_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            candidate_id = st.text_input(
                "Candidate ID",
                value=f"candidate_{uuid.uuid4().hex[:8]}",
                help="Unique identifier for the candidate"
            )
            
            st.markdown("#### 🎓 Education")
            edu_level = st.selectbox(
                "Education Level",
                ["Bachelor's", "Master's", "PhD", "Associate's", "High School"]
            )
            
            edu_field = st.text_input(
                "Field of Study",
                placeholder="e.g., Computer Science"
            )
            
            university = st.text_input(
                "University/Institution",
                placeholder="e.g., MIT"
            )
        
        with col2:
            st.markdown("#### 💼 Skills")
            skills_input = st.text_area(
                "Technical Skills (comma-separated)",
                placeholder="Python, JavaScript, FastAPI, PostgreSQL, Docker",
                height=100
            )
            
            st.markdown("#### 📍 Preferences")
            locations = st.text_input(
                "Preferred Locations (comma-separated)",
                placeholder="Remote, New York, San Francisco"
            )
            
            job_types = st.multiselect(
                "Preferred Job Types",
                ["Full-time", "Part-time", "Internship", "Contract", "Working Student"],
                default=["Full-time"]
            )
            
            industries = st.text_input(
                "Interested Industries (comma-separated)",
                placeholder="Tech, Finance, Healthcare"
            )
        
        submitted = st.form_submit_button("💾 Save Candidate Profile", use_container_width=True)
        
        if submitted:
            if not skills_input:
                st.error("Please enter at least some skills")
            else:
                # Parse inputs
                skills = [s.strip() for s in skills_input.split(",") if s.strip()]
                location_list = [l.strip() for l in locations.split(",") if l.strip()] if locations else []
                industry_list = [i.strip() for i in industries.split(",") if i.strip()] if industries else []
                
                profile_data = {
                    "skills": skills,
                    "education": {
                        "level": edu_level,
                        "field": edu_field,
                        "university": university
                    },
                    "preferences": {
                        "locations": location_list,
                        "job_types": job_types,
                        "industries": industry_list
                    }
                }
                
                with st.spinner("💾 Saving candidate profile..."):
                    async def do_save():
                        return await update_candidate(candidate_id, profile_data)
                    
                    result = asyncio.run(do_save())
                    
                    if result["success"]:
                        st.success("✅ Candidate profile saved successfully!")
                        
                        # Store in session
                        st.session_state.candidates.append({
                            "candidate_id": candidate_id,
                            "profile_data": profile_data
                        })
                        
                        # Show summary
                        st.markdown("#### Profile Summary:")
                        st.markdown(f"**Skills:** {', '.join(skills[:8])}")
                        st.markdown(f"**Education:** {edu_level} in {edu_field}")
                        st.markdown(f"**Locations:** {', '.join(location_list) or 'Any'}")
                    else:
                        st.error(f"❌ Failed to save: {result['error']}")

with tab2:
    st.markdown("### Existing Candidates")
    
    # Demo candidates
    demo_candidates = [
        {
            "id": "candidate_001",
            "name": "Candidate A",
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "AWS"],
            "education": "Master's in Computer Science",
            "location": "Remote"
        },
        {
            "id": "candidate_002",
            "name": "Candidate B",
            "skills": ["Python", "Django", "React", "PostgreSQL"],
            "education": "Bachelor's in Software Engineering",
            "location": "Berlin"
        },
        {
            "id": "candidate_003",
            "name": "Candidate C",
            "skills": ["Java", "Spring Boot", "Kubernetes", "AWS"],
            "education": "Master's in Information Systems",
            "location": "London"
        },
        {
            "id": "candidate_004",
            "name": "Candidate D",
            "skills": ["Python", "TensorFlow", "PyTorch", "ML Ops", "Docker"],
            "education": "PhD in Machine Learning",
            "location": "San Francisco"
        },
        {
            "id": "candidate_005",
            "name": "Candidate E",
            "skills": ["JavaScript", "Node.js", "React", "MongoDB"],
            "education": "Bachelor's in Computer Science",
            "location": "New York"
        },
        {
            "id": "candidate_006",
            "name": "Candidate F",
            "skills": ["Python", "Spark", "Airflow", "AWS", "SQL"],
            "education": "Master's in Data Science",
            "location": "Remote"
        },
        {
            "id": "candidate_007",
            "name": "Candidate G",
            "skills": ["Go", "Kubernetes", "Terraform", "AWS", "CI/CD"],
            "education": "Bachelor's in Computer Engineering",
            "location": "Remote"
        },
        {
            "id": "candidate_008",
            "name": "Candidate H",
            "skills": ["Python", "FastAPI", "React", "PostgreSQL", "Redis"],
            "education": "Master's in Computer Science",
            "location": "Munich"
        }
    ]
    
    # Display as grid
    col1, col2 = st.columns(2)
    
    for i, candidate in enumerate(demo_candidates):
        with col1 if i % 2 == 0 else col2:
            with st.container():
                st.markdown(f"""
                <div style="background: linear-gradient(145deg, #1e3a5f, #2d5a87); padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
                    <h4 style="color: #ff6b6b; margin: 0;">{candidate['name']}</h4>
                    <p style="color: #b0c4de; margin: 0.25rem 0;">📍 {candidate['location']} | 🎓 {candidate['education']}</p>
                    <p style="color: white; margin: 0.5rem 0 0 0;">
                        <strong>Skills:</strong> {', '.join(candidate['skills'][:5])}
                    </p>
                    <p style="color: #666; font-size: 0.8rem; margin: 0.5rem 0 0 0;">ID: {candidate['id']}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Show newly added candidates
    if st.session_state.candidates:
        st.markdown("### Recently Added Candidates")
        for c in st.session_state.candidates:
            skills = c['profile_data'].get('skills', [])[:5]
            st.info(f"**{c['candidate_id']}** - Skills: {', '.join(skills)}")

