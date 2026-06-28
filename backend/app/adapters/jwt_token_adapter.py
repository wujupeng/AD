import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt, JWTError

from app.interfaces.i_token_provider import ITokenProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


class JwtTokenAdapter(ITokenProvider):
    def __init__(self):
        self._secret = settings.JWT_SECRET
        self._algorithm = settings.JWT_ALGORITHM
        self._access_expire = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self._refresh_expire = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS

    async def issue_token(self, payload: dict[str, Any], expires_delta: int | None = None) -> str:
        to_encode = payload.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta or self._access_expire)
        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": "access"})
        return jwt.encode(to_encode, self._secret, algorithm=self._algorithm)

    async def validate_token(self, token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            if payload.get("type") != "access":
                raise JWTError("Invalid token type")
            return payload
        except JWTError as e:
            logger.warning("JWT validation failed: %s", str(e))
            raise ValueError("AUTH_TOKEN_INVALID") from e

    async def validate_refresh_token(self, refresh_token: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(refresh_token, self._secret, algorithms=[self._algorithm])
            if payload.get("type") != "refresh":
                raise JWTError("Invalid token type")
            return payload
        except JWTError as e:
            logger.warning("Refresh token validation failed: %s", str(e))
            raise ValueError("AUTH_REFRESH_TOKEN_INVALID") from e

    async def issue_refresh_token(self, payload: dict[str, Any]) -> str:
        to_encode = payload.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=self._refresh_expire)
        to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": "refresh"})
        return jwt.encode(to_encode, self._secret, algorithm=self._algorithm)

    async def revoke_token(self, token_id: str) -> bool:
        return True