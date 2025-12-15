"""Matching page - Run AI-powered matching and view results."""

import streamlit as st
import asyncio
from utils.api_client import find_candidates_for_job, find_jobs_for_candidate

st.set_page_config(page_title="Matching - TalentMatch AI", page_icon="🎯", layout="wide")

st.title("🎯 AI-Powered Matching")
st.markdown("Find the best candidates for jobs or best jobs for candidates")

# Tabs for different matching directions
tab1, tab2 = st.tabs(["👥 Find Candidates for Job", "💼 Find Jobs for Candidate"])

with tab1:
    st.markdown("### Find Best Candidates for a Job")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        job_id = st.selectbox(
            "Select Job",
            ["job_001", "job_002", "job_003", "job_004", "job_005"],
            format_func=lambda x: {
                "job_001": "Senior Python Developer (TechCorp)",
                "job_002": "Data Engineer (DataFlow Inc)",
                "job_003": "ML Engineer (AI Solutions)",
                "job_004": "DevOps Engineer (CloudNative Co)",
                "job_005": "Backend Developer (FinTech Pro)"
            }.get(x, x)
        )
    
    with col2:
        top_k = st.slider("Number of Results", 1, 20, 5)
        min_score = st.slider("Minimum Score", 0.5, 1.0, 0.70, 0.05)
    
    # Ranking weights
    with st.expander("⚙️ Customize Ranking Weights"):
        st.markdown("Adjust how candidates are ranked:")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            similarity_weight = st.slider("Semantic Similarity", 0.0, 1.0, 0.6, 0.1)
        with col2:
            required_weight = st.slider("Required Skills", 0.0, 1.0, 0.3, 0.1)
        with col3:
            preferred_weight = st.slider("Preferred Skills", 0.0, 1.0, 0.1, 0.1)
        
        # Normalize
        total = similarity_weight + required_weight + preferred_weight
        if total > 0:
            st.info(f"Normalized: Similarity {similarity_weight/total:.0%}, Required {required_weight/total:.0%}, Preferred {preferred_weight/total:.0%}")
    
    if st.button("🔍 Find Matching Candidates", key="find_candidates", use_container_width=True):
        with st.spinner("🤖 AI is finding the best candidates..."):
            async def do_match():
                weights = {
                    "similarity": similarity_weight,
                    "required_skills": required_weight,
                    "preferred_skills": preferred_weight
                }
                return await find_candidates_for_job(job_id, top_k, min_score, weights)
            
            result = asyncio.run(do_match())
            
            if result["success"]:
                data = result["data"]
                
                st.success(f"✅ Found {data.get('returned_count', 0)} matching candidates!")
                
                st.markdown(f"**Job:** {data.get('job_title', 'Unknown')}")
                st.markdown(f"**Total candidates scanned:** {data.get('total_candidates', 0)}")
                
                st.markdown("---")
                st.markdown("### 🏆 Top Matches")
                
                matches = data.get("matches", [])
                
                for match in matches:
                    rank = match.get("rank", 0)
                    score = match.get("similarity_score", 0)
                    insights = match.get("match_insights", {})
                    
                    # Color based on rank
                    if rank == 1:
                        medal = "🥇"
                        color = "#ffd700"
                    elif rank == 2:
                        medal = "🥈"
                        color = "#c0c0c0"
                    elif rank == 3:
                        medal = "🥉"
                        color = "#cd7f32"
                    else:
                        medal = f"#{rank}"
                        color = "#666"
                    
                    with st.container():
                        col1, col2 = st.columns([1, 3])
                        
                        with col1:
                            st.markdown(f"""
                            <div style="text-align: center; padding: 1rem;">
                                <h1 style="color: {color}; margin: 0;">{medal}</h1>
                                <h3 style="color: #ff6b6b; margin: 0;">{score:.0%}</h3>
                                <p style="color: #666;">Match Score</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown(f"**Candidate ID:** `{match.get('external_student_id', 'Unknown')}`")
                            
                            # Show AI insights if available
                            if insights.get("ai_powered"):
                                st.markdown(f"🤖 **AI Assessment:** {insights.get('match_quality', 'Good')}")
                                
                                reasons = insights.get("recommended_because", [])
                                if reasons:
                                    st.markdown("**Why recommended:**")
                                    for reason in reasons[:3]:
                                        st.markdown(f"- {reason}")
                                
                                skill_analysis = insights.get("skill_analysis", {})
                                if skill_analysis.get("strong_matches"):
                                    st.markdown(f"**Strong skills:** {', '.join(skill_analysis['strong_matches'][:5])}")
                                if skill_analysis.get("skill_gaps"):
                                    st.markdown(f"**Skill gaps:** {', '.join(skill_analysis['skill_gaps'][:3])}")
                            else:
                                # Show skills breakdown
                                breakdown = insights.get("skills_breakdown", {})
                                st.markdown(f"**Final Score:** {insights.get('final_score', score):.0%}")
                                st.markdown(f"**Required Skills:** {breakdown.get('required_matched_count', 0)}/{breakdown.get('required_total_count', 0)}")
                                st.markdown(f"**Summary:** {insights.get('summary', 'N/A')}")
                        
                        st.markdown("---")
            else:
                st.error(f"❌ Matching failed: {result['error']}")

with tab2:
    st.markdown("### Find Best Jobs for a Candidate")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        candidate_id = st.selectbox(
            "Select Candidate",
            ["candidate_001", "candidate_002", "candidate_003", "candidate_004", 
             "candidate_005", "candidate_006", "candidate_007", "candidate_008"],
            format_func=lambda x: {
                "candidate_001": "Candidate A (Python, FastAPI, AWS)",
                "candidate_002": "Candidate B (Python, Django, React)",
                "candidate_003": "Candidate C (Java, Spring Boot, K8s)",
                "candidate_004": "Candidate D (ML, TensorFlow, PyTorch)",
                "candidate_005": "Candidate E (JavaScript, Node.js)",
                "candidate_006": "Candidate F (Data Eng, Spark, Airflow)",
                "candidate_007": "Candidate G (DevOps, Go, Terraform)",
                "candidate_008": "Candidate H (Full-stack, Python, React)"
            }.get(x, x)
        )
    
    with col2:
        top_k_jobs = st.slider("Number of Results", 1, 10, 5, key="top_k_jobs")
        min_score_jobs = st.slider("Minimum Score", 0.5, 1.0, 0.70, 0.05, key="min_score_jobs")
    
    if st.button("🔍 Find Matching Jobs", key="find_jobs", use_container_width=True):
        with st.spinner("🤖 AI is finding the best job opportunities..."):
            async def do_job_match():
                return await find_jobs_for_candidate(candidate_id, top_k_jobs, min_score_jobs)
            
            result = asyncio.run(do_job_match())
            
            if result["success"]:
                data = result["data"]
                matches = data.get("matches", [])
                
                st.success(f"✅ Found {len(matches)} matching jobs!")
                
                st.markdown("---")
                st.markdown("### 🎯 Recommended Jobs")
                
                for match in matches:
                    rank = match.get("rank", 0)
                    score = match.get("similarity_score", 0)
                    insights = match.get("match_insights", {})
                    
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"### {match.get('job_title', 'Unknown Position')}")
                            st.markdown(f"🏢 **{match.get('company_name', 'Unknown Company')}**")
                            
                            if insights.get("ai_powered"):
                                st.markdown(f"🤖 **AI Assessment:** {insights.get('match_assessment', 'Good Fit')}")
                                
                                reasons = insights.get("why_recommended", [])
                                if reasons:
                                    st.markdown("**Why this job fits you:**")
                                    for reason in reasons[:3]:
                                        st.markdown(f"- {reason}")
                                
                                next_steps = insights.get("next_steps", "")
                                if next_steps:
                                    st.success(f"💡 **Next Steps:** {next_steps}")
                            else:
                                st.markdown(f"**Summary:** {insights.get('summary', 'N/A')}")
                        
                        with col2:
                            st.markdown(f"""
                            <div style="text-align: center; background: linear-gradient(145deg, #1e3a5f, #2d5a87); padding: 1rem; border-radius: 10px;">
                                <h3 style="color: #ff6b6b; margin: 0;">#{rank}</h3>
                                <h2 style="color: white; margin: 0.5rem 0;">{score:.0%}</h2>
                                <p style="color: #b0c4de; margin: 0;">Match</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.markdown("---")
            else:
                st.error(f"❌ Matching failed: {result['error']}")

# Help section
st.markdown("---")
with st.expander("ℹ️ How Matching Works"):
    st.markdown("""
    **TalentMatch AI uses a multi-stage matching process:**
    
    1. **Semantic Embedding**: Both jobs and candidates are converted to 768-dimensional vectors using Gemini's text-embedding-004 model
    
    2. **Vector Search**: Qdrant finds the most similar candidates/jobs based on cosine similarity
    
    3. **Skills Analysis**: Required and preferred skills are compared for coverage scoring
    
    4. **Weighted Ranking**: Final scores combine similarity, required skills, and preferred skills based on customizable weights
    
    5. **AI Insights**: Top matches receive detailed AI-generated explanations using Gemini 2.5 Flash-Lite
    
    **Ranking Weights:**
    - **Semantic Similarity (default 60%)**: How well the overall profile matches the job description
    - **Required Skills (default 30%)**: Coverage of must-have skills
    - **Preferred Skills (default 10%)**: Coverage of nice-to-have skills
    """)

