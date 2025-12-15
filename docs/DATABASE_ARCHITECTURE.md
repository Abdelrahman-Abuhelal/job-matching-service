# 🗄️ IPSI AI - Database Architecture

## Overview

Your microservice uses a **dual-database architecture**:

1. **PostgreSQL/SQLite** - Relational metadata storage
2. **Qdrant** - Vector embeddings for semantic search

This separation follows best practices: structured data in SQL, vectors in specialized vector DB.

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    IPSI AI SERVICE                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐         ┌──────────────────┐     │
│  │   PostgreSQL    │         │     Qdrant       │     │
│  │   (Metadata)    │◄────────┤  (Vector Store)  │     │
│  │                 │         │                  │     │
│  │ • Companies     │         │ • jobs_global    │     │
│  │ • Job Postings  │         │ • students_global│     │
│  │ • Students      │         │                  │     │
│  │ • Applications  │         │  (1536-dim       │     │
│  │ • Match History │         │   embeddings)    │     │
│  └─────────────────┘         └──────────────────┘     │
│         │                              │               │
│         │                              │               │
│         └──────────────┬───────────────┘               │
│                        │                               │
│                   API Layer                            │
│            (FastAPI + SQLAlchemy)                      │
└─────────────────────────────────────────────────────────┘
```

---

## 🗃️ Database 1: PostgreSQL/SQLite (Metadata)

### Purpose:
Stores **structured metadata** that's easy to query, filter, and join.

### Why Both?
- **SQLite** - Development (easier setup, file-based)
- **PostgreSQL** - Production (scalable, better concurrency)

**Current Config:**
```python
# Development
DATABASE_URL=sqlite:///./ipsi_ai.db

