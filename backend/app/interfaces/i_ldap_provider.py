from abc import ABC, abstractmethod
from typing import Any


class ILdapProvider(ABC):
    @abstractmethod
    async def bind(self, username: str, password: str) -> dict[str, Any]:
        ...

    @abstractmethod
    async def search(self, base_dn: str, filter_str: str, attributes: list[str] | None = None) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def search_changed_objects(self, base_dn: str, usn_from: int, object_class: str = "*") -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def modify_group_member(self, group_dn: str, member_dn: str, operation: str = "add") -> bool:
        ...

    @abstractmethod
    async def lock_account(self, user_dn: str) -> bool:
        ...

    @abstractmethod
    async def get_user_groups(self, user_dn: str) -> list[str]:
        ...

    @abstractmethod
    async def get_user_attributes(self, user_dn: str, attributes: list[str] | None = None) -> dict[str, Any]:
        ...