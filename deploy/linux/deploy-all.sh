#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DRY_RUN=false
SKIP_STEPS=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)    DRY_RUN=true; shift ;;
        --skip-step=*) SKIP_STEPS="${SKIP_STEPS} ${1#--skip-step=}"; shift ;;
        *)            echo "Unknown option: $1"; exit 1 ;;
    esac
done

STEPS=(
    "01:01-prepare-server.sh:Server Environment Preparation"
    "02:02-setup-samba-ad-dc.sh:Samba4 AD Domain Controller Setup"
    "03:03-init-ad-testdata.sh:AD Test Data Initialization"
    "04:04-deploy-backend.sh:AD Biz Sys Backend Deployment"
    "05:05-deploy-frontend.sh:AD Biz Sys Frontend Deployment"
    "06:06-verify-deployment.sh:Deployment Verification"
)

echo -e "\033[0;36m========================================\033[0m"
echo -e "\033[0;36m  AD Biz Sys - One-Click Deployment\033[0m"
echo -e "\033[0;36m========================================\033[0m"
echo ""

if [ "${DRY_RUN}" = true ]; then
    echo -e "\033[1;33m[DRY RUN] The following steps will be executed:\033[0m"
    for step in "${STEPS[@]}"; do
        IFS=':' read -r num script name <<< "$step"
        if echo "${SKIP_STEPS}" | grep -qw "${num}"; then
            echo -e "  \033[0;33m[SKIP] Step ${num}: ${name}\033[0m"
        else
            echo -e "  \033[0;32m[RUN]  Step ${num}: ${name}\033[0m"
        fi
    done
    exit 0
fi

source "${SCRIPT_DIR}/00-load-env.sh"

FAILED_STEPS=()

for step in "${STEPS[@]}"; do
    IFS=':' read -r num script name <<< "$step"

    if echo "${SKIP_STEPS}" | grep -qw "${num}"; then
        echo -e "\033[1;33m[SKIP] Step ${num}: ${name}\033[0m"
        continue
    fi

    echo -e "\n\033[0;36m>>> Executing Step ${num}: ${name}\033[0m"
    if bash "${SCRIPT_DIR}/${script}"; then
        echo -e "\033[0;32m<<< Step ${num} completed successfully\033[0m"
    else
        echo -e "\033[0;31m<<< Step ${num} FAILED!\033[0m"
        FAILED_STEPS+=("${num}:${name}")
        echo -e "\033[1;33mChoose action:\033[0m"
        echo "  1) Continue to next step"
        echo "  2) Retry this step"
        echo "  3) Abort deployment"
        echo "  4) Rollback everything"
        read -rp "Enter choice [1-4]: " choice
        case "${choice}" in
            1) continue ;;
            2)
                if bash "${SCRIPT_DIR}/${script}"; then
                    echo -e "\033[0;32m<<< Step ${num} retry succeeded\033[0m"
                else
                    echo -e "\033[0;31m<<< Step ${num} retry FAILED, aborting\033[0m"
                    exit 1
                fi
                ;;
            3) exit 1 ;;
            4) bash "${SCRIPT_DIR}/07-rollback.sh" all; exit 1 ;;
            *) exit 1 ;;
        esac
    fi
done

echo -e "\n\033[0;36m========================================\033[0m"
if [ ${#FAILED_STEPS[@]} -eq 0 ]; then
    echo -e "\033[0;32m  Deployment Completed Successfully!\033[0m"
else
    echo -e "\033[0;31m  Deployment completed with ${#FAILED_STEPS[@]} failed steps\033[0m"
    for fs in "${FAILED_STEPS[@]}"; do
        echo -e "\033[0;31m    - ${fs}\033[0m"
    done
fi
echo -e "\033[0;36m========================================\033[0m"