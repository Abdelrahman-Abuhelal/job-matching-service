"""Jobs page - Add and manage job postings."""

import streamlit as st
import asyncio
import uuid
from utils.api_client import parse_job

st.set_page_config(page_title="Jobs - TalentMatch AI", page_icon="💼", layout="wide")

st.title("💼 Job Management")
st.markdown("Add and manage job postings with AI-powered parsing")

# Initialize session state for jobs
if "jobs" not in st.session_state:
    st.session_state.jobs = []

# Tabs for different actions
tab1, tab2 = st.tabs(["➕ Add New Job", "📋 View Jobs"])

with tab1:
    st.markdown("### Add a New Job Posting")
    st.markdown("Enter a job description and our AI will automatically extract structured data.")
    
    with st.form("add_job_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input(
                "Company Name",
                placeholder="e.g., TechCorp Inc."
            )
            
            job_id = st.text_input(
                "Job ID (Optional)",
                value=f"job_{uuid.uuid4().hex[:8]}",
                help="Unique identifier for the job"
            )
        
        with col2:
            company_id = st.text_input(
                "Company ID (Optional)",
                value=f"company_{uuid.uuid4().hex[:8]}",
                help="Unique identifier for the company"
            )
        
        raw_description = st.text_area(
            "Job Description",
            height=300,
            placeholder="""Paste your job description here. For example:

Senior Python Developer - Remote

We are looking for an experienced Python developer to join our backend team.

Requirements:
- 5+ years of Python experience
- Strong knowledge of FastAPI or Django
- Experience with PostgreSQL and Redis
- Familiarity with Docker and Kubernetes

Nice to have:
- Experience with machine learning
- Knowledge of cloud platforms (AWS/GCP)

Location: Remote (US timezone)
Salary: $120,000 - $160,000

Benefits:
- Health insurance
- 401(k) matching
- Unlimited PTO
""",
            help="Enter the full job description - AI will extract structured data"
        )
        
        submitted = st.form_submit_button("🚀 Parse & Save Job", use_container_width=True)
        
        if submitted:
            if not company_name or not raw_description:
                st.error("Please fill in company name and job description")
            else:
                with st.spinner("🤖 AI is parsing your job description..."):
                    async def do_parse():
                        return await parse_job(
                            job_id,
                            company_id,
                            company_name,
                            raw_description
                        )
                    
                    result = asyncio.run(do_parse())
                    
                    if result["success"]:
                        st.success("✅ Job parsed and saved successfully!")
                        
                        # Store in session state
                        st.session_state.jobs.append({
                            "job_id": job_id,
                            "company_id": company_id,
                            "company_name": company_name,
                            "data": result["data"]
                        })
                        
                        # Display parsed data
                        st.markdown("#### 📝 Extracted Data:")
                        
                        data = result["data"].get("structured_data", {})
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Title:** {data.get('title', 'N/A')}")
                            st.markdown(f"**Location:** {data.get('location', 'N/A')}")
                            st.markdown(f"**Job Type:** {data.get('job_type', 'N/A')}")
                            st.markdown(f"**Education:** {data.get('education_level', 'N/A')}")
                        
                        with col2:
                            st.markdown(f"**Experience:** {data.get('experience_years', 'N/A')}")
                        
                        st.markdown("**Required Skills:**")
                        skills = data.get("required_skills", [])
                        if skills:
                            st.markdown(" ".join([f"`{s}`" for s in skills[:10]]))
                        
                        st.markdown("**Preferred Skills:**")
                        pref_skills = data.get("preferred_skills", [])
                        if pref_skills:
                            st.markdown(" ".join([f"`{s}`" for s in pref_skills[:5]]))
                        
                    else:
                        st.error(f"❌ Failed to parse job: {result['error']}")

with tab2:
    st.markdown("### Existing Jobs")
    
    # Demo jobs
    demo_jobs = [
        {
            "job_id": "job_001",
            "company": "TechCorp",
            "title": "Senior Python Developer",
            "location": "Remote",
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"]
        },
        {
            "job_id": "job_002",
            "company": "DataFlow Inc",
            "title": "Data Engineer",
            "location": "Berlin, Germany",
            "skills": ["Python", "Spark", "AWS", "Airflow"]
        },
        {
            "job_id": "job_003",
            "company": "AI Solutions",
            "title": "Machine Learning Engineer",
            "location": "San Francisco, CA",
            "skills": ["Python", "TensorFlow", "PyTorch", "ML Ops"]
        },
        {
            "job_id": "job_004",
            "company": "CloudNative Co",
            "title": "DevOps Engineer",
            "location": "Remote",
            "skills": ["Kubernetes", "Terraform", "AWS", "CI/CD"]
        },
        {
            "job_id": "job_005",
            "company": "FinTech Pro",
            "title": "Backend Developer",
            "location": "London, UK",
            "skills": ["Java", "Spring Boot", "PostgreSQL", "Kafka"]
        }
    ]
    
    # Display as cards
    for job in demo_jobs:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"**{job['title']}**")
                st.markdown(f"🏢 {job['company']} | 📍 {job['location']}")
            
            with col2:
                st.markdown("**Skills:**")
                st.markdown(" ".join([f"`{s}`" for s in job['skills'][:4]]))
            
            with col3:
                st.markdown(f"ID: `{job['job_id']}`")
            
            st.markdown("---")
    
    # Show newly added jobs from session
    if st.session_state.jobs:
        st.markdown("### Recently Added Jobs")
        for job in st.session_state.jobs:
            st.info(f"**{job['company_name']}** - Job ID: `{job['job_id']}`")

