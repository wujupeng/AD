<#
.SYNOPSIS
    Initialize database for AD Biz Sys
.DESCRIPTION
    Creates database, user, runs Alembic migrations, creates audit roles, seeds site data
.PARAMETER DbHost
    Database host (default: localhost)
.PARAMETER DbPort
    Database port (default: 5432)
.PARAMETER DbUser
    PostgreSQL admin user (default: postgres)
.PARAMETER DbPassword
    PostgreSQL admin password
#>

param(
    [string]$DbHost = "localhost",
    [int]$DbPort = 5432,
    [string]$DbUser = "postgres",
    [Parameter(Mandatory=$true)]
    [string]$DbPassword
)

$ErrorActionPreference = "Stop"

$env:PGPASSWORD = $DbPassword

Write-Host "=== Initializing AD Biz Sys Database ===" -ForegroundColor Cyan

Write-Host "[1/5] Creating database and user..." -ForegroundColor Yellow
$dbName = "adbizsys"
$dbUser = "aduser"
$dbPass = "adpass"

psql -h $DbHost -p $DbPort -U $DbUser -c "SELECT 1 FROM pg_database WHERE datname='$dbName'" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    psql -h $DbHost -p $DbPort -U $DbUser -c "CREATE DATABASE $dbName;"
    psql -h $DbHost -p $DbPort -U $DbUser -c "CREATE USER $dbUser WITH PASSWORD '$dbPass';"
    psql -h $DbHost -p $DbPort -U $DbUser -c "GRANT ALL PRIVILEGES ON DATABASE $dbName TO $dbUser;"
    Write-Host "[OK] Database created" -ForegroundColor Green
} else {
    Write-Host "[SKIP] Database already exists" -ForegroundColor Yellow
}

Write-Host "[2/5] Running Alembic migrations..." -ForegroundColor Yellow
Push-Location backend
try {
    pip install -e . 2>&1 | Out-Null
    alembic upgrade head
    Write-Host "[OK] Migrations applied" -ForegroundColor Green
} finally {
    Pop-Location
}

Write-Host "[3/5] Creating audit roles..." -ForegroundColor Yellow
$env:PGPASSWORD = $dbPass
psql -h $DbHost -p $DbPort -U $dbUser -d $dbName -c "DO \$\$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'audit_reader') THEN CREATE ROLE audit_reader; END IF; IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'audit_writer') THEN CREATE ROLE audit_writer; END IF; END \$\$;"
psql -h $DbHost -p $DbPort -U $dbUser -d $dbName -c "GRANT SELECT ON audit_events TO audit_reader;"
psql -h $DbHost -p $DbPort -U $dbUser -d $dbName -c "GRANT INSERT ON audit_events TO audit_writer;"
Write-Host "[OK] Audit roles created" -ForegroundColor Green

Write-Host "[4/5] Seeding site data..." -ForegroundColor Yellow
$sitesSql = @"
INSERT INTO site_configs (site_code, site_name, region, country, subnet_ranges, dc_priority_list, timezone, language) VALUES
('shanghai_hq', 'Shanghai HQ', 'China', 'CN', '10.0.1.0/24', '["dc01.company.local","dc02.company.local"]', 'Asia/Shanghai', 'zh-CN'),
('shanghai_factory', 'Shanghai Factory', 'China', 'CN', '10.0.2.0/23', '["dc03.company.local","dc01.company.local"]', 'Asia/Shanghai', 'zh-CN'),
('ningde', 'Ningde', 'China', 'CN', '10.0.10.0/24', '["dc04.company.local","dc01.company.local"]', 'Asia/Shanghai', 'zh-CN'),
('chuzhou', 'Chuzhou', 'China', 'CN', '10.0.20.0/24', '["dc05.company.local","dc01.company.local"]', 'Asia/Shanghai', 'zh-CN'),
('huaian', 'Huaian', 'China', 'CN', '10.0.30.0/24', '["dc06.company.local","dc01.company.local"]', 'Asia/Shanghai', 'zh-CN'),
('changzhou', 'Changzhou', 'China', 'CN', '10.0.40.0/24', '["dc07.company.local","dc01.company.local"]', 'Asia/Shanghai', 'zh-CN'),
('hungary', 'Hungary', 'Europe', 'HU', '10.1.0.0/24', '["dc08.company.local","dc01.company.local"]', 'Europe/Budapest', 'hu'),
('vietnam', 'Vietnam', 'SEA', 'VN', '10.2.0.0/24', '["dc09.company.local","dc01.company.local"]', 'Asia/Ho_Chi_Minh', 'vi'),
('mexico', 'Mexico', 'Americas', 'MX', '10.3.0.0/24', '["dc10.company.local","dc01.company.local"]', 'America/Mexico_City', 'es-MX')
ON CONFLICT (site_code) DO NOTHING;
"@
psql -h $DbHost -p $DbPort -U $dbUser -d $dbName -c $sitesSql
Write-Host "[OK] Site data seeded" -ForegroundColor Green

Write-Host "[5/5] Verification..." -ForegroundColor Yellow
$tables = psql -h $DbHost -p $DbPort -U $dbUser -d $dbName -c "\dt" 2>&1
Write-Host $tables
Write-Host "[OK] Database initialization complete" -ForegroundColor Green

Remove-Item Env:\PGPASSWORD