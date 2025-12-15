# TalentMatch AI

> AI-powered talent matching service using semantic search and Gemini AI

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash_Lite-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Overview

TalentMatch AI is a standalone AI-powered matching service that intelligently connects candidates with job opportunities. It uses Google Gemini for AI capabilities and Qdrant vector database for semantic similarity search.

### Key Features

- **Intelligent Job Parsing**: Uses Gemini 2.5 Flash-Lite to extract structured data from raw job descriptions
- **Semantic Matching**: Generates embeddings for jobs and candidates for similarity-based matching
- **AI-Powered Insights**: Detailed match explanations with skill analysis and recommendations
- **Streamlit Demo UI**: Modern web interface for showcasing capabilities
- **RESTful API**: Clean, documented API endpoints for integration
- **JWT Authentication**: Secure authentication for all endpoints
- **Docker Ready**: Fully containerized for easy deployment

## Architecture

```
┌─────────────────────┐
│  Streamlit Demo UI  │ (Frontend)
└──────────┬──────────┘
           │ HTTP Requests
           ▼
┌─────────────────────────────────────┐
│   TalentMatch AI Backend            │
│   ┌─────────────┐  ┌─────────────┐  │
│   │   FastAPI   │  │   SQLite    │  │
│   │   Service   │──│  (Metadata) │  │
│   └──────┬──────┘  └─────────────┘  │
│          │                          │
│          ▼                          │
│   ┌─────────────┐                   │
│   │   Qdrant    │                   │
│   │  (Vectors)  │                   │
│   └─────────────┘                   │
└─────────────────────────────────────┘
           │
           ▼
   Google Gemini API (Embeddings + AI)
```

## Tech Stack

