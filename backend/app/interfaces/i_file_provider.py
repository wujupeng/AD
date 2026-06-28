from abc import ABC, abstractmethod
from typing import Any


class IFileProvider(ABC):
    @abstractmethod
    async def list_directory(self, path: str, site_code: str | None = None) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def download_file(self, path: str, site_code: str | None = None) -> bytes:
        ...

    @abstractmethod
    async def upload_file(self, path: str, data: bytes, site_code: str | None = None) -> bool:
        ...

    @abstractmethod
    async def delete_file(self, path: str, site_code: str | None = None) -> bool:
        ...

    @abstractmethod
    async def resolve_path(self, dfs_path: str, site_code: str | None = None) -> str:
        ...