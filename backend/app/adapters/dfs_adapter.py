import asyncio
import logging
import re
from typing import Any

from app.interfaces.i_file_provider import IFileProvider

logger = logging.getLogger(__name__)

SITE_SHARE_CONFIG: dict[str, dict[str, str]] = {
    "cii_factory": {
        "host": "******",
        "share": "share",
        "domain": "CII",
        "username": "Administrator",
        "password": "*****",
    },
    "cii_factory_dc4": {
        "host": "******",
        "share": "C$",
        "domain": "CII",
        "username": "Administrator",
        "password": "*****",
    },
    "cluster_test": {
        "host": "******",
        "share": "C$",
        "domain": "CII",
        "username": "Administrator",
        "password": "*****",
    },
}

ROOT_PATHS: dict[str, str] = {
    "cii_factory": "\\\\dcser1\\share",
    "cii_factory_dc4": "\\\\dc4\\C$",
    "cluster_test": "\\\\******\\C$",
}


class DfsAdapter(IFileProvider):
    def _get_share_config(self, site_code: str | None) -> dict[str, str] | None:
        if site_code and site_code in SITE_SHARE_CONFIG:
            return SITE_SHARE_CONFIG[site_code]
        if SITE_SHARE_CONFIG:
            return next(iter(SITE_SHARE_CONFIG.values()))
        return None

    def _parse_smb_path(self, path: str, site_code: str | None) -> tuple[str, str]:
        config = self._get_share_config(site_code)
        if not config:
            return "share", ""
        share = config["share"]
        sub_path = ""
        if path.startswith("\\\\") or path.startswith("//"):
            normalized = path.replace("/", "\\")
            parts = [p for p in normalized.split("\\") if p]
            if len(parts) >= 2:
                share = parts[1]
            if len(parts) >= 3:
                sub_path = "/".join(parts[2:])
        elif path.startswith("/"):
            sub_path = path.lstrip("/")
        else:
            sub_path = path
        return share, sub_path

    async def _run_smbclient(self, args: list[str], site_code: str | None) -> str:
        config = self._get_share_config(site_code)
        if not config:
            raise ValueError(f"No SMB share configured for site: {site_code}")
        creds = f"{config['username']}%{config['password']}"
        cmd = [
            "smbclient",
            f"//{config['host']}/{args[0]}",
            "-U", creds,
        ]
        domain = config.get("domain", "")
        if domain:
            cmd.extend(["-W", domain])
        cmd.extend(["-c", args[1]])
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=15)
            output = stdout.decode("utf-8", errors="replace")
            if proc.returncode != 0:
                err = stderr.decode("utf-8", errors="replace")
                logger.error("smbclient error: %s", err.strip())
            return output
        except asyncio.TimeoutError:
            logger.error("smbclient timeout for site=%s", site_code)
            return ""
        except Exception as e:
            logger.error("smbclient exception: %s", e)
            return ""

    async def list_directory(self, path: str, site_code: str | None = None) -> list[dict[str, Any]]:
        logger.info("DFS list_directory: path=%s, site=%s", path, site_code)
        share, sub_path = self._parse_smb_path(path, site_code)
        cmd = "ls" if not sub_path else f'ls "{sub_path}/*"'
        output = await self._run_smbclient([share, cmd], site_code)
        items = []
        for line in output.strip().split("\n"):
            line = line.strip()
            if not line or line.startswith("NT_STATUS") or line.startswith("Sharename"):
                continue
            match = re.match(
                r'\s*(.+?)\s+([A-Z])\s+(\d+)\s+(\w+\s+\w+\s+\d+\s+\d+:\d+:\d+\s+\d+)',
                line
            )
            if match:
                name = match.group(1).strip()
                attr = match.group(2)
                size = int(match.group(3))
                modified = match.group(4)
                is_dir = attr == "D"
                if name in (".", ".."):
                    continue
                full_path = f"{path}\\{name}"
                items.append({
                    "name": name,
                    "path": full_path,
                    "type": "directory" if is_dir else "file",
                    "size": size,
                    "modified": modified,
                })
            else:
                parts = line.split()
                if len(parts) >= 2 and parts[-1] in ("D",):
                    name = " ".join(parts[:-1])
                    if name not in (".", ".."):
                        items.append({
                            "name": name,
                            "path": f"{path}/{name}",
                            "type": "directory",
                            "size": 0,
                            "modified": "",
                        })
        return items

    async def download_file(self, path: str, site_code: str | None = None) -> bytes:
        logger.info("DFS download_file: path=%s, site=%s", path, site_code)
        share, sub_path = self._parse_smb_path(path, site_code)
        filename = sub_path.split("/")[-1] if "/" in sub_path else sub_path
        cmd = f'get "{sub_path}" /tmp/dfs_download_{filename}'
        output = await self._run_smbclient([share, cmd], site_code)
        try:
            with open(f"/tmp/dfs_download_{filename}", "rb") as f:
                data = f.read()
            return data
        except FileNotFoundError:
            logger.error("Downloaded file not found: %s", filename)
            return b""

    async def upload_file(self, path: str, data: bytes, site_code: str | None = None) -> bool:
        logger.info("DFS upload_file: path=%s, site=%s, size=%d", path, site_code, len(data))
        share, sub_path = self._parse_smb_path(path, site_code)
        tmp_file = f"/tmp/dfs_upload_{sub_path.split('/')[-1]}"
        try:
            with open(tmp_file, "wb") as f:
                f.write(data)
            cmd = f'put "{tmp_file}" "{sub_path}"'
            output = await self._run_smbclient([share, cmd], site_code)
            return "putting file" in output.lower() or "NT_STATUS" not in output
        except Exception as e:
            logger.error("Upload failed: %s", e)
            return False

    async def delete_file(self, path: str, site_code: str | None = None) -> bool:
        logger.info("DFS delete_file: path=%s, site=%s", path, site_code)
        share, sub_path = self._parse_smb_path(path, site_code)
        cmd = f'del "{sub_path}"'
        output = await self._run_smbclient([share, cmd], site_code)
        return "NT_STATUS" not in output

    async def resolve_path(self, dfs_path: str, site_code: str | None = None) -> str:
        logger.info("DFS resolve_path: dfs_path=%s, site=%s", dfs_path, site_code)
        if site_code and site_code in ROOT_PATHS:
            return ROOT_PATHS[site_code]
        config = self._get_share_config(site_code)
        if config:
            return f"\\\\{config['host']}\\{config['share']}"
        return dfs_path

    async def list_shares(self, site_code: str | None = None) -> list[dict[str, Any]]:
        config = self._get_share_config(site_code)
        if not config:
            return []
        creds = f"{config['username']}%{config['password']}"
        cmd = [
            "smbclient", "-L", config["host"],
            "-U", creds,
        ]
        domain = config.get("domain", "")
        if domain:
            cmd.extend(["-W", domain])
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=15)
            output = stdout.decode("utf-8", errors="replace")
        except Exception:
            return []

        shares = []
        in_share_section = False
        for line in output.split("\n"):
            line = line.strip()
            if "Sharename" in line and "Type" in line:
                in_share_section = True
                continue
            if in_share_section and "---" in line:
                continue
            if in_share_section and not line:
                in_share_section = False
                continue
            if in_share_section:
                parts = line.split()
                if len(parts) >= 2:
                    shares.append({
                        "name": parts[0],
                        "type": parts[1],
                        "comment": " ".join(parts[2:]) if len(parts) > 2 else "",
                    })
        return shares
