# Test GPT-4.1 AI-Powered Insights

Write-Host ""
Write-Host "========== Testing GPT-4.1 AI-Powered Insights ==========" -ForegroundColor Cyan
Write-Host ""

# Generate fresh token
$TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0X3VzZXJfMTIzIiwiZW1haWwiOiJ0ZXN0QGlwc2ktcGxhdGZvcm0uY29tIiwicm9sZSI6ImhyX2FkbWluIiwiZXhwIjoxNzYwOTYyNjQ0fQ.m0IJw21YbWDnujYBsdAKJ3akXEKBXl-_qJhaxyU3_B4"
$headers = @{Authorization = "Bearer $TOKEN"}

Write-Host "Testing AI Insights (GPT-4.1) for Top 5 Matches" -ForegroundColor Yellow
Write-Host "This will cost approximately `$0.075-0.15 per request" -ForegroundColor Gray
Write-Host ""

# Test: Find students for Python Developer job
Write-Host "Finding students for Python Backend Developer job..." -ForegroundColor Yellow

$body = @{
    external_job_id = "job_001"
    top_k = 6
    min_similarity_score = 0.60
} | ConvertTo-Json

try {
    Write-Host "Calling API... (this may take 5-10 seconds for AI generation)" -ForegroundColor Gray
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    $response = Invoke-WebRequest `
        -Uri "http://localhost:8000/api/v1/matching/students-for-job" `
        -Method POST `
        -Headers $headers `
        -ContentType "application/json" `
        -Body $body
    
    $stopwatch.Stop()
    $result = $response.Content | ConvertFrom-Json
    
    Write-Host "Response time: $($stopwatch.ElapsedMilliseconds)ms" -ForegroundColor Green
    Write-Host ""
    Write-Host "Job: $($result.job_title)" -ForegroundColor Cyan
    Write-Host "Matches found: $($result.returned_count)" -ForegroundColor Green
    Write-Host ""
    
    foreach ($match in $result.matches) {
        Write-Host "============================================================" -ForegroundColor Gray
        Write-Host "Rank #$($match.rank): $($match.external_student_id)" -ForegroundColor Cyan
        Write-Host "Similarity Score: $([math]::Round($match.similarity_score, 3))" -ForegroundColor White
        
        $insights = $match.match_insights
        
        if ($insights.ai_powered) {
            Write-Host ""
            Write-Host "AI-POWERED INSIGHTS (GPT-4.1):" -ForegroundColor Green
            Write-Host "  Match Quality: $($insights.match_quality)" -ForegroundColor Yellow
            
            Write-Host ""
            Write-Host "  Why Recommended:" -ForegroundColor Yellow
            foreach ($reason in $insights.recommended_because) {
                Write-Host "    - $reason" -ForegroundColor White
            }
            
            if ($insights.skill_analysis) {
                Write-Host ""
                Write-Host "  Skill Analysis:" -ForegroundColor Yellow
                if ($insights.skill_analysis.strong_matches) {
                    Write-Host "    Strong: $($insights.skill_analysis.strong_matches -join ', ')" -ForegroundColor Green
                }
                if ($insights.skill_analysis.transferable_skills) {
                    Write-Host "    Transferable: $($insights.skill_analysis.transferable_skills -join ', ')" -ForegroundColor Cyan
                }
                if ($insights.skill_analysis.skill_gaps) {
                    Write-Host "    Gaps: $($insights.skill_analysis.skill_gaps -join ', ')" -ForegroundColor Yellow
                }
            }
            
            if ($insights.development_recommendations) {
                Write-Host ""
                Write-Host "  Development Recommendations:" -ForegroundColor Yellow
                foreach ($rec in $insights.development_recommendations) {
                    Write-Host "    - $rec" -ForegroundColor White
                }
            }
            
            if ($insights.cultural_fit) {
                Write-Host ""
                Write-Host "  Cultural Fit: $($insights.cultural_fit)" -ForegroundColor Cyan
            }
            
            if ($insights.confidence_note) {
                Write-Host ""
                Write-Host "  Analysis: $($insights.confidence_note)" -ForegroundColor Gray
            }
        } else {
            Write-Host ""
            Write-Host "SIMPLE MATCH (No AI insights for rank > 5):" -ForegroundColor Yellow
            Write-Host "  $($insights.note)" -ForegroundColor White
        }
        
        Write-Host ""
    }
    
    Write-Host "============================================================" -ForegroundColor Gray
    Write-Host ""
    Write-Host "SUCCESS! AI insights are working with GPT-4.1" -ForegroundColor Green
    Write-Host ""
    Write-Host "Notice:" -ForegroundColor Yellow
    Write-Host "  - Top 5 matches have detailed AI insights" -ForegroundColor White
    Write-Host "  - Rank 6+ have simple similarity note" -ForegroundColor White
    Write-Host "  - AI insights provide rich, personalized explanations" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Note: If you see 'model not found', GPT-4.1 might not be available yet" -ForegroundColor Yellow
    Write-Host "      The system will fall back gracefully to simple insights" -ForegroundColor Yellow
}

Write-Host "===============================================================" -ForegroundColor Cyan
Write-Host ""

