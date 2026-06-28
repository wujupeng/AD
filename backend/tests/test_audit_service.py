import hashlib
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone
from app.adapters.pg_audit_adapter import PgAuditAdapter


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    return session


@pytest.fixture
def audit_adapter(mock_session):
    return PgAuditAdapter(mock_session)


@pytest.mark.asyncio
async def test_log_event(audit_adapter, mock_session):
    mock_session.execute.return_value = MagicMock(scalar_one_or_none=lambda: "0" * 64)

    event = {
        "event_type": "AUTH_LOGIN_SUCCESS",
        "user_sid": "S-1-5-21-123",
        "username": "testuser",
        "result": "success",
        "occurred_at": datetime.now(timezone.utc),
    }

    event_id = await audit_adapter.log_event(event)

    mock_session.add.assert_called_once()
    mock_session.flush.assert_called_once()


@pytest.mark.asyncio
async def test_check_integrity_valid(audit_adapter, mock_session):
    hash1 = hashlib.sha256("0".encode()).hexdigest()
    hash2 = hashlib.sha256(f"{hash1}test".encode()).hexdigest()

    record1 = MagicMock()
    record1.id = 1
    record1.event_hash = hash1
    record1.previous_hash = "0" * 64

    record2 = MagicMock()
    record2.id = 2
    record2.event_hash = hash2
    record2.previous_hash = hash1

    mock_session.execute.return_value = MagicMock(scalars=lambda: MagicMock(all=lambda: [record1, record2]))

    result = await audit_adapter.check_integrity()

    assert result["is_valid"] is True
    assert result["total_records"] == 2


@pytest.mark.asyncio
async def test_check_integrity_broken_chain(audit_adapter, mock_session):
    record1 = MagicMock()
    record1.id = 1
    record1.event_hash = "hash1"
    record1.previous_hash = "0" * 64

    record2 = MagicMock()
    record2.id = 2
    record2.event_hash = "hash2"
    record2.previous_hash = "wrong_hash"

    mock_session.execute.return_value = MagicMock(scalars=lambda: MagicMock(all=lambda: [record1, record2]))

    result = await audit_adapter.check_integrity()

    assert result["is_valid"] is False
    assert result["broken_chains"] == 1