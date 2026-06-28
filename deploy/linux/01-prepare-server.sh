#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/00-load-env.sh"

log_step "01" "Server Environment Preparation"

log_step "01-1" "Verify SSH connection and sudo"
if ssh_exec "whoami" | grep -q "root"; then
    log_ok "SSH connection and sudo verified"
else
    handle_error "DEPLOY_SSH_FAILED" "Cannot establish SSH with sudo"
fi

log_step "01-2" "Check disk space"
AVAIL_GB=$(ssh_exec "df -BG / | tail -1 | awk '{print \$4}' | tr -d 'G'")
if [ "${AVAIL_GB:-0}" -lt 5 ]; then
    handle_error "DEPLOY_DISK_FULL" "Available disk space ${AVAIL_GB}GB is less than 5GB"
else
    log_ok "Disk space: ${AVAIL_GB}GB available"
fi

log_step "01-3" "Set hostname and /etc/hosts"
ssh_exec "hostnamectl set-hostname ${SERVER_HOSTNAME} 2>/dev/null || echo '${SERVER_HOSTNAME}' > /etc/hostname"
ssh_exec "grep -q '${SERVER_HOSTNAME}' /etc/hosts || echo '127.0.1.1 ${SERVER_HOSTNAME} ${SERVER_HOSTNAME%%.*}' >> /etc/hosts"
log_ok "Hostname set to ${SERVER_HOSTNAME}"

log_step "01-4" "Update system packages"
log_info "Running apt update && apt upgrade (this may take a while)..."
ssh_exec "apt update -qq && apt upgrade -y -qq" || log_warn "apt upgrade had warnings"
log_ok "System packages updated"

log_step "01-5" "Install system dependencies"
PACKAGES="python3 python3-venv python3-pip python3-dev
postgresql postgresql-client libpq-dev
redis-server nginx
samba samba-ad-dc samba-dsdb-modules samba-vfs-modules
krb5-config krb5-user libkrb5-dev
libldap2-dev libsasl2-dev
nodejs npm ntp rsync curl jq openssl acl"
ssh_exec "apt install -y -qq ${PACKAGES}" || log_warn "Some packages may have failed to install"
log_ok "System dependencies installed"

log_step "01-6" "Configure UFW firewall"
ssh_exec "ufw allow 53,88,389,445,636,5432,6379,80,443/tcp" || log_warn "UFW TCP rules may have issues"
ssh_exec "ufw allow 53,88/udp" || log_warn "UFW UDP rules may have issues"
ssh_exec "echo 'y' | ufw enable 2>/dev/null || true"
log_ok "Firewall rules configured"

log_step "01-7" "Enable NTP time sync"
ssh_exec "systemctl enable --now ntp 2>/dev/null || systemctl enable --now systemd-timesyncd 2>/dev/null || true"
log_ok "NTP time sync enabled"

log_step "01-8" "Environment preparation summary"
print_summary