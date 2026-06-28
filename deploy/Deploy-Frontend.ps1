<#
.SYNOPSIS
    Build and deploy AD Biz Sys frontend to IIS
.DESCRIPTION
    Installs npm dependencies, builds React app, deploys to IIS static site
#>

param(
    [string]$FrontendPath = (Join-Path $PSScriptRoot "..\frontend"),
    [string]$DeployPath = "C:\inetpub\ad-biz-sys",
    [string]$SiteName = "ADBizSys"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Deploying AD Biz Sys Frontend ===" -ForegroundColor Cyan

Write-Host "[1/4] Installing npm dependencies..." -ForegroundColor Yellow
Push-Location $FrontendPath
try {
    npm install
    Write-Host "[OK] Dependencies installed" -ForegroundColor Green
} finally {
    Pop-Location
}

Write-Host "[2/4] Building production bundle..." -ForegroundColor Yellow
Push-Location $FrontendPath
try {
    npm run build
    Write-Host "[OK] Build complete" -ForegroundColor Green
} finally {
    Pop-Location
}

Write-Host "[3/4] Deploying to IIS..." -ForegroundColor Yellow
if (-not (Test-Path $DeployPath)) {
    New-Item -ItemType Directory -Force -Path $DeployPath | Out-Null
}

$distPath = Join-Path $FrontendPath "dist"
if (Test-Path $distPath) {
    Copy-Item -Path "$distPath\*" -Destination $DeployPath -Recurse -Force
    Write-Host "[OK] Files deployed to $DeployPath" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Build output not found at $distPath" -ForegroundColor Red
    exit 1
}

Write-Host "[4/4] Configuring IIS site..." -ForegroundColor Yellow
$iisCmd = Get-Command "appcmd" -ErrorAction SilentlyContinue
if ($iisCmd) {
    appcmd add site /name:$SiteName /physicalPath:$DeployPath /bindings:http/*:80:ad-biz-sys.company.local
    appcmd set site $SiteName /[path=''].applicationDefaults.applicationPool='.NET v4.5'
    Write-Host "[OK] IIS site configured: $SiteName" -ForegroundColor Green
} else {
    Write-Host "[WARN] appcmd not found. Configure IIS manually." -ForegroundColor Yellow
    Write-Host "  Site path: $DeployPath"
    Write-Host "  Binding: http://ad-biz-sys.company.local:80"
}

Write-Host "`n[DONE] Frontend deployment complete" -ForegroundColor Green