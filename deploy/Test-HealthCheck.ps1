<#
.SYNOPSIS
    Health check for AD Biz Sys
.DESCRIPTION
    Calls /health endpoint, verifies component status, outputs verification evidence
.PARAMETER BaseUrl
    Base URL of the backend API (default: http://localhost:8000)
#>

param(
    [string]$BaseUrl = "http://localhost:8000"
)

$ErrorActionPreference = "Stop"

Write-Host "=== AD Biz Sys Health Check ===" -ForegroundColor Cyan
Write-Host "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host "Target: $BaseUrl"

Write-Host "`n[1/3] Checking /api/health endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/api/health" -Method Get -ContentType "application/json"
    Write-Host "[OK] Health endpoint responded" -ForegroundColor Green
    Write-Host "  Status: $($response.data.status)"
    Write-Host "  Version: $($response.data.version)"
    Write-Host "  Components:"
    foreach ($key in $response.data.components.PSObject.Properties.Name) {
        $status = $response.data.components.$key
        $color = if ($status -eq "healthy" -or $status -eq "up") { "Green" } else { "Red" }
        Write-Host "    $key : $status" -ForegroundColor $color
    }
} catch {
    Write-Host "[FAIL] Health endpoint unreachable: $_" -ForegroundColor Red
}

Write-Host "`n[2/3] Checking /api/health/metrics endpoint..." -ForegroundColor Yellow
try {
    $metrics = Invoke-RestMethod -Uri "$BaseUrl/api/health/metrics" -Method Get -ContentType "application/json"
    Write-Host "[OK] Metrics endpoint responded" -ForegroundColor Green
    Write-Host "  Auth success rate: $($metrics.data.auth_success_rate)"
    Write-Host "  Auth latency (ms): $($metrics.data.auth_latency_ms)"
    Write-Host "  Active sessions: $($metrics.data.active_sessions)"
} catch {
    Write-Host "[FAIL] Metrics endpoint unreachable: $_" -ForegroundColor Red
}

Write-Host "`n[3/3] Checking frontend..." -ForegroundColor Yellow
try {
    $frontendUrl = $BaseUrl -replace ':8000', ':5173'
    $frontendResp = Invoke-WebRequest -Uri $frontendUrl -Method Head -ErrorAction Stop
    Write-Host "[OK] Frontend reachable (status: $($frontendResp.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Frontend not reachable at $frontendUrl" -ForegroundColor Yellow
}

Write-Host "`n=== Health Check Complete ===" -ForegroundColor Cyan
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"