"""Tests for production configuration safety checks."""


import pytest

from devhub.app import create_app
from devhub.config import _PLACEHOLDER_KEY, ProductionConfig, TestingConfig


def test_placeholder_key_constant_is_known_value():
    """The placeholder key value must not change silently."""
    assert _PLACEHOLDER_KEY == "dev-secret-change-me"


def test_production_config_debug_is_false():
    """ProductionConfig must have DEBUG=False."""
    assert ProductionConfig.DEBUG is False


def test_production_config_testing_is_false():
    """ProductionConfig must have TESTING=False."""
    assert ProductionConfig.TESTING is False


def test_startup_refuses_placeholder_key_in_production(monkeypatch):
    """create_app must raise RuntimeError when DEVHUB_ENV=production and key is placeholder."""
    monkeypatch.setenv("DEVHUB_ENV", "production")
    monkeypatch.setenv("DEVHUB_SECRET_KEY", _PLACEHOLDER_KEY)

    with pytest.raises(RuntimeError, match="DEVHUB_SECRET_KEY"):
        create_app(ProductionConfig)


def test_startup_refuses_missing_key_in_production(monkeypatch):
    """create_app must raise RuntimeError when DEVHUB_ENV=production and key is empty."""
    monkeypatch.setenv("DEVHUB_ENV", "production")
    monkeypatch.delenv("DEVHUB_SECRET_KEY", raising=False)

    # ProductionConfig.SECRET_KEY is evaluated at class load time from env; patch manually.
    original = ProductionConfig.SECRET_KEY
    try:
        ProductionConfig.SECRET_KEY = ""
        with pytest.raises(RuntimeError, match="DEVHUB_SECRET_KEY"):
            create_app(ProductionConfig)
    finally:
        ProductionConfig.SECRET_KEY = original


def test_startup_accepts_strong_key_in_production(monkeypatch):
    """create_app must succeed when DEVHUB_ENV=production and a real key is set."""
    monkeypatch.setenv("DEVHUB_ENV", "production")
    strong_key = "s3cur3-r@nd0m-k3y-that-is-not-a-placeholder!"
    monkeypatch.setenv("DEVHUB_SECRET_KEY", strong_key)

    original = ProductionConfig.SECRET_KEY
    try:
        ProductionConfig.SECRET_KEY = strong_key
        app = create_app(ProductionConfig)
        assert app is not None
    finally:
        ProductionConfig.SECRET_KEY = original


def test_startup_allows_placeholder_key_outside_production():
    """create_app must NOT raise when DEVHUB_ENV is not set (local dev)."""
    # DEVHUB_ENV is not set in the test environment; using TestingConfig always works.
    app = create_app(TestingConfig)
    assert app is not None
