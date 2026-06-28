from typing import Any


class RemoteAccessService:
    def __init__(
        self,
        vpn_gateway_repo: Any = None,
        vpn_session_repo: Any = None,
        vpn_policy_repo: Any = None,
        device_classification_repo: Any = None,
        remote_access_audit_repo: Any = None,
        remote_access_provider: Any = None,
        vpn_provider: Any = None,
        defender_provider: Any = None,
    ):
        self._gw_repo = vpn_gateway_repo
        self._sess_repo = vpn_session_repo
        self._pol_repo = vpn_policy_repo
        self._dc_repo = device_classification_repo
        self._audit_repo = remote_access_audit_repo
        self._ra_provider = remote_access_provider
        self._vpn_provider = vpn_provider
        self._defender_provider = defender_provider

    async def get_vpn_gateways(self) -> list[dict[str, Any]]:
        if not self._gw_repo:
            return []
        gateways = await self._gw_repo.get_all()
        return [
            {
                "gateway_id": gw.gateway_id,
                "gateway_name": gw.gateway_name,
                "gateway_site": gw.gateway_site,
                "gateway_ip": gw.gateway_ip,
                "gateway_role": gw.gateway_role,
                "tunnel_protocol": gw.tunnel_protocol,
                "max_concurrent_sessions": gw.max_concurrent_sessions,
                "active_sessions": gw.active_sessions,
                "cpu_usage_percent": gw.cpu_usage_percent,
                "bandwidth_usage_mbps": gw.bandwidth_usage_mbps,
                "health_status": gw.health_status,
                "served_sites": gw.served_sites or [],
                "last_health_check": gw.last_health_check.isoformat() if gw.last_health_check else None,
            }
            for gw in gateways
        ]

    async def get_vpn_gateway_detail(self, gateway_id: str) -> dict[str, Any] | None:
        if not self._gw_repo:
            return None
        gw = await self._gw_repo.get_by_id(gateway_id)
        if not gw:
            return None
        return {
            "gateway_id": gw.gateway_id,
            "gateway_name": gw.gateway_name,
            "gateway_site": gw.gateway_site,
            "gateway_ip": gw.gateway_ip,
            "gateway_role": gw.gateway_role,
            "tunnel_protocol": gw.tunnel_protocol,
            "max_concurrent_sessions": gw.max_concurrent_sessions,
            "active_sessions": gw.active_sessions,
            "cpu_usage_percent": gw.cpu_usage_percent,
            "bandwidth_usage_mbps": gw.bandwidth_usage_mbps,
            "health_status": gw.health_status,
            "served_sites": gw.served_sites or [],
            "last_health_check": gw.last_health_check.isoformat() if gw.last_health_check else None,
        }

    async def get_vpn_sessions(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        if not self._sess_repo:
            return []
        sessions = await self._sess_repo.get_active_sessions(limit=limit, offset=offset)
        return [
            {
                "session_id": s.session_id,
                "user_account": s.user_account,
                "device_hostname": s.device_hostname,
                "user_site": s.user_site,
                "tunnel_type": s.tunnel_type,
                "connected_gateway_id": s.connected_gateway_id,
                "connection_time": s.connection_time.isoformat() if s.connection_time else None,
                "client_ip": s.client_ip,
                "auth_method": s.auth_method,
                "is_active": s.is_active,
                "bytes_in": s.bytes_in,
                "bytes_out": s.bytes_out,
            }
            for s in sessions
        ]

    async def get_vpn_policies(self) -> list[dict[str, Any]]:
        if not self._pol_repo:
            return []
        policies = await self._pol_repo.get_all()
        return [
            {
                "policy_id": p.policy_id,
                "policy_type": p.policy_type,
                "policy_name": p.policy_name,
                "policy_config": p.policy_config,
                "target_ou_dns": p.target_ou_dns or [],
                "is_enabled": p.is_enabled,
            }
            for p in policies
        ]

    async def update_vpn_policy(self, policy_id: str, config: dict[str, Any]) -> dict[str, Any]:
        if not self._pol_repo:
            return {"status": "error", "message": "Repository not available"}
        await self._pol_repo.update_config(policy_id, config)
        return {"status": "success", "message": "VPN policy updated"}

    async def get_cached_cred_policy(self) -> dict[str, Any]:
        if not self._pol_repo:
            return {"status": "not_configured"}
        policies = await self._pol_repo.get_by_type("cached_credentials")
        if policies:
            p = policies[0]
            return {"policy_id": p.policy_id, "policy_name": p.policy_name, "policy_config": p.policy_config, "is_enabled": p.is_enabled}
        return {"status": "not_configured"}

    async def configure_cached_cred_policy(self, config: dict[str, Any]) -> dict[str, Any]:
        if not self._pol_repo:
            return {"status": "error", "message": "Repository not available"}
        policies = await self._pol_repo.get_by_type("cached_credentials")
        if policies:
            await self._pol_repo.update_config(policies[0].policy_id, config)
            return {"status": "success", "message": "Cached credential policy updated"}
        return {"status": "error", "message": "No cached credential policy found"}

    async def get_device_classifications(self) -> list[dict[str, Any]]:
        if not self._dc_repo:
            return []
        classifications = await self._dc_repo.get_all()
        return [
            {
                "device_class": dc.device_class,
                "display_name": dc.display_name,
                "auth_methods": dc.auth_methods or [],
                "vpn_tunnel_type": dc.vpn_tunnel_type,
                "cached_logon_count": dc.cached_logon_count,
                "conditional_access_level": dc.conditional_access_level,
                "bitlocker_required": dc.bitlocker_required,
                "defender_required": dc.defender_required,
                "target_ou_dn": dc.target_ou_dn,
            }
            for dc in classifications
        ]

    async def update_device_classification(self, device_class: str, **kwargs: Any) -> dict[str, Any]:
        if not self._dc_repo:
            return {"status": "error", "message": "Repository not available"}
        await self._dc_repo.update_policy(device_class, **kwargs)
        return {"status": "success", "message": f"Device classification {device_class} updated"}

    async def get_conditional_access_policies(self) -> list[dict[str, Any]]:
        if self._ra_provider:
            return await self._ra_provider.query_conditional_access_policies()
        return []

    async def get_hybrid_join_status(self) -> dict[str, Any]:
        return {"status": "not_configured", "total_devices": 0, "registered": 0, "pending": 0, "failed": 0, "message": "Entra Hybrid Join requires Phase2+"}

    async def configure_hybrid_join(self, config: dict[str, Any]) -> dict[str, Any]:
        if self._ra_provider:
            return await self._ra_provider.configure_hybrid_join(config)
        return {"status": "not_implemented", "message": "Hybrid Join requires Entra ID Connect"}

    async def get_dc_isolation_policy(self) -> dict[str, Any]:
        if self._ra_provider:
            return await self._ra_provider.query_dc_isolation_policy()
        return {"isolation_enabled": True, "rules": [], "message": "DC isolation policy requires firewall/ACL configuration"}

    async def configure_dc_isolation(self, policy: dict[str, Any]) -> dict[str, Any]:
        if self._ra_provider:
            return await self._ra_provider.configure_dc_isolation(policy)
        return {"status": "not_implemented", "message": "DC isolation configuration requires firewall/ACL deployment"}

    async def trigger_password_sync(self, user_account: str) -> dict[str, Any]:
        if self._ra_provider:
            return await self._ra_provider.update_vpn_credentials(user_account)
        return {"status": "not_implemented", "message": "Password sync requires Entra ID Connect"}

    async def trigger_gpo_update(self, target_ou: str, computer_list: list[str]) -> dict[str, Any]:
        if self._ra_provider:
            return await self._ra_provider.trigger_gpo_update(target_ou, computer_list)
        return {"status": "not_implemented", "message": "GPO remote update requires WinRM"}

    async def get_bitlocker_remote_status(self) -> dict[str, Any]:
        return {"status": "not_configured", "message": "BitLocker remote management requires Intune/WinRM integration"}

    async def enable_bitlocker_remotely(self, computer_name: str) -> dict[str, Any]:
        if self._ra_provider:
            return await self._ra_provider.enable_bitlocker_remotely(computer_name)
        return {"status": "not_implemented", "message": "BitLocker remote enable requires WinRM/Intune"}

    async def rotate_bitlocker_key(self, computer_name: str) -> dict[str, Any]:
        if self._ra_provider:
            return await self._ra_provider.rotate_bitlocker_recovery_key_remotely(computer_name)
        return {"status": "not_implemented", "message": "BitLocker key rotation requires WinRM/Intune"}

    async def get_defender_status(self) -> dict[str, Any]:
        if self._defender_provider:
            return await self._defender_provider.query_device_onboarding()
        return {"status": "not_configured", "total_devices": 0, "onboarded": 0, "not_onboarded": 0}

    async def get_intune_compliance_detail(self) -> dict[str, Any]:
        return {"status": "not_configured", "message": "Intune compliance requires Phase3+"}

    async def get_sso_status(self) -> dict[str, Any]:
        return {"status": "not_configured", "message": "SSO requires Entra Hybrid Join (Phase2+)"}

    async def get_kerberos_recovery_status(self, hours: int = 24) -> dict[str, Any]:
        if not self._audit_repo:
            return {"recovered": 0, "failed": 0, "ntlm_fallback": 0}
        stats = await self._audit_repo.get_stats_24h()
        return {
            "kerberos_recovered": stats.get("kerberos_recovered", 0),
            "kerberos_recovery_failed": stats.get("kerberos_recovery_failed", 0),
            "ntlm_fallback": stats.get("ntlm_fallback", 0),
            "hours": hours,
        }

    async def get_vpn_audit_log(self, hours: int = 24, limit: int = 200) -> list[dict[str, Any]]:
        if not self._audit_repo:
            return []
        logs = await self._audit_repo.get_recent(hours=hours, limit=limit)
        return [
            {
                "log_id": log.log_id,
                "event_type": log.event_type,
                "user_account": log.user_account,
                "device_hostname": log.device_hostname,
                "source_site": log.source_site,
                "tunnel_type": log.tunnel_type,
                "event_time": log.event_time.isoformat() if log.event_time else None,
                "details": log.details,
            }
            for log in logs
        ]

    async def get_tunnel_status(self, tunnel_type: str, identifier: str) -> dict[str, Any]:
        if self._vpn_provider:
            if tunnel_type == "device":
                return await self._vpn_provider.query_device_tunnel_status(identifier)
            elif tunnel_type == "user":
                return await self._vpn_provider.query_user_tunnel_status(identifier)
        return {"status": "not_configured", "message": "VPN provider not configured"}