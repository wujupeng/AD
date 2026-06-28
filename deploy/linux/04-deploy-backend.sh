#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/00-load-env.sh"

log_step "04" "AD Biz Sys Backend Deployment"

log_step "04-1" "Transfer backend code"
ssh_exec "mkdir -p ${DEPLOY_BASE_DIR}/backend"
LOCAL_BACKEND="${SCRIPT_DIR}/${LOCAL_BACKEND_DIR}"
if [ -d "${LOCAL_BACKEND}" ]; then
    rsync -avz --delete --exclude='__pycache__' --exclude='*.pyc' --exclude='venv/' --exclude='.env' --exclude='.git' \
        -e "sshpass -p ${SSH_PASSWORD} ssh -o StrictHostKeyChecking=no" \
        "${LOCAL_BACKEND}/" "${SSH_USER}@${SERVER_IP}:${DEPLOY_BASE_DIR}/backend/"
    log_ok "Backend code transferred"
else
    handle_error "DEPLOY_CODE_MISSING" "Backend directory not found at ${LOCAL_BACKEND}"
fi

log_step "04-2" "Create Python virtual environment"
ssh_exec "python3 -m venv ${DEPLOY_BASE_DIR}/backend/venv"
log_ok "Python virtual environment created"

log_step "04-3" "Install Python dependencies"
ssh_exec "${DEPLOY_BASE_DIR}/backend/venv/bin/pip install --upgrade pip setuptools wheel" || log_warn "pip upgrade had warnings"
if ! ssh_exec "${DEPLOY_BASE_DIR}/backend/venv/bin/pip install -e ${DEPLOY_BASE_DIR}/backend" 2>/dev/null; then
    log_warn "pip install failed, installing system dev libraries and retrying..."
    ssh_exec "apt install -y -qq python3-dev libpq-dev libldap2-dev libsasl2-dev libkrb5-dev build-essential" || true
    ssh_exec "${DEPLOY_BASE_DIR}/backend/venv/bin/pip install -e ${DEPLOY_BASE_DIR}/backend" || handle_error "DEPLOY_PIP_FAILED" "pip install failed after retry"
fi
log_ok "Python dependencies installed"

log_step "04-4" "Configure PostgreSQL"
ssh_exec "systemctl enable --now postgresql"
ssh_exec "su - postgres -c \"psql -c \\\"CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';\\\"\" 2>/dev/null || true"
ssh_exec "su - postgres -c \"psql -c \\\"CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};\\\"\" 2>/dev/null || true"
ssh_exec "su - postgres -c \"psql -d ${DB_NAME} -c \\\"CREATE EXTENSION IF NOT EXISTS pgcrypto;\\\"\" 2>/dev/null || true"
log_ok "PostgreSQL configured"

log_step "04-5" "Run Alembic migrations"
ssh_exec "cd ${DEPLOY_BASE_DIR}/backend && ${DEPLOY_BASE_DIR}/backend/venv/bin/alembic upgrade head" || log_warn "Alembic migration may have issues (tables may already exist)"
log_ok "Database migrations applied"

log_step "04-6" "Create audit roles"
ssh_exec "su - postgres -c \"psql -d ${DB_NAME} -c \\\"DO \\\$\\\$ BEGIN IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'audit_reader') THEN CREATE ROLE audit_reader; END IF; IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'audit_writer') THEN CREATE ROLE audit_writer; END IF; END \\\$\\\$;\\\"\" 2>/dev/null || true"
ssh_exec "su - postgres -c \"psql -d ${DB_NAME} -c \\\"GRANT SELECT ON audit_events TO audit_reader;\\\"\" 2>/dev/null || true"
ssh_exec "su - postgres -c \"psql -d ${DB_NAME} -c \\\"GRANT INSERT ON audit_events TO audit_writer;\\\"\" 2>/dev/null || true"
log_ok "Audit roles created"

log_step "04-7" "Generate backend .env configuration"
AD_SEARCH_BASE="DC=${AD_DOMAIN%%.*},DC=${AD_DOMAIN#*.}"
REDIS_URL="redis://localhost:6379/0"
[ -n "${REDIS_PASSWORD}" ] && REDIS_URL="redis://:${REDIS_PASSWORD}@localhost:6379/0"

ssh_exec "cat > ${DEPLOY_BASE_DIR}/backend/.env <<ENVEOF
APP_NAME=AD Biz Sys
APP_VERSION=0.1.0
DEBUG=false
DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@localhost:5432/${DB_NAME}
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
REDIS_URL=${REDIS_URL}
REDIS_PASSWORD=${REDIS_PASSWORD}
AD_DOMAIN=${AD_DOMAIN}
AD_DC_LIST=[\"${SERVER_HOSTNAME}\"]
AD_LDAPS_PORT=636
AD_SEARCH_BASE=${AD_SEARCH_BASE}
AD_SERVICE_ACCOUNT_DN=CN=svc_adbiz,OU=ServiceAccounts,OU=Company,${AD_SEARCH_BASE}
AD_SERVICE_ACCOUNT_PASSWORD=${SVC_ACCOUNT_PASSWORD}
JWT_SECRET=${JWT_SECRET}
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
SAML_IDP_ENTITY_ID=https://${SERVER_IP}/saml/metadata
AUTH_MAX_LOGIN_ATTEMPTS=5
AUTH_ACCOUNT_LOCKOUT_MINUTES=30
ORG_SYNC_INTERVAL_MINUTES=5
GAL_SYNC_INTERVAL_MINUTES=60
CORS_ORIGINS=[\"https://${SERVER_IP}\",\"http://localhost:5173\"]
NTP_SERVER=time.windows.com
ENVEOF"
ssh_exec "chmod 600 ${DEPLOY_BASE_DIR}/backend/.env"
log_ok "Backend .env generated"

log_step "04-8" "Create systemd service for backend"
ssh_copy "${SCRIPT_DIR}/conf/ad-biz-sys-backend.service" "/etc/systemd/system/ad-biz-sys-backend.service"
ssh_exec "systemctl daemon-reload"
ssh_exec "systemctl enable ad-biz-sys-backend"
log_ok "Backend systemd service created"

log_step "04-9" "Start backend service"
ssh_exec "systemctl start ad-biz-sys-backend"
sleep 3
log_ok "Backend service started"

log_step "04-10" "Verify backend health"
if ssh_exec "curl -sf http://127.0.0.1:8000/api/health" 2>/dev/null; then
    log_ok "Backend health check passed"
else
    log_warn "Backend health check failed (service may still be starting)"
fi

print_summary