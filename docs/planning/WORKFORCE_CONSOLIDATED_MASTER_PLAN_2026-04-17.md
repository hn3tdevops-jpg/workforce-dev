<!-- Installed via DevHub feature-doc intake.
Original filename: workforce_consolidated_master_plan_2026-04-17.md
Installed at: 2026-05-15T15:24:26Z
This is a planning/reference document. Do not edit casually; revise via PR. -->

# Workforce Consolidated Master Plan

**Prepared:** April 17, 2026

**Status:** Consolidated planning draft based on the most recent roadmap and implementation-plan files surfaced in the available project sources.

## 1. Executive Summary

Workforce is now best understood as a single multi-tenant operations platform with distinct control, tenant, worker, and agent planes running on one backend and expressed through permission-driven workspaces in the UI.

The canonical planning direction is no longer a single-purpose hospitable application. The project has converged on a broader Workforce platform that keeps Hospitable Ops as one important module while adding superadmin, tenant administration, workforce operations, system settings, and future specialized modules such as CRM, communications, AI, timeline, restaurant/POS, and widget-driven dashboards.

The most stable architectural decisions are: preserve tenant isolation everywhere; keep user accounts separate from employer-managed employee files; derive access from explicit role assignments in business or location scope; treat job title as display-only; keep scheduling and timeclock authoritative in Workforce; and keep Hospitable Ops focused on rooms, tasks, inspections, issues, checklists, event logging, and shift-aware assignment.

The frontend direction has also stabilized. The plan is to extend the existing Next.js application rather than replace it, build a shared app shell, move navigation to a permission-aware registry, expose business and location as first-class context selectors, and hydrate the shell through a bootstrap/session endpoint that returns the current user, permissions, active context, and enabled workspaces.

Operationally, the repo is expected to use a planning system centered on HN3T_MASTER_PLAN, PROGRESS_REPORT, scripts/run_plan.sh, and repo-local Copilot guidance. Work should be executed in narrow, reviewable slices with explicit status vocabulary, evidence, and tenant/RBAC safety preserved.

## 2. Source Basis and Freshness

This document is a synthesis. It favors the most recent canonical roadmaps plus the stable architectural rules that have remained consistent across the project.

- **HN3T_MASTER_PLAN.md** — Canonical platform and architecture roadmap; surfaced from Google Drive; modified March 10, 2026.
- **workforce-merged-roadmap.md** — Latest merged UI roadmap and phase order; created April 4, 2026.
- **WORKFORCE_WEB_UI_COPILOT_IMPLEMENTATION.md** — Detailed implementation brief for evolving the existing Next.js app into the main Workforce web UI; created April 4, 2026.
- **REFERENCE_CATALOGUE.pdf** — Identity and employment architecture reference covering user, employee profile, linkage, and effective access rules; created March 28, 2026.
- **Workforce_Repo_Convention_Planning_Pack_Reference.pdf** — Planning-system reference for HN3T_MASTER_PLAN, PROGRESS_REPORT, run_plan workflow, and documentation structure; modified March 28, 2026.
- **AI_WIDGET_AGENT_IMPLEMENTATION_PLAN.md** — Future-facing widget and AI-assisted dashboard workstream plan; created April 4, 2026.
- **WF_Server_Boundary_Reference_Catalogue.pdf** — Deployment and PythonAnywhere boundary plan separating backend, frontend, and admin tooling; created March 31, 2026.
- **Workforce Prompt Pack / related prompt files** — Backend demo slice expectations, scoped RBAC and hospitable task model requirements, and API alignment guidance; last updated late March 2026.

> Important note: explicit up-to-the-minute PROJECT_STATE_REPORT or current PROGRESS_REPORT files were not surfaced in the available search results during this consolidation. Where those would normally refine status, this document relies on the canonical master-plan direction, the latest UI roadmap material, and existing ongoing project context.

## 3. Canonical Architectural Decisions

### Identity and workforce linkage

- System users are independent from employee records.
- Businesses own employee files; users own personal account data.
- A user may be linked to an employee record through an explicit relationship lifecycle.
- Effective workforce access should only exist when user state, link state, employee state, and employee-scoped role assignments are all active.

### Tenancy and scoping

- Business is the main tenant boundary.
- Location is a first-class operational scope under business.
- Tenant-owned tables must carry business scope and location scope where relevant.
- Cross-tenant or cross-location shortcuts are not acceptable unless explicitly authorized.

### RBAC model

- Permissions come from roles, not job titles.
- Roles may be business-scoped or location-scoped.
- Users can hold different roles at different locations.
- Every role and assignment mutation must be auditable.

### Hospitable integration rules

- Workforce remains the source of truth for employees, shifts, schedules, and timeclock.
- Hospitable Ops stores references to external employees and shifts, not duplicate labor systems.
- Hospitable owns units/rooms, housekeeping tasks, inspections, issues, checklists, and operational event history.

## 4. Program Scope and Product Shape

The current plan treats Workforce as a modular operations platform rather than a single-purpose hospitality app. The platform is expected to support multiple operating surfaces while sharing one backend policy and data core.

The base product already centers on Workforce Core and Hospitable Ops, but the roadmap also anticipates future module expansion into CRM, communication, AI gateway, Studio, timeline/event projection, restaurant or POS/KDS-style workflows, and configurable widget-driven dashboards.

That means implementation must preserve boundaries. Future modules should be added as coherent workstreams with clear ownership and service contracts instead of being bolted into one undifferentiated monolith.

- Control-plane administration
- Tenant/business administration
- Worker self-service
- Workforce operations
- Hospitable operations
- System configuration
- AI and integration surfaces
- Future CRM / Studio / restaurant / widget modules

## 5. Current Working Repo and Environment Context

- **Backend repo:** /home/hn3t/workforce_api — FastAPI, SQLAlchemy, Alembic, Pydantic v2, and multi-tenant service-layer enforcement.
- **Frontend repo:** /home/hn3t/workforce_frontend_app — pnpm workspace with a Vite/React or Next.js oriented frontend artifact flow depending on the workstream being advanced.
- **Dev hub:** /home/hn3t/dev_hub — static documentation and project-state presentation surface.
- **Primary backend domain:** hn3t.pythonanywhere.com is the active API surface.
- **Target frontend / combined experience domain:** wf-hn3t.pythonanywhere.com is the intended user-facing web root for frontend and adjacent dev-hub routing.

## 6. Major Workstreams

### Foundation architecture
- **Primary objective:** Finalize the shared platform rules, especially identity, tenancy, RBAC, and role/link access resolution.
- **Planning note:** This is the non-negotiable substrate under every module.

### Backend core
- **Primary objective:** Continue hardening auth, bootstrap, business/location scoping, role assignment, permission resolution, and tenant-safe CRUD/service patterns.
- **Planning note:** Includes keeping routers thin, using Alembic for schema evolution, and preserving auditability.

### Hospitable Ops
- **Primary objective:** Complete location-scoped housekeeping workflows including units, tasks, inspections, issues, templates, checklist runs, event logs, auto-assignment, and offline-aware behavior.
- **Planning note:** Should integrate with Workforce schedule data rather than reimplement it.

### Workforce Web UI
- **Primary objective:** Promote the current hospitable-focused web app into the primary Workforce console with shared shell, route groups, selectors, typed DTOs, and permission-driven navigation.
- **Planning note:** Should preserve current hospitable value while broadening access layers.

### Deployment and boundaries
- **Primary objective:** Separate backend runtime, frontend runtime, and admin/dev tooling cleanly on PythonAnywhere.
- **Planning note:** The backend should be API-only long term; the frontend should own SPA/login delivery.

### Planning framework
- **Primary objective:** Keep HN3T_MASTER_PLAN as the master roadmap and use PROGRESS_REPORT plus scripts/run_plan.sh for narrow checkbox execution.
- **Planning note:** This is the program-management operating system for the repo.

### Future modules
- **Primary objective:** Prepare structured workstreams for CRM, communication, AI gateway, Studio, timeline/event projections, restaurant/POS, widget builder, and advanced dashboards.
- **Planning note:** These should remain modular and not collapse into an undifferentiated monolith.

## 7. Backend Master Plan

### Planes

- Control plane: business provisioning, global audit, permission templates, agent registry, data import/export, and platform-level oversight.
- Tenant plane: employees, roles, permissions, locations, schedules, reports, and integrations at the business level.
- Worker plane: self-service schedule, timeclock, requests, tasks, and role-aware profile experience.
- Agent plane: AI/integration credentials, scoped permissions, run tracking, logs, and least-privilege execution.

### Core entities

- Business
- Location
- User
- EmployeeProfile
- UserEmployeeLink
- Role
- Permission
- UserRoleAssignment / employee-scoped role assignment
- Effective access context

### Core backend rules

- Never bypass tenant or location scoping in queries or services.
- Validate business and location consistency on every scoped write.
- Keep business logic in services or domain modules rather than route handlers.
- Use migrations for schema changes and keep models, schemas, services, and tests in sync.
- Capture audit events for security-sensitive or workflow-critical mutations.

### Hospitable data model direction

- Units/rooms with location scope and operational status.
- Tasks with unique daily constraints by unit/date/type, assignment references, due/start/complete timestamps, and validated transitions.
- Inspections tied to tasks, with failure optionally sending work back to in-progress.
- Issues/maintenance states with open-to-closed lifecycle.
- Checklist templates, checklist runs, and locked completed runs.
- EmployeeRef and ShiftRef integration tables referencing external workforce identities.

### Required endpoint families

- Auth and bootstrap
- Users / roles / assignments
- Locations / units / tasks
- Inspections / issues / checklists
- Dashboard summary and bootstrap/session surfaces
- Integration upserts and health checks
- Audit and event-history reads

## 8. Workforce Web UI Plan

### Primary direction

- Do not build a brand-new frontend from scratch.
- Extend the existing app as the main Workforce Web UI.
- Move from a hospitable-only shell to a module-oriented Workforce shell.

### Required shell capabilities

- Shared app shell with topbar, sidebar, workspace switcher, business selector, location selector, alerts stub, and user menu.
- Permission-aware navigation registry rather than hardcoded route-only sidebars.
- Current-user and bootstrap/session hooks with typed DTOs and mock fallback when backend support is incomplete.
- Desktop nav collapse state persisted locally; mobile drawer supported.

### Target route families

- Root dashboard / overview
- /superadmin/*
- /admin/*
- /workforce/*
- /hospitable/*
- /system/*

### Known phased order

- Phase 0: stabilize backend boot, migrations, auth, seed data, CORS, and visible shell.
- Phase 1: shared shell and permission-driven navigation.
- Phase 2: route refactor and hospitable page re-homing.
- Phase 3: typed API client expansion and DTO cleanup.
- Phase 4: superadmin pages.
- Phase 5: tenant admin pages.
- Phase 6: workforce and hospitable completion.
- Phase 7: polish, theming, contrast cleanup, and tests.
- Phase 8: advanced features such as widget builder, feature flags, dashboard templates, visual room map, and audit detail viewer.

### Illustrative target information architecture

- Root overview / dashboard
- Superadmin: businesses, locations, users, roles, permissions, feature flags, audit, integrations, API keys, jobs
- Tenant Admin: overview, business settings, locations, members, roles, dashboards, modules
- Workforce: overview, scheduling, shifts, assignments, timeclock
- Hospitable: dashboard, rooms, housekeeping, maintenance, inventory, property setup
- System: profile, preferences, notifications, access

## 9. Hospitable Ops Plan Inside the Workforce Program

### Purpose

- Hospitable Ops is the housekeeping and property-operations module inside Workforce, not a replacement for Workforce itself.
- Its job is to manage units/rooms, tasks, inspections, issues, checklists, event logs, and shift-aware assignment while consuming schedule and labor context from the authoritative Workforce side.

### Core domain expectations

- Units and rooms are location-scoped operational entities.
- Tasks are generated and managed per unit/date/type with validated transitions.
- Inspections and issues are first-class workflow events, not afterthought comments.
- Checklist templates and runs support repeatable operating standards.
- Every meaningful mutation should produce audit and workflow history.
- Offline-aware execution and idempotent replay are part of the target design.

### Out-of-scope protections

- Do not rebuild a separate scheduling engine inside Hospitable Ops.
- Do not duplicate timeclock or payroll responsibilities.
- Do not let hospitable convenience shortcuts weaken business or location scoping.

## 10. Planning and Execution Operating Model

- Treat HN3T_MASTER_PLAN.md as the canonical roadmap document.
- Use docs/planning as the reusable long-form planning library when installed or synchronized.
- Use PROGRESS_REPORT templates and explicit status vocabulary rather than ad hoc progress prose.
- Use scripts/run_plan.sh and one-checkbox execution discipline for implementation slices.
- Prefer additive, reviewable patches; do not replace stronger existing repo guidance with generic package text.

### Recommended execution discipline

1. Start from a module spec or approved plan section.
2. Translate it into phased build-order and, where appropriate, atomic execution checkboxes.
3. Execute one small coherent slice at a time.
4. Update progress artifacts with evidence, not just narrative.
5. Carry forward only the minimal next scope needed for the following patch.

## 11. Deployment, Boundaries, and Runtime Shape

- Use separate frontend- and backend-serving webapps on PythonAnywhere.
- Keep backend runtime responsible for API concerns only; it should not remain the durable owner of SPA fallback once the frontend webapp is fully established.
- Keep OpenAI secrets and server-side calls in backend or intentional admin/dev contexts only.
- Keep Copilot prompts, wrappers, and operator scripts in repo-local docs or admin/dev areas rather than in runtime web roots.
- Serve the dev hub as a static documentation surface that aggregates plan, progress, and state visibility.

The deployment direction supports a cleaner long-term split: backend API on its own webapp, frontend delivery on its own webapp, and documentation/admin tooling in clearly bounded surfaces.

## 12. Recommended Near-Term Sequence

1. Finalize and harden the identity/employee-link architecture in the backend so future modules inherit correct access semantics.
2. Complete the bootstrap/session API contract that the shell depends on.
3. Advance the Workforce Web UI shell and route-group refactor on top of the existing app.
4. Complete the core hospitable operational loop end to end: unit -> task -> assignment -> status -> inspection -> issue/event visibility.
5. Finish PythonAnywhere separation so frontend delivery, backend API, and dev/admin surfaces are cleanly bounded.
6. Normalize the planning workflow and state reporting so code execution remains aligned with the master plan.

## 13. Open Decisions and Design Questions

- Which frontend artifact path and routing strategy should be considered the long-term canonical delivery target once the current mixed experiments settle?
- How much of the current superadmin and tenant API contract already exists in canonical backend modules versus older or duplicate packages?
- Which future module should be converted into the next detailed atomic execution section after the current core Workforce + Hospitable work: CRM, Communication, AI Gateway, Studio, Timeline, or Restaurant/POS?
- How should the timeline/event-log projection workstream be positioned relative to current operational slices so it adds value without slowing core delivery?

## Appendix A. Working Acceptance Criteria by Area

### Identity and access

- User records and employee records remain distinct.
- Link lifecycle is explicit and auditable.
- Effective access context is derivable from active user, active link, active employee state, and active scoped assignments.
- Job title never becomes a hidden permission shortcut.

### Backend core

- Auth, bootstrap, scoped role assignment, and tenant-safe CRUD/service patterns are operational and tested.
- Alembic migrations are authoritative for schema evolution.
- Core routes return frontend-usable contracts.

### Workforce Web UI

- One shared shell exists and is reused across workspaces.
- Navigation is driven by permissions.
- Business and location selectors are visible and meaningful.
- Bootstrap/session hydration exists or has a clear adapter/fallback path.

### Hospitable Ops

- Rooms/units, tasks, assignments, inspections, issues, and dashboard summaries can run through a coherent end-to-end loop.
- Task and room state transitions are validated in services.
- Audit and event history exists for operationally meaningful changes.

### Deployment

- Frontend and backend runtimes are no longer conflated.
- Frontend assets and login experience are owned by the frontend delivery surface.
- Backend remains the owner of API, database, and server-side integrations.

## Appendix B. Source Summary for This Consolidation

- **HN3T_MASTER_PLAN.md** — Canonical platform and architecture roadmap; surfaced from Google Drive; modified March 10, 2026.
- **workforce-merged-roadmap.md** — Latest merged UI roadmap and phase order; created April 4, 2026.
- **WORKFORCE_WEB_UI_COPILOT_IMPLEMENTATION.md** — Detailed implementation brief for evolving the existing Next.js app into the main Workforce web UI; created April 4, 2026.
- **REFERENCE_CATALOGUE.pdf** — Identity and employment architecture reference covering user, employee profile, linkage, and effective access rules; created March 28, 2026.
- **Workforce_Repo_Convention_Planning_Pack_Reference.pdf** — Planning-system reference for HN3T_MASTER_PLAN, PROGRESS_REPORT, run_plan workflow, and documentation structure; modified March 28, 2026.
- **AI_WIDGET_AGENT_IMPLEMENTATION_PLAN.md** — Future-facing widget and AI-assisted dashboard workstream plan; created April 4, 2026.
- **WF_Server_Boundary_Reference_Catalogue.pdf** — Deployment and PythonAnywhere boundary plan separating backend, frontend, and admin tooling; created March 31, 2026.
- **Workforce Prompt Pack / related prompt files** — Backend demo slice expectations, scoped RBAC and hospitable task model requirements, and API alignment guidance; last updated late March 2026.

**Working note:** This version is written to be edited. It is intended to become the next durable planning handoff or repo-side master-plan companion, not a static one-off summary.