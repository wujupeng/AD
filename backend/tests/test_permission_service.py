import pytest
from unittest.mock import AsyncMock
from app.services.permission_service import PermissionService


@pytest.fixture
def mock_ldap():
    return AsyncMock()


@pytest.fixture
def mock_cache():
    return AsyncMock()


@pytest.fixture
def permission_service(mock_ldap, mock_cache):
    return PermissionService(mock_ldap, mock_cache)


@pytest.mark.asyncio
async def test_resolve_groups_cache_hit(permission_service, mock_cache):
    import json
    cached_data = json.dumps([{"dn": "CN=GG_Admin,DC=company,DC=local", "name": "GG_Admin"}])
    mock_cache.get.return_value = cached_data

    result = await permission_service.resolve_groups("S-1-5-21-123")

    assert len(result) == 1
    assert result[0]["name"] == "GG_Admin"


@pytest.mark.asyncio
async def test_resolve_groups_cache_miss(permission_service, mock_ldap, mock_cache):
    mock_cache.get.return_value = None
    mock_ldap.get_user_groups.return_value = ["CN=GG_Admin,DC=company,DC=local", "CN=DL_FileRead,DC=company,DC=local"]
    mock_cache.set.return_value = True

    result = await permission_service.resolve_groups("S-1-5-21-123")

    assert len(result) == 2
    assert result[0]["name"] == "GG_Admin"


@pytest.mark.asyncio
async def test_get_effective_permissions(permission_service, mock_cache):
    mock_cache.get.return_value = None
    mock_ldap.get_user_groups.return_value = ["CN=GG_Admin,DC=company,DC=local"]
    mock_cache.set.return_value = True

    result = await permission_service.get_effective_permissions("S-1-5-21-123")

    assert result["user_sid"] == "S-1-5-21-123"
    assert len(result["global_groups"]) == 1
    assert result["global_groups"][0]["name"] == "GG_Admin"


@pytest.mark.asyncio
async def test_invalidate_cache(permission_service, mock_cache):
    mock_cache.delete.return_value = True

    count = await permission_service.invalidate_cache("S-1-5-21-123")

    assert count == 2
    assert mock_cache.delete.call_count == 2


@pytest.mark.asyncio
async def test_check_permission_allowed(permission_service, mock_cache):
    import json
    effective = {
        "user_sid": "S-1-5-21-123",
        "global_groups": [],
        "domain_local_groups": [],
        "resources": {
            "dfs://Engineering": {
                "allowed_actions": ["read", "write"],
                "granting_groups": ["DL_FileRead"],
            }
        },
    }
    mock_cache.get.return_value = json.dumps(effective)

    result = await permission_service.check_permission("S-1-5-21-123", "dfs://Engineering", "read")

    assert result["allowed"] is True