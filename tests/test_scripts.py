"""Tests proving script execution cannot run arbitrary commands."""

import pytest

from devhub.script_runner import run_script


def test_script_runner_raises_not_implemented():
    """run_script must raise NotImplementedError, never execute anything."""
    with pytest.raises(NotImplementedError):
        run_script(None)


def test_script_runner_raises_for_dry_run():
    """Even dry_run=True must not execute; it raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        run_script(None, dry_run=True)


def test_script_runner_raises_for_live_run():
    """dry_run=False must also raise NotImplementedError."""
    with pytest.raises(NotImplementedError):
        run_script(None, dry_run=False)


def test_script_runner_error_message_is_informative():
    """The error message must mention the feature flag so users know how to proceed."""
    with pytest.raises(NotImplementedError, match="DEVHUB_ENABLE_SCRIPT_EXECUTION"):
        run_script(object())


def test_api_reports_script_execution_disabled(client):
    """The /api/status endpoint must report script_execution_enabled=False in test config."""
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["script_execution_enabled"] is False


def test_scripts_index_shows_disabled_notice(client):
    """The scripts list page must contain the disabled notice when execution is off."""
    response = client.get("/scripts/")
    assert response.status_code == 200
    assert b"disabled" in response.data.lower()


def test_scripts_view_shows_disabled_notice(client, app):
    """The script detail page must contain the disabled notice when execution is off."""
    from devhub.extensions import db
    from devhub.models import Script

    with app.app_context():
        script = Script(name="test-script", risk_level="safe")
        db.session.add(script)
        db.session.commit()
        script_id = script.id

    response = client.get(f"/scripts/{script_id}")
    assert response.status_code == 200
    assert b"disabled" in response.data.lower()
