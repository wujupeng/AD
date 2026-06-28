#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/00-load-env.sh"

COMPONENT="${1:-all}"

log_step "07" "Deployment Rollback (component: ${COMPONENT})"

rollback_backend() {
    log_info "Rolling back backend..."
    ssh_exec "systemctl stop ad-biz-sys-backend 2>/dev/null || true"
    ssh_exec "systemctl disable ad-biz-sys-backend 2>/dev/null || true"
    ssh_exec "rm -f /etc/systemd/system/ad-biz-sys-backend.service"
    ssh_exec "rm -rf ${DEPLOY_BASE_DIR}/backend"
    ssh_exec "su - postgres -c \"dropdb --if-exists ${DB_NAME}\" 2>/dev/null || true"
    ssh_exec "su - postgres -c \"dropuser --if-exists ${DB_USER}\" 2>/dev/null || true"
    ssh_exec "systemctl daemon-reload"
    log_ok "Backend rolled back"
}

rollback_frontend() {
    log_info "Rolling back frontend..."
    ssh_exec "rm -rf ${DEPLOY_BASE_DIR}/frontend"
    ssh_exec "rm -f /etc/nginx/sites-enabled/ad-biz-sys"
    ssh_exec "rm -f /etc/nginx/sites-available/ad-biz-sys"
    backup_config "/etc/nginx/"
    ssh_exec "systemctl restart nginx 2>/dev/null || true"
    log_ok "Frontend rolled back"
}

rollback_samba() {
    log_info "Rolling back Samba4 AD DC..."
    ssh_exec "systemctl stop samba-ad-dc 2>/dev/null || true"
    ssh_exec "systemctl disable samba-ad-dc 2>/dev/null || true"
    ssh_exec "rm -f /etc/systemd/system/samba-ad-dc.service"
    ssh_exec "rm -rf /etc/samba/smb.conf /var/lib/samba/private /var/lib/samba/sysvol /var/lib/samba/state"
    ssh_exec "rm -f /etc/krb5.conf"
    ssh_exec "systemctl daemon-reload"
    log_ok "Samba4 AD DC rolled back"
}

rollback_all() {
    rollback_backend
    rollback_frontend
    rollback_samba
    ssh_exec "rm -rf ${DEPLOY_BASE_DIR}"
    log_ok "Full rollback completed"
}

case "${COMPONENT}" in
    backend)  rollback_backend ;;
    frontend) rollback_frontend ;;
    samba)    rollback_samba ;;
    all)      rollback_all ;;
    *)        handle_error "ROLLBACK_INVALID_COMPONENT" "Unknown component: ${COMPONENT}. Use: backend|frontend|samba|all" ;;
esac

print_summary