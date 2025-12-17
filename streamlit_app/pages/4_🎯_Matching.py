"""Matching page - Run AI-powered matching and view results."""

import streamlit as st
import asyncio
from utils.api_client import find_candidates_for_job, find_jobs_for_candidate, get_token, get_match_history

st.set_page_config(page_title="Matching — TalentMatch AI", page_icon="🎯", layout="wide")

st.title("🎯 Matching")
st.markdown("Search for candidates that match your job requirements, or find jobs that fit a candidate's profile.")

# Check if JWT token is configured
if not get_token():
    st.warning(
        "**Authentication required.** Configure your API token in the Dashboard → API Configuration section."
    )

# Tabs for different matching directions
tab1, tab2, tab3 = st.tabs(["👥 Find Candidates for Job", "💼 Find Jobs for Candidate", "📜 Match History"])

# =============================================================================
# TAB 1: Find Candidates for Job
# =============================================================================
with tab1:
    st.markdown("### Select a Job")
    st.caption("Choose a job posting and configure ranking preferences. Results are ranked by skill fit and profile alignment.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Combine sample jobs with session-added jobs
        sample_jobs = ["job_001", "job_002", "job_003", "job_004", "job_005"]
        session_jobs = [j["job_id"] for j in st.session_state.get("jobs", [])[-20:]]
        all_jobs = list(dict.fromkeys(sample_jobs + session_jobs))
        
        job_id = st.selectbox(
            "Job Posting",
            all_jobs,
            format_func=lambda x: {
                "job_001": "Python Backend Developer Internship",
                "job_002": "Data Science Internship",
                "job_003": "Full-Stack Developer Internship (React + Node.js)",
                "job_004": "Junior Software Engineer - Banking Platform",
                "job_005": "Machine Learning Research Intern"
            }.get(x, x),
            help="Sample jobs (job_001–job_005) are pre-loaded for testing."
        )
    
    with col2:
        top_k = st.slider("Max results to return", 1, 20, 5)
        min_score = st.slider("Minimum match threshold", 0.5, 1.0, 0.70, 0.05, 
                              help="Candidates below this score will be filtered out.")
    
    # -------------------------------------------------------------------------
    # Ranking Configuration
    # -------------------------------------------------------------------------
    st.markdown("### 🧮 Ranking Configuration")
    st.caption("Adjust how candidates are ranked. Higher weight = more influence on the final score.")

    PRESETS = {
        "Balanced": {"similarity": 0.60, "required_skills": 0.30, "preferred_skills": 0.10},
        "Skills-first": {"similarity": 0.35, "required_skills": 0.55, "preferred_skills": 0.10},
        "Potential-first": {"similarity": 0.75, "required_skills": 0.15, "preferred_skills": 0.10},
        "Nice-to-have matters": {"similarity": 0.55, "required_skills": 0.25, "preferred_skills": 0.20},
    }
    CUSTOM_OPTION = "Custom"

    # Initialize state
    if "ranking_preset" not in st.session_state:
        st.session_state["ranking_preset"] = "Balanced"
    preset_for_defaults = st.session_state.get("ranking_preset")
    if preset_for_defaults not in PRESETS:
        preset_for_defaults = st.session_state.get("_last_non_custom_preset", "Balanced")
        if preset_for_defaults not in PRESETS:
            preset_for_defaults = "Balanced"
    
    if "w_similarity" not in st.session_state:
        st.session_state["w_similarity"] = PRESETS[preset_for_defaults]["similarity"]
    if "w_required_skills" not in st.session_state:
        st.session_state["w_required_skills"] = PRESETS[preset_for_defaults]["required_skills"]
    if "w_preferred_skills" not in st.session_state:
        st.session_state["w_preferred_skills"] = PRESETS[preset_for_defaults]["preferred_skills"]
    if "custom_similarity" not in st.session_state:
        st.session_state["custom_similarity"] = st.session_state["w_similarity"]
    if "custom_required_skills" not in st.session_state:
        st.session_state["custom_required_skills"] = st.session_state["w_required_skills"]
    if "custom_preferred_skills" not in st.session_state:
        st.session_state["custom_preferred_skills"] = st.session_state["w_preferred_skills"]

    preset = st.radio(
        "Ranking preset",
        list(PRESETS.keys()) + [CUSTOM_OPTION],
        key="ranking_preset",
        horizontal=True,
    )

    # Sync preset changes
    if st.session_state.get("_last_ranking_preset") != preset:
        st.session_state["_last_ranking_preset"] = preset
        if preset != CUSTOM_OPTION:
            st.session_state["w_similarity"] = PRESETS[preset]["similarity"]
            st.session_state["w_required_skills"] = PRESETS[preset]["required_skills"]
            st.session_state["w_preferred_skills"] = PRESETS[preset]["preferred_skills"]

    is_custom = preset == CUSTOM_OPTION

    if is_custom:
        st.session_state["_last_non_custom_preset"] = st.session_state.get("_last_non_custom_preset", "Balanced")
        col1, col2, col3 = st.columns(3)
        with col1:
            similarity_weight = st.slider(
                "Profile Fit", 0.0, 1.0, st.session_state["custom_similarity"], 0.05,
                key="custom_similarity",
                help="How well the overall profile matches semantically."
            )
        with col2:
            required_weight = st.slider(
                "Required Skills", 0.0, 1.0, st.session_state["custom_required_skills"], 0.05,
                key="custom_required_skills",
                help="Coverage of must-have skills from the job posting."
            )
        with col3:
            preferred_weight = st.slider(
                "Preferred Skills", 0.0, 1.0, st.session_state["custom_preferred_skills"], 0.05,
                key="custom_preferred_skills",
                help="Coverage of nice-to-have skills."
            )
    else:
        st.session_state["_last_non_custom_preset"] = preset
        with st.expander("Fine-tune weights", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                similarity_weight = st.slider(
                    "Profile Fit", 0.0, 1.0, st.session_state["w_similarity"], 0.05,
                    key="w_similarity",
                    help="How well the overall profile matches semantically."
                )
            with col2:
                required_weight = st.slider(
                    "Required Skills", 0.0, 1.0, st.session_state["w_required_skills"], 0.05,
                    key="w_required_skills",
                    help="Coverage of must-have skills from the job posting."
                )
            with col3:
                preferred_weight = st.slider(
                    "Preferred Skills", 0.0, 1.0, st.session_state["w_preferred_skills"], 0.05,
                    key="w_preferred_skills",
                    help="Coverage of nice-to-have skills."
                )

    # Normalize weights
    total = similarity_weight + required_weight + preferred_weight
    if total <= 0:
        similarity_weight, required_weight, preferred_weight = 0.60, 0.30, 0.10
        total = 1.0

    normalized = {
        "similarity": similarity_weight / total,
        "required_skills": required_weight / total,
        "preferred_skills": preferred_weight / total,
    }

    # Show current config summary
    config_summary = []
    if normalized["required_skills"] >= 0.5:
        config_summary.append("strict skill matching")
    elif normalized["similarity"] >= 0.7:
        config_summary.append("profile potential prioritized")
    else:
        config_summary.append("balanced approach")
    
    st.info(
        f"**Current weights:** Profile Fit {normalized['similarity']:.0%}, "
        f"Required Skills {normalized['required_skills']:.0%}, "
        f"Preferred Skills {normalized['preferred_skills']:.0%} — "
        f"_{', '.join(config_summary)}_"
    )
    
    # -------------------------------------------------------------------------
    # Run Matching Button
    # -------------------------------------------------------------------------
    if st.button("Run Matching", key="find_candidates", use_container_width=True, type="primary"):
        with st.spinner("Evaluating candidates..."):
            async def do_match():
                return await find_candidates_for_job(job_id, top_k, min_score, normalized)
            
            result = asyncio.run(do_match())
            
            if result["success"]:
                data = result["data"]
                matches = data.get("matches", [])
                total_scanned = data.get("total_candidates", 0)
                returned_count = data.get("returned_count", len(matches))
                
                # Summary message
                st.success(
                    f"**Match completed** — {total_scanned} candidates evaluated, "
                    f"{returned_count} returned above {min_score:.0%} threshold."
                )
                
                st.markdown(f"**Job:** {data.get('job_title', job_id)}")
                
                if not matches:
                    st.warning(
                        "No candidates matched your criteria. "
                        "Try lowering the minimum score threshold or adjusting the ranking weights."
                    )
                else:
                    st.markdown("---")
                    st.markdown("### 🏆 Top Matches")
                    
                    for match in matches:
                        rank = match.get("rank", 0)
                        insights = match.get("match_insights", {})
                        final_score = insights.get("final_score", match.get("similarity_score", 0))
                        raw_similarity = insights.get("similarity_score_raw", match.get("similarity_score", 0))
                        breakdown = insights.get("skills_breakdown", {})
                        
                        # Rank indicator with medals
                        if rank == 1:
                            rank_display = "🥇 1st"
                        elif rank == 2:
                            rank_display = "🥈 2nd"
                        elif rank == 3:
                            rank_display = "🥉 3rd"
                        else:
                            rank_display = f"#{rank}"
                        
                        with st.container():
                            # Header row
                            header_col1, header_col2 = st.columns([3, 1])
                            with header_col1:
                                st.markdown(f"#### {rank_display} — Candidate `{match.get('external_student_id', 'Unknown')}`")
                            with header_col2:
                                st.markdown(f"<h2 style='text-align: right; color: #2e7d32; margin: 0;'>{final_score:.0%}</h2>", unsafe_allow_html=True)
                            
                            # Main content in columns
                            col_left, col_right = st.columns([2, 1])
                            
                            with col_left:
                                # Why Recommended section
                                if insights.get("ai_powered"):
                                    st.markdown("**Why Recommended** _(AI-generated)_")
                                    reasons = insights.get("recommended_because", [])
                                    if reasons:
                                        for reason in reasons[:3]:
                                            st.markdown(f"- {reason}")
                                    
                                    skill_analysis = insights.get("skill_analysis", {})
                                    if skill_analysis.get("strong_matches"):
                                        st.markdown(f"**Strong skills:** {', '.join(skill_analysis['strong_matches'][:5])}")
                                    if skill_analysis.get("skill_gaps"):
                                        st.markdown(f"**Gaps:** {', '.join(skill_analysis['skill_gaps'][:3])}")
                                else:
                                    st.markdown("**Why Recommended** _(rule-based)_")
                                    summary = insights.get("summary", "")
                                    if summary:
                                        st.markdown(summary)
                                
                                # Skills Breakdown
                                st.markdown("**Skills Breakdown**")
                                
                                req_matched = breakdown.get("required_skills_matched", [])
                                req_missing = breakdown.get("required_skills_missing", [])
                                pref_matched = breakdown.get("preferred_skills_matched", [])
                                
                                if req_matched:
                                    st.markdown(f"✅ **Matched required:** {', '.join(req_matched[:6])}")
                                if req_missing:
                                    st.markdown(f"❌ **Missing required:** {', '.join(req_missing[:4])}")
                                if pref_matched:
                                    st.markdown(f"➕ **Bonus (preferred):** {', '.join(pref_matched[:4])}")
                                
                                if not req_matched and not req_missing and not pref_matched:
                                    st.caption("No detailed skill data available.")
                            
                            with col_right:
                                # Score Breakdown
                                st.markdown("**Score Breakdown**")
                                
                                req_coverage = breakdown.get("required_coverage", 0)
                                pref_coverage = breakdown.get("preferred_coverage", 0)
                                
                                # Show calculation
                                sim_contrib = raw_similarity * normalized["similarity"]
                                req_contrib = req_coverage * normalized["required_skills"]
                                pref_contrib = pref_coverage * normalized["preferred_skills"]
                                
                                st.caption(f"Profile Fit: {raw_similarity:.0%} × {normalized['similarity']:.0%} = {sim_contrib:.1%}")
                                st.caption(f"Required: {req_coverage:.0%} × {normalized['required_skills']:.0%} = {req_contrib:.1%}")
                                st.caption(f"Preferred: {pref_coverage:.0%} × {normalized['preferred_skills']:.0%} = {pref_contrib:.1%}")
                                st.caption(f"**Final: {final_score:.0%}**")
                            
                            st.markdown("---")
            else:
                error_msg = result.get("error", "Unknown error")
                if "not found" in error_msg.lower():
                    st.error("Job not found. Please add the job first, then run matching.")
                else:
                    st.error(f"Matching failed: {error_msg}")

# =============================================================================
# TAB 2: Find Jobs for Candidate
# =============================================================================
with tab2:
    st.markdown("### Select a Candidate")
    st.caption("Choose a candidate profile to find matching job opportunities.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Combine sample candidates with session-added candidates
        sample_candidates = ["student_001", "student_002", "student_003", "student_004", 
                            "student_005", "student_006", "student_007", "student_008"]
        session_candidates = [c["candidate_id"] for c in st.session_state.get("candidates", [])[-20:]]
        all_candidates = list(dict.fromkeys(sample_candidates + session_candidates))
        
        candidate_id = st.selectbox(
            "Candidate",
            all_candidates,
            format_func=lambda x: {
                "student_001": "Candidate 001 (Python, FastAPI, PostgreSQL)",
                "student_002": "Candidate 002 (Python, ML, Data Science)",
                "student_003": "Candidate 003 (JavaScript, React, Node.js)",
                "student_004": "Candidate 004 (Java, Spring Boot, Banking)",
                "student_005": "Candidate 005 (Python, PyTorch, AI Research)",
                "student_006": "Candidate 006 (Python, Django, Web Dev)",
                "student_007": "Candidate 007 (Python, Data Analysis)",
                "student_008": "Candidate 008 (React, Next.js, UI/UX)"
            }.get(x, x),
            help="Sample candidates (student_001–student_008) are pre-loaded for testing."
        )
    
    with col2:
        top_k_jobs = st.slider("Max results to return", 1, 10, 5, key="top_k_jobs")
        min_score_jobs = st.slider("Minimum match threshold", 0.5, 1.0, 0.70, 0.05, key="min_score_jobs")
    
    if st.button("Run Matching", key="find_jobs", use_container_width=True, type="primary"):
        with st.spinner("Evaluating job opportunities..."):
            async def do_job_match():
                return await find_jobs_for_candidate(candidate_id, top_k_jobs, min_score_jobs)
            
            result = asyncio.run(do_job_match())
            
            if result["success"]:
                data = result["data"]
                matches = data.get("matches", [])
                
                st.success(f"**Match completed** — {len(matches)} jobs found above {min_score_jobs:.0%} threshold.")
                
                if not matches:
                    st.warning(
                        "No jobs matched this candidate's profile. "
                        "Try lowering the minimum score threshold."
                    )
                else:
                    st.markdown("---")
                    st.markdown("### 🎯 Recommended Jobs")
                    
                    for match in matches:
                        rank = match.get("rank", 0)
                        insights = match.get("match_insights", {})
                        final_score = insights.get("final_score", match.get("similarity_score", 0))
                        raw_similarity = insights.get("similarity_score_raw", match.get("similarity_score", 0))
                        breakdown = insights.get("skills_breakdown", {})
                        
                        # Rank indicator with medals
                        if rank == 1:
                            rank_display = "🥇"
                        elif rank == 2:
                            rank_display = "🥈"
                        elif rank == 3:
                            rank_display = "🥉"
                        else:
                            rank_display = f"#{rank}"
                        
                        with st.container():
                            header_col1, header_col2 = st.columns([3, 1])
                            with header_col1:
                                st.markdown(f"#### {rank_display} {match.get('job_title', 'Unknown Position')}")
                                st.markdown(f"**{match.get('company_name', 'Unknown Company')}**")
                            with header_col2:
                                st.markdown(f"<h2 style='text-align: right; color: #2e7d32; margin: 0;'>{final_score:.0%}</h2>", unsafe_allow_html=True)
                            
                            col_left, col_right = st.columns([2, 1])
                            
                            with col_left:
                                if insights.get("ai_powered"):
                                    st.markdown("**Why this job fits** _(AI-generated)_")
                                    reasons = insights.get("why_recommended", [])
                                    if reasons:
                                        for reason in reasons[:3]:
                                            st.markdown(f"- {reason}")
                                    
                                    next_steps = insights.get("next_steps", "")
                                    if next_steps:
                                        st.info(f"**Next step:** {next_steps}")
                                else:
                                    st.markdown("**Why this job fits** _(rule-based)_")
                                    summary = insights.get("summary", "")
                                    if summary:
                                        st.markdown(summary)
                                
                                # Skills info
                                skill_strengths = breakdown.get("required_skills_matched", []) or insights.get("skill_strengths", [])
                                skill_gaps = breakdown.get("required_skills_missing", []) or insights.get("growth_opportunities", [])
                                
                                if skill_strengths:
                                    st.markdown(f"✅ **Your matching skills:** {', '.join(skill_strengths[:5])}")
                                if skill_gaps:
                                    st.markdown(f"📈 **Skills to develop:** {', '.join(skill_gaps[:3])}")
                            
                            with col_right:
                                st.markdown("**Match Score**")
                                st.caption(f"Profile Fit: {raw_similarity:.0%}")
                                req_coverage = breakdown.get("required_coverage", 0)
                                if req_coverage > 0:
                                    st.caption(f"Required Skills: {req_coverage:.0%}")
                                st.caption(f"**Final: {final_score:.0%}**")
                            
                            st.markdown("---")
            else:
                error_msg = result.get("error", "Unknown error")
                if "not found" in error_msg.lower():
                    st.error("Candidate not found. Please add the candidate first, then run matching.")
                else:
                    st.error(f"Matching failed: {error_msg}")

# =============================================================================
# TAB 3: Match History
# =============================================================================
with tab3:
    st.markdown("### Past Matching Sessions")
    st.caption("View and revisit results from previous matching runs.")
    
    # Filter options
    col1, col2 = st.columns([2, 1])
    with col1:
        # Job filter
        sample_jobs = ["", "job_001", "job_002", "job_003", "job_004", "job_005"]
        session_jobs = [j["job_id"] for j in st.session_state.get("jobs", [])[-20:]]
        all_jobs_for_filter = list(dict.fromkeys(sample_jobs + session_jobs))
        
        filter_job_id = st.selectbox(
            "Filter by Job",
            all_jobs_for_filter,
            format_func=lambda x: "All Jobs" if x == "" else {
                "job_001": "Python Backend Developer Internship",
                "job_002": "Data Science Internship",
                "job_003": "Full-Stack Developer Internship",
                "job_004": "Junior Software Engineer",
                "job_005": "ML Research Intern"
            }.get(x, x),
            key="history_filter_job"
        )
    with col2:
        history_limit = st.slider("Max sessions to show", 5, 50, 20, key="history_limit")
    
    if st.button("Load History", use_container_width=True, key="load_history"):
        with st.spinner("Loading match history..."):
            async def do_load():
                return await get_match_history(
                    job_id=filter_job_id if filter_job_id else None,
                    limit=history_limit
                )
            
            result = asyncio.run(do_load())
            
            if result["success"]:
                data = result["data"]
                sessions = data.get("sessions", [])
                
                if not sessions:
                    st.info("No matching history found. Run some matches first, then they will appear here.")
                else:
                    st.success(f"Found {len(sessions)} matching sessions.")
                    
                    for session in sessions:
                        session_id = session.get("session_id", "unknown")
                        job_title = session.get("job_title", "Unknown Job")
                        created_at = session.get("created_at", "")[:16].replace("T", " ")
                        candidates_matched = session.get("candidates_matched", 0)
                        top_score = session.get("top_score", 0)
                        
                        with st.expander(f"**{job_title}** — {created_at} — {candidates_matched} candidates, top score {top_score:.0%}"):
                            matches = session.get("matches", [])
                            
                            if matches:
                                st.markdown("**Matched Candidates:**")
                                for match in matches[:10]:
                                    student_id = match.get("external_student_id", "Unknown")
                                    score = match.get("similarity_score", 0)
                                    rank = match.get("rank_position", 0)
                                    
                                    col_id, col_score = st.columns([3, 1])
                                    with col_id:
                                        st.markdown(f"#{rank} — `{student_id}`")
                                    with col_score:
                                        st.markdown(f"**{score:.0%}**")
                                
                                if len(matches) > 10:
                                    st.caption(f"...and {len(matches) - 10} more")
                            else:
                                st.caption("No match details available.")
            else:
                st.error(f"Could not load history: {result.get('error', 'Unknown error')}")

# =============================================================================
# Help Section
# =============================================================================
st.markdown("---")
with st.expander("How matching works"):
    st.markdown("""
**TalentMatch AI uses a multi-stage matching process:**

1. **Profile Analysis** — Jobs and candidates are converted to semantic vectors that capture meaning, not just keywords.

2. **Similarity Search** — The system finds profiles that are semantically similar to the target.

3. **Skills Verification** — Required and preferred skills are compared to calculate coverage scores.

4. **Weighted Ranking** — Final scores combine profile fit, required skills, and preferred skills based on your configuration.

5. **Explanations** — Top matches receive detailed explanations (AI-generated for top results, rule-based for others).

**Understanding the score:**
- **Profile Fit** — How well the overall background aligns (experience, education, context)
- **Required Skills** — Percentage of must-have skills the candidate has
- **Preferred Skills** — Percentage of nice-to-have skills matched
    """)
