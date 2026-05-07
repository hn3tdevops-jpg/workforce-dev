# Security Model

## Overview

Workforce Dev Hub is designed as an internal developer tool. This document describes the security model, trust boundaries, and threat mitigations.

## Authentication

- **Flask-Login** is used for session-based authentication.
- Passwords are hashed with **Werkzeug's `generate_password_hash`** (PBKDF2-SHA256 by default).
- CSRF protection is enabled globally via **Flask-WTF/CSRFProtect** on all POST forms.
- Sessions are signed with `DEVHUB_SECRET_KEY` — this key must be kept secret and rotated if compromised.

## Authorization

The app enforces a deliberately simple access policy suited for an internal developer tool:

### Public (no login required)
- All read-only views: docs index/view, progress index/view/report, scripts index/view,
  packages index/view, projects index/view, search, main dashboard.
- JSON API endpoints: `/api/status`, `/api/search`, `/api/projects`, `/api/docs`,
  `/api/scripts`, `/api/progress/recent`.

**Rationale:** The app is intended for deployment inside a trusted network or behind
PythonAnywhere account-level access controls. Public read-only access simplifies
collaboration within the internal team.

### Login required
- All write operations: create, edit, delete documents; create/edit progress entries;
  create/edit scripts; upload packages.

### Admin required (`is_admin=True`)
- Package approval, install triggering.
- User management (`/admin/users`).
- Audit log (`/admin/audit`).
- Settings page (`/admin/settings`).

> **Production note:** If the hub will be exposed beyond your trusted network, add
> `@login_required` to the read-only views and API endpoints in `devhub/routes/`.
> See `docs/LOCAL_DEVELOPMENT.md` for configuration guidance.

## Package Security

Packages go through a strict quarantine workflow:

1. **Upload** — file is saved to the quarantine directory (never directly to production paths).
2. **Validation** — `package_validator.validate_package()` checks:
   - Valid zip file
   - No path traversal in zip entries (`..` or absolute paths)
   - Presence of `devhub-package.json` manifest
   - All required manifest fields present
   - Valid `risk_level` value
   - `intended_paths` do not escape workspace roots
3. **Admin Approval** — only admin users can approve a quarantined package.
4. **Install** — disabled by default (`DEVHUB_ENABLE_PACKAGE_INSTALL=false`). Even when enabled, the current implementation requires manual review.

### Path Traversal Prevention

- Zip entries are checked for `..`, leading `/`, and absolute paths.
- Manifest `intended_paths` are validated using `pathlib.Path.resolve()` and
  `os.path.commonpath()` to prevent prefix-escape attacks (e.g., `/workspace_api_evil`
  escaping root `/workspace_api`) and to normalise `..`/`.` segments and redundant slashes.

## Script Execution Security

- Script execution is **disabled by default** (`DEVHUB_ENABLE_SCRIPT_EXECUTION=false`).
- When disabled, no script commands are run regardless of UI actions.
- The Script library is a read-only catalog when execution is disabled.
- Scripts are tagged with `risk_level`: `safe`, `moderate`, or `dangerous`.
- All script runs are logged to `ScriptRunLog` with stdout, stderr, exit code, and who ran them.

## Audit Logging

All sensitive actions are written to the `AuditLog` table:
- Package uploads and approvals
- (Extendable to: user creation, document deletion, etc.)

Audit logs are viewable by admin users at `/admin/audit`.

## Secrets Management

- `DEVHUB_SECRET_KEY` — must be a long random string in production.
- Never commit `.env` to git (`.gitignore` excludes it).
- PythonAnywhere deployments should set environment variables in the WSGI config file.
- No credentials are hardcoded in source code.

## Input Validation

- All forms use **WTForms validators** (DataRequired, Email, Optional).
- CSRF tokens are required on all POST forms.
- File uploads are restricted to `.zip` only via extension check and `secure_filename`.
- Package manifest JSON is parsed safely with error handling.

## Threat Model

| Threat | Mitigation |
|--------|-----------|
| CSRF attacks | Flask-WTF CSRF protection on all forms |
| Password brute force | No rate limiting built-in (add nginx/PythonAnywhere rate limiting) |
| Path traversal in packages | Zip entry and manifest path validation |
| Malicious package install | Disabled by default; requires admin approval first |
| Script injection | Execution disabled by default |
| Session hijacking | Signed sessions; use HTTPS in production |
| XSS | Jinja2 auto-escaping enabled |
| Secrets exposure | `.env` excluded from git; secret key configurable via env |

## Recommendations for Production

1. Use HTTPS (PythonAnywhere provides this automatically).
2. Set a strong, random `DEVHUB_SECRET_KEY`.
3. Keep `DEVHUB_ENABLE_SCRIPT_EXECUTION=false` and `DEVHUB_ENABLE_PACKAGE_INSTALL=false`.
4. Regularly rotate the secret key.
5. Review audit logs periodically.
6. Restrict access to the PythonAnywhere account itself.
