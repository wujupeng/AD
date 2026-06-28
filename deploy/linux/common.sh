#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

_OK=0
_FAIL=0
_WARN=0

log_ok()   { echo -e "${GREEN}[OK]${NC} $*"; ((_OK++)); }
log_fail() { echo -e "${RED}[FAIL]${NC} $*"; ((_FAIL++)); }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; ((_WARN++)); }
log_info() { echo -e "${CYAN}[INFO]${NC} $*"; }
log_step() { echo -e "\n${CYAN}=== Step $1: $2 ===${NC}"; }

ssh_exec() {
    local cmd="$1"
    local max_retries="${2:-3}"
    local retry=0
    local rc=0
    while [ $retry -lt $max_retries ]; do
        sshpass -p "${SSH_PASSWORD}" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "${SSH_USER}@${SERVER_IP}" \
            "echo '${SUDO_PASSWORD}' | sudo -S bash -c '${cmd}'" 2>/dev/null && rc=0 && break
        rc=$?
        retry=$((retry + 1))
        if [ $retry -lt $max_retries ]; then
            log_warn "SSH command failed (attempt $retry/$max_retries), retrying in 5s..."
            sleep 5
        fi
    done
    return $rc
}

ssh_exec_nosudo() {
    local cmd="$1"
    local max_retries="${2:-3}"
    local retry=0
    local rc=0
    while [ $retry -lt $max_retries ]; do
        sshpass -p "${SSH_PASSWORD}" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "${SSH_USER}@${SERVER_IP}" \
            "${cmd}" 2>/dev/null && rc=0 && break
        rc=$?
        retry=$((retry + 1))
        if [ $retry -lt $max_retries ]; then
            log_warn "SSH command failed (attempt $retry/$max_retries), retrying in 5s..."
            sleep 5
        fi
    done
    return $rc
}

ssh_copy() {
    local src="$1"
    local dst="$2"
    sshpass -p "${SSH_PASSWORD}" scp -o StrictHostKeyChecking=no -r "${src}" "${SSH_USER}@${SERVER_IP}:${dst}"
}

ssh_copy_to() {
    local src="$1"
    local dst="$2"
    ssh_copy "${src}" "/tmp/ad-biz-sys-upload/"
    ssh_exec "mkdir -p $(dirname ${dst}) && cp -r /tmp/ad-biz-sys-upload/$(basename ${src}) ${dst} && rm -rf /tmp/ad-biz-sys-upload/"
}

check_service_exists() {
    local service="$1"
    ssh_exec "systemctl is-active ${service}" 2>/dev/null
}

check_file_exists() {
    local filepath="$1"
    ssh_exec "test -f ${filepath}" 2>/dev/null
}

check_port_listening() {
    local port="$1"
    ssh_exec "ss -tlnp | grep -q ':${port} '" 2>/dev/null
}

check_ad_provisioned() {
    ssh_exec "test -f /etc/samba/smb.conf && grep -q 'domain controller' /etc/samba/smb.conf" 2>/dev/null
}

handle_error() {
    local code="$1"
    local message="${2:-Unknown error}"
    log_fail "[$code] $message"
    if [ "${ERROR_MODE:-abort}" = "abort" ]; then
        log_fail "Deployment aborted."
        exit 1
    fi
}

backup_config() {
    local filepath="$1"
    local timestamp
    timestamp=$(date +%Y%m%d_%H%M%S)
    ssh_exec "mkdir -p ${DEPLOY_BASE_DIR}/backup && cp -r ${filepath} ${DEPLOY_BASE_DIR}/backup/$(basename ${filepath}).${timestamp} 2>/dev/null || true"
}

print_summary() {
    echo -e "\n${CYAN}=== Summary ===${NC}"
    echo -e "  ${GREEN}OK:${NC}   ${_OK}"
    echo -e "  ${RED}FAIL:${NC} ${_FAIL}"
    echo -e "  ${YELLOW}WARN:${NC} ${_WARN}"
    if [ ${_FAIL} -gt 0 ]; then
        echo -e "\n${RED}Deployment completed with errors!${NC}"
        return 1
    else
        echo -e "\n${GREEN}Deployment completed successfully!${NC}"
        return 0
    fi
}