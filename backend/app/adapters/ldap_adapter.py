import asyncio
import logging
import re
import subprocess
from typing import Any

import ldap3

from app.interfaces.i_ldap_provider import ILdapProvider
from app.core.config import settings

logger = logging.getLogger(__name__)

MULTI_DC_CONFIG: dict[str, dict[str, Any]] = {
    "cii_factory": {
        "dc_ip": "******",
        "domain": "cii.sh.cn",
        "netbios_domain": "CII",
        "admin_user": "Administrator",
        "admin_pass": "*****",
        "base_dn": "DC=cii,DC=sh,DC=cn",
        "use_rpc_fallback": True,
    },
    "cluster_test": {
        "dc_ip": "******",
        "domain": "cii.sh.cn",
        "netbios_domain": "CII",
        "admin_user": "Administrator",
        "admin_pass": "*****",
        "base_dn": "DC=cii,DC=sh,DC=cn",
        "use_rpc_fallback": True,
    },
}


class LdapAdapter(ILdapProvider):
    def __init__(self):
        self._servers = [ldap3.Server(dc, port=settings.AD_LDAPS_PORT, use_ssl=True, connect_timeout=5) for dc in settings.AD_DC_LIST]
        self._current_server_idx = 0

    def _get_connection(self, user_dn: str | None = None, password: str | None = None) -> ldap3.Connection:
        for i in range(len(self._servers)):
            idx = (self._current_server_idx + i) % len(self._servers)
            server = self._servers[idx]
            try:
                if user_dn and password:
                    if "@" not in user_dn:
                        username = user_dn.split(",")[0].replace("CN=", "")
                        user_dn = f"{username}@{settings.AD_DOMAIN}"
                    conn = ldap3.Connection(server, user=user_dn, password=password, auto_bind=True, raise_exceptions=True)
                else:
                    svc_upn = f"svc_adbiz@{settings.AD_DOMAIN}"
                    conn = ldap3.Connection(
                        server,
                        user=svc_upn,
                        password=settings.AD_SERVICE_ACCOUNT_PASSWORD,
                        auto_bind=True,
                        raise_exceptions=True,
                    )
                self._current_server_idx = idx
                return conn
            except ldap3.core.exceptions.LDAPException:
                logger.warning("Failed to connect to DC: %s", server.host)
                continue
        raise ConnectionError("All DC servers unreachable")

    async def bind(self, username: str, password: str) -> dict[str, Any]:
        for site_code, dc_config in MULTI_DC_CONFIG.items():
            if dc_config.get("use_rpc_fallback"):
                result = await self._rpc_bind(username, password, dc_config)
                if result.get("success"):
                    return result
                if result.get("error") == "AUTH_INVALID_CREDENTIALS":
                    return result

        try:
            server = self._servers[0]
            user_upn = f"{username}@{settings.AD_DOMAIN}"
            conn = ldap3.Connection(server, user=user_upn, password=password, auto_bind=True, raise_exceptions=True)
            conn.search(
                settings.AD_SEARCH_BASE,
                f"(sAMAccountName={username})",
                search_scope=ldap3.SUBTREE,
                attributes=["distinguishedName"],
            )
            user_dn = str(conn.entries[0].distinguishedName) if conn.entries else user_upn
            conn.unbind()
            return {"success": True, "user_dn": user_dn}
        except ldap3.core.exceptions.LDAPInvalidCredentialsResult:
            return {"success": False, "error": "AUTH_INVALID_CREDENTIALS"}
        except (ConnectionError, ldap3.core.exceptions.LDAPException) as e:
            logger.warning("LDAP bind failed for user %s: %s", username, e)
            return {"success": False, "error": "AUTH_DC_UNREACHABLE"}

    async def _rpc_bind(self, username: str, password: str, dc_config: dict) -> dict[str, Any]:
        dc_ip = dc_config["dc_ip"]
        domain = dc_config["netbios_domain"]
        try:
            cmd = [
                "rpcclient", "-U", f"{username}%{password}",
                "-W", domain, "-I", dc_ip,
                "-c", "enumdomusers", dc_config.get("dc_hostname", dc_ip),
            ]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)
            output = stdout.decode("utf-8", errors="replace")
            if proc.returncode == 0 and "user:" in output:
                base_dn = dc_config.get("base_dn", "")
                user_dn = f"CN={username},{base_dn}"
                return {"success": True, "user_dn": user_dn, "site_code": next((k for k, v in MULTI_DC_CONFIG.items() if v is dc_config), None)}
            elif "NT_STATUS_LOGON_FAILURE" in output or "NT_STATUS_ACCESS_DENIED" in output:
                return {"success": False, "error": "AUTH_INVALID_CREDENTIALS"}
            elif "NT_STATUS_ACCOUNT_LOCKED_OUT" in output:
                return {"success": False, "error": "AUTH_ACCOUNT_LOCKED"}
            else:
                logger.warning("RPC bind unexpected result for %s: %s", username, output[:200])
                return {"success": False, "error": "AUTH_DC_UNREACHABLE"}
        except asyncio.TimeoutError:
            return {"success": False, "error": "AUTH_DC_UNREACHABLE"}
        except Exception as e:
            logger.warning("RPC bind error for %s: %s", username, e)
            return {"success": False, "error": "AUTH_DC_UNREACHABLE"}

    async def _net_ads_search(self, filter_str: str, attrs: list[str], dc_config: dict) -> list[dict[str, Any]]:
        dc_ip = dc_config["dc_ip"]
        admin_user = dc_config["admin_user"]
        admin_pass = dc_config["admin_pass"]
        cmd = [
            "net", "ads", "search",
            "-U", f"{admin_user}%{admin_pass}",
            "-S", dc_ip,
            filter_str,
        ] + attrs
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
            output = stdout.decode("utf-8", errors="replace")
            return self._parse_net_ads_output(output)
        except Exception as e:
            logger.error("net ads search error: %s", e)
            return []

    def _parse_net_ads_output(self, output: str) -> list[dict[str, Any]]:
        entries = []
        current: dict[str, Any] = {}
        for line in output.split("\n"):
            line = line.strip()
            if ":" in line and not line.startswith("Got") and not line.startswith("gensec"):
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip()
                if key in ("distinguishedName", "sAMAccountName", "displayName", "name", "description", "mail", "telephoneNumber", "department", "title", "company", "physicalDeliveryOfficeName", "userAccountControl", "memberOf"):
                    if key == "distinguishedName" and "distinguishedName" in current:
                        entries.append(current)
                        current = {}
                    if key == "memberOf":
                        current.setdefault("memberOf", []).append(value)
                    else:
                        current[key] = value
            elif line == "" and current:
                entries.append(current)
                current = {}
        if current:
            entries.append(current)
        return entries

    async def search(self, base_dn: str, filter_str: str, attributes: list[str] | None = None) -> list[dict[str, Any]]:
        for site_code, dc_config in MULTI_DC_CONFIG.items():
            dc_base_dn = dc_config.get("base_dn", "")
            if base_dn.endswith(dc_base_dn) or dc_base_dn.endswith(base_dn):
                if dc_config.get("use_rpc_fallback"):
                    return await self._net_ads_search(filter_str, attributes or [], dc_config)

        conn = self._get_connection()
        try:
            conn.search(base_dn, filter_str, attributes=attributes or ldap3.ALL_ATTRIBUTES)
            results = []
            for entry in conn.entries:
                results.append(entry.entry_attributes_as_dict)
            return results
        finally:
            conn.unbind()

    async def search_changed_objects(self, base_dn: str, usn_from: int, object_class: str = "*") -> list[dict[str, Any]]:
        filter_str = f"(&(objectClass={object_class})(uSNChanged>={usn_from}))"
        return await self.search(base_dn, filter_str, attributes=ldap3.ALL_ATTRIBUTES)

    async def modify_group_member(self, group_dn: str, member_dn: str, operation: str = "add") -> bool:
        conn = self._get_connection()
        try:
            op = ldap3.MODIFY_ADD if operation == "add" else ldap3.MODIFY_DELETE
            conn.modify(group_dn, {"member": [(op, [member_dn])]})
            return conn.result["description"] == "success"
        finally:
            conn.unbind()

    async def lock_account(self, user_dn: str) -> bool:
        conn = self._get_connection()
        try:
            conn.modify(user_dn, {"userAccountControl": [(ldap3.MODIFY_REPLACE, [66050])]})
            return conn.result["description"] == "success"
        finally:
            conn.unbind()

    def _resolve_dc_config(self, dn: str) -> tuple[dict[str, Any] | None, str]:
        for site_code, dc_config in MULTI_DC_CONFIG.items():
            dc_base_dn = dc_config.get("base_dn", "")
            if dc_base_dn and dn.endswith(dc_base_dn):
                return dc_config, site_code
        return None, ""

    async def get_user_groups(self, user_dn: str) -> list[str]:
        dc_config, site_code = self._resolve_dc_config(user_dn)
        if dc_config and dc_config.get("use_rpc_fallback"):
            return await self._rpc_get_user_groups(user_dn, dc_config)

        conn = self._get_connection()
        try:
            conn.search(settings.AD_SEARCH_BASE, f"(member={user_dn})", attributes=["distinguishedName"])
            return [entry.distinguishedName.value for entry in conn.entries]
        finally:
            conn.unbind()

    async def get_user_attributes(self, user_dn: str, attributes: list[str] | None = None) -> dict[str, Any]:
        dc_config, site_code = self._resolve_dc_config(user_dn)
        if dc_config and dc_config.get("use_rpc_fallback"):
            return await self._rpc_get_user_attributes(user_dn, dc_config)

        conn = self._get_connection()
        try:
            conn.search(user_dn, "(objectClass=user)", attributes=attributes or ldap3.ALL_ATTRIBUTES, search_scope=ldap3.BASE)
            if conn.entries:
                return conn.entries[0].entry_attributes_as_dict
            return {}
        finally:
            conn.unbind()

    async def _rpc_get_user_attributes(self, user_dn: str, dc_config: dict) -> dict[str, Any]:
        cn_start = user_dn.find("CN=")
        if cn_start < 0:
            return {}
        cn_end = user_dn.find(",", cn_start)
        cn_value = user_dn[cn_start + 3:cn_end] if cn_end > cn_start else user_dn[cn_start + 3:]
        results = await self._net_ads_search(
            f"(&(objectClass=user)(distinguishedName={user_dn}))",
            ["sAMAccountName", "displayName", "mail", "telephoneNumber", "department", "title", "company", "userAccountControl"],
            dc_config,
        )
        if results:
            entry = results[0]
            attrs: dict[str, Any] = {}
            for key, value in entry.items():
                if key == "memberOf":
                    attrs[key] = value if isinstance(value, list) else [value]
                else:
                    attrs[key] = [value] if value else []
            uac_str = entry.get("userAccountControl", "512")
            try:
                attrs["userAccountControl"] = [int(uac_str)]
            except (ValueError, TypeError):
                attrs["userAccountControl"] = [512]
            if "objectSid" not in attrs:
                sam = entry.get("sAMAccountName", cn_value)
                attrs["objectSid"] = [f"cii-{sam}-{abs(hash(user_dn)) % 1000000}"]
            return attrs
        return {"sAMAccountName": [cn_value], "objectSid": [f"cii-{cn_value}-0"], "userAccountControl": [512]}

    async def _rpc_get_user_groups(self, user_dn: str, dc_config: dict) -> list[str]:
        cn_start = user_dn.find("CN=")
        if cn_start < 0:
            return []
        cn_end = user_dn.find(",", cn_start)
        cn_value = user_dn[cn_start + 3:cn_end] if cn_end > cn_start else user_dn[cn_start + 3:]
        results = await self._net_ads_search(
            f"(&(objectClass=group)(member={user_dn}))",
            ["distinguishedName"],
            dc_config,
        )
        groups = []
        for r in results:
            if "distinguishedName" in r:
                groups.append(r["distinguishedName"])
        if not groups:
            dc_ip = dc_config["dc_ip"]
            domain = dc_config["netbios_domain"]
            admin_user = dc_config["admin_user"]
            admin_pass = dc_config["admin_pass"]
            try:
                cmd = ["net", "rpc", "user", "info", cn_value,
                       "-U", f"{admin_user}%{admin_pass}",
                       "-S", dc_ip, "-W", domain]
                proc = await asyncio.create_subprocess_exec(
                    *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                )
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
                output = stdout.decode("utf-8", errors="replace")
                for line in output.strip().split("\n"):
                    group_name = line.strip()
                    if group_name:
                        base_dn = dc_config.get("base_dn", "")
                        groups.append(f"CN={group_name},OU=scii,{base_dn}")
            except Exception as e:
                logger.warning("RPC get groups error: %s", e)
        return groups

    async def health_check(self, site_code: str | None = None) -> dict[str, Any]:
        if site_code and site_code in MULTI_DC_CONFIG:
            dc_config = MULTI_DC_CONFIG[site_code]
            dc_ip = dc_config["dc_ip"]
            try:
                cmd = ["rpcclient", "-U", f"{dc_config['admin_user']}%{dc_config['admin_pass']}",
                       "-W", dc_config["netbios_domain"], "-I", dc_ip,
                       "-c", "enumdomusers", dc_config.get("dc_hostname", dc_ip)]
                proc = await asyncio.create_subprocess_exec(
                    *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
                )
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
                output = stdout.decode("utf-8", errors="replace")
                if proc.returncode == 0 and "user:" in output:
                    return {"status": "healthy", "dc_ip": dc_ip, "site_code": site_code}
                return {"status": "degraded", "dc_ip": dc_ip, "site_code": site_code, "error": output[:100]}
            except Exception as e:
                return {"status": "unhealthy", "dc_ip": dc_ip, "site_code": site_code, "error": str(e)}

        try:
            conn = self._get_connection()
            conn.unbind()
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}
