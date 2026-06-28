from typing import Any
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


def _parse_datetime(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            pass
    return value


def _normalize_datetimes(data: dict[str, Any], datetime_fields: list[str]) -> dict[str, Any]:
    result = dict(data)
    for field in datetime_fields:
        if field in result:
            result[field] = _parse_datetime(result[field])
    return result


_EVENT_TYPE_MAP = {
    "onboarding": "onboarding_started",
    "offboarding": "offboarding_started",
    "transfer": "transfer_started",
    "onboarding_completed": "onboarding_completed",
    "offboarding_completed": "offboarding_completed",
    "transfer_completed": "transfer_completed",
    "onboarding_partial_failed": "onboarding_partial_failed",
    "offboarding_partial_failed": "offboarding_partial_failed",
    "transfer_partial_failed": "transfer_partial_failed",
}



class IdentityCenterService:
    def __init__(
        self,
        lifecycle_repo: Any = None,
        onboarding_repo: Any = None,
        offboarding_repo: Any = None,
        transfer_repo: Any = None,
        print_cost_repo: Any = None,
        wifi_policy_repo: Any = None,
        autopilot_repo: Any = None,
        ca_rule_repo: Any = None,
        saml_oidc_repo: Any = None,
        identity_source_repo: Any = None,
    ):
        self._lifecycle_repo = lifecycle_repo
        self._onboarding_repo = onboarding_repo
        self._offboarding_repo = offboarding_repo
        self._transfer_repo = transfer_repo
        self._print_cost_repo = print_cost_repo
        self._wifi_policy_repo = wifi_policy_repo
        self._autopilot_repo = autopilot_repo
        self._ca_rule_repo = ca_rule_repo
        self._saml_oidc_repo = saml_oidc_repo
        self._identity_source_repo = identity_source_repo

    async def trigger_onboarding(self, data: dict[str, Any]) -> dict[str, Any]:
        if not self._onboarding_repo:
            return {"status": "error", "message": "Repository not available"}
        field_map = {"ad_account": "sam_account_name", "title": "position", "site_code": "site"}
        for old, new in field_map.items():
            if old in data and new not in data:
                data[new] = data.pop(old)
        if "start_date" in data:
            data.pop("start_date")
        normalized = _normalize_datetimes(data, [])
        allowed = {"request_id", "employee_name", "employee_name_en", "department", "position", "site", "sam_account_name", "card_id", "card_type", "device_type", "erp_role", "mes_permission", "plm_permission", "gitlab_role", "manager_account", "status", "step_results", "trigger_source", "created_at", "completed_at", "estimated_completion_at"}
        filtered = {k: v for k, v in normalized.items() if k in allowed}
        if "department" not in filtered:
            filtered["department"] = "default"
        if "position" not in filtered:
            filtered["position"] = "employee"
        if "site" not in filtered:
            filtered["site"] = "hq"
        sam = filtered.get("sam_account_name", "")
        existing = await self._onboarding_repo.get_all(limit=1000)
        if any(r.sam_account_name == sam for r in existing):
            return {"status": "duplicate", "request_id": None, "message": f"Onboarding request for {sam} already exists"}
        request = await self._onboarding_repo.create(filtered)
        sam = filtered.get("sam_account_name", "")
        dept = filtered.get("department", "")
        site = filtered.get("site", "hq")
        await self._record_lifecycle("onboarding", sam, "hr_system", {"department": dept, "position": filtered.get("position", ""), "site": site})
        step_results = {"db_record": "success"}
        if sam:
            ad_result = await self._create_ad_user(sam, filtered.get("employee_name", sam), dept, site)
            step_results["ad_user_created"] = ad_result
            if ad_result == "success":
                await self._update_db_user_enabled(sam, True, site)
                await self._record_lifecycle("onboarding_completed", sam, "system_auto", {"ad_user": sam})
        try:
            request.step_results = step_results
            request.status = "completed" if all(v == "success" for v in step_results.values()) else "partial_failed"
            await self._onboarding_repo._session.commit()
        except Exception:
            pass
        return {"status": request.status, "request_id": request.request_id, "message": "Onboarding request processed", "step_results": step_results}

    async def list_onboarding(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self._onboarding_repo:
            return []
        items = await self._onboarding_repo.get_all(limit=limit)
        return [{"request_id": r.request_id, "employee_name": r.employee_name, "sam_account_name": r.sam_account_name, "department": r.department, "position": r.position, "site": r.site, "status": r.status, "step_results": r.step_results, "created_at": r.created_at.isoformat() if r.created_at else None} for r in items]

    async def execute_onboarding(self, request_id: str) -> dict[str, Any]:
        if not self._onboarding_repo:
            return {"status": "error", "message": "Repository not available"}
        req = await self._onboarding_repo.get_by_id(request_id)
        if not req:
            return {"status": "error", "message": "Request not found"}
        sam = req.sam_account_name
        step_results = dict(req.step_results or {})
        ad_result = await self._create_ad_user(sam, req.employee_name, req.department, req.site)
        step_results["ad_user_created"] = ad_result
        if ad_result == "success":
            await self._update_db_user_enabled(sam, True, req.site)
            await self._record_lifecycle("onboarding_completed", sam, "admin_manual", {"ad_user": sam})
        req.step_results = step_results
        req.status = "completed" if all(v == "success" for v in step_results.values()) else "partial_failed"
        await self._onboarding_repo._session.commit()
        return {"status": req.status, "request_id": request_id, "step_results": step_results}

    async def get_onboarding_status(self, request_id: str) -> dict[str, Any] | None:
        if not self._onboarding_repo:
            return None
        return await self._onboarding_repo.get_by_id(request_id)

    async def trigger_offboarding(self, data: dict[str, Any]) -> dict[str, Any]:
        if not self._offboarding_repo:
            return {"status": "error", "message": "Repository not available"}
        normalized = _normalize_datetimes(data, ["offboarding_date"])
        if "wipe_devices" in normalized and "wipe_device" not in normalized:
            normalized["wipe_device"] = normalized.pop("wipe_devices")
        allowed = {"request_id", "ad_account", "offboarding_date", "mailbox_retention_days", "mailbox_forward_to", "wipe_device", "revoke_all_access", "status", "step_results", "trigger_source", "created_at", "completed_at", "estimated_completion_at"}
        filtered = {k: v for k, v in normalized.items() if k in allowed}
        request = await self._offboarding_repo.create(filtered)
        ad_account = filtered.get("ad_account", "")
        await self._record_lifecycle("offboarding", ad_account, "hr_system", {"offboarding_date": str(filtered.get("offboarding_date", "")), "revoke_all_access": filtered.get("revoke_all_access", True)})
        step_results = {"db_record": "success"}
        if ad_account and filtered.get("revoke_all_access", True):
            disable_result = await self._disable_ad_user(ad_account)
            step_results["ad_account_disabled"] = disable_result
            if disable_result == "success":
                await self._update_db_user_enabled(ad_account, False)
                await self._record_lifecycle("offboarding_completed", ad_account, "system_auto", {"account_disabled": True})
        try:
            request.step_results = step_results
            request.status = "completed" if all(v == "success" for v in step_results.values()) else "partial_failed"
            await self._offboarding_repo._session.commit()
        except Exception:
            pass
        return {"status": request.status, "request_id": request.request_id, "message": "Offboarding request processed", "step_results": step_results}

    async def list_offboarding(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self._offboarding_repo:
            return []
        items = await self._offboarding_repo.get_all(limit=limit)
        return [{"request_id": r.request_id, "ad_account": r.ad_account, "offboarding_date": r.offboarding_date.isoformat() if r.offboarding_date else None, "mailbox_retention_days": r.mailbox_retention_days, "wipe_device": r.wipe_device, "revoke_all_access": r.revoke_all_access, "status": r.status, "step_results": r.step_results, "created_at": r.created_at.isoformat() if r.created_at else None} for r in items]

    async def get_offboarding_status(self, request_id: str) -> dict[str, Any] | None:
        if not self._offboarding_repo:
            return None
        return await self._offboarding_repo.get_by_id(request_id)

    async def execute_offboarding(self, request_id: str) -> dict[str, Any]:
        if not self._offboarding_repo:
            return {"status": "error", "message": "Repository not available"}
        req = await self._offboarding_repo.get_by_id(request_id)
        if not req:
            return {"status": "error", "message": "Request not found"}
        ad_account = req.ad_account
        step_results = dict(req.step_results or {})
        disable_result = await self._disable_ad_user(ad_account)
        step_results["ad_account_disabled"] = disable_result
        if disable_result == "success":
            await self._update_db_user_enabled(ad_account, False)
            await self._record_lifecycle("offboarding_completed", ad_account, "admin_manual", {"account_disabled": True})
        req.step_results = step_results
        req.status = "completed" if all(v == "success" for v in step_results.values()) else "partial_failed"
        await self._offboarding_repo._session.commit()
        return {"status": req.status, "request_id": request_id, "step_results": step_results}

    async def trigger_transfer(self, data: dict[str, Any]) -> dict[str, Any]:
        if not self._transfer_repo:
            return {"status": "error", "message": "Repository not available"}
        normalized = _normalize_datetimes(data, ["transfer_date"])
        allowed = {"request_id", "ad_account", "from_department", "to_department", "from_site", "to_site", "transfer_date", "new_title", "new_manager", "status", "step_results", "trigger_source", "created_at", "completed_at", "estimated_completion_at"}
        filtered = {k: v for k, v in normalized.items() if k in allowed}
        request = await self._transfer_repo.create(filtered)
        await self._record_lifecycle("transfer", filtered.get("ad_account", ""), "hr_system", {"from_department": filtered.get("from_department", ""), "to_department": filtered.get("to_department", ""), "from_site": filtered.get("from_site", ""), "to_site": filtered.get("to_site", "")})
        return {"status": "pending", "request_id": request.request_id, "message": "Transfer request created"}

    async def list_transfer(self, limit: int = 50) -> list[dict[str, Any]]:
        if not self._transfer_repo:
            return []
        items = await self._transfer_repo.get_all(limit=limit)
        return [{"request_id": r.request_id, "ad_account": r.ad_account, "from_department": r.from_department, "to_department": r.to_department, "status": r.status, "created_at": r.created_at.isoformat() if r.created_at else None} for r in items]

    async def get_transfer_status(self, request_id: str) -> dict[str, Any] | None:
        if not self._transfer_repo:
            return None
        return await self._transfer_repo.get_by_id(request_id)

    async def _disable_ad_user(self, username: str) -> str:
        try:
            proc = await asyncio.create_subprocess_exec(
                "samba-tool", "user", "disable", username, "-H", "ldap://127.0.0.1",
                "-U", "Administrator%*****",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.wait(), timeout=15)
            if proc.returncode == 0:
                logger.info("Disabled AD user %s via samba-tool", username)
                return "success"
            stderr = await proc.stderr.read()
            err = stderr.decode()[:200]
            logger.warning("samba-tool disable failed for %s: %s, trying rpcclient", username, err)
            proc2 = await asyncio.create_subprocess_exec(
                "rpcclient", "-U", "CII/Administrator%*****", "-c", f"userdisablentlm {username}", "******",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc2.wait(), timeout=15)
            if proc2.returncode == 0:
                logger.info("Disabled AD user %s via rpcclient on cii_factory", username)
                return "success"
            proc3 = await asyncio.create_subprocess_exec(
                "winexe", "--ostype=2", "-U", "CII/Administrator%*****", "//******",
                f'powershell -Command "Disable-ADAccount -Identity {username}"',
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc3.wait(), timeout=30)
            if proc3.returncode == 0:
                logger.info("Disabled AD user %s via winexe/PowerShell on cii_factory", username)
                return "success"
            logger.warning("All disable methods failed for %s", username)
            return "failed"
        except Exception as e:
            logger.warning("Error disabling AD user %s: %s", username, e)
            return "error"

    async def _create_ad_user(self, sam_account: str, display_name: str, department: str, site: str) -> str:
        try:
            if site in ("cii_factory", "FactoryCN", "cii.sh.cn"):
                return await self._create_ad_user_remote(sam_account, display_name, department)
            password = "*****"
            proc = await asyncio.create_subprocess_exec(
                "samba-tool", "user", "create", sam_account, password,
                "--given-name", display_name, "--mail", f"{sam_account}@company.local",
                "-H", "ldap://127.0.0.1", "-U", "Administrator%*****",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.wait(), timeout=15)
            if proc.returncode == 0:
                logger.info("Created AD user %s via samba-tool", sam_account)
                return "success"
            stderr = await proc.stderr.read()
            err = stderr.decode()
            if "already_exists" in err.lower() or "already exists" in err.lower():
                logger.info("AD user %s already exists", sam_account)
                return "success"
            logger.warning("Failed to create AD user %s: %s", sam_account, err[:300])
            return "failed"
        except Exception as e:
            logger.warning("Error creating AD user %s: %s", sam_account, e)
            return "error"

    async def _create_ad_user_remote(self, sam_account: str, display_name: str, department: str) -> str:
        try:
            proc = await asyncio.create_subprocess_exec(
                "rpcclient", "-U", "CII/Administrator%*****", "-c",
                f"createdomuser {sam_account}",
                "******",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.wait(), timeout=15)
            created = False
            if proc.returncode == 0:
                created = True
                logger.info("Created AD user %s via rpcclient on cii_factory", sam_account)
            else:
                stderr = await proc.stderr.read()
                err = stderr.decode()
                if "already exists" in err.lower() or "STATUS_OBJECT_NAME_COLLISION" in err:
                    created = True
                    logger.info("AD user %s already exists on cii_factory", sam_account)
                else:
                    logger.warning("rpcclient create failed for %s: %s", sam_account, err[:200])

            if not created:
                return "failed"

            await self._set_remote_user_password(sam_account)
            await self._enable_remote_user(sam_account, display_name)
            return "success"
        except Exception as e:
            logger.warning("Error creating AD user %s on cii_factory: %s", sam_account, e)
            return "error"

    async def _set_remote_user_password(self, sam_account: str):
        try:
            proc = await asyncio.create_subprocess_exec(
                "rpcclient", "-U", "CII/Administrator%*****", "-c",
                f"setuserinfo2 {sam_account} 23 *****",
                "******",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.wait(), timeout=15)
            if proc.returncode == 0:
                logger.info("Set password for %s on cii_factory", sam_account)
            else:
                logger.warning("Failed to set password for %s on cii_factory", sam_account)
        except Exception as e:
            logger.warning("Error setting password for %s: %s", sam_account, e)

    async def _enable_remote_user(self, sam_account: str, display_name: str):
        try:
            import tempfile, os
            ps_content = (
                f"$secpasswd = ConvertTo-SecureString '*****' -AsPlainText -Force\n"
                f"$cred = New-Object System.Management.Automation.PSCredential ('cii\\Administrator', $secpasswd)\n"
                f"Enable-ADAccount -Identity '{sam_account}' -Server dcser1.cii.sh.cn -Credential $cred\n"
                f"Set-ADUser -Identity '{sam_account}' -Server dcser1.cii.sh.cn -Credential $cred "
                f"-DisplayName '{display_name}' -GivenName '{display_name}'\n"
            )
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
                f.write(ps_content)
                ps_path = f.name

            proc_upload = await asyncio.create_subprocess_exec(
                "smbclient", "-U", "CII/Administrator%*****",
                "//******/C$", "-c", f"put {ps_path} enable_ad_user.ps1",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc_upload.wait(), timeout=15)
            upload_out = await proc_upload.stdout.read()
            upload_err = await proc_upload.stderr.read()
            logger.info("smbclient upload for %s: rc=%d out=%s err=%s", sam_account, proc_upload.returncode, upload_out.decode()[:100], upload_err.decode()[:100])
            os.unlink(ps_path)

            proc_exec = await asyncio.create_subprocess_exec(
                "winexe", "--ostype=2", "-U", "CII/Administrator%*****", "//******",
                "powershell -ExecutionPolicy Bypass -File C:\\enable_ad_user.ps1",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc_exec.wait(), timeout=30)
            exec_out = await proc_exec.stdout.read()
            exec_err = await proc_exec.stderr.read()
            logger.info("winexe enable for %s: rc=%d out=%s err=%s", sam_account, proc_exec.returncode, exec_out.decode()[:200], exec_err.decode()[:200])
            if proc_exec.returncode == 0 or not exec_err.strip():
                logger.info("Enabled AD user %s via winexe/PowerShell on cii_factory", sam_account)
            else:
                logger.warning("Failed to enable AD user %s on cii_factory: rc=%d stderr=%s", sam_account, proc_exec.returncode, exec_err.decode()[:200])
        except Exception as e:
            logger.warning("Error enabling AD user %s on cii_factory: %s", sam_account, e)

    async def _update_db_user_enabled(self, username: str, enabled: bool, site: str = "hq"):
        try:
            from app.core.database import async_session_factory
            from sqlalchemy import update, select
            from app.models.ad_objects import AdUser
            async with async_session_factory() as session:
                result = await session.execute(select(AdUser).where(AdUser.username == username))
                existing = result.scalar_one_or_none()
                if existing:
                    existing.is_enabled = enabled
                    await session.commit()
                    logger.info("Updated DB user %s is_enabled=%s", username, enabled)
                else:
                    if site in ("cii_factory", "FactoryCN", "cii.sh.cn"):
                        site_code = "cii_factory"
                        dn = f"CN={username},CN=Users,DC=cii,DC=sh,DC=cn"
                    else:
                        site_code = "hq"
                        dn = f"CN={username},CN=Users,DC=company,DC=local"
                    if enabled:
                        new_user = AdUser(
                            sid=f"ad-{username}",
                            dn=dn,
                            username=username,
                            display_name=username,
                            site_code=site_code,
                            is_enabled=enabled,
                            is_deleted=False,
                            is_locked=False,
                            user_account_control=512 if enabled else 514,
                            password_expired=False,
                            ou_dn=dn,
                        )
                        session.add(new_user)
                        await session.commit()
                        logger.info("Created DB user %s is_enabled=%s site=%s", username, enabled, site_code)
        except Exception as e:
            logger.warning("Failed to update DB user %s: %s", username, e)

    async def _record_lifecycle(self, action: str, ad_account: str, trigger_source: str, details: dict[str, Any] | None = None):
        if not self._lifecycle_repo:
            return
        import json
        event_type = _EVENT_TYPE_MAP.get(action, f"{action}_started")
        affected_systems = ["ad", "hr_system"]
        if action == "offboarding":
            affected_systems.extend(["exchange", "vpn", "print"])
        elif action == "onboarding":
            affected_systems.extend(["exchange", "erp"])
        elif action == "transfer":
            affected_systems.extend(["exchange", "erp"])
        try:
            await self._lifecycle_repo.create({
                "event_type": event_type,
                "ad_account": ad_account,
                "trigger_source": trigger_source,
                "old_value": json.dumps({k: v for k, v in (details or {}).items() if k.startswith("from_") or k.startswith("old_")}) if details else None,
                "new_value": json.dumps({k: v for k, v in (details or {}).items() if k.startswith("to_") or k.startswith("new_") or (not k.startswith("from_") and not k.startswith("old_"))}) if details else None,
                "affected_systems": affected_systems,
                "details": details or {},
            })
        except Exception as e:
            logger.warning("Failed to record lifecycle event: %s", e)

    async def get_lifecycle_report(self, ad_account: str) -> dict[str, Any]:
        if not self._lifecycle_repo:
            return {"ad_account": ad_account, "events": []}
        events = await self._lifecycle_repo.get_by_account(ad_account)
        return {
            "ad_account": ad_account,
            "events": [
                {
                    "event_type": e.event_type,
                    "trigger_source": e.trigger_source,
                    "event_time": e.event_time.isoformat() if e.event_time else None,
                    "old_value": e.old_value,
                    "new_value": e.new_value,
                    "affected_systems": e.affected_systems or [],
                    "details": e.details,
                }
                for e in events
            ],
        }

    async def get_lifecycle_events(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        if not self._lifecycle_repo:
            return []
        events = await self._lifecycle_repo.get_recent(limit=limit, offset=offset)
        return [
            {
                "event_id": e.event_id,
                "event_type": e.event_type,
                "ad_account": e.ad_account,
                "trigger_source": e.trigger_source,
                "event_time": e.event_time.isoformat() if e.event_time else None,
                "affected_systems": e.affected_systems or [],
                "details": e.details,
            }
            for e in events
        ]

    async def card_auth(self, card_id: str, target_system: str) -> dict[str, Any]:
        return {"status": "not_implemented", "message": "Card authentication requires LDAP/Kerberos/SAML integration", "card_id": card_id, "target_system": target_system}

    async def get_identity_source_policy(self) -> dict[str, Any]:
        if not self._identity_source_repo:
            return {"status": "not_configured"}
        policies = await self._identity_source_repo.get_all()
        if policies:
            p = policies[0]
            return {
                "policy_id": p.policy_id,
                "policy_name": p.policy_name,
                "primary_source": p.primary_source,
                "internet_extension": p.internet_extension,
                "allow_cloud_only_users": p.allow_cloud_only_users,
                "sync_failure_threshold_hours": p.sync_failure_threshold_hours,
                "downstream_systems": p.downstream_systems or [],
                "is_enabled": p.is_enabled,
            }
        return {"status": "not_configured"}

    async def configure_identity_source_policy(self, policy_id: str, **kwargs: Any) -> dict[str, Any]:
        if not self._identity_source_repo:
            return {"status": "error", "message": "Repository not available"}
        await self._identity_source_repo.update(policy_id, **kwargs)
        return {"status": "success", "message": "Identity source policy updated"}

    async def get_entra_extension_status(self) -> dict[str, Any]:
        return {"status": "not_configured", "message": "Entra ID extension requires Phase2+", "cloud_only_users_detected": 0}

    async def get_print_convergence(self) -> dict[str, Any]:
        return {"status": "not_configured", "message": "Print convergence requires Universal Print integration"}

    async def get_print_cost_audit(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        if not self._print_cost_repo:
            return []
        records = await self._print_cost_repo.get_recent(limit=limit, offset=offset)
        return [
            {
                "cost_audit_id": r.cost_audit_id,
                "owner_account": r.owner_account,
                "department": r.department,
                "operation_time": r.operation_time.isoformat() if r.operation_time else None,
                "country": r.country,
                "factory": r.factory,
                "printer_name": r.printer_name,
                "page_count": r.page_count,
                "duplex_mode": r.duplex_mode,
                "color_mode": r.color_mode,
                "paper_size": r.paper_size,
                "estimated_cost": r.estimated_cost,
                "cost_currency": r.cost_currency,
                "auth_method": r.auth_method,
            }
            for r in records
        ]

    async def generate_print_cost_report(self, params: dict[str, Any]) -> dict[str, Any]:
        if not self._print_cost_repo:
            return {"status": "error", "message": "Repository not available"}
        stats = await self._print_cost_repo.get_stats_by_department()
        return {"status": "success", "department_stats": stats, "params": params}

    async def get_saml_oidc_apps(self) -> list[dict[str, Any]]:
        if not self._saml_oidc_repo:
            return []
        apps = await self._saml_oidc_repo.get_all()
        return [
            {
                "app_id": a.app_id,
                "app_name": a.app_name,
                "protocol": a.protocol,
                "status": a.status,
                "entity_id": a.entity_id,
                "client_id": a.client_id,
                "allowed_groups": a.allowed_groups or [],
                "last_auth_time": a.last_auth_time.isoformat() if a.last_auth_time else None,
                "total_users": a.total_users,
            }
            for a in apps
        ]

    async def register_saml_oidc_app(self, data: dict[str, Any]) -> dict[str, Any]:
        if not self._saml_oidc_repo:
            return {"status": "error", "message": "Repository not available"}
        app = await self._saml_oidc_repo.create(data)
        return {"status": "success", "app_id": app.app_id, "message": "Application registered"}

    async def update_saml_oidc_app(self, app_id: str, **kwargs: Any) -> dict[str, Any]:
        if not self._saml_oidc_repo:
            return {"status": "error", "message": "Repository not available"}
        await self._saml_oidc_repo.update(app_id, **kwargs)
        return {"status": "success", "message": "Application updated"}

    async def delete_saml_oidc_app(self, app_id: str) -> dict[str, Any]:
        if not self._saml_oidc_repo:
            return {"status": "error", "message": "Repository not available"}
        await self._saml_oidc_repo.delete(app_id)
        return {"status": "success", "message": "Application deleted"}

    async def get_wifi_policies(self) -> list[dict[str, Any]]:
        if not self._wifi_policy_repo:
            return []
        policies = await self._wifi_policy_repo.get_all()
        return [
            {
                "policy_id": p.policy_id,
                "policy_name": p.policy_name,
                "ssid": p.ssid,
                "auth_method": p.auth_method,
                "certificate_template": p.certificate_template,
                "required_group": p.required_group,
                "nps_server": p.nps_server,
                "nps_port": p.nps_port,
                "is_enabled": p.is_enabled,
            }
            for p in policies
        ]

    async def create_wifi_policy(self, data: dict[str, Any]) -> dict[str, Any]:
        if not self._wifi_policy_repo:
            return {"status": "error", "message": "Repository not available"}
        policy = await self._wifi_policy_repo.create(data)
        return {"status": "success", "policy_id": policy.policy_id}

    async def update_wifi_policy(self, policy_id: str, **kwargs: Any) -> dict[str, Any]:
        if not self._wifi_policy_repo:
            return {"status": "error", "message": "Repository not available"}
        await self._wifi_policy_repo.update(policy_id, **kwargs)
        return {"status": "success", "message": "Wi-Fi policy updated"}

    async def get_autopilot_profiles(self) -> list[dict[str, Any]]:
        if not self._autopilot_repo:
            return []
        profiles = await self._autopilot_repo.get_all()
        return [
            {
                "profile_id": p.profile_id,
                "profile_name": p.profile_name,
                "target_ou_dn": p.target_ou_dn,
                "domain_join_type": p.domain_join_type,
                "intune_compliance_policy": p.intune_compliance_policy,
                "vpn_profile": p.vpn_profile,
                "wifi_profile": p.wifi_profile,
                "app_list": p.app_list or [],
                "device_type": p.device_type,
                "is_enabled": p.is_enabled,
            }
            for p in profiles
        ]

    async def create_autopilot_profile(self, data: dict[str, Any]) -> dict[str, Any]:
        if not self._autopilot_repo:
            return {"status": "error", "message": "Repository not available"}
        profile = await self._autopilot_repo.create(data)
        return {"status": "success", "profile_id": profile.profile_id}

    async def update_autopilot_profile(self, profile_id: str, **kwargs: Any) -> dict[str, Any]:
        if not self._autopilot_repo:
            return {"status": "error", "message": "Repository not available"}
        await self._autopilot_repo.update(profile_id, **kwargs)
        return {"status": "success", "message": "Autopilot profile updated"}

    async def get_conditional_access_rules(self) -> list[dict[str, Any]]:
        if not self._ca_rule_repo:
            return []
        rules = await self._ca_rule_repo.get_all()
        return [
            {
                "rule_id": r.rule_id,
                "rule_name": r.rule_name,
                "is_enabled": r.is_enabled,
                "conditions": r.conditions,
                "controls": r.controls,
                "target_resources": r.target_resources or [],
                "priority": r.priority,
            }
            for r in rules
        ]

    async def create_conditional_access_rule(self, data: dict[str, Any]) -> dict[str, Any]:
        if not self._ca_rule_repo:
            return {"status": "error", "message": "Repository not available"}
        rule = await self._ca_rule_repo.create(data)
        return {"status": "success", "rule_id": rule.rule_id}

    async def update_conditional_access_rule(self, rule_id: str, **kwargs: Any) -> dict[str, Any]:
        if not self._ca_rule_repo:
            return {"status": "error", "message": "Repository not available"}
        await self._ca_rule_repo.update(rule_id, **kwargs)
        return {"status": "success", "message": "Conditional access rule updated"}

    async def get_lifecycle_audit(self, ad_account: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        return await self.get_lifecycle_events(limit=limit)