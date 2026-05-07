"""
UI tests: login page branding, dashboard render, navigation links,
and package security regressions.
"""

import io
import json
import zipfile

import pytest


# ---------------------------------------------------------------------------
# Isolated client fixture for login-page tests
# Avoids Flask-Login's g-based user cache being polluted by other tests.
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def ui_client():
    """A completely isolated Flask app + client for login-page content tests."""
    from devhub.app import create_app
    from devhub.config import TestingConfig
    from devhub.extensions import db as _db

    a = create_app(TestingConfig)
    with a.app_context():
        _db.create_all()
        c = a.test_client()
        # Seed admin user so credential tests work
        from devhub.models import User

        if not User.query.filter_by(email="uiadmin@example.com").first():
            u = User(email="uiadmin@example.com", is_admin=True)
            u.set_password("uipass123")
            _db.session.add(u)
            _db.session.commit()
        yield c
        _db.drop_all()


# ---------------------------------------------------------------------------
# Login page
# ---------------------------------------------------------------------------


def test_login_page_renders(ui_client):
    response = ui_client.get("/login")
    assert response.status_code == 200


def test_login_page_branded_title(ui_client):
    response = ui_client.get("/login")
    assert b"Workforce Developer Hub" in response.data


def test_login_page_subtitle(ui_client):
    response = ui_client.get("/login")
    assert b"Sign in to manage" in response.data


def test_login_page_security_note(ui_client):
    response = ui_client.get("/login")
    assert b"Authorized users only" in response.data


def test_login_page_has_email_field(ui_client):
    response = ui_client.get("/login")
    assert b"email" in response.data.lower()


def test_login_page_has_password_field(ui_client):
    response = ui_client.get("/login")
    assert b"password" in response.data.lower()


def test_login_page_has_remember_me(ui_client):
    response = ui_client.get("/login")
    assert b"Remember" in response.data


def test_login_page_has_form(ui_client):
    response = ui_client.get("/login")
    assert b"<form" in response.data


def test_login_invalid_credentials_flashes_error(ui_client):
    response = ui_client.post(
        "/login",
        data={"email": "nobody@example.com", "password": "bad"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Invalid email or password" in response.data


def test_login_valid_credentials_redirects_to_dashboard(ui_client):
    # The ui_client fixture seeds "uiadmin@example.com"
    with ui_client.session_transaction() as sess:
        sess.clear()
    response = ui_client.post(
        "/login",
        data={"email": "uiadmin@example.com", "password": "uipass123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Dashboard" in response.data


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------


def test_dashboard_renders_when_anonymous(client):
    response = client.get("/")
    assert response.status_code == 200


def test_dashboard_renders_after_login(client, admin_user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_user.id)
        sess["_fresh"] = True
    response = client.get("/")
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_dashboard_contains_stats_section(client, admin_user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_user.id)
        sess["_fresh"] = True
    response = client.get("/")
    # Stats cards link to main sections
    assert b"Projects" in response.data
    assert b"Docs" in response.data
    assert b"Packages" in response.data


def test_dashboard_quick_action_buttons_for_authed_user(client, admin_user):
    with client.session_transaction() as sess:
        sess["_user_id"] = str(admin_user.id)
        sess["_fresh"] = True
    response = client.get("/")
    assert b"Log Progress" in response.data
    assert b"New Doc" in response.data
    assert b"Upload Package" in response.data


# ---------------------------------------------------------------------------
# Primary navigation links
# ---------------------------------------------------------------------------


def test_nav_dashboard_link(client):
    response = client.get("/")
    assert b"Dashboard" in response.data


def test_nav_projects_link(client):
    response = client.get("/")
    assert b"/projects" in response.data


def test_nav_docs_link(client):
    response = client.get("/")
    assert b"/docs" in response.data


def test_nav_progress_link(client):
    response = client.get("/")
    assert b"/progress" in response.data


def test_nav_scripts_link(client):
    response = client.get("/")
    assert b"/scripts" in response.data


def test_nav_packages_link(client):
    response = client.get("/")
    assert b"/packages" in response.data


# ---------------------------------------------------------------------------
# Package security regressions
# ---------------------------------------------------------------------------


def test_package_install_still_admin_only(app, client, db):
    """Non-admin cannot trigger install even when feature flag is on."""
    import uuid

    with app.app_context():
        from devhub.models import Package, User

        user = User(email=f"nonadmin-{uuid.uuid4().hex}@example.com", is_admin=False)
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()
        uid = user.id

        pkg = Package(
            filename="ui-test.zip",
            quarantine_path="quarantine/ui/ui-test.zip",
            manifest_valid=True,
            status="approved",
            risk_level="safe",
            requires_manual_review=False,
        )
        db.session.add(pkg)
        db.session.commit()
        pkg_id = pkg.id

    original = app.config["ENABLE_PACKAGE_INSTALL"]
    app.config["ENABLE_PACKAGE_INSTALL"] = True
    try:
        with client.session_transaction() as sess:
            sess["_user_id"] = str(uid)
            sess["_fresh"] = True
        response = client.post(f"/packages/{pkg_id}/install", follow_redirects=True)
        assert response.status_code == 200
        assert b"Admin access required." in response.data
    finally:
        app.config["ENABLE_PACKAGE_INSTALL"] = original


def test_package_approve_still_admin_only(app, client, db):
    """Non-admin cannot approve a package."""
    import uuid

    with app.app_context():
        from devhub.models import Package, User

        user = User(email=f"nonadmin2-{uuid.uuid4().hex}@example.com", is_admin=False)
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()
        uid = user.id

        pkg = Package(
            filename="ui-test2.zip",
            quarantine_path="quarantine/ui2/ui-test2.zip",
            manifest_valid=True,
            status="quarantined",
            risk_level="safe",
            requires_manual_review=False,
        )
        db.session.add(pkg)
        db.session.commit()
        pkg_id = pkg.id

    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True
    response = client.post(f"/packages/{pkg_id}/approve", follow_redirects=True)
    assert response.status_code == 200
    assert b"Admin access required." in response.data

    with app.app_context():
        from devhub.models import Package

        pkg = db.session.get(Package, pkg_id)
        assert pkg.status == "quarantined"


def test_install_button_not_shown_to_non_admin(app, client, db):
    """Install button must not appear in package view for non-admin."""
    import uuid

    with app.app_context():
        from devhub.models import Package, User

        user = User(email=f"viewer-{uuid.uuid4().hex}@example.com", is_admin=False)
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()
        uid = user.id

        pkg = Package(
            filename="ui-view-test.zip",
            quarantine_path="quarantine/view/test.zip",
            manifest_valid=True,
            status="approved",
            risk_level="safe",
            requires_manual_review=False,
        )
        db.session.add(pkg)
        db.session.commit()
        pkg_id = pkg.id

    original = app.config["ENABLE_PACKAGE_INSTALL"]
    app.config["ENABLE_PACKAGE_INSTALL"] = True
    try:
        with client.session_transaction() as sess:
            sess["_user_id"] = str(uid)
            sess["_fresh"] = True
        page = client.get(f"/packages/{pkg_id}")
        assert page.status_code == 200
        assert b"> Install<" not in page.data
    finally:
        app.config["ENABLE_PACKAGE_INSTALL"] = original
