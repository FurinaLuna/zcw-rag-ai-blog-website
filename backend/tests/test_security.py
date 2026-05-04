"""测试安全模块：JWT 签发/校验 + bcrypt 密码哈希"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


def test_hash_password():
    password = "test-password-123"
    hashed = hash_password(password)
    assert hashed != password
    assert len(hashed) > 0
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")


def test_verify_password_correct():
    password = "correct-password"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    password = "correct-password"
    hashed = hash_password(password)
    assert verify_password("wrong-password", hashed) is False


def test_hash_password_different_salts():
    password = "same-password"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    assert hash1 != hash2  # 不同盐值应产生不同哈希
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True


def test_verify_empty_password():
    password = ""
    hashed = hash_password(password)
    # 空密码应该也能验证（虽然生产环境不应使用）
    assert verify_password(password, hashed) is True


def test_create_access_token():
    token = create_access_token(data={"sub": 1, "username": "admin"})
    assert isinstance(token, str)
    assert len(token) > 0
    # JWT 应该包含三段 (header.payload.signature)
    assert token.count(".") == 2


def test_create_access_token_with_expiry():
    from datetime import timedelta

    token = create_access_token(
        data={"sub": 1}, expires_delta=timedelta(minutes=30)
    )
    assert isinstance(token, str)
    assert token.count(".") == 2


def test_decode_valid_token():
    token = create_access_token(data={"sub": 42, "username": "testuser"})
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["username"] == "testuser"
    assert "exp" in payload


def test_decode_invalid_token():
    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_access_token("invalid.token.string")


def test_decode_empty_token():
    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_access_token("")


def test_decode_tampered_token():
    token = create_access_token(data={"sub": 1})
    # 篡改 token 中间部分
    parts = token.split(".")
    tampered = f"{parts[0]}.{parts[1]}x.{parts[2]}"
    with pytest.raises(ValueError, match="Invalid or expired token"):
        decode_access_token(tampered)


def test_token_contains_exp():
    token = create_access_token(data={"sub": 1})
    payload = decode_access_token(token)
    assert "exp" in payload
    import datetime as dt

    assert payload["exp"] > dt.datetime.now(tz=dt.timezone.utc).timestamp()


def test_token_custom_claims():
    token = create_access_token(
        data={"sub": 100, "username": "admin", "role": "admin"}
    )
    payload = decode_access_token(token)
    assert payload["sub"] == "100"
    assert payload["username"] == "admin"
    assert payload["role"] == "admin"
