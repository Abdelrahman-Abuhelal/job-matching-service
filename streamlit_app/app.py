"""TalentMatch AI - Streamlit Application (Home Page)."""

import streamlit as st
import asyncio
import uuid
import pandas as pd

from utils.api_client import (
    find_candidates_for_job,
    find_jobs_for_candidate,
    parse_job,
    update_candidate,
    get_token,
)
from utils.import_helpers import (
    JOBS_SCHEMA,
    CANDIDATES_SCHEMA,
    validate_columns,
    candidate_profile_from_row,
    split_csvish,
)

# Page configuration
st.set_page_config(
    page_title="TalentMatch AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        color: white;
        font-size: 2.2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .main-header p {
        color: #b0c4de;
        font-size: 1rem;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>TalentMatch AI</h1>
    <p>AI-powered candidate-job matching using semantic search</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if "jobs" not in st.session_state:
    st.session_state.jobs = []
if "candidates" not in st.session_state:
    st.session_state.candidates = []

# Token reminder
if not get_token():
    st.warning(
        "**Authentication required.** Go to Dashboard → API Configuration to set your API token."
    )

st.markdown("## Quick Actions")
st.caption("Add data or run matching from this page. Use the sidebar for full-featured pages.")

left, middle, right = st.columns([2, 2, 1])

# =============================================================================
# Candidates Column
# =============================================================================
with left:
    st.markdown("### Candidates")
    c_view, c_import, c_add = st.tabs(["View", "Import", "Add"])

    with c_view:
        st.markdown("**Sample Data** _(pre-loaded for testing)_")
        for c in ["student_001", "student_002", "student_003", "student_004",
                  "student_005", "student_006", "student_007", "student_008"]:
            st.caption(f"`{c}`")
        
        if st.session_state.candidates:
            st.markdown("---")
            st.markdown("**Your Candidates**")
            for c in st.session_state.candidates[-8:][::-1]:
                skills = c["profile_data"].get("skills", [])[:4]
                st.markdown(f"`{c['candidate_id']}` — {', '.join(skills)}")

    with c_import:
        template_df = pd.DataFrame([{
            "external_student_id": "candidate_1001",
            "skills": "Python, FastAPI, PostgreSQL",
            "education_level": "Bachelor's",
            "education_field": "Computer Science",
            "university": "Example University",
            "preferred_locations": "Remote, Berlin",
            "preferred_job_types": "Internship, Full-time",
            "industries": "Tech, Software Development",
        }])
        st.download_button(
            "Download CSV Template",
            data=template_df.to_csv(index=False).encode("utf-8"),
            file_name="candidates_import_template.csv",
            mime="text/csv",
            use_container_width=True,
        )
        upload = st.file_uploader(
            "Upload CSV/Excel",
            type=["csv", "xlsx", "xls"],
            key="candidates_upload_home",
            help=f"Required: {', '.join(CANDIDATES_SCHEMA.required_columns)}",
        )
        if upload is not None:
            try:
                df = pd.read_csv(upload) if upload.name.lower().endswith(".csv") else pd.read_excel(upload)
            except Exception as e:
                st.error(f"Could not read file: {e}")
                df = None
            if df is not None:
                ok, missing, extra = validate_columns(df.columns, CANDIDATES_SCHEMA)
                if not ok:
                    st.error(f"Missing columns: {', '.join(missing)}")
                if extra:
                    st.warning(f"Extra columns ignored: {', '.join(extra)}")
                if ok and st.button("Import", use_container_width=True, key="import_candidates_home"):
                    progress = st.progress(0)
                    count = 0
                    for i, row in enumerate(df.to_dict(orient="records")):
                        progress.progress((i + 1) / max(len(df), 1))
                        sid = str(row.get("external_student_id", "")).strip()
                        if not sid:
                            continue
                        profile = candidate_profile_from_row(row)
                        if not profile.get("skills"):
                            continue

                        async def do_save():
                            return await update_candidate(sid, profile)

                        r = asyncio.run(do_save())
                        if r.get("success"):
                            st.session_state.candidates.append({"candidate_id": sid, "profile_data": profile})
                            count += 1
                    st.success(f"Imported {count} candidates.")

    with c_add:
        sid = st.text_input("Candidate ID", value=f"candidate_{uuid.uuid4().hex[:8]}", key="manual_student_id_home")
        skills_input = st.text_area("Skills (comma-separated)", placeholder="Python, FastAPI, PostgreSQL", key="manual_student_skills_home")
        edu_level = st.selectbox("Education", ["Bachelor's", "Master's", "PhD", "Associate's", "High School"], key="manual_student_edu_level_home")
        edu_field = st.text_input("Field of Study", key="manual_student_edu_field_home")
        university = st.text_input("University", key="manual_student_university_home")
        locations = st.text_input("Locations (comma-separated)", key="manual_student_locations_home")
        job_types = st.text_input("Job Types (comma-separated)", key="manual_student_job_types_home")
        industries = st.text_input("Industries (comma-separated)", key="manual_student_industries_home")

        if st.button("Add Candidate", use_container_width=True, key="save_candidate_home"):
            profile = {
                "skills": split_csvish(skills_input),
                "education": {"level": edu_level, "field": edu_field, "university": university},
                "preferences": {
                    "locations": split_csvish(locations),
                    "job_types": split_csvish(job_types),
                    "industries": split_csvish(industries),
                },
            }

            async def do_save():
                return await update_candidate(sid, profile)

            r = asyncio.run(do_save())
            if r.get("success"):
                st.session_state.candidates.append({"candidate_id": sid, "profile_data": profile})
                st.success(f"Candidate `{sid}` added.")
            else:
                st.error(r.get("error"))

# =============================================================================
# Jobs Column
# =============================================================================
with middle:
    st.markdown("### Jobs")
    j_view, j_import, j_add = st.tabs(["View", "Import", "Add"])

    with j_view:
        st.markdown("**Sample Data** _(pre-loaded for testing)_")
        for j in ["job_001", "job_002", "job_003", "job_004", "job_005"]:
            st.caption(f"`{j}`")
        
        if st.session_state.jobs:
            st.markdown("---")
            st.markdown("**Your Jobs**")
            for j in st.session_state.jobs[-8:][::-1]:
                st.markdown(f"`{j['job_id']}` — {j['company_name']}")

    with j_import:
        st.caption("Each job triggers AI parsing. Large imports may take time.")
        template_df = pd.DataFrame([{
            "external_job_id": "job_1001",
            "external_company_id": "company_acme",
            "company_name": "Acme Corp",
            "raw_description": "Paste full job description here...",
        }])
        st.download_button(
            "Download CSV Template",
            data=template_df.to_csv(index=False).encode("utf-8"),
            file_name="jobs_import_template.csv",
            mime="text/csv",
            use_container_width=True,
        )
        upload = st.file_uploader(
            "Upload CSV/Excel",
            type=["csv", "xlsx", "xls"],
            key="jobs_upload_home",
            help=f"Required: {', '.join(JOBS_SCHEMA.required_columns)}",
        )
        if upload is not None:
            try:
                df = pd.read_csv(upload) if upload.name.lower().endswith(".csv") else pd.read_excel(upload)
            except Exception as e:
                st.error(f"Could not read file: {e}")
                df = None
            if df is not None:
                ok, missing, extra = validate_columns(df.columns, JOBS_SCHEMA)
                if not ok:
                    st.error(f"Missing columns: {', '.join(missing)}")
                if extra:
                    st.warning(f"Extra columns ignored: {', '.join(extra)}")
                if ok and st.button("Import", use_container_width=True, key="import_jobs_home"):
                    progress = st.progress(0)
                    count = 0
                    for i, row in enumerate(df.to_dict(orient="records")):
                        progress.progress((i + 1) / max(len(df), 1))
                        jid = str(row.get("external_job_id", "")).strip()
                        cid = str(row.get("external_company_id", "")).strip()
                        cname = str(row.get("company_name", "")).strip()
                        desc = str(row.get("raw_description", "")).strip()
                        if not (jid and cid and cname and desc):
                            continue

                        async def do_parse():
                            return await parse_job(jid, cid, cname, desc)

                        r = asyncio.run(do_parse())
                        if r.get("success"):
                            st.session_state.jobs.append({"job_id": jid, "company_id": cid, "company_name": cname, "data": r.get("data", {})})
                            count += 1
                    st.success(f"Imported {count} jobs.")

    with j_add:
        company_name = st.text_input("Company Name", key="manual_job_company_home")
        job_id = st.text_input("Job ID", value=f"job_{uuid.uuid4().hex[:8]}", key="manual_job_id_home")
        company_id = st.text_input("Company ID", value=f"company_{uuid.uuid4().hex[:8]}", key="manual_company_id_home")
        raw_description = st.text_area("Job Description", height=200, key="manual_job_desc_home")
        
        if st.button("Add Job", use_container_width=True, key="save_job_home"):
            if not (company_name and raw_description):
                st.error("Please provide company name and job description.")
            else:
                with st.spinner("Parsing job description..."):
                    async def do_parse():
                        return await parse_job(job_id, company_id, company_name, raw_description)
                    r = asyncio.run(do_parse())
                    if r.get("success"):
                        st.session_state.jobs.append({"job_id": job_id, "company_id": company_id, "company_name": company_name, "data": r.get("data", {})})
                        st.success(f"Job `{job_id}` added.")
                    else:
                        st.error(r.get("error"))

# =============================================================================
# Matching Column
# =============================================================================
with right:
    st.markdown("### Quick Match")
    st.caption("Run matching from here or use the full Matching page.")

    available_jobs = ["job_001", "job_002", "job_003", "job_004", "job_005"] + [
        j["job_id"] for j in st.session_state.jobs[-20:]
    ]
    available_students = [
        "student_001", "student_002", "student_003", "student_004",
        "student_005", "student_006", "student_007", "student_008",
    ] + [c["candidate_id"] for c in st.session_state.candidates[-20:]]

    job_id = st.selectbox("Job", list(dict.fromkeys(available_jobs)), key="match_job_home")
    student_id = st.selectbox("Candidate", list(dict.fromkeys(available_students)), key="match_student_home")

    top_k = st.slider("Results", 1, 20, 5, key="match_top_k_home")
    min_score = st.slider("Min Score", 0.5, 1.0, 0.70, 0.05, key="match_min_score_home")

    if st.button("Find Candidates", use_container_width=True, key="match_candidates_btn_home"):
        with st.spinner("Matching..."):
            async def do_match():
                return await find_candidates_for_job(job_id, top_k, min_score, None)
            r = asyncio.run(do_match())
            if r.get("success"):
                matches = r["data"].get("matches", [])
                st.success(f"Found {len(matches)} candidates")
                for m in matches[:5]:
                    ins = m.get("match_insights", {})
                    score = ins.get('final_score', 0)
                    st.caption(f"`{m.get('external_student_id')}` — {score:.0%}")
            else:
                st.error(r.get("error"))

    if st.button("Find Jobs", use_container_width=True, key="match_jobs_btn_home"):
        with st.spinner("Matching..."):
            async def do_match():
                return await find_jobs_for_candidate(student_id, top_k, min_score)
            r = asyncio.run(do_match())
            if r.get("success"):
                matches = r["data"].get("matches", [])
                st.success(f"Found {len(matches)} jobs")
                for m in matches[:5]:
                    ins = m.get("match_insights", {})
                    score = ins.get('final_score', 0)
                    st.caption(f"`{m.get('external_job_id')}` — {score:.0%}")
            else:
                st.error(r.get("error"))
