#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/00-load-env.sh"

log_step "06" "Deployment Verification & End-to-End Testing"

REPORT_FILE="${DEPLOY_BASE_DIR}/reports/verify-$(date +%Y%m%d_%H%M%S).json"
ssh_exec "mkdir -p ${DEPLOY_BASE_DIR}/reports"

V_PASS=0
V_FAIL=0
RESULTS=""

verify() {
    local id="$1"
    local name="$2"
    shift 2
    if "$@" 2>/dev/null; then
        log_ok "[${id}] ${name}"
        RESULTS="${RESULTS}, {\"id\":\"${id}\",\"name\":\"${name}\",\"result\":\"PASS\"}"
        V_PASS=$((V_PASS + 1))
    else
        log_fail "[${id}] ${name}"
        RESULTS="${RESULTS}, {\"id\":\"${id}\",\"name\":\"${name}\",\"result\":\"FAIL\"}"
        V_FAIL=$((V_FAIL + 1))
    fi
}

log_step "06-A" "Component Health Checks"
verify "V01" "samba-ad-dc service active" ssh_exec "systemctl is-active samba-ad-dc | grep -q active"
verify "V02" "PostgreSQL service active" ssh_exec "systemctl is-active postgresql | grep -q active"
verify "V03" "Redis service active" ssh_exec "systemctl is-active redis-server | grep -q active"
verify "V04" "Nginx service active" ssh_exec "systemctl is-active nginx | grep -q active"
verify "V05" "Backend service active" ssh_exec "systemctl is-active ad-biz-sys-backend | grep -q active"

log_step "06-B" "AD Integration Verification"
verify "V06" "Kerberos authentication" ssh_exec_nosudo "echo '${AD_ADMIN_PASSWORD}' | kinit Administrator@${AD_REALM}"
verify "V07" "LDAP Bind authentication" ssh_exec "ldapsearch -H ldaps://${SERVER_HOSTNAME} -D 'CN=Administrator,CN=Users,DC=${AD_DOMAIN%%.*},DC=${AD_DOMAIN#*.}' -w '${AD_ADMIN_PASSWORD}' -b 'DC=${AD_DOMAIN%%.*},DC=${AD_DOMAIN#*.}' -s base dn 2>/dev/null | grep -q 'dn:'"
verify "V08" "DNS resolution" ssh_exec "host ${SERVER_HOSTNAME} 127.0.0.1 | grep -q 'has address'"
verify "V09" "AD OU data exists" ssh_exec "samba-tool ou list | grep -q 'Company'"

log_step "06-C" "API Functional Verification"
verify "V10" "Health endpoint" ssh_exec "curl -sf http://127.0.0.1:8000/api/health | grep -q 'healthy'"
verify "V11" "Login endpoint responds" ssh_exec "curl -sf -X POST http://127.0.0.1:8000/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"zhangwei\",\"password\":\"UserP@ss2026!\"}' | grep -q 'code'"
verify "V12" "OU tree endpoint" ssh_exec "curl -sf http://127.0.0.1:8000/api/org/ou-tree | grep -q 'code'"
verify "V13" "User list endpoint" ssh_exec "curl -sf http://127.0.0.1:8000/api/org/users | grep -q 'code'"
verify "V14" "HTTPS frontend access" ssh_exec "curl -k -sf https://${NGINX_SERVER_NAME}/ | grep -q 'html'"

log_step "06-D" "Generate Verification Report"
RESULTS="${RESULTS#, }"
ssh_exec "cat > ${REPORT_FILE} <<'REPORTEOF'
{
    \"timestamp\": \"$(date -Iseconds)\",
    \"server\": \"${SERVER_IP}\",
    \"total_checks\": $((V_PASS + V_FAIL)),
    \"passed\": ${V_PASS},
    \"failed\": ${V_FAIL},
    \"results\": [${RESULTS}]
}
REPORTEOF"
log_ok "Verification report written to ${REPORT_FILE}"

echo -e "\n${CYAN}=== Verification Summary ===${NC}"
echo -e "  ${GREEN}PASS:${NC} ${V_PASS}"
echo -e "  ${RED}FAIL:${NC} ${V_FAIL}"

if [ ${V_FAIL} -gt 0 ]; then
    echo -e "\n${RED}Verification completed with ${V_FAIL} failures!${NC}"
    exit 1
else
    echo -e "\n${GREEN}All ${V_PASS} verification checks passed!${NC}"
fi