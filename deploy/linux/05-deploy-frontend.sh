#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/00-load-env.sh"

log_step "05" "AD Biz Sys Frontend Deployment"

log_step "05-1" "Build frontend locally"
LOCAL_FRONTEND="${SCRIPT_DIR}/${LOCAL_FRONTEND_DIR}"
if [ ! -d "${LOCAL_FRONTEND}" ]; then
    handle_error "DEPLOY_FRONTEND_MISSING" "Frontend directory not found at ${LOCAL_FRONTEND}"
fi

cd "${LOCAL_FRONTEND}"
npm install --prefer-offline 2>/dev/null || npm install
VITE_API_BASE_URL="/api" npm run build
log_ok "Frontend built successfully"

log_step "05-2" "Transfer frontend build to server"
ssh_exec "mkdir -p ${DEPLOY_BASE_DIR}/frontend/dist"
rsync -avz --delete \
    -e "sshpass -p ${SSH_PASSWORD} ssh -o StrictHostKeyChecking=no" \
    "${LOCAL_FRONTEND}/dist/" "${SSH_USER}@${SERVER_IP}:${DEPLOY_BASE_DIR}/frontend/dist/"
log_ok "Frontend build transferred"

log_step "05-3" "Generate Nginx SSL certificate"
ssh_exec "mkdir -p ${DEPLOY_BASE_DIR}/certs"
ssh_exec "openssl req -new -x509 -keyout ${DEPLOY_BASE_DIR}/certs/nginx.key -out ${DEPLOY_BASE_DIR}/certs/nginx.crt -days 3650 -nodes -subj '/CN=${NGINX_SERVER_NAME}'" 2>/dev/null
ssh_exec "chmod 600 ${DEPLOY_BASE_DIR}/certs/nginx.key"
log_ok "Nginx SSL certificate generated"

log_step "05-4" "Configure Nginx site"
ssh_copy "${SCRIPT_DIR}/conf/ad-biz-sys.nginx.conf" "/etc/nginx/sites-available/ad-biz-sys"
ssh_exec "sed -i 's|__DEPLOY_BASE_DIR__|${DEPLOY_BASE_DIR}|g' /etc/nginx/sites-available/ad-biz-sys"
ssh_exec "sed -i 's|__SERVER_IP__|${NGINX_SERVER_NAME}|g' /etc/nginx/sites-available/ad-biz-sys"
log_ok "Nginx configuration deployed"

log_step "05-5" "Enable Nginx site"
ssh_exec "ln -sf /etc/nginx/sites-available/ad-biz-sys /etc/nginx/sites-enabled/ad-biz-sys"
ssh_exec "rm -f /etc/nginx/sites-enabled/default"
if ssh_exec "nginx -t 2>&1"; then
    log_ok "Nginx configuration syntax OK"
else
    handle_error "DEPLOY_NGINX_CONFIG_FAILED" "Nginx configuration syntax error"
fi

log_step "05-6" "Start Nginx"
ssh_exec "systemctl enable --now nginx"
log_ok "Nginx started and enabled"

log_step "05-7" "Verify frontend access"
sleep 2
if ssh_exec "curl -k -sf https://${NGINX_SERVER_NAME}/" 2>/dev/null; then
    log_ok "Frontend accessible via HTTPS"
else
    log_warn "Frontend HTTPS access check failed"
fi

if ssh_exec "curl -k -sf https://${NGINX_SERVER_NAME}/api/health" 2>/dev/null; then
    log_ok "API proxy working"
else
    log_warn "API proxy check failed"
fi

print_summary