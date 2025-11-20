# API Latency Testing Script for Inception Labs
# Usage: .\test-api-latency.ps1

$apiKey = "sk_b6653d5f88ab8548f882d7db105abcdb"
$apiUrl = "https://api.inceptionlabs.ai/v1/chat/completions"
$numTests = 10

Write-Host "Testing API Latency - Running $numTests requests..." -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$results = @()

for ($i = 1; $i -le $numTests; $i++) {
    Write-Host "Request $i of ${numTests}..." -NoNewline
    
    $body = @{
        messages = @(
            @{
                role = "user"
                content = "What is the meaning of life?"
            }
        )
        model = "mercury"
    } | ConvertTo-Json -Depth 10
    
    $headers = @{
        "Authorization" = "Bearer $apiKey"
        "Content-Type" = "application/json"
    }
    
    $stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
    
    try {
        $response = Invoke-RestMethod -Uri $apiUrl -Method Post -Headers $headers -Body $body -ErrorAction Stop
        $stopwatch.Stop()
        
        $latencyMs = $stopwatch.ElapsedMilliseconds
        $results += $latencyMs
        
        Write-Host " ${latencyMs}ms" -ForegroundColor Green
    }
    catch {
        $stopwatch.Stop()
        Write-Host " FAILED" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Start-Sleep -Milliseconds 500
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Results Summary:" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

if ($results.Count -gt 0) {
    $avgLatency = ($results | Measure-Object -Average).Average
    $minLatency = ($results | Measure-Object -Minimum).Minimum
    $maxLatency = ($results | Measure-Object -Maximum).Maximum
    
    Write-Host "Successful Requests: $($results.Count)/$numTests" -ForegroundColor Green
    Write-Host "Average Latency: $([math]::Round($avgLatency, 2))ms" -ForegroundColor Yellow
    Write-Host "Min Latency: ${minLatency}ms" -ForegroundColor Green
    Write-Host "Max Latency: ${maxLatency}ms" -ForegroundColor Red
    Write-Host ""
    Write-Host "All Results (ms): $($results -join ', ')" -ForegroundColor Gray
}
else {
    Write-Host "All requests failed!" -ForegroundColor Red
}
