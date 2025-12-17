# TalentMatch AI — Business One‑Pager + Data Flow

### Executive summary (1 minute)
**TalentMatch AI** helps HR teams **find the best candidates for a job** (and helps candidates discover relevant jobs) by turning job descriptions and candidate profiles into **clear, ranked recommendations** with short explanations.

**Outcome:** faster shortlists, more consistent screening, and better transparency on *why* someone is recommended.

---

### Who it’s for
- **HR / Recruiters**: quickly shortlist top candidates for a given job.
- **Hiring managers**: see *evidence-based* fit (skills match + reasoning) to make faster decisions.
- **Candidates / Students (optional view)**: discover jobs that match their profile and see improvement suggestions.

---

### The problem it solves
Traditional screening is slow and inconsistent because:
- Job descriptions are unstructured (free text).
- Candidate profiles vary widely in format and completeness.
- Keyword matching misses relevant people (synonyms, transferable skills).
- “Why this candidate?” is hard to explain and audit.

---

### What the system does (in plain language)
1. **Understand job posts**: extract key requirements (title, skills, location, type, etc.).
2. **Understand candidate profiles**: summarize skills + education + preferences.
3. **Find similar profiles**: identify candidates/jobs that “mean the same thing” even if wording differs.
4. **Rank with business rules**: combine “overall fit” + “must-have skills” + “nice-to-have skills”.
5. **Explain results**: show matched skills, missing skills, and short recommendations.

---

### Data flow (business view)
```mermaid
flowchart LR
  A[HR / Recruiter] -->|adds job| B[TalentMatch AI]
  C[Candidates / Students] -->|add or update profile| B

  B --> D[AI Understanding\n(standardizes job + profile)]
  D --> E[Matching & Ranking\n(shortlist + ordering)]
  E --> F[Insights\nwhy recommended + skill gaps]

  F --> G[HR Results\nranked candidates]
  F --> H[Candidate Results\nranked jobs]

  B --> I[(Data Store)\nJobs, profiles, match history]
```

---

### What goes in / what comes out
- **Inputs**
  - Job description text (plus company/job IDs)
  - Candidate profile (skills, education, preferences)
  - Optional ranking preference (how strict you want must‑have skills to be)

- **Outputs**
  - Ranked list of matches (Top K)
  - For each match:
    - **Final score** (overall)
    - **Skills matched / missing**
    - Short explanation (“recommended because…”)
  - Stored match history (for review and analytics)

---

### How ranking is controlled (business knobs)
HR can control *what “best match” means* by adjusting weights:
- **Overall fit**: best when you want broad potential / transferable skills.
- **Must‑have match**: best when missing skills is a deal‑breaker.
- **Nice‑to‑have bonus**: best when extras differentiate top candidates.

The system then produces a **single final score** and re-orders results accordingly.

---

### Security & access (business view)
- The system requires a **token** to use protected actions (add/update data and run matching).
- This prevents unauthorized usage and supports controlled access in demos and deployments.

---

### Operational notes (what to expect)
- **Best use case**: internships / early careers where transferable skills matter and volume is high.
- **Limitations**: large bulk imports can be rate-limited by the AI provider; missing profile data reduces match quality.

---

### Success metrics (suggested KPIs)
- **Time-to-shortlist** (minutes per job) ↓
- **Recruiter consistency** (variance between reviewers) ↓
- **Interview conversion rate** (shortlist → interview) ↑
- **Coverage transparency** (% matches with clear skill breakdown) ↑

---

### If you want a technical appendix
Tell me your audience (e.g., “CEO pitch deck”, “HR team”, or “engineering handover”) and I’ll add a short optional appendix that maps this business flow to the exact API endpoints and components.


