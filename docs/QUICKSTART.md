# Quick Start Guide

Get the IPSI AI Matching Service up and running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- 4GB RAM available
- Port 8000, 5432, and 6333 available

## Step 1: Get the Code

```bash
# Extract or clone the repository
cd ipsi-ai-matching
```

## Step 2: Configure Environment

```bash
# Create .env file with your OpenAI API key
# On Windows (PowerShell):
(Get-Content .env.example) -replace 'sk-your-openai-api-key-here', 'sk-YOUR_ACTUAL_KEY' | Set-Content .env

# On Linux/Mac:
# sed 's/sk-your-openai-api-key-here/sk-YOUR_ACTUAL_KEY/' .env.example > .env
```

Or manually create `.env`:

```
OPENAI_API_KEY=sk-your-actual-openai-api-key-here
```

## Step 3: Start Services

```bash
# Build and start all containers
docker-compose up -d

# Wait for services to be ready (about 30 seconds)
# Check status
docker-compose ps
```

You should see:
- ipsi-ai-matching (FastAPI)
- ipsi-postgres (PostgreSQL)
- ipsi-qdrant (Vector DB)

## Step 4: Initialize Database

```bash
# Create database tables
docker-compose exec fastapi python scripts/init_db.py
```

## Step 5: Load Sample Data

```bash
# Load sample jobs and students
docker-compose exec fastapi python scripts/seed_database.py
```

This creates:
- 5 sample job postings from various companies
- 8 sample student profiles with different skills
- Embeddings for all jobs and students

## Step 6: Test the API

### Generate a test token

```bash
docker-compose exec fastapi python scripts/generate_test_token.py
```

Copy the generated token.

### Test with curl (Windows PowerShell)

```powershell
$TOKEN = "paste-your-token-here"
$headers = @{Authorization = "Bearer $TOKEN"}

# Test health endpoint
Invoke-WebRequest -Uri http://localhost:8000/api/v1/health -Headers $headers | Select-Object -Expand Content

# Find students for a job
$body = @{
    external_job_id = "job_001"
    top_k = 5
    min_similarity_score = 0.70
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:8000/api/v1/matching/students-for-job `
    -Method POST `
    -Headers $headers `
    -ContentType "application/json" `
    -Body $body | Select-Object -Expand Content
```

### Or visit the API docs

Open in your browser:
- http://localhost:8000/docs (Swagger UI)
- Click "Authorize" and paste your token

Now you can test all endpoints interactively!

## What's Next?

### View Logs

```bash
# View all logs
docker-compose logs -f

# View only API logs
docker-compose logs -f fastapi
```

### Stop Services

```bash
# Stop but keep data
docker-compose stop

# Stop and remove everything
docker-compose down

# Stop and remove volumes (deletes all data)
docker-compose down -v
```

### Add More Data

```bash
# You can run the seed script multiple times
docker-compose exec fastapi python scripts/seed_database.py
```

### Integration

See [API_EXAMPLES.md](API_EXAMPLES.md) for:
- Complete API usage examples
- Code samples in Python and JavaScript
- Error handling
- Best practices

See [README.md](README.md) for:
- Architecture details
- Full feature list
- Development setup

See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Production deployment
- Cloud Run deployment
- Security hardening

## Troubleshooting

### Port already in use

```bash
# On Windows, check what's using port 8000
netstat -ano | findstr :8000

# Change port in docker-compose.yml:
# ports:
#   - "8001:8000"  # Use 8001 instead
```

### OpenAI API errors

- Check your API key is correct
- Verify you have credits: https://platform.openai.com/account/usage
- Ensure you have access to GPT-4 and embeddings models

### Services not starting

```bash
# Check logs for errors
docker-compose logs

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database connection errors

```bash
# Wait longer for PostgreSQL to be ready
sleep 10
docker-compose exec fastapi python scripts/init_db.py
```

## Need Help?

- Check the logs: `docker-compose logs`
- Read the full [README.md](README.md)
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for advanced topics
- Open an issue on GitHub

---

**Ready to integrate?** See [API_EXAMPLES.md](API_EXAMPLES.md) for integration examples!



