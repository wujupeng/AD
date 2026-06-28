<#
.SYNOPSIS
    Install prerequisites for AD Biz Sys
.DESCRIPTION
    Checks and installs Python 3.11+, Node.js 18+, PostgreSQL 16+, Redis 7+
#>

$ErrorActionPreference = "Stop"

function Test-Command {
    param([string]$Name)
    try { Get-Command $Name -ErrorAction Stop | Out-Null; return $true } catch { return $false }
}

function Test-Python {
    if (Test-Command "python") {
        $version = (python --version 2>&1).ToString() -replace "Python ", ""
        if ([version]$version -ge [version]"3.11.0") {
            Write-Host "[OK] Python $version" -ForegroundColor Green
            return $true
        }
    }
    Write-Host "[MISSING] Python 3.11+ not found" -ForegroundColor Yellow
    return $false
}

function Test-Node {
    if (Test-Command "node") {
        $version = (node --version).ToString() -replace "v", ""
        if ([version]$version -ge [version]"18.0.0") {
            Write-Host "[OK] Node.js $version" -ForegroundColor Green
            return $true
        }
    }
    Write-Host "[MISSING] Node.js 18+ not found" -ForegroundColor Yellow
    return $false
}

function Test-PostgreSQL {
    if (Test-Command "psql") {
        $version = (psql --version).ToString() -replace "psql \(PostgreSQL\) ", ""
        Write-Host "[OK] PostgreSQL $version" -ForegroundColor Green
        return $true
    }
    Write-Host "[MISSING] PostgreSQL not found" -ForegroundColor Yellow
    return $false
}

function Test-Redis {
    if (Test-Command "redis-server") {
        Write-Host "[OK] Redis found" -ForegroundColor Green
        return $true
    }
    Write-Host "[MISSING] Redis not found" -ForegroundColor Yellow
    return $false
}

Write-Host "=== AD Biz Sys Prerequisites Check ===" -ForegroundColor Cyan

$allOk = $true
if (-not (Test-Python)) { $allOk = $false }
if (-not (Test-Node)) { $allOk = $false }
if (-not (Test-PostgreSQL)) { $allOk = $false }
if (-not (Test-Redis)) { $allOk = $false }

if ($allOk) {
    Write-Host "`n[SUCCESS] All prerequisites are installed" -ForegroundColor Green
} else {
    Write-Host "`n[ACTION REQUIRED] Install missing prerequisites before continuing" -ForegroundColor Red
    Write-Host "  Python: https://www.python.org/downloads/"
    Write-Host "  Node.js: https://nodejs.org/"
    Write-Host "  PostgreSQL: https://www.postgresql.org/download/windows/"
    Write-Host "  Redis: https://github.com/tporadowski/redis/releases"
}