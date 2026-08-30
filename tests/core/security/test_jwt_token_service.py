from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app.core.security.jwt_token_service import JwtTokenService
from app.core.security.token_service import TokenError


class TestIssueAndVerify:
    def test_verify_returns_the_subject_that_was_issued(self):
        service = JwtTokenService(secret_key="test-secret", expires_minutes=60)
        token = service.issue("user-123")

        payload = service.verify(token)

        assert payload.subject == "user-123"

    def test_verify_raises_for_a_garbage_token(self):
        service = JwtTokenService(secret_key="test-secret", expires_minutes=60)

        with pytest.raises(TokenError):
            service.verify("not-a-real-token")

    def test_verify_raises_for_an_expired_token(self):
        service = JwtTokenService(secret_key="test-secret", expires_minutes=60)
        expired_payload = {
            "sub": "user-123",
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        expired_token = jwt.encode(expired_payload, "test-secret", algorithm="HS256")

        with pytest.raises(TokenError):
            service.verify(expired_token)

    def test_verify_raises_for_a_token_signed_with_a_different_secret(self):
        issuer = JwtTokenService(secret_key="secret-a", expires_minutes=60)
        verifier = JwtTokenService(secret_key="secret-b", expires_minutes=60)
        token = issuer.issue("user-123")

        with pytest.raises(TokenError):
            verifier.verify(token)