- **Backend**: Python 3.11, FastAPI
- **Database**: SQLite (demo) / PostgreSQL (production), Qdrant (vector search)
- **AI/ML**: Google Gemini 2.5 Flash-Lite, text-embedding-004
- **Frontend**: Streamlit
- **Authentication**: JWT tokens
- **Deployment**: Docker, Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Google Gemini API key (free at [Google AI Studio](https://aistudio.google.com/))
- Python 3.11+ (for local development)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd talentmatch-ai

# Create .env file
cp .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your-gemini-api-key-here
```

### 2. Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# The API will be available at http://localhost:8000
# API documentation: http://localhost:8000/docs
# Streamlit UI: http://localhost:8501
```

### 3. Initialize Database

```bash
# In a new terminal, run database initialization
docker-compose exec fastapi python scripts/init_db.py
```

### 4. Seed Sample Data

```bash
# Load sample jobs and candidates
docker-compose exec fastapi python scripts/seed_database.py
```

### 5. Generate Test Token

```bash
# Generate a JWT token for testing
docker-compose exec fastapi python scripts/generate_test_token.py
```

## API Endpoints

### Health Check

```bash
GET /api/v1/health
```

Returns the health status of the service and its dependencies.

### Parse Job Description

```bash
POST /api/v1/jobs/parse
Authorization: Bearer <token>

{
  "external_job_id": "job_12345",
  "external_company_id": "company_abc",
  "company_name": "Tech Corp",
  "raw_description": "We are seeking a Python developer..."
}
```

Parses a job description using Gemini AI and stores it with embeddings.

### Update Candidate Profile

```bash
POST /api/v1/students/update
Authorization: Bearer <token>

{
  "external_student_id": "candidate_789",
  "profile_data": {
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "education": {
      "level": "Bachelor's",
      "field": "Computer Science",
      "university": "University X"
    },
    "preferences": {
      "locations": ["Remote", "New York"],
      "job_types": ["Full-time"],
      "industries": ["Tech", "Finance"]
    }
  }
}
```

Creates or updates a candidate profile with embeddings.

### Find Candidates for Job

```bash
POST /api/v1/matching/students-for-job
Authorization: Bearer <token>

{
  "external_job_id": "job_12345",
  "top_k": 10,
  "min_similarity_score": 0.75,
  "ranking_weights": {
    "similarity": 0.6,
    "required_skills": 0.3,
    "preferred_skills": 0.1
  }
}
```

Returns top matching candidates for a specific job.

### Find Jobs for Candidate

```bash
POST /api/v1/matching/jobs-for-student
Authorization: Bearer <token>

{
  "external_student_id": "candidate_789",
  "company_ids": ["company_abc"],
  "top_k": 5,
  "min_similarity_score": 0.70
}
```

Returns top matching jobs for a specific candidate.

## Streamlit Demo UI

The included Streamlit application provides a visual interface to:

- View dashboard with system stats
- Add and manage job postings
- Add and manage candidate profiles
- Run matching and view AI-powered insights
- Export results

Run Streamlit:

```bash
cd streamlit_app
streamlit run app.py
```

## Development

### Local Setup (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=sqlite:///./talentmatch.db
export QDRANT_HOST=localhost
export QDRANT_PORT=6333
export GEMINI_API_KEY=your-gemini-api-key

# Run the application
uvicorn app.main:app --reload
```

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | Database connection string | No | sqlite:///./talentmatch.db |
| `QDRANT_HOST` | Qdrant server host | Yes | localhost |
| `QDRANT_PORT` | Qdrant server port | Yes | 6333 |
| `QDRANT_API_KEY` | Qdrant API key (production) | No | - |
| `GEMINI_API_KEY` | Google Gemini API key | Yes | - |
| `GEMINI_EMBEDDING_MODEL` | Embedding model name | No | text-embedding-004 |
| `GEMINI_CHAT_MODEL` | Chat model for parsing | No | gemini-2.5-flash-lite |
| `JWT_SECRET_KEY` | Secret key for JWT | Yes | - |
| `JWT_ALGORITHM` | JWT algorithm | No | HS256 |
| `ALLOWED_ORIGINS` | CORS allowed origins | No | http://localhost:3000,http://localhost:8501 |
| `ENVIRONMENT` | Environment (dev/prod) | No | development |
| `LOG_LEVEL` | Logging level | No | INFO |

## Project Structure

```
talentmatch-ai/
├── app/
│   ├── api/v1/              # API endpoints
│   ├── core/                # Core functionality (Gemini, Qdrant, security)
│   ├── models/              # Database models and Pydantic schemas
│   ├── services/            # Business logic
│   ├── db/                  # Database session and migrations
│   ├── config.py            # Configuration management
│   ├── dependencies.py      # FastAPI dependencies
│   └── main.py              # FastAPI application
├── streamlit_app/           # Streamlit demo UI
│   ├── app.py               # Main Streamlit entry point
│   └── pages/               # Streamlit pages
├── scripts/                 # Utility scripts
│   ├── init_db.py           # Database initialization
│   ├── seed_database.py     # Sample data seeding
│   └── generate_test_token.py
├── tests/                   # Test suite
├── docker-compose.yml       # Development Docker setup
├── Dockerfile               # Container image definition
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Performance

- **Job Parsing**: < 2s per job description
- **Embedding Generation**: < 1s per job/candidate
- **Matching Query**: < 500ms for top-10 results
- **Concurrent Requests**: Supports 10+ simultaneous matches

## Troubleshooting

### Common Issues

**1. Gemini API errors**
- Verify your API key is correct
- Check if you've exceeded free tier limits (1500 requests/day)
- Ensure you have access to the models

**2. Qdrant connection errors**
- Ensure Qdrant container is running: `docker-compose ps`
- Check Qdrant logs: `docker-compose logs qdrant`
- Verify QDRANT_HOST and QDRANT_PORT settings

**3. Database connection errors**
- Ensure SQLite file is writable
- For PostgreSQL, verify DATABASE_URL is correct
- Check database logs: `docker-compose logs postgres`

**4. Authentication errors**
- Verify JWT token is valid and not expired
- Check JWT_SECRET_KEY matches between services
- Generate a new test token: `python scripts/generate_test_token.py`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Roadmap

### Current (v1.0)
- [x] Gemini AI integration
- [x] Semantic vector matching
- [x] AI-powered insights
- [x] FastAPI backend
- [x] Streamlit demo UI

### Future Enhancements
- [ ] Cohere rerank integration for improved results
- [ ] Batch processing for multiple jobs/candidates
- [ ] Redis caching for frequent queries
- [ ] Analytics dashboard
- [ ] Resume PDF parsing
- [ ] Multi-language support

---

**Built with ❤️ using Gemini AI and Qdrant**
