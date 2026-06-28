<#
.SYNOPSIS
    Install AD Biz Sys backend as Windows Service
.DESCRIPTION
    Creates Python virtual environment, installs dependencies, configures Windows Service via NSSM
#>

param(
    [string]$InstallPath = "C:\AD-Biz-Sys\backend",
    [string]$ServiceName = "ADBizSys-Backend",
    [string]$EnvFile
)

$ErrorActionPreference = "Stop"

Write-Host "=== Installing AD Biz Sys Backend Service ===" -ForegroundColor Cyan

Write-Host "[1/4] Creating virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path $InstallPath)) {
    New-Item -ItemType Directory -Force -Path $InstallPath | Out-Null
}

$venvPath = Join-Path $InstallPath "venv"
if (-not (Test-Path $venvPath)) {
    python -m venv $venvPath
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "[SKIP] Virtual environment already exists" -ForegroundColor Yellow
}

Write-Host "[2/4] Installing dependencies..." -ForegroundColor Yellow
$pipPath = Join-Path $venvPath "Scripts\pip.exe"
& $pipPath install -e (Join-Path $PSScriptRoot "..\backend")
Write-Host "[OK] Dependencies installed" -ForegroundColor Green

Write-Host "[3/4] Configuring environment..." -ForegroundColor Yellow
if ($EnvFile -and (Test-Path $EnvFile)) {
    Copy-Item $EnvFile (Join-Path $InstallPath ".env")
    Write-Host "[OK] Environment file copied" -ForegroundColor Green
} else {
    $envTemplate = Join-Path $PSScriptRoot ".env.template"
    if (Test-Path $envTemplate) {
        Copy-Item $envTemplate (Join-Path $InstallPath ".env")
        Write-Host "[WARN] Using template .env - please configure before starting service" -ForegroundColor Yellow
    }
}

Write-Host "[4/4] Registering Windows Service..." -ForegroundColor Yellow
$nssmPath = Get-Command "nssm" -ErrorAction SilentlyContinue
if ($nssmPath) {
    $pythonPath = Join-Path $venvPath "Scripts\python.exe"
    $scriptPath = Join-Path $InstallPath "app\main.py"
    $moduleArg = "-m"
    $uvicornArg = "uvicorn"
    $hostArg = "--host"
    $hostVal = "0.0.0.0"
    $portArg = "--port"
    $portVal = "8000"

    nssm install $ServiceName $pythonPath "$moduleArg $uvicornArg app.main:app $hostArg $hostVal $portArg $portVal"
    nssm set $ServiceName AppDirectory $InstallPath
    nssm set $ServiceName DisplayName "AD Biz Sys Backend"
    nssm set $ServiceName Description "AD-integrated business system backend service"
    nssm set $ServiceName Start SERVICE_AUTO_START
    Write-Host "[OK] Service registered: $ServiceName" -ForegroundColor Green
} else {
    Write-Host "[WARN] NSSM not found. Manual service registration required." -ForegroundColor Yellow
    Write-Host "  Install NSSM: https://nssm.cc/download"
}

Write-Host "`n[DONE] Backend installation complete" -ForegroundColor Green
Write-Host "  Install path: $InstallPath"
Write-Host "  Service name: $ServiceName"