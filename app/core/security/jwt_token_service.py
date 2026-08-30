from datetime import datetime, timedelta, timezone

import jwt

from app.core.security.token_service import TokenError, TokenPayload, TokenService


class JwtTokenService(TokenService):

    def __init__(
        self,
        *,
        secret_key: str,
        algorithm: str = "HS256",
        expires_minutes: int = 10080,
    ) -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm
        self._expires_minutes = expires_minutes

    def issue(self, subject: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": subject,
            "iat": now,
            "exp": now + timedelta(minutes=self._expires_minutes),
        }

        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def verify(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except jwt.PyJWTError as error:
            raise TokenError("Invalid or expired token") from error

        subject = payload.get("sub")
        expires_at_timestamp = payload.get("exp")

        if not isinstance(subject, str) or not isinstance(expires_at_timestamp, (int, float)):
            raise TokenError("Token is missing required claims")

        return TokenPayload(
            subject=subject,
            expires_at=datetime.fromtimestamp(expires_at_timestamp, tz=timezone.utc),
        )
