#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/00-load-env.sh"

log_step "02" "Samba4 AD Domain Controller Setup"

log_step "02-1" "Check if AD is already provisioned"
if check_ad_provisioned; then
    log_warn "Samba4 AD DC already provisioned, skipping"
    exit 0
fi

log_step "02-2" "Stop conflicting services"
ssh_exec "systemctl stop smbd nmbd winbind 2>/dev/null || true"
ssh_exec "systemctl disable smbd nmbd winbind 2>/dev/null || true"
log_ok "Conflicting services stopped"

log_step "02-3" "Backup existing Samba and Kerberos config"
backup_config "/etc/samba/"
backup_config "/etc/krb5.conf"
log_ok "Existing config backed up"

log_step "02-4" "Provision Samba4 AD DC"
ssh_exec "rm -f /etc/samba/smb.conf"
ssh_exec "samba-tool domain provision \
    --domain=${AD_NETBIOS_NAME} \
    --realm=${AD_REALM} \
    --server-role=dc \
    --dns-backend=SAMBA_INTERNAL \
    --adminpass='${AD_ADMIN_PASSWORD}' \
    --use-rfc2307 \
    --option='idmap_ldb:use rfc2307 = yes'" || handle_error "SAMBA_PROVISION_FAILED" "samba-tool domain provision failed"
log_ok "Samba4 AD DC provisioned"

log_step "02-5" "Configure Kerberos"
ssh_exec "cp -f /var/lib/samba/private/krb5.conf /etc/krb5.conf"
log_ok "Kerberos configured"

log_step "02-6" "Configure DNS forwarder"
ssh_exec "sed -i 's/dns forwarder = .*/dns forwarder = ${AD_DNS_FORWARDER}/' /etc/samba/smb.conf"
log_ok "DNS forwarder set to ${AD_DNS_FORWARDER}"

log_step "02-7" "Generate LDAPS self-signed certificate"
ssh_exec "mkdir -p ${DEPLOY_BASE_DIR}/certs"
ssh_exec "openssl req -new -x509 -keyout ${DEPLOY_BASE_DIR}/certs/samba.key -out ${DEPLOY_BASE_DIR}/certs/samba.crt -days 3650 -nodes -subj '/CN=${SERVER_HOSTNAME}'"
ssh_exec "chmod 600 ${DEPLOY_BASE_DIR}/certs/samba.key"
ssh_exec "cat >> /etc/samba/smb.conf <<'EOF'

[tls]
    certfile = ${DEPLOY_BASE_DIR}/certs/samba.crt
    keyfile = ${DEPLOY_BASE_DIR}/certs/samba.key
EOF"
log_ok "LDAPS certificate generated and configured"

log_step "02-8" "Create systemd service for Samba AD DC"
ssh_copy "${SCRIPT_DIR}/conf/samba-ad-dc.service" "/etc/systemd/system/samba-ad-dc.service"
ssh_exec "systemctl daemon-reload"
ssh_exec "systemctl enable samba-ad-dc"
log_ok "samba-ad-dc systemd service created"

log_step "02-9" "Start Samba AD DC"
ssh_exec "systemctl start samba-ad-dc"
sleep 5
log_ok "Samba AD DC started"

log_step "02-10" "Verify AD DC service"
if ssh_exec "systemctl is-active samba-ad-dc" | grep -q "active"; then
    log_ok "samba-ad-dc service is active"
else
    handle_error "SAMBA_SERVICE_FAILED" "samba-ad-dc service is not active"
fi

if ssh_exec_nosudo "echo '${AD_ADMIN_PASSWORD}' | kinit Administrator@${AD_REALM}" 2>/dev/null; then
    log_ok "Kerberos authentication successful"
else
    log_warn "Kerberos authentication test failed (may need DNS fix)"
fi

if ssh_exec "host ${SERVER_HOSTNAME} 127.0.0.1" 2>/dev/null; then
    log_ok "DNS resolution working"
else
    log_warn "DNS resolution test failed"
fi

print_summary