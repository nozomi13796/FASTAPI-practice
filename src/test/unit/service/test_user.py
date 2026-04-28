from datetime import timedelta
import importlib
import pytest

import service.user as user_module
from model.user import User


def test_get_hash_and_verify_password():
    plain = "s3cr3t"
    hashed = user_module.get_hash(plain)
    assert isinstance(hashed, str) and hashed
    assert user_module.verify_password(plain, hashed)
    assert not user_module.verify_password("wrong", hashed)


def test_get_jwt_username_and_create_token():
    token = user_module.create_access_token({"sub": "alice"}, expires=timedelta(minutes=5))
    assert user_module.get_jwt_username(token) == "alice"
    # malformed token
    assert user_module.get_jwt_username("not-a-token") is None


def test_get_current_user_and_auth_user(monkeypatch):
    # prepare a User with a hashed password
    u = User(name="bob", hash=user_module.get_hash("pwd"))

    # monkeypatch underlying data.get used by lookup_user
    class DummyData:
        def get(self, name):
            return u if name == "bob" else None

    monkeypatch.setattr(user_module, "data", DummyData())

    # reload module to ensure functions reference patched data
    importlib.reload(user_module)

    # create token for bob
    token = user_module.create_access_token({"sub": "bob"})
    # current user should be the patched user
    current = user_module.get_current_user(token)
    assert current is not None
    assert current.name == "bob"

    # token with unknown subject -> None
    token_unknown = user_module.create_access_token({"sub": "nobody"})
    assert user_module.get_current_user(token_unknown) is None

    # auth_user success and failures
    assert user_module.auth_user("bob", "pwd") is not None
    assert user_module.auth_user("bob", "bad") is None
    assert user_module.auth_user("nobody", "pwd") is None
