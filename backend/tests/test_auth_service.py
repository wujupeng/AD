import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.auth_service import AuthService
from app.core.config import settings


@pytest.fixture
def mock_ldap():
    return AsyncMock()


@pytest.fixture
def mock_kerberos():
    return AsyncMock()


@pytest.fixture
def mock_token():
    return AsyncMock()


@pytest.fixture
def mock_cache():
    return AsyncMock()


@pytest.fixture
def mock_audit():
    return AsyncMock()


@pytest.fixture
def auth_service(mock_ldap, mock_kerberos, mock_token, mock_cache, mock_audit):
    return AuthService(mock_ldap, mock_kerberos, mock_token, mock_cache, mock_audit)


@pytest.mark.asyncio
async def test_authenticate_password_success(auth_service, mock_ldap, mock_token, mock_cache, mock_audit):
    mock_cache.get.return_value = None
    mock_ldap.bind.return_value = {"success": True, "user_dn": "CN=testuser,DC=company,DC=local"}
    mock_ldap.get_user_attributes.return_value = {
        "objectSid": ["S-1-5-21-123"],
        "displayName": ["Test User"],
        "mail": ["test@company.com"],
        "userAccountControl": [512],
    }
    mock_ldap.get_user_groups.return_value = ["CN=Domain Users,DC=company,DC=local"]
    mock_token.issue_token.return_value = "access_token_123"
    mock_token.issue_refresh_token.return_value = "refresh_token_123"
    mock_cache.set.return_value = True
    mock_audit.log_event.return_value = "1"

    result = await auth_service.authenticate_password("testuser", "password123")

    assert result["success"] is True
    assert "access_token" in result
    assert "refresh_token" in result
    assert result["user"]["username"] == "testuser"


@pytest.mark.asyncio
async def test_authenticate_password_invalid_credentials(auth_service, mock_ldap, mock_cache, mock_audit):
    mock_cache.get.return_value = None
    mock_ldap.bind.return_value = {"success": False, "error": "AUTH_INVALID_CREDENTIALS"}
    mock_cache.set.return_value = True
    mock_audit.log_event.return_value = "1"

    result = await auth_service.authenticate_password("testuser", "wrong_password")

    assert result["success"] is False
    assert result["error"] == "AUTH_INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_authenticate_password_account_locked(auth_service, mock_cache, mock_audit):
    mock_cache.get.return_value = str(settings.AUTH_MAX_LOGIN_ATTEMPTS)
    mock_audit.log_event.return_value = "1"

    result = await auth_service.authenticate_password("testuser", "password123")

    assert result["success"] is False
    assert result["error"] == "AUTH_ACCOUNT_LOCKED"


@pytest.mark.asyncio
async def test_authenticate_password_dc_unreachable(auth_service, mock_ldap, mock_cache, mock_audit):
    mock_cache.get.return_value = None
    mock_ldap.bind.return_value = {"success": False, "error": "AUTH_DC_UNREACHABLE"}
    mock_cache.set.return_value = True
    mock_audit.log_event.return_value = "1"

    result = await auth_service.authenticate_password("testuser", "password123")

    assert result["success"] is False
    assert result["error"] == "AUTH_DC_UNREACHABLE"


@pytest.mark.asyncio
async def test_authenticate_password_disabled_account(auth_service, mock_ldap, mock_cache, mock_audit):
    mock_cache.get.return_value = None
    mock_ldap.bind.return_value = {"success": True, "user_dn": "CN=testuser,DC=company,DC=local"}
    mock_ldap.get_user_attributes.return_value = {
        "objectSid": ["S-1-5-21-123"],
        "userAccountControl": [514],
    }
    mock_ldap.get_user_groups.return_value = []

    result = await auth_service.authenticate_password("testuser", "password123")

    assert result["success"] is False
    assert result["error"] == "AUTH_ACCOUNT_DISABLED"


@pytest.mark.asyncio
async def test_refresh_token_success(auth_service, mock_token, mock_cache):
    mock_token.validate_refresh_token.return_value = {"sub": "S-1-5-21-123", "username": "testuser"}
    mock_token.issue_token.return_value = "new_access_token"
    mock_token.issue_refresh_token.return_value = "new_refresh_token"
    mock_cache.set.return_value = True

    result = await auth_service.refresh_token("valid_refresh_token")

    assert result["success"] is True
    assert result["access_token"] == "new_access_token"


@pytest.mark.asyncio
async def test_refresh_token_invalid(auth_service, mock_token):
    mock_token.validate_refresh_token.side_effect = ValueError("AUTH_REFRESH_TOKEN_INVALID")

    result = await auth_service.refresh_token("invalid_token")

    assert result["success"] is False


@pytest.mark.asyncio
async def test_logout(auth_service, mock_cache, mock_audit, mock_token):
    mock_cache.delete.return_value = True
    mock_token.revoke_token.return_value = True
    mock_audit.log_event.return_value = "1"

    result = await auth_service.logout("S-1-5-21-123", "token_123")

    assert result is True
    mock_cache.delete.assert_called_once_with("session:S-1-5-21-123")