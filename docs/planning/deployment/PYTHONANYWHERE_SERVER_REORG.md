<!-- Installed via DevHub feature-doc intake.
Original filename: 10_COPILOT_PROMPT_SERVER_REORG.md
Installed at: 2026-05-15T15:24:26Z
This is a planning/reference document. Do not edit casually; revise via PR. -->

# Copilot Prompt — PythonAnywhere Server Reorganization

You are working on a PythonAnywhere-hosted Workforce deployment. Your job is to reorganize the host and project boundaries without breaking the running services.

## Mission

Cleanly separate the backend runtime, frontend runtime, and admin/dev tooling so that:

- backend is stable and API-only
- frontend is its own independent project
- `wf-hn3t.pythonanywhere.com` serves the frontend/login page
- the frontend project lives in `/home/hn3t/workforce_frontend_app`
- the frontend project is cloned from `hn3tdevops-jpg/Workforce-Showcase`
- do not set up any automatic synchronization/pull behavior for that frontend repo
- OpenAI is present only where actually used
- Copilot tooling is present only where useful for development/admin work
- a current-state workspace report can be generated and reviewed

## Non-negotiable rules

1. Do not make destructive moves before taking inventory and backups.
2. Do not delete anything merely because it looks old; first classify it as canonical, duplicate, archive, or unknown.
3. Do not put frontend deployment responsibility inside the backend unless needed as a temporary fallback during transition.
4. Do not place OpenAI secrets or server-side OpenAI execution in the frontend/browser project.
5. Do not make production runtime depend on Copilot being installed.
6. Keep one clearly active WSGI entrypoint per webapp.
7. Prefer small, reviewable changes with explicit verification after each phase.

## Target boundaries

### Backend canonical path
`/home/hn3t/projects_active`

### Frontend canonical path
`/home/hn3t/workforce_frontend_app`

### Frontend source repo
`hn3tdevops-jpg/Workforce-Showcase`

### Frontend domain responsibility
`wf-hn3t.pythonanywhere.com` serves the login page and frontend assets.

### Backend responsibility
API only.

## Required work sequence

### Phase 1 — Inventory
Create a report that identifies:

- git roots under `/home/hn3t`
- branches/remotes
- frontend build directories
- WSGI files under `/var/www`
- PythonAnywhere logs under `/var/log`
- virtual environments
- environment files by path
- duplicated or suspicious project roots

Write the report to a dedicated reports folder.

### Phase 2 — Classify
Classify each relevant directory/file as one of:

- canonical runtime
- canonical source
- admin/dev tooling
- duplicate
- archive candidate
- unknown / needs human review

### Phase 3 — Separate frontend and backend
Ensure the frontend project is isolated in `/home/hn3t/workforce_frontend_app`.
Ensure the backend remains isolated in `/home/hn3t/projects_active`.

### Phase 4 — Webapp cleanup
Identify the current active WSGI files.
Create or cleanly standardize:
- one backend entrypoint
- one frontend entrypoint

Make comments in those files stating their responsibility.

### Phase 5 — OpenAI/Copilot placement
Move or document OpenAI integration so it exists only in backend/admin contexts that truly use it.
Move Copilot helper clutter into admin/docs areas and leave only necessary repo-local instruction files.

### Phase 6 — Verification
Verify:
- frontend domain loads login page
- frontend assets load
- backend health endpoint works
- logs show no import/bootstrap failure
- frontend references correct API base URL
- OpenAI smoke test works if enabled on backend

## Deliverables

Produce:
1. a Markdown inventory report
2. a Markdown boundary decision report
3. a list of files moved or flagged
4. minimal code/config patches
5. verification notes

## Output format

For code changes: unified diff only.
For reports: Markdown.
For shell automation: safe, idempotent scripts preferred.
Do not output vague advice. Make grounded changes based on actual files found.
