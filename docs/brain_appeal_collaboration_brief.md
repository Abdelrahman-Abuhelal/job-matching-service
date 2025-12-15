## IPSI AI Matching Service – Collaboration Brief (for Brain Appeal)

### 1. What This Service Does

The goal is to add an **AI-powered matching service** to the IPSI platform that:

- For a given **job**, returns a **ranked list of student candidates** for that job, with simple explanations (skills matched, gaps, etc.).
- For a given **student**, returns a **ranked list of job candidates**, also with explanations.

In other words: this service turns IPSI’s matching from a largely **manual matching** into a **systematic, automated ranking engine** for jobs and students, drastically reducing the time needed to find the right candidates or opportunities.
IPSI keeps full control over data, user experience, and final decisions, while the AI continuously analyzes profiles and jobs in the background to surface the best matches and clear “reasons why” for each one.

---

### 2. Technologies Involved (High Level)

On my side, the matching logic will run in a small, self-contained service built with:

- **FastAPI** (Python) to expose a few HTTP APIs that IPSI can call.
- **Qdrant** as a vector database to store numerical “embeddings” of jobs and students for semantic search.
- The **Aleph Alpha** platform to:
  - Convert job descriptions and student profiles into embeddings.
  - Optionally generate natural-language insights for top matches.
- **Docker** to package the service so it can be deployed **inside IPSI’s infrastructure**, typically behind an existing reverse proxy such as **nginx** for HTTPS and routing.

From the IPSI / Brain Appeal side, the idea is that this runs **alongside** the existing IPSI platform:

- IPSI provides an environment where a Dockerized HTTP service can run safely (and, if desired, fronts it with your existing nginx or other reverse proxy).
- IPSI’s backend calls the AI service via standard HTTP requests, using the current IPSI technology stack – **no fundamental change** to how IPSI itself is built.

We should also discuss **Aleph Alpha integration**: for example, if an enterprise or institutional account is required, I would need support from your side to onboard and configure that integration under IPSI’s policies.

#### 2.1 Data Storage on the AI Side (High Level)

In production, the AI service expects two main storage components on its side:

- A small **PostgreSQL** database for structured, non-PII matching data, such as:
  - Internal records for jobs (IDs, titles, parsed fields).
  - Internal records for students (IDs and the fields actually used for matching).
  - Companies (ID, name, basic metadata if needed).
  - Optional match history (job–student pairs with scores/timestamps) for debugging and evaluation.

  We intentionally keep only a **small, non‑PII subset** of job and student data here (skills, education, location, etc.) so we can efficiently re‑embed when models or formats change, generate clear “why recommended” explanations, and debug or audit matches without repeatedly pulling full records from the IPSI database.

- **Qdrant** for the vector data:
  - One embedding per job and per student.
  - Lightweight payloads with external IDs and a few searchable attributes (e.g. type=job/student, basic filters).

The idea is that IPSI continues to be the **source of truth** for all platform data; the AI service keeps only what it needs for efficient matching and explanation.

---

### 3. How Data Flows (Conceptual)

Because we do not yet know IPSI’s exact database schema, this section is about **concepts**, not exact fields.

#### 3.1 Jobs

IPSI already stores jobs. When a job is **created** or **meaningfully updated**, IPSI would send the AI service:

- An internal **job ID** and its **company ID**.
- The **job title** and **description** (as HR writes it).
- Any structured information that exists and is relevant for matching, such as:
  - Required / preferred skills or tags.
  - Location / remote options.
  - Job type (internship, full-time, working student, etc.).
  - Education / experience expectations.

The AI service:

- Parses and stores a structured representation of that job.
- Creates or updates an embedding in Qdrant so we can later find matching students.

The same API call can be used for both first-time creation and later updates (an “upsert”).

#### 3.2 Students

IPSI already stores student profiles. When a student **creates** or **updates** their profile, IPSI would send:

- A **pseudonymous student ID** (no names or contact details needed).
- Their **skills** (technical and, if available, languages).
- **Education** (level, field, institution, graduation year).
- **Experience** entries (internships, working student jobs, projects) if available.
- **Preferences**, if IPSI tracks them (locations, job types, industries, remote preference).

The AI service:

- Stores a structured representation of the student.
- Creates or updates a student embedding in Qdrant.

Whether this happens immediately on every profile change or only at certain points (e.g. when HR runs matching) is an open decision we should take together.

#### 3.3 Matching Calls

There are two main use cases:

- **HR view** – “Find candidates for this job”  
  IPSI calls the service with a job ID (and possibly filters) to get:
  - A ranked list of students.
  - The scores and basic explanations per candidate.

- **Student view** – “Find jobs for this student”  
  IPSI calls the service with a student ID (and possibly company/other filters) to get:
  - A ranked list of jobs.
  - The scores and explanations per job.

On IPSI’s side, you can also add short-lived caching so repeated HR page loads do not repeatedly call the AI service, and invalidate the cache when a job or profile changes.

---

### 4. Data We Expect (High-Level, To Be Mapped)

