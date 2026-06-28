import pytest
from unittest.mock import AsyncMock
from app.services.site_awareness_service import SiteAwarenessService


@pytest.fixture
def mock_cache():
    return AsyncMock()


@pytest.fixture
def mock_site_repo():
    return AsyncMock()


@pytest.fixture
def site_awareness_service(mock_cache, mock_site_repo):
    return SiteAwarenessService(mock_cache, mock_site_repo)


@pytest.mark.asyncio
async def test_resolve_site_by_ip(site_awareness_service, mock_site_repo):
    mock_site = AsyncMock()
    mock_site.site_code = "shanghai_hq"
    mock_site.site_name = "Shanghai HQ"
    mock_site.timezone = "Asia/Shanghai"
    mock_site.language = "zh-CN"
    mock_site_repo.match_by_ip.return_value = mock_site

    result = await site_awareness_service.resolve_site("10.0.1.100")

    assert result["site_code"] == "shanghai_hq"
    assert result["timezone"] == "Asia/Shanghai"


@pytest.mark.asyncio
async def test_resolve_site_default(site_awareness_service, mock_site_repo):
    mock_site_repo.match_by_ip.return_value = None
    mock_default = AsyncMock()
    mock_default.site_code = "shanghai_hq"
    mock_default.site_name = "Shanghai HQ"
    mock_default.timezone = "Asia/Shanghai"
    mock_default.language = "zh-CN"
    mock_site_repo.get_by_code.return_value = mock_default

    result = await site_awareness_service.resolve_site("192.168.1.1")

    assert result["site_code"] == "shanghai_hq"


@pytest.mark.asyncio
async def test_get_nearest_dc(site_awareness_service, mock_site_repo, mock_cache):
    mock_site_repo.get_dc_priority.return_value = ["dc01.company.local", "dc02.company.local"]
    mock_cache.get_dc_health.return_value = None

    result = await site_awareness_service.get_nearest_dc("shanghai_hq")

    assert result == "dc01.company.local"


@pytest.mark.asyncio
async def test_get_nearest_dc_failover(site_awareness_service, mock_site_repo, mock_cache):
    mock_site_repo.get_dc_priority.return_value = ["dc01.company.local", "dc02.company.local"]
    mock_cache.get_dc_health.side_effect = [
        {"hostname": "dc01.company.local", "status": "down"},
        None,
    ]

    result = await site_awareness_service.get_nearest_dc("shanghai_hq")

    assert result == "dc02.company.local"