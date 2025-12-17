"""Jobs page - Add and manage job postings."""

import streamlit as st
import asyncio
import uuid
from utils.api_client import parse_job
import pandas as pd

from utils.import_helpers import JOBS_SCHEMA, validate_columns

st.set_page_config(page_title="Job Postings — TalentMatch AI", page_icon="💼", layout="wide")

st.title("Job Postings")
st.markdown("Add and manage job postings. The AI extracts structured data from job descriptions.")

# Initialize session state for jobs
if "jobs" not in st.session_state:
    st.session_state.jobs = []

# Tabs for different actions
tab_view, tab_import, tab_add = st.tabs(["View Jobs", "Import from File", "Add Job"])

with tab_view:
    st.markdown("### Jobs in System")

    # Sample data section
    st.markdown("#### Sample Data")
    st.caption("Pre-loaded for testing. You can use these in the Matching page.")

    sample_jobs = [
        {"job_id": "job_001", "company": "Tech Corp", "title": "Python Backend Developer Internship"},
        {"job_id": "job_002", "company": "Data Solutions Inc", "title": "Data Science Internship"},
        {"job_id": "job_003", "company": "Creative Web Studio", "title": "Full-Stack Developer Internship (React + Node.js)"},
        {"job_id": "job_004", "company": "FinTech Solutions", "title": "Junior Software Engineer - Banking Platform"},
        {"job_id": "job_005", "company": "AI Research Lab", "title": "Machine Learning Research Intern"},
    ]

    for job in sample_jobs:
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{job['title']}**")
                st.caption(f"{job['company']}")
            with col2:
                st.code(job['job_id'], language=None)
            st.markdown("---")

    # User-added jobs
    if st.session_state.jobs:
        st.markdown("#### Your Jobs")
        st.caption("Jobs you added this session.")
        for job in st.session_state.jobs[-10:][::-1]:
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    title = job.get("data", {}).get("structured_data", {}).get("title", "Untitled")
                    st.markdown(f"**{title}**")
                    st.caption(job['company_name'])
                with col2:
                    st.code(job['job_id'], language=None)
                st.markdown("---")


with tab_import:
    st.markdown("### Import Jobs from CSV or Excel")
    st.caption(
        "Each row triggers AI parsing and embedding generation. "
        "Large imports may take time or hit API rate limits."
    )

    template_df = pd.DataFrame(
        [
            {
                "external_job_id": "job_1001",
                "external_company_id": "company_acme",
                "company_name": "Acme Corp",
                "raw_description": "Paste full job description text here...",
            }
        ]
    )
    st.download_button(
        "Download CSV Template",
        data=template_df.to_csv(index=False).encode("utf-8"),
        file_name="jobs_import_template.csv",
        mime="text/csv",
        use_container_width=True,
    )

    upload = st.file_uploader(
        "Upload CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        help=f"Required columns: {', '.join(JOBS_SCHEMA.required_columns)}",
    )

    if upload is not None:
        try:
            if upload.name.lower().endswith(".csv"):
                df = pd.read_csv(upload)
            else:
                df = pd.read_excel(upload)
        except Exception as e:
            st.error(f"Could not read file: {e}")
            df = None

        if df is not None:
            ok, missing, extra = validate_columns(df.columns, JOBS_SCHEMA)
            if not ok:
                st.error(f"Missing required columns: {', '.join(missing)}")
            if extra:
                st.warning(f"Extra columns will be ignored: {', '.join(extra)}")

            if ok:
                st.dataframe(df.head(25), use_container_width=True)
                if st.button("Import Jobs", use_container_width=True, type="primary"):
                    progress = st.progress(0)
                    results = {"success": 0, "failed": 0}
                    status_text = st.empty()
                    
                    for i, row in enumerate(df.to_dict(orient="records")):
                        progress.progress((i + 1) / max(len(df), 1))
                        status_text.text(f"Processing row {i + 1} of {len(df)}...")
                        
                        external_job_id = str(row.get("external_job_id", "")).strip()
                        external_company_id = str(row.get("external_company_id", "")).strip()
                        company_name = str(row.get("company_name", "")).strip()
                        raw_description = str(row.get("raw_description", "")).strip()

                        if not (external_job_id and external_company_id and company_name and raw_description):
                            results["failed"] += 1
                            continue

                        async def do_parse():
                            return await parse_job(
                                external_job_id,
                                external_company_id,
                                company_name,
                                raw_description,
                            )

                        r = asyncio.run(do_parse())
                        if r.get("success"):
                            results["success"] += 1
                            st.session_state.jobs.append(
                                {
                                    "job_id": external_job_id,
                                    "company_id": external_company_id,
                                    "company_name": company_name,
                                    "data": r.get("data", {}),
                                }
                            )
                        else:
                            results["failed"] += 1

                    status_text.empty()
                    st.success(
                        f"**Import completed.** {results['success']} jobs added successfully, "
                        f"{results['failed']} failed."
                    )


with tab_add:
    st.markdown("### Add a New Job")
    st.caption("Enter a job description. The AI will extract title, skills, requirements, and other structured data.")
    
    with st.form("add_job_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input(
                "Company Name",
                placeholder="e.g., TechCorp Inc."
            )
            
            job_id = st.text_input(
                "Job ID",
                value=f"job_{uuid.uuid4().hex[:8]}",
                help="A unique identifier for this job"
            )
        
        with col2:
            company_id = st.text_input(
                "Company ID",
                value=f"company_{uuid.uuid4().hex[:8]}",
                help="A unique identifier for the company"
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
""",
            help="The AI will extract structured data from this description"
        )
        
        submitted = st.form_submit_button("Add Job", use_container_width=True, type="primary")
        
        if submitted:
            if not company_name or not raw_description:
                st.error("Please provide both company name and job description.")
            else:
                with st.spinner("Parsing job description..."):
                    async def do_parse():
                        return await parse_job(
                            job_id,
                            company_id,
                            company_name,
                            raw_description
                        )
                    
                    result = asyncio.run(do_parse())
                    
                    if result["success"]:
                        st.success(
                            f"**Job added successfully.** "
                            f"You can now use `{job_id}` in the Matching page."
                        )
                        
                        # Store in session state
                        st.session_state.jobs.append({
                            "job_id": job_id,
                            "company_id": company_id,
                            "company_name": company_name,
                            "data": result["data"]
                        })
                        
                        # Display parsed data
                        st.markdown("#### Extracted Data")
                        
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
                        else:
                            st.caption("None extracted")
                        
                        st.markdown("**Preferred Skills:**")
                        pref_skills = data.get("preferred_skills", [])
                        if pref_skills:
                            st.markdown(" ".join([f"`{s}`" for s in pref_skills[:5]]))
                        else:
                            st.caption("None extracted")
                        
                    else:
                        st.error(f"Could not parse job: {result['error']}")