In our early meetings we should map IPSI’s existing data model to the following conceptual needs:

- **Job**
  - Unique job ID and company ID.
  - Title and human-readable description.
  - Any existing structure for skills/tags, location, job type, education/experience.

- **Student**
  - Pseudonymous student ID.
  - Skills or tags.
  - Education information.
  - Experience and projects (if available).
  - Preferences (if tracked).

- **Company**
  - Company ID and name.
  - Optionally: industry, location, future matching preferences.

- **Relations**
  - Information about who applied to which job (if we want to support “rank applicants only” as a mode, in addition to searching all students).

We will not decide every field in advance. The goal is to understand what you already have and which fields give the best matching quality with minimal extra work.

---

### 5. Key Questions to Discuss Together

These are the main design choices where I need your input:

- **When to call the AI service**
  - For jobs: on initial creation and whenever matching-relevant fields change (title, description, skills, location, type), not for every minor edit.
  - For students: do we update embeddings as soon as profiles change, or at specific times (e.g. when running matching)?

- **Who is matched against whom**
  - For a job:  
    - Only students who applied to that job,  
    - All eligible students in the system,  
    - Or both options available in the IPSI UI.
  - For a student:  
    - All open jobs, or limited by certain business rules (e.g. certain companies or locations)?

- **HR control over ranking**
  - How should HR express their preferences?
    - As simple **textual options** (e.g. “strict on required skills”, “more flexible”), which we interpret inside the service, or
    - As **explicit percentages/weights** (e.g. sliders for similarity vs skills vs other factors) that are used in an extra calculation on top of the similarity search.
  - Which approach fits best with IPSI’s UX and HR expectations?

- **Caching**
  - Likely best handled in the IPSI backend (e.g. cache match results for a short time and clear them when jobs or profiles change), so the AI service can remain stateless.

- **UI interfaces**
  - Which screens or components will IPSI need to build or adapt?
    - HR job view showing ranked candidates and explanations.
    - Controls for HR to adjust ranking preferences (if we expose them).
    - Student dashboard elements for “recommended jobs”.
  - How these should look and behave is something we should design together.

---

### 6. Privacy, Consent, and GDPR – Principles

Some initial principles we can refine with your legal and compliance teams:

- **Data minimization**
  - The AI service does not need direct identifiers:
    - No names, emails, phone numbers, full postal addresses, or dates of birth.
  - We work only with IDs and matching-related attributes (skills, education, experience, preferences).

- **Roles and control**
  - IPSI remains the controller of all student and company data.
  - The AI service runs inside your infrastructure and is used solely for matching and recommendations.
  - IPSI decides what is sent, when, and under which legal basis (consent, contract, legitimate interest).

- **Consent and transparency**
  - If IPSI wants explicit consent for “AI-based matching / recommendations”, we can respect a simple flag (e.g. include or exclude students from AI matching based on a consent field you manage).
  - Explanations from the service (“skills matched”, “skills missing”) can help keep the matching process transparent.

- **Rights and retention**
  - IPSI defines data retention policies and how to handle deletion/exports.
  - The AI service can later expose mechanisms to delete or export a student’s data from the matching store, so IPSI can fulfil GDPR requests end-to-end.

---

### 7. 12-Week Timeline – How We Could Work Together

Given a 12-week window, a pragmatic high-level plan could be:

- **Weeks 1–2 – Understanding & Design**
  - Walk through IPSI’s data model for jobs, students, companies, and applications.
  - Agree on what data to exchange and when the AI service will be called.
  - Clarify privacy/consent expectations and constraints.

- **Weeks 3–6 – Prototype Integration**
  - Deploy the Dockerized AI service in a test environment (behind nginx or similar).
  - Wire basic data flows: sending jobs and students on meaningful changes, calling the matching APIs from a staging HR/student UI.
  - Get early feedback on match quality and responsiveness.

- **Weeks 7–10 – Hardening**
  - Improve error handling and fallbacks when the AI service is slow or unavailable.
  - Tune default ranking behaviour with HR/product stakeholders.
  - Review logging and monitoring, and verify we are respecting privacy and minimization.

- **Weeks 11–12 – Pilot & Go-Live Preparation**
  - Run a limited pilot with selected HR users and/or students.
  - Apply final tweaks based on feedback.
  - Prepare production rollout and basic post-launch support/monitoring.

From your side, the main needs are:

- A contact person who understands the IPSI data model and backend.
- A place to run the Dockerized service in your infrastructure (with nginx or another reverse proxy managed by your DevOps/operations team).
- Support with **Aleph Alpha integration** (e.g. access to an appropriate account, configuration under IPSI’s usage and security policies).
- Time in the first weeks to co-design data mapping, call timing, and privacy constraints.
- Agreement on a **communication channel** (e.g. Teams/Slack/email) for day-to-day questions and quick clarifications.

This brief is intended as a discussion starter for our first 1–2 hour meeting, not a fixed specification. We can adjust details once we see your current system and constraints.


