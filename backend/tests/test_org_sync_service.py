import pytest
from unittest.mock import AsyncMock
from app.services.org_sync_service import OrgSyncService


@pytest.fixture
def mock_ldap():
    return AsyncMock()


@pytest.fixture
def mock_cache():
    return AsyncMock()


@pytest.fixture
def mock_audit():
    return AsyncMock()


@pytest.fixture
def mock_user_repo():
    return AsyncMock()


@pytest.fixture
def mock_ou_repo():
    return AsyncMock()


@pytest.fixture
def mock_group_repo():
    return AsyncMock()


@pytest.fixture
def org_sync_service(mock_ldap, mock_cache, mock_audit, mock_user_repo, mock_ou_repo, mock_group_repo):
    return OrgSyncService(mock_ldap, mock_cache, mock_audit, mock_user_repo, mock_ou_repo, mock_group_repo)


@pytest.mark.asyncio
async def test_sync_incremental_no_changes(org_sync_service, mock_ldap, mock_cache, mock_audit):
    mock_cache.get.return_value = "1000"
    mock_ldap.search_changed_objects.return_value = []
    mock_audit.log_event.return_value = "1"

    result = await org_sync_service.sync_incremental()

    assert result["ous"]["created"] == 0
    assert result["ous"]["updated"] == 0
    assert result["ous"]["deleted"] == 0
    assert result["users"]["created"] == 0
    assert result["groups"]["created"] == 0


@pytest.mark.asyncio
async def test_sync_incremental_with_ou_changes(org_sync_service, mock_ldap, mock_cache, mock_audit, mock_ou_repo):
    mock_cache.get.return_value = "0"
    mock_ldap.search_changed_objects.side_effect = [
        [{"distinguishedName": "OU=Shanghai,DC=company,DC=local", "ou": ["Shanghai"], "uSNChanged": [100]}],
        [],
        [],
    ]
    mock_ou_repo.get_by_dn.return_value = None
    mock_ou_repo.create_or_update.return_value = AsyncMock()
    mock_audit.log_event.return_value = "1"

    result = await org_sync_service.sync_incremental()

    assert result["ous"]["created"] == 1


@pytest.mark.asyncio
async def test_sync_incremental_with_user_deletions(org_sync_service, mock_ldap, mock_cache, mock_audit, mock_user_repo):
    mock_cache.get.return_value = "0"
    mock_ldap.search_changed_objects.side_effect = [
        [],
        [{"distinguishedName": "CN=deleted_user,DC=company,DC=local", "objectSid": ["S-1-5-21-999"], "isDeleted": [True], "uSNChanged": [200]}],
        [],
    ]
    mock_user_repo.soft_delete.return_value = True
    mock_audit.log_event.return_value = "1"

    result = await org_sync_service.sync_incremental()

    assert result["users"]["deleted"] == 1