from app.core.security.bcrypt_password_hasher import BcryptPasswordHasher


class TestHashAndVerify:
    def test_verify_succeeds_for_correct_password(self):
        hasher = BcryptPasswordHasher(rounds=4)
        hashed = hasher.hash("correct-horse-battery-staple")

        assert hasher.verify("correct-horse-battery-staple", hashed) is True

    def test_verify_fails_for_incorrect_password(self):
        hasher = BcryptPasswordHasher(rounds=4)
        hashed = hasher.hash("correct-horse-battery-staple")

        assert hasher.verify("wrong-password", hashed) is False

    def test_hash_is_not_the_plaintext_password(self):
        hasher = BcryptPasswordHasher(rounds=4)
        hashed = hasher.hash("correct-horse-battery-staple")

        assert hashed != "correct-horse-battery-staple"
