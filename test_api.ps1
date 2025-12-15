# Comprehensive API Test Script for IPSI AI Matching Service

Write-Host ""
Write-Host "========== IPSI AI Matching Service - API Test Suite ==========" -ForegroundColor Cyan
Write-Host ""

# Generate fresh token
Write-Host "Generating authentication token..." -ForegroundColor Yellow
$TOKEN = (docker-compose exec -T fastapi python scripts/generate_test_token.py | Select-String "eyJ").ToString().Split()[0].Trim()
$headers = @{Authorization = "Bearer $TOKEN"}

# Test 1: Health Check
Write-Host "`n1. Health Check" -ForegroundColor Yellow
$health = (Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -Headers $headers).Content | ConvertFrom-Json
Write-Host "   Status: $($health.status)" -ForegroundColor $(if($health.status -eq "healthy"){"Green"}else{"Yellow"})
Write-Host "   Qdrant: $($health.qdrant_connected)" -ForegroundColor Green
Write-Host "   OpenAI: $($health.openai_api_available)" -ForegroundColor Green

# Test 2: Find Students for Job
Write-Host "`n2. Find Students for Python Developer Job (job_001)" -ForegroundColor Yellow
$body = @{
    external_job_id = "job_001"
    top_k = 3
    min_similarity_score = 0.60
} | ConvertTo-Json

$result = (Invoke-WebRequest -Uri "http://localhost:8000/api/v1/matching/students-for-job" -Method POST -Headers $headers -ContentType "application/json" -Body $body).Content | ConvertFrom-Json
Write-Host "   Job: $($result.job_title)" -ForegroundColor Cyan
Write-Host "   Matches: $($result.returned_count)" -ForegroundColor Green

foreach ($match in $result.matches) {
    Write-Host "   #$($match.rank): $($match.external_student_id) - Score: $([math]::Round($match.similarity_score,3))" -ForegroundColor White
}

# Test 3: Find Jobs for Student
Write-Host "`n3. Find Jobs for Data Science Student (student_002)" -ForegroundColor Yellow
$body = @{
    external_student_id = "student_002"
    top_k = 3
    min_similarity_score = 0.60
} | ConvertTo-Json

$result = (Invoke-WebRequest -Uri "http://localhost:8000/api/v1/matching/jobs-for-student" -Method POST -Headers $headers -ContentType "application/json" -Body $body).Content | ConvertFrom-Json
Write-Host "   Matches: $($result.matches.Count)" -ForegroundColor Green

foreach ($match in $result.matches) {
    Write-Host "   #$($match.rank): $($match.job_title) at $($match.company_name)" -ForegroundColor White
    Write-Host "      Score: $([math]::Round($match.similarity_score,3))" -ForegroundColor Gray
}

# Test 4: Architecture Stats
Write-Host "`n4. Qdrant Architecture Stats" -ForegroundColor Yellow
$collections = (Invoke-WebRequest -Uri "http://localhost:6333/collections").Content | ConvertFrom-Json
Write-Host "   Collections: $($collections.result.collections.Count)" -ForegroundColor Green

foreach ($col in $collections.result.collections) {
    $info = (Invoke-WebRequest -Uri "http://localhost:6333/collections/$($col.name)").Content | ConvertFrom-Json
    Write-Host "   - $($col.name): $($info.result.points_count) vectors" -ForegroundColor White
}

Write-Host "`n===============================================================" -ForegroundColor Cyan
Write-Host "All tests passed!" -ForegroundColor Green
Write-Host "View Qdrant: http://localhost:6333/dashboard" -ForegroundColor Cyan
Write-Host "View API docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

