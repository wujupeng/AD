#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/common.sh"

if [ ! -f "${SCRIPT_DIR}/deploy.env" ]; then
    log_fail "deploy.env not found at ${SCRIPT_DIR}/deploy.env"
    exit 1
fi

set -a
source "${SCRIPT_DIR}/deploy.env"
set +a

REQUIRED_VARS=(
    SERVER_IP SSH_USER SSH_PASSWORD SUDO_PASSWORD
    AD_DOMAIN AD_REALM AD_NETBIOS_NAME AD_ADMIN_PASSWORD
    SVC_ACCOUNT_PASSWORD DB_PASSWORD
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var:-}" ]; then
        handle_error "DEPLOY_ENV_MISSING" "Required variable ${var} is not set"
    fi
done

DEPLOY_BASE_DIR="${DEPLOY_BASE_DIR:-/opt/ad-biz-sys}"
DB_NAME="${DB_NAME:-adbizsys}"
DB_USER="${DB_USER:-aduser}"
AD_DNS_FORWARDER="${AD_DNS_FORWARDER:-8.8.8.8}"
SERVER_HOSTNAME="${SERVER_HOSTNAME:-dc01.${AD_DOMAIN}}"
REDIS_PASSWORD="${REDIS_PASSWORD:-}"
NGINX_SERVER_NAME="${NGINX_SERVER_NAME:-${SERVER_IP}}"

if [ -z "${JWT_SECRET:-}" ]; then
    JWT_SECRET=$(openssl rand -hex 32 2>/dev/null || cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 64 | head -n 1)
    log_info "JWT_SECRET auto-generated"
fi

export SERVER_IP SSH_USER SSH_PASSWORD SUDO_PASSWORD
export AD_DOMAIN AD_REALM AD_NETBIOS_NAME AD_ADMIN_PASSWORD AD_DNS_FORWARDER SERVER_HOSTNAME
export SVC_ACCOUNT_PASSWORD DB_NAME DB_USER DB_PASSWORD REDIS_PASSWORD JWT_SECRET
export DEPLOY_BASE_DIR NGINX_SERVER_NAME LOCAL_BACKEND_DIR LOCAL_FRONTEND_DIR

log_ok "Environment loaded successfully"
log_info "  SERVER_IP:       ${SERVER_IP}"
log_info "  AD_DOMAIN:       ${AD_DOMAIN}"
log_info "  SERVER_HOSTNAME: ${SERVER_HOSTNAME}"
log_info "  DEPLOY_BASE_DIR: ${DEPLOY_BASE_DIR}"