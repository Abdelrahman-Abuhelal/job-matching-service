"""Candidates page - Add and manage candidate profiles."""

import streamlit as st
import asyncio
import uuid
from utils.api_client import update_candidate
import pandas as pd

from utils.import_helpers import CANDIDATES_SCHEMA, validate_columns, candidate_profile_from_row, split_csvish

st.set_page_config(page_title="Candidate Profiles — TalentMatch AI", page_icon="👥", layout="wide")

st.title("Candidate Profiles")
st.markdown("Add and manage candidate profiles for matching against job postings.")

# Initialize session state
if "candidates" not in st.session_state:
    st.session_state.candidates = []

# Tabs
tab_view, tab_import, tab_add = st.tabs(["View Candidates", "Import from File", "Add Candidate"])

with tab_view:
    st.markdown("### Candidates in System")

    # Sample data section
    st.markdown("#### Sample Data")
    st.caption("Pre-loaded for testing. You can use these in the Matching page.")

    sample_candidates = [
        {"id": "student_001", "summary": "Python, FastAPI, PostgreSQL"},
        {"id": "student_002", "summary": "Python, ML, Data Science"},
        {"id": "student_003", "summary": "JavaScript, React, Node.js"},
        {"id": "student_004", "summary": "Java, Spring Boot, Banking"},
        {"id": "student_005", "summary": "Python, PyTorch, AI Research"},
        {"id": "student_006", "summary": "Python, Django, Web Dev"},
        {"id": "student_007", "summary": "Python, Data Analysis"},
        {"id": "student_008", "summary": "React, Next.js, UI/UX"},
    ]
    
    for c in sample_candidates:
        col1, col2 = st.columns([1, 3])
        with col1:
            st.code(c['id'], language=None)
        with col2:
            st.caption(c['summary'])

    # User-added candidates
    if st.session_state.candidates:
        st.markdown("---")
        st.markdown("#### Your Candidates")
        st.caption("Candidates you added this session.")
        for c in st.session_state.candidates[-15:][::-1]:
            skills = c["profile_data"].get("skills", [])[:6]
            col1, col2 = st.columns([1, 3])
            with col1:
                st.code(c['candidate_id'], language=None)
            with col2:
                st.markdown(f"{', '.join(skills)}")


with tab_import:
    st.markdown("### Import Candidates from CSV or Excel")

    template_df = pd.DataFrame(
        [
            {
                "external_student_id": "candidate_1001",
                "skills": "Python, FastAPI, PostgreSQL",
                "education_level": "Bachelor's",
                "education_field": "Computer Science",
                "university": "Example University",
                "preferred_locations": "Remote, Berlin",
                "preferred_job_types": "Internship, Full-time",
                "industries": "Tech, Software Development",
            }
        ]
    )
    st.download_button(
        "Download CSV Template",
        data=template_df.to_csv(index=False).encode("utf-8"),
        file_name="candidates_import_template.csv",
        mime="text/csv",
        use_container_width=True,
    )

    upload = st.file_uploader(
        "Upload CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        help=f"Required columns: {', '.join(CANDIDATES_SCHEMA.required_columns)}",
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
            ok, missing, extra = validate_columns(df.columns, CANDIDATES_SCHEMA)
            if not ok:
                st.error(f"Missing required columns: {', '.join(missing)}")
            if extra:
                st.warning(f"Extra columns will be ignored: {', '.join(extra)}")

            if ok:
                st.dataframe(df.head(25), use_container_width=True)
                if st.button("Import Candidates", use_container_width=True, type="primary"):
                    progress = st.progress(0)
                    results = {"success": 0, "failed": 0}
                    status_text = st.empty()
                    
                    for i, row in enumerate(df.to_dict(orient="records")):
                        progress.progress((i + 1) / max(len(df), 1))
                        status_text.text(f"Processing row {i + 1} of {len(df)}...")
                        
                        external_student_id = str(row.get("external_student_id", "")).strip()
                        if not external_student_id:
                            results["failed"] += 1
                            continue

                        profile_data = candidate_profile_from_row(row)
                        if not profile_data.get("skills"):
                            results["failed"] += 1
                            continue

                        async def do_save():
                            return await update_candidate(external_student_id, profile_data)

                        r = asyncio.run(do_save())
                        if r.get("success"):
                            results["success"] += 1
                            st.session_state.candidates.append(
                                {"candidate_id": external_student_id, "profile_data": profile_data}
                            )
                        else:
                            results["failed"] += 1

                    status_text.empty()
                    st.success(
                        f"**Import completed.** {results['success']} candidates added successfully, "
                        f"{results['failed']} failed."
                    )


with tab_add:
    st.markdown("### Add a New Candidate")
    st.caption("Enter the candidate's skills, education, and preferences.")
    
    with st.form("add_candidate_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            candidate_id = st.text_input(
                "Candidate ID",
                value=f"candidate_{uuid.uuid4().hex[:8]}",
                help="A unique identifier for this candidate"
            )
            
            st.markdown("#### Education")
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
            st.markdown("#### Skills")
            skills_input = st.text_area(
                "Technical Skills (comma-separated)",
                placeholder="Python, JavaScript, FastAPI, PostgreSQL, Docker",
                height=100
            )
            
            st.markdown("#### Preferences")
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
        
        submitted = st.form_submit_button("Add Candidate", use_container_width=True, type="primary")
        
        if submitted:
            if not skills_input:
                st.error("Please enter at least one skill.")
            else:
                # Parse inputs
                skills = split_csvish(skills_input)
                location_list = split_csvish(locations)
                industry_list = split_csvish(industries)
                
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
                
                with st.spinner("Saving candidate profile..."):
                    async def do_save():
                        return await update_candidate(candidate_id, profile_data)
                    
                    result = asyncio.run(do_save())
                    
                    if result["success"]:
                        st.success(
                            f"**Candidate added successfully.** "
                            f"You can now use `{candidate_id}` in the Matching page."
                        )
                        
                        # Store in session
                        st.session_state.candidates.append({
                            "candidate_id": candidate_id,
                            "profile_data": profile_data
                        })
                        
                        # Show summary
                        st.markdown("#### Profile Summary")
                        st.markdown(f"**Skills:** {', '.join(skills[:8])}")
                        st.markdown(f"**Education:** {edu_level} in {edu_field}")
                        st.markdown(f"**Preferred Locations:** {', '.join(location_list) if location_list else 'Any'}")
                    else:
                        st.error(f"Could not save candidate: {result['error']}")
