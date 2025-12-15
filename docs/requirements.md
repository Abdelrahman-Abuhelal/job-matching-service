IPSI-AI MVP – Technical Requirements for Implementation
1. Project Overview

This MVP aims to integrate an AI-powered candidate–job matching engine into the IPSI platform.
Due to DHBW’s technical and legal restrictions, the AI module must run as a separate, self-contained service with no direct access to DHBW servers or IPSI source code.

The integration will be done exclusively through secure API endpoints implemented by Brain Appeal on the IPSI side.

The AI service (developed by me) will:

Receive anonymized student and job data via API

Process and generate match scores / rankings

Return results to IPSI via a response endpoint

Run entirely inside DHBW / Brain Appeal’s local environment via Docker

The MVP implementer will turn the existing prototype into a stable, deployable application.

2. Constraints (Important)
2.1 No direct access to IPSI program code

I cannot read or modify IPSI source code.

Brain Appeal must implement any internal changes needed for integration.

All interactions must happen via documented APIs they create.

2.2 No direct access to DHBW servers

I cannot log in, deploy, or modify anything inside DHBW infrastructure.

The AI service must be delivered as:

A runnable Docker container, or

A ready-to-deploy set of Docker images + Compose file.

2.3 No access to personal student/company data

All data used must be:

anonymized, OR

synthetic sample data, OR

real data only from users who explicitly give consent.

The AI module must not store any personal identifiers.

2.4 GDPR & EU compliance

All storage (embeddings, metadata, logs) must stay on DHBW/Brain Appeal machines.

No cloud-hosted components unless DHBW explicitly approves (e.g., Aleph Alpha).

3. Architecture Requirements
3.1 High-Level Flow

IPSI sends student profile + job specification (anonymized) → AI API

AI module processes:

embeddings generation

matching score computation

ranking

AI module returns a JSON response with:

match_score

top reasons (optional)

extracted skills (optional)

IPSI displays scores using their existing UI.

3.2 AI Service Responsibilities

The AI service must include:

A. Embedding Component

Generates vector embeddings for:

Student CV text

Skills

Job descriptions

Pluggable backend:

Aleph Alpha (preferred for EU)

OpenAI (if allowed)

Local embedding model (optional for future)

B. Vector Store

Must use self-hosted Qdrant.

Should run inside the same Docker environment.

Handles similarity search.

C. Matching Engine

Implements:

Semantic similarity

Skills extraction (regex/ML)

Weighted scoring formula:

skills match %

text similarity

optional preference match

D. API Layer (FastAPI or Node recommended)

Endpoints needed:

Endpoint	Method	Description
/embed/student	POST	Receives student data → returns embedding
/embed/job	POST	Receives job data → returns embedding
/match/student-job	POST	Receives both → returns match score + explanation
/health	GET	Health check for deployment

All responses must be clean JSON.

4. Data Requirements
4.1 Required Data From IPSI

You will only receive what IPSI can legally provide.
These fields are the minimum needed for meaningful matching:

Student Data Fields

skills_text — list or free-text skills

experience_text — short description

education_text — optional

preferences — optional (cities, type, etc.)

Job Data Fields

job_description_text

required_skills

optional_skills

tags (from IPSI form)

What You Never Receive

❌ names
❌ emails
❌ addresses
❌ phone numbers
❌ IDs

Everything must be anonymized.

5. Deployment & Packaging Requirements
5.1 Deliverables

The MVP implementer must produce:

Dockerfile for AI backend

docker-compose.yml including:

AI service container

Qdrant container

Environment variable structure:

model access keys (if any)

logging toggle

embedding provider type (e.g., ALEPH_ALPHA vs OPENAI vs LOCAL)

5.2 Logging

Must be anonymized.

No raw data should be written to logs.

Only technical logs allowed (errors, latency, etc.).

6. Security Requirements

HTTPS or internal mTLS

Token-based API authentication (JWT or static API key)

Rate limiting optional for now

No data persistence outside Qdrant

No outbound traffic unless approved (e.g., Aleph Alpha)

7. MVP Deliverables

The MVP should include:

1. Functional AI Matching Module

Student→Job match score computation

Simple rules + semantic similarity

Basic explanation (“skills overlap: X%, semantic similarity: Y%”)

2. API Implementation

All endpoints functional and testable with sample data.

3. Local Deployment

A team at DHBW / Brain Appeal must be able to run:

docker compose up


and have the system running locally.

4. Documentation

API documentation (OpenAPI/Swagger)

Integration guide for Brain Appeal:

endpoints

request/response examples

authentication instructions

8. What the MVP Is NOT Required To Do

To avoid overbuilding, the MVP does not need:

UI components

Full machine-learning model training

Multi-user management

Stored historical match results

Advanced analytics

The first goal is a working AI engine that IPSI can call.

9. Next Step for the Implementer

The implementer should:

Turn the prototype/MVP logic into production-ready code

Implement the API architecture described above

Package it into a self-contained Dockerized application

Ensure all components run locally with no external dependencies

Provide clear integration documentation for Brain Appeal