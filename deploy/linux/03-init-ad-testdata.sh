#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/00-load-env.sh"

source "${SCRIPT_DIR}/ad-testdata.conf"

log_step "03" "AD Test Data Initialization"

renew_kerberos() {
    if ! ssh_exec_nosudo "klist -s 2>/dev/null"; then
        ssh_exec_nosudo "echo '${AD_ADMIN_PASSWORD}' | kinit Administrator@${AD_REALM}" 2>/dev/null || true
    fi
}

log_step "03-1" "Obtain Kerberos ticket"
ssh_exec_nosudo "echo '${AD_ADMIN_PASSWORD}' | kinit Administrator@${AD_REALM}" 2>/dev/null || log_warn "kinit failed, trying with samba-tool directly"
log_ok "Kerberos ticket obtained"

log_step "03-2" "Create Organizational Units"
OU_BASE="DC=${AD_DOMAIN%%.*},DC=${AD_DOMAIN#*.}"
while IFS= read -r ou_path; do
    [ -z "$ou_path" ] && continue
    ou_path=$(echo "$ou_path" | xargs)
    IFS='/' read -ra parts <<< "$ou_path"
    parent_dn="$OU_BASE"
    for part in "${parts[@]}"; do
        ou_dn="OU=${part},${parent_dn}"
        if ! ssh_exec "samba-tool ou list 2>/dev/null | grep -q '${ou_dn}'" 2>/dev/null; then
            ssh_exec "samba-tool ou create '${ou_dn}'" 2>/dev/null && log_ok "Created OU: ${ou_dn}" || log_warn "OU may already exist: ${ou_dn}"
        else
            log_info "OU already exists: ${ou_dn}"
        fi
        parent_dn="$ou_dn"
    done
done <<< "$OU_LIST"

log_step "03-3" "Create test users"
while IFS=',' read -r username displayname email department city givenname surname; do
    [ -z "$username" ] && continue
    username=$(echo "$username" | xargs)
    renew_kerberos
    OU_DN="OU=${city},OU=China,OU=Company,${OU_BASE}"
    if [ "${city}" = "Hungary" ]; then
        OU_DN="OU=Hungary,OU=Company,${OU_BASE}"
    elif [ "${city}" = "Vietnam" ]; then
        OU_DN="OU=Vietnam,OU=Company,${OU_BASE}"
    elif [ "${city}" = "Mexico" ]; then
        OU_DN="OU=Mexico,OU=Company,${OU_BASE}"
    fi
    if ssh_exec "samba-tool user list 2>/dev/null | grep -q '^${username}$'"; then
        log_info "User already exists: ${username}"
    else
        ssh_exec "samba-tool user create '${username}' '${USER_PASSWORD}' \
            --mail='${email}' \
            --department='${department}' \
            --given-name='${givenname}' \
            --surname='${surname}' \
            --company='Company'" 2>/dev/null && log_ok "Created user: ${username}" || log_warn "Failed to create user: ${username}"
        ssh_exec "samba-tool user move '${username}' '${OU_DN}'" 2>/dev/null || true
    fi
done <<< "$USERS_CSV"

log_step "03-4" "Create global groups (GG_)"
while IFS= read -r group; do
    [ -z "$group" ] && continue
    group=$(echo "$group" | xargs)
    renew_kerberos
    if ssh_exec "samba-tool group list 2>/dev/null | grep -q '^${group}$'"; then
        log_info "Group already exists: ${group}"
    else
        ssh_exec "samba-tool group add '${group}' --group-scope=Global" 2>/dev/null && log_ok "Created global group: ${group}" || log_warn "Failed to create group: ${group}"
    fi
done <<< "$GLOBAL_GROUPS"

log_step "03-5" "Create domain local groups (DL_)"
while IFS= read -r group; do
    [ -z "$group" ] && continue
    group=$(echo "$group" | xargs)
    renew_kerberos
    if ssh_exec "samba-tool group list 2>/dev/null | grep -q '^${group}$'"; then
        log_info "Group already exists: ${group}"
    else
        ssh_exec "samba-tool group add '${group}' --group-scope=DomainLocal" 2>/dev/null && log_ok "Created domain local group: ${group}" || log_warn "Failed to create group: ${group}"
    fi
done <<< "$DOMAIN_LOCAL_GROUPS"

log_step "03-6" "Configure group memberships (GG_)"
while IFS= read -r line; do
    [ -z "$line" ] && continue
    group=$(echo "$line" | cut -d: -f1 | xargs)
    members=$(echo "$line" | cut -d: -f2 | xargs)
    renew_kerberos
    for member in $(echo "$members" | tr ',' ' '); do
        member=$(echo "$member" | xargs)
        ssh_exec "samba-tool group addmembers '${group}' '${member}'" 2>/dev/null && log_ok "Added ${member} to ${group}" || log_info "${member} may already be in ${group}"
    done
done <<< "$GROUP_MEMBERS_GG"

log_step "03-6b" "Configure group memberships (DL_)"
while IFS= read -r line; do
    [ -z "$line" ] && continue
    group=$(echo "$line" | cut -d: -f1 | xargs)
    members=$(echo "$line" | cut -d: -f2 | xargs)
    renew_kerberos
    for member in $(echo "$members" | tr ',' ' '); do
        member=$(echo "$member" | xargs)
        ssh_exec "samba-tool group addmembers '${group}' '${member}'" 2>/dev/null && log_ok "Added ${member} to ${group}" || log_info "${member} may already be in ${group}"
    done
done <<< "$GROUP_MEMBERS_DL"

log_step "03-7" "Create service account"
renew_kerberos
if ssh_exec "samba-tool user list 2>/dev/null | grep -q '^svc_adbiz$'"; then
    log_info "Service account already exists: svc_adbiz"
else
    ssh_exec "samba-tool user create 'svc_adbiz' '${SVC_ACCOUNT_PASSWORD}' \
        --given-name='AD Biz Sys' \
        --surname='Service Account' \
        --company='Company'" 2>/dev/null && log_ok "Created service account: svc_adbiz" || log_warn "Failed to create svc_adbiz"
    SA_OU="OU=ServiceAccounts,OU=Company,${OU_BASE}"
    ssh_exec "samba-tool user move 'svc_adbiz' '${SA_OU}'" 2>/dev/null || true
fi

log_step "03-9" "Verify data integrity"
OU_COUNT=$(ssh_exec "samba-tool ou list 2>/dev/null | wc -l" || echo "0")
USER_COUNT=$(ssh_exec "samba-tool user list 2>/dev/null | wc -l" || echo "0")
GROUP_COUNT=$(ssh_exec "samba-tool group list 2>/dev/null | wc -l" || echo "0")
log_info "AD data: ${OU_COUNT} OUs, ${USER_COUNT} users, ${GROUP_COUNT} groups"

ssh_exec "samba-tool group listmembers 'GG_ERP_Finance' 2>/dev/null" && log_ok "GG_ERP_Finance members verified" || log_warn "GG_ERP_Finance member verification failed"

print_summary