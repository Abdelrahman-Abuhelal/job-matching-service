# IPSI AI Matching Service

> AI-powered student-internship matching microservice for the IPSI platform

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## Overview

The IPSI AI Matching Service is a standalone microservice that uses AI and vector search to intelligently match students with internship opportunities. It integrates with the existing IPSI platform via REST APIs and provides semantic similarity-based matching using OpenAI embeddings and Qdrant vector database.

### Key Features

- **Intelligent Job Parsing**: Uses GPT-4 to extract structured data from raw job descriptions
- **Semantic Matching**: Generates embeddings for jobs and students for similarity-based matching
- **Multi-Company Support**: Isolated Qdrant collections per company for data separation (GDPR compliant)
- **Match Insights**: AI-generated explanations for matches (skill overlap, gaps, recommendations)
- **RESTful API**: Clean, documented API endpoints for integration
- **JWT Authentication**: Secure authentication for all endpoints
- **Docker Ready**: Fully containerized for easy deployment

## Architecture

```
┌─────────────────┐
│  IPSI Platform  │ (External - sends requests)
└────────┬────────┘
         │ REST API (JWT Auth)
         ▼
┌─────────────────────────────────────┐
│   AI Matching Microservice          │
│   ┌─────────────┐  ┌─────────────┐ │
│   │   FastAPI   │  │  PostgreSQL │ │
│   │   Service   │──│  (Metadata) │ │
│   └──────┬──────┘  └─────────────┘ │
│          │                          │
│          ▼                          │
│   ┌─────────────┐                  │
│   │   Qdrant    │                  │
│   │  (Vectors)  │                  │
│   └─────────────┘                  │
└─────────────────────────────────────┘
         │
         ▼
   OpenAI API (Embeddings + GPT-4)
```

## Tech Stack

- **Backend**: Python 3.11, FastAPI
- **Database**: PostgreSQL (metadata), Qdrant (vector search)
- **AI/ML**: OpenAI (text-embedding-3-large, GPT-4)
- **Authentication**: JWT tokens
- **Deployment**: Docker, Docker Compose

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Python 3.11+ (for local development)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd ipsi-ai-matching

# Create .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

### 2. Run with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# The API will be available at http://localhost:8000
# API documentation: http://localhost:8000/docs
```

### 3. Initialize Database

```bash
# In a new terminal, run database initialization
docker-compose exec fastapi python scripts/init_db.py
```

### 4. Seed Sample Data

```bash
# Load sample jobs and students
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

Parses a job description using GPT-4 and stores it with embeddings.

### Update Student Profile

```bash
POST /api/v1/students/update
Authorization: Bearer <token>

{
  "external_student_id": "student_789",
  "profile_data": {
    "skills": ["Python", "FastAPI", "PostgreSQL"],
    "education": {
      "level": "Bachelor's",
      "field": "Computer Science",
      "university": "University X"
    },
    "preferences": {
      "locations": ["Remote", "Paris"],
      "job_types": ["Internship"],
      "industries": ["Tech", "Finance"]
    }
  }
}
```

Creates or updates a student profile with embeddings.

### Find Students for Job

```bash
POST /api/v1/matching/students-for-job
Authorization: Bearer <token>

{
  "external_job_id": "job_12345",
  "top_k": 10,
  "min_similarity_score": 0.75,
  "filters": {
    "education_level": ["Bachelor's", "Master's"]
  }
}
```

Returns top matching students for a specific job.

### Find Jobs for Student

```bash
POST /api/v1/matching/jobs-for-student
Authorization: Bearer <token>

{
  "external_student_id": "student_789",
  "company_ids": ["company_abc"],
  "top_k": 5,
  "min_similarity_score": 0.70
}
```

Returns top matching jobs for a specific student.

## Development

### Local Setup (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql://user:password@localhost:5432/ipsi_ai
export QDRANT_HOST=localhost
export QDRANT_PORT=6333
export OPENAI_API_KEY=sk-your-key

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

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Deployment

### Docker Build for Production

```bash
# Build production image
docker build -t ipsi-ai-matching:latest .

# Tag for registry
docker tag ipsi-ai-matching:latest gcr.io/PROJECT_ID/ipsi-ai-matching:latest

# Push to registry
docker push gcr.io/PROJECT_ID/ipsi-ai-matching:latest
```

### Google Cloud Run Deployment

```bash
# Build and deploy to Cloud Run
gcloud builds submit --tag gcr.io/PROJECT_ID/ipsi-ai-matching

gcloud run deploy ipsi-ai-matching \
  --image gcr.io/PROJECT_ID/ipsi-ai-matching \
  --platform managed \
  --region europe-west1 \
  --set-env-vars DATABASE_URL=... \
  --set-secrets OPENAI_API_KEY=openai-key:latest \
  --allow-unauthenticated=false
```

See `DEPLOYMENT.md` for detailed deployment instructions.

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `QDRANT_HOST` | Qdrant server host | Yes | localhost |
| `QDRANT_PORT` | Qdrant server port | Yes | 6333 |
| `QDRANT_API_KEY` | Qdrant API key (production) | No | - |
| `OPENAI_API_KEY` | OpenAI API key | Yes | - |
| `OPENAI_EMBEDDING_MODEL` | Embedding model name | No | text-embedding-3-large |
| `OPENAI_CHAT_MODEL` | Chat model for parsing | No | gpt-4-turbo-preview |
| `JWT_SECRET_KEY` | Secret key for JWT | Yes | - |
| `JWT_ALGORITHM` | JWT algorithm | No | HS256 |
| `ALLOWED_ORIGINS` | CORS allowed origins | No | * |
| `ENVIRONMENT` | Environment (dev/prod) | No | development |
| `LOG_LEVEL` | Logging level | No | INFO |

## Project Structure

```
ipsi-ai-matching/
├── app/
│   ├── api/v1/              # API endpoints
│   ├── core/                # Core functionality (OpenAI, Qdrant, security)
│   ├── models/              # Database models and Pydantic schemas
│   ├── services/            # Business logic
│   ├── db/                  # Database session and migrations
│   ├── config.py            # Configuration management
│   ├── dependencies.py      # FastAPI dependencies
│   └── main.py              # FastAPI application
├── scripts/                 # Utility scripts
│   ├── init_db.py          # Database initialization
│   ├── seed_database.py    # Sample data seeding
│   └── generate_test_token.py
├── tests/                   # Test suite
├── docker-compose.yml       # Development Docker setup
├── docker-compose.prod.yml  # Production Docker reference
├── Dockerfile               # Container image definition
├── requirements.txt         # Python dependencies
├── alembic.ini             # Alembic configuration
└── README.md               # This file
```

## Security & Compliance

### GDPR Compliance

- **Data Isolation**: Each company has a separate Qdrant collection
- **Right to Erasure**: DELETE endpoints available for data removal
- **Data Minimization**: Only necessary data is stored
- **EU Data Residency**: Deploy to EU regions (europe-west1)
- **Audit Logs**: All matches logged in match_history table

### Authentication

All API endpoints require JWT authentication. Tokens should be obtained from the IPSI platform and included in the Authorization header:

```
Authorization: Bearer <jwt_token>
```

## Performance Benchmarks

- **Job Parsing**: < 2s per job description
- **Embedding Generation**: < 1s per job/student
- **Matching Query**: < 500ms for top-10 results
- **Concurrent Requests**: Supports 10+ simultaneous matches

## Troubleshooting

### Common Issues

**1. OpenAI API errors**
- Verify your API key is correct
- Check if you have sufficient credits
- Ensure you have access to the models (text-embedding-3-large, GPT-4)

**2. Qdrant connection errors**
- Ensure Qdrant container is running: `docker-compose ps`
- Check Qdrant logs: `docker-compose logs qdrant`
- Verify QDRANT_HOST and QDRANT_PORT settings

**3. Database connection errors**
- Ensure PostgreSQL is running
- Verify DATABASE_URL is correct
- Check database logs: `docker-compose logs postgres`

**4. Authentication errors**
- Verify JWT token is valid and not expired
- Check JWT_SECRET_KEY matches between services
- Generate a new test token: `python scripts/generate_test_token.py`

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
- Open an issue on GitHub
- Contact: support@ipsi-platform.com

## Roadmap

### Phase 2 (Future Enhancements)
- [ ] Cohere rerank integration for improved results
- [ ] Batch processing for multiple jobs/students
- [ ] Redis caching for frequent queries
- [ ] Async job processing with Celery

### Phase 3
- [ ] HR feedback loop for model improvement
- [ ] Analytics dashboard
- [ ] Interview question generation
- [ ] Resume parsing from PDFs

### Phase 4
- [ ] Multi-language support (French, German, etc.)
- [ ] Video interview analysis
- [ ] Automated outreach system

## Acknowledgments

- FastAPI for the excellent web framework
- OpenAI for powerful AI capabilities
- Qdrant for efficient vector search
- The IPSI team for requirements and feedback

---

**Built with ❤️ for the IPSI Platform**