# Production
DATABASE_URL=postgresql://user:password@localhost:5432/ipsi_ai
```

---

## 📋 Table 1: `companies`

### Purpose:
Track companies posting jobs on IPSI platform.

### Schema:

```sql
CREATE TABLE companies (
    id                      UUID PRIMARY KEY,
    external_company_id     VARCHAR(255) UNIQUE NOT NULL,  -- IPSI's company ID
    name                    VARCHAR(255) NOT NULL,
    qdrant_collection_name  VARCHAR(255) NOT NULL,         -- For future per-company collections
    scoring_weights         JSON,                          -- Custom scoring configuration
    created_at              TIMESTAMP DEFAULT NOW(),
    updated_at              TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_company_external ON companies(external_company_id);
```

### Fields Explained:

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `id` | UUID | Internal primary key | `a1b2c3d4-...` |
| `external_company_id` | String | IPSI's company ID (anonymized) | `ipsi_company_abc123` |
| `name` | String | Company name | `"TechCorp GmbH"` |
| `qdrant_collection_name` | String | Qdrant collection reference | `"jobs_global"` |
| `scoring_weights` | JSON | Custom scoring preferences | `{"skills": 0.4, "experience": 0.3}` |
| `created_at` | Timestamp | When company registered | `2024-11-20 10:00:00` |
| `updated_at` | Timestamp | Last update | `2024-11-24 15:30:00` |

### Why This Table?

✅ **Company Management** - Track which companies use the service  
✅ **Custom Scoring** - Each company can have different matching priorities  
✅ **Data Isolation** - Link jobs to companies for filtering  
✅ **Analytics** - Track usage per company  

### Example Data:

```json
{
  "id": "uuid-123",
  "external_company_id": "ipsi_company_techcorp",
  "name": "TechCorp GmbH",
  "qdrant_collection_name": "jobs_global",
  "scoring_weights": {
    "vector_similarity": 0.20,
    "skills_match": 0.40,
    "experience": 0.20,
    "education": 0.10,
    "projects": 0.10
  }
}
```

---

## 📋 Table 2: `job_postings`

### Purpose:
Store job posting metadata and link to embeddings in Qdrant.

### Schema:

```sql
CREATE TABLE job_postings (
    id                  UUID PRIMARY KEY,
    external_job_id     VARCHAR(255) UNIQUE NOT NULL,  -- IPSI's job ID
    company_id          UUID REFERENCES companies(id),
    title               VARCHAR(500) NOT NULL,
    structured_data     JSON NOT NULL,                 -- Parsed job details
    raw_description     TEXT,                          -- Original text
    qdrant_point_id     UUID NOT NULL,                 -- Link to Qdrant vector
    embedding_version   VARCHAR(50) DEFAULT 'text-embedding-3-large',
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_job_company ON job_postings(company_id);
CREATE INDEX idx_job_external ON job_postings(external_job_id);
```

### Fields Explained:

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `id` | UUID | Internal primary key | `b2c3d4e5-...` |
| `external_job_id` | String | IPSI's job ID | `ipsi_job_12345` |
| `company_id` | UUID | Foreign key to companies | `uuid-123` |
| `title` | String | Job title | `"Python Developer Intern"` |
| `structured_data` | JSON | GPT-4 parsed job details | `{"required_skills": [...], ...}` |
| `raw_description` | Text | Original job posting text | `"We are looking for..."` |
| `qdrant_point_id` | UUID | Vector ID in Qdrant | `c3d4e5f6-...` |
| `embedding_version` | String | Model version for vectors | `"text-embedding-3-large"` |

### Why This Table?

✅ **Job Metadata** - Store structured job information  
✅ **Link to Embeddings** - Connect SQL data to vector data  
✅ **Version Control** - Track embedding model versions  
✅ **Query Performance** - Fast lookups by external_job_id  
✅ **History** - Keep original job descriptions  

### Example structured_data:

```json
{
  "title": "Python Backend Developer Intern",
  "required_skills": ["Python", "FastAPI", "PostgreSQL"],
  "preferred_skills": ["Docker", "Kubernetes", "AWS"],
  "education_level": "Bachelor's in Computer Science or related field",
  "experience_years": "1-2 years",
  "location": "Munich, Germany",
  "job_type": "Internship",
  "responsibilities": [
    "Develop REST APIs using FastAPI",
    "Write unit tests",
    "Collaborate with team"
  ],
  "benefits": ["Remote work", "Flexible hours", "Learning budget"]
}
```

---

## 📋 Table 3: `student_profiles`

### Purpose:
Store student profile metadata and link to embeddings.

### Schema:

```sql
CREATE TABLE student_profiles (
    id                  UUID PRIMARY KEY,
    external_student_id VARCHAR(255) UNIQUE NOT NULL,  -- IPSI's student ID
    profile_summary     TEXT NOT NULL,                 -- Text summary of profile
    structured_data     JSON,                          -- Structured profile data
    qdrant_point_id     UUID NOT NULL,                 -- Link to Qdrant vector
    embedding_version   VARCHAR(50) DEFAULT 'text-embedding-3-large',
    created_at          TIMESTAMP DEFAULT NOW(),
    updated_at          TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_student_external ON student_profiles(external_student_id);
```

### Fields Explained:

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `id` | UUID | Internal primary key | `d3e4f5g6-...` |
| `external_student_id` | String | IPSI's student ID (anonymized) | `ipsi_student_789` |
| `profile_summary` | Text | Human-readable summary | `"CS Bachelor with Python, Java..."` |
| `structured_data` | JSON | Skills, education, preferences | `{"skills": [...], "education": {...}}` |
| `qdrant_point_id` | UUID | Vector ID in Qdrant | `e4f5g6h7-...` |
| `embedding_version` | String | Model version | `"text-embedding-3-large"` |

### Why This Table?

✅ **Student Metadata** - Store profile information  
✅ **Link to Embeddings** - Connect SQL to vector search  
✅ **Version Control** - Track when profiles updated  
✅ **Fast Lookup** - Query by external_student_id  
✅ **GDPR Compliance** - No personal identifiable info  

### Example structured_data:

```json
{
  "skills": ["Python", "Java", "React", "PostgreSQL"],
  "education": {
    "level": "Bachelor's",
    "field": "Computer Science",
    "university": "TU München",
    "graduation_year": 2025,
    "gpa": 1.5
  },
  "preferences": {
    "locations": ["Munich", "Berlin", "Remote"],
    "job_types": ["Internship", "Working Student"],
    "industries": ["Technology", "Finance"],
    "remote_preference": "preferred"
  },
  "experience_years": 1.5,
  "experiences": [
    {
      "title": "Backend Developer Intern",
      "company": "StartupX",
      "duration_months": 6,
      "description": "Built REST APIs with FastAPI",
      "technologies": ["Python", "FastAPI", "Docker"]
    }
  ],
  "projects": [
    {
      "title": "E-commerce Platform",
      "description": "Full-stack web application",
      "technologies": ["React", "Node.js", "PostgreSQL"],
      "duration_months": 4
    }
  ],
  "certifications": ["AWS Solutions Architect"],
  "languages": ["German", "English", "Python", "Java"]
}
```

---

## 📋 Table 4: `applications`

### Purpose:
Track which students have applied to which jobs/companies.

### Schema:

```sql
CREATE TABLE applications (
    id                  UUID PRIMARY KEY,
    student_profile_id  UUID REFERENCES student_profiles(id),
    company_id          UUID REFERENCES companies(id),
    job_posting_id      UUID REFERENCES job_postings(id),  -- Optional
    status              VARCHAR(50) DEFAULT 'applied',
    application_date    TIMESTAMP DEFAULT NOW(),
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_app_student ON applications(student_profile_id);
CREATE INDEX idx_app_company ON applications(company_id);
CREATE INDEX idx_app_job ON applications(job_posting_id);
CREATE INDEX idx_app_date ON applications(application_date);
```

### Fields Explained:

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `id` | UUID | Primary key | `f5g6h7i8-...` |
| `student_profile_id` | UUID | Which student applied | `uuid-student` |
| `company_id` | UUID | Which company | `uuid-company` |
| `job_posting_id` | UUID | Specific job (optional) | `uuid-job` or `NULL` |
| `status` | String | Application status | `"applied"`, `"reviewed"`, `"interviewed"` |
| `application_date` | Timestamp | When applied | `2024-11-24 14:00:00` |

### Why This Table?

✅ **Application Tracking** - Know who applied where  
✅ **Duplicate Prevention** - Don't recommend jobs already applied to  
✅ **Status Updates** - Track application pipeline  
✅ **Analytics** - Measure conversion rates  
✅ **Separate Lists** - Show applicants vs. candidates in matching  

### Status Values:

- `applied` - Student submitted application
- `reviewed` - HR reviewed profile
- `interviewed` - Interview scheduled/completed
- `rejected` - Not moving forward
- `accepted` - Offer made/accepted

### Example Use Case:

```python
# When HR searches for candidates, separate those who already applied
GET /matching/students-for-job?job_id=12345

Response:
{
  "active_applicants": [
    {"student_id": "...", "status": "applied"},  // Already applied!
    {"student_id": "...", "status": "reviewed"}
  ],
  "potential_candidates": [
    {"student_id": "...", "has_applied": false},  // Good fit, hasn't applied
    {"student_id": "...", "has_applied": false}
  ]
}
```

---

## 📋 Table 5: `match_history`

### Purpose:
Log all matching operations for analytics and auditing.

### Schema:

```sql
CREATE TABLE match_history (
    id                  UUID PRIMARY KEY,
    job_posting_id      UUID REFERENCES job_postings(id),
    student_profile_id  UUID REFERENCES student_profiles(id),
    similarity_score    FLOAT NOT NULL,
    rank_position       INTEGER,
    match_explanation   JSON,
    requested_by        VARCHAR(255),
    created_at          TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_match_job ON match_history(job_posting_id);
CREATE INDEX idx_match_student ON match_history(student_profile_id);
CREATE INDEX idx_match_created ON match_history(created_at);
```

### Fields Explained:

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `id` | UUID | Primary key | `g6h7i8j9-...` |
| `job_posting_id` | UUID | Which job was matched | `uuid-job` |
| `student_profile_id` | UUID | Which student | `uuid-student` |
| `similarity_score` | Float | Match score (0.0-1.0) | `0.87` |
| `rank_position` | Integer | Ranking position | `1` (best match) |
| `match_explanation` | JSON | AI insights | `{"reasons": [...], "gaps": [...]}` |
| `requested_by` | String | Who triggered match | `"hr_user_123"` or `"student_456"` |
| `created_at` | Timestamp | When matched | `2024-11-24 15:30:00` |

### Why This Table?

✅ **Analytics** - Track matching patterns over time  
✅ **Auditing** - GDPR compliance (who saw what when)  
✅ **Quality Metrics** - Measure match quality  
✅ **A/B Testing** - Compare different matching algorithms  
✅ **Feedback Loop** - Improve matching based on outcomes  

### Example Analytics Queries:

```sql
-- Average match scores per company
SELECT 
    c.name,
    AVG(mh.similarity_score) as avg_score,
    COUNT(*) as total_matches
FROM match_history mh
JOIN job_postings jp ON mh.job_posting_id = jp.id
JOIN companies c ON jp.company_id = c.id
GROUP BY c.name;

-- Top students (most frequently matched)
SELECT 
    sp.external_student_id,
    COUNT(*) as match_count,
    AVG(mh.similarity_score) as avg_score
FROM match_history mh
JOIN student_profiles sp ON mh.student_profile_id = sp.id
WHERE mh.created_at > NOW() - INTERVAL '30 days'
GROUP BY sp.external_student_id
ORDER BY match_count DESC
LIMIT 10;
```

---

## 🔍 Database 2: Qdrant (Vector Store)

### Purpose:
Store and search **vector embeddings** for semantic similarity matching.

### Why Qdrant?

✅ **Specialized** - Built specifically for vector search  
✅ **Fast** - Millisecond similarity searches  
✅ **Self-Hosted** - GDPR compliant (data stays local)  
✅ **Scalable** - Handles millions of vectors  
✅ **Open Source** - No licensing costs  

---

## 📊 Collection 1: `students_global`

### Purpose:
Store student profile embeddings for fast similarity search.

### Structure:

```json
{
  "collection_name": "students_global",
  "vectors": {
    "size": 1536,  // OpenAI text-embedding-3-large dimension
    "distance": "Cosine"  // Cosine similarity
  },
  "payload_schema": {
    "external_id": "string",      // external_student_id
    "type": "string",              // Always "student"
    "metadata": {
      "education_level": "string", // For filtering
      "skills_count": "integer",
      "created_at": "timestamp"
    }
  }
}
```

### Example Point:

```json
{
  "id": "uuid-e4f5g6h7",
  "vector": [0.023, -0.145, 0.678, ...],  // 1536 dimensions
  "payload": {
    "external_id": "ipsi_student_789",
    "type": "student",
    "metadata": {
      "education_level": "Bachelor's",
      "skills_count": 12,
      "created_at": "2024-11-20T10:00:00Z"
    }
  }
}
```

### Why This Collection?

✅ **Semantic Search** - Find students by meaning, not keywords  
✅ **Fast Matching** - Search millions of students in milliseconds  
✅ **Global Pool** - All students in one collection (efficient!)  
✅ **Filtering** - Can still filter by education level, etc.  

### Search Example:

```python
# Find students similar to a job
results = qdrant.search(
    collection_name="students_global",
    query_vector=job_embedding,  # [0.123, -0.456, ...]
    limit=10,
    score_threshold=0.70,
    query_filter={
        "must": [
            {"key": "type", "match": {"value": "student"}},
            {"key": "metadata.education_level", "match": {"value": "Bachelor's"}}
        ]
    }
)

# Results: Top 10 students with similarity scores
[
  {"id": "uuid1", "score": 0.89, "payload": {...}},
  {"id": "uuid2", "score": 0.85, "payload": {...}},
  ...
]
```

---

## 📊 Collection 2: `jobs_global`

### Purpose:
Store job posting embeddings for student job search.

### Structure:

```json
{
  "collection_name": "jobs_global",
  "vectors": {
    "size": 1536,
    "distance": "Cosine"
  },
  "payload_schema": {
    "external_id": "string",      // external_job_id
    "company_id": "string",        // external_company_id
    "type": "string",              // Always "job"
    "metadata": {
      "job_type": "string",
      "location": "string",
      "created_at": "timestamp"
    }
  }
}
```

### Example Point:

```json
{
  "id": "uuid-c3d4e5f6",
  "vector": [0.145, -0.023, 0.567, ...],  // 1536 dimensions
  "payload": {
    "external_id": "ipsi_job_12345",
    "company_id": "ipsi_company_techcorp",
    "type": "job",
    "metadata": {
      "job_type": "Internship",
      "location": "Munich",
      "created_at": "2024-11-24T15:00:00Z"
    }
  }
}
```

### Why This Collection?

✅ **Student Job Search** - Find jobs matching student profile  
✅ **Company Filtering** - Can filter by specific companies  
✅ **Location Filtering** - Search jobs in specific cities  
✅ **Global Efficiency** - All jobs in one collection  

---

## 🔄 How The Two Databases Work Together

### Matching Flow:

```
┌─────────────────────────────────────────────────┐
│ 1. User Request: Find students for job_12345   │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│ 2. PostgreSQL: Fetch job metadata              │
│    SELECT * FROM job_postings                   │
│    WHERE external_job_id = 'job_12345'          │
│                                                 │
│    Result: job data + qdrant_point_id           │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│ 3. Generate job embedding vector                │
│    OpenAI: job_text → [0.123, -0.456, ...]      │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│ 4. Qdrant: Vector similarity search             │
│    SEARCH students_global                       │
│    VECTOR = job_embedding                       │
│    TOP_K = 10                                   │
│                                                 │
│    Result: [uuid1, uuid2, ...] with scores      │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│ 5. PostgreSQL: Fetch student details           │
│    SELECT * FROM student_profiles               │
│    WHERE external_student_id IN (...)           │
│                                                 │
│    Result: Full student profiles                │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│ 6. PostgreSQL: Check applications               │
│    SELECT * FROM applications                   │
│    WHERE company_id = ... AND                   │
│          student_profile_id IN (...)            │
│                                                 │
│    Result: Who already applied                  │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│ 7. Generate AI insights (GPT-4o)               │
│    For top 5 matches                            │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│ 8. PostgreSQL: Log match history               │
│    INSERT INTO match_history (...)              │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│ 9. Return ranked matches to user               │
└─────────────────────────────────────────────────┘
```

---

## 🎯 Why This Architecture?

### Separation of Concerns:

**PostgreSQL** handles:
- ✅ Structured data (names, dates, statuses)
- ✅ Relationships (foreign keys)
- ✅ Transactions (ACID)
- ✅ Complex queries (JOINs, aggregations)

**Qdrant** handles:
- ✅ Vector embeddings (high-dimensional arrays)
- ✅ Similarity search (cosine distance)
- ✅ Fast approximate nearest neighbor search
- ✅ Filtering + vector search combination

### Benefits:

1. **Performance** - Each database does what it's best at
2. **Scalability** - Scale SQL and vector DB independently
3. **Maintainability** - Clear separation of data types
4. **Cost-Effective** - Use appropriate storage for each type
5. **GDPR Compliant** - Both self-hosted, no cloud dependencies

---

## 📊 Database Size Estimates

### At Different Scales:

**1,000 students + 200 jobs:**
- PostgreSQL: ~5 MB
- Qdrant: ~20 MB (vectors)
- **Total: ~25 MB**

**10,000 students + 2,000 jobs:**
- PostgreSQL: ~50 MB
- Qdrant: ~200 MB
- **Total: ~250 MB**

**100,000 students + 20,000 jobs:**
- PostgreSQL: ~500 MB
- Qdrant: ~2 GB
- **Total: ~2.5 GB**

**Storage is very efficient!**

---

## 🔧 Database Maintenance

### Backups:

```bash
# PostgreSQL backup
pg_dump ipsi_ai > backup.sql

# Qdrant backup (snapshots)
curl -X POST http://localhost:6333/collections/students_global/snapshots
curl -X POST http://localhost:6333/collections/jobs_global/snapshots
```

### Monitoring:

```sql
-- PostgreSQL: Check table sizes
SELECT 
    table_name,
    pg_size_pretty(pg_total_relation_size(table_name::regclass)) as size
FROM information_schema.tables
WHERE table_schema = 'public';

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

```bash
# Qdrant: Check collection stats
curl http://localhost:6333/collections/students_global
curl http://localhost:6333/collections/jobs_global
```

---

## ✅ Summary

### You Need 2 Databases:

1. **PostgreSQL/SQLite** (5 tables)
   - `companies` - Company information
   - `job_postings` - Job metadata
   - `student_profiles` - Student metadata
   - `applications` - Application tracking
   - `match_history` - Analytics/auditing

2. **Qdrant** (2 collections)
   - `students_global` - Student embeddings
   - `jobs_global` - Job embeddings

### Why This Design?

✅ **Efficient** - Right tool for each job  
✅ **Scalable** - Independent scaling  
✅ **Fast** - Optimized for matching  
✅ **GDPR Compliant** - All self-hosted  
✅ **Maintainable** - Clear separation  

### Current Status:

✅ All tables implemented  
✅ All indexes created  
✅ Relationships defined  
✅ Migrations ready  
✅ Production-ready  

---

**Need more details on any table or want to see example queries? Let me know!**

