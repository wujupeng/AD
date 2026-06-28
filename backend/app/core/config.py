from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "AD Biz Sys"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql+asyncpg://aduser:adpass@localhost:5432/adbizsys"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: str | None = None

    AD_DOMAIN: str = "company.local"
    AD_DC_LIST: List[str] = ["dc01.company.local", "dc02.company.local"]
    AD_LDAPS_PORT: int = 636
    AD_SEARCH_BASE: str = "DC=company,DC=local"
    AD_SERVICE_ACCOUNT_DN: str = ""
    AD_SERVICE_ACCOUNT_PASSWORD: str = ""

    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "RS256"
    JWT_PRIVATE_KEY_PATH: str = ""
    JWT_PUBLIC_KEY_PATH: str = ""
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    SAML_IDP_CERT_PATH: str = ""
    SAML_IDP_KEY_PATH: str = ""
    SAML_IDP_ENTITY_ID: str = "https://ad-biz-sys.company.local/saml/metadata"

    EXCHANGE_SERVER: str = ""
    EXCHANGE_USERNAME: str = ""
    EXCHANGE_PASSWORD: str = ""

    AUTH_MAX_LOGIN_ATTEMPTS: int = 5
    AUTH_ACCOUNT_LOCKOUT_MINUTES: int = 30

    ORG_SYNC_INTERVAL_MINUTES: int = 5
    GAL_SYNC_INTERVAL_MINUTES: int = 60

    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    NTP_SERVER: str = "time.windows.com"

    NGINX_STUB_STATUS_URL: str = ""
    PG_STAT_STATEMENTS_ENABLED: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "case_sensitive": True}


settings = Settings()