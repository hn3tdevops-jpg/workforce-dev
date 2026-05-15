<!-- Installed via DevHub feature-doc intake.
Original filename: workforce-merged-roadmap.md
Installed at: 2026-05-15T15:24:26Z
This is a planning/reference document. Do not edit casually; revise via PR. -->

# Workforce UI merged implementation roadmap

## What the uploaded materials agree on

- Keep `apps/web/hospitable-web` as the main web app and extend it rather than rebuilding the frontend from scratch.
- Move from a Hospitable-only UI to a module-oriented Workforce shell with workspaces for Superadmin, Tenant Admin, Workforce, Hospitable, and System.
- Make navigation permission-driven, not route-only.
- Treat business and location as first-class context selectors.
- Keep existing `/api/v1` backend conventions and reuse existing hospitable APIs where possible.
- Add a lightweight bootstrap/session endpoint so the frontend can hydrate current user, permissions, business, location, and enabled workspaces from one call.
- Build incrementally: shell first, then typed API and DTOs, then superadmin, then tenant admin, then workforce modules, then advanced features like widget builder and feature flags.

## Conflicts resolved

- The docs show both `app/(console)/layout.tsx` and top-level `app/superadmin/*`.
- In Next.js App Router, the safe implementation is:
  - `app/(console)/layout.tsx`
  - `app/(console)/superadmin/page.tsx`
  - `app/(console)/admin/page.tsx`
  - `app/(console)/workforce/page.tsx`
  - `app/(console)/hospitable/page.tsx`
  - `app/(console)/system/*`
- This keeps URLs the same while letting one shared layout wrap those routes.

## Phase order

### Phase 0 — stabilize base product
- Confirm backend boot, migrations, auth, `/auth/me`, seed data, CORS, and the browser-visible shell.
- Add or confirm a bootstrap/session endpoint for frontend hydration.
- Keep scope tight: auth, session, rooms, tasks, shell.

### Phase 1 — shared shell and navigation
- Add a generic `AppShell`.
- Refactor sidebar into a permission-aware navigation renderer.
- Add topbar with:
  - workspace switcher
  - business selector
  - location selector
  - alerts stub
  - user menu
- Add `CurrentUser`, `BootstrapSession`, permission helpers, `useCurrentUser`, `usePermissions`, `useWorkspace`.
- Persist desktop nav collapse state in `localStorage`.
- Use mock fallback when bootstrap/session is not ready yet.

### Phase 2 — route refactor
- Keep legacy root hospitable pages temporarily.
- Add new grouped console routes under `(console)`.
- Re-home hospitable pages under `/hospitable/*`.
- After the new pages exist, add explicit redirects:
  - `/rooms` -> `/hospitable/rooms`
  - `/housekeeping` -> `/hospitable/housekeeping`
  - `/maintenance` -> `/hospitable/maintenance`
  - `/inventory` -> `/hospitable/inventory`
  - `/property-setup` -> `/hospitable/property-setup`
  - `/settings` -> `/system/preferences` or `/admin/business-settings`

### Phase 3 — typed API client expansion
- Keep existing hospitable methods.
- Expand `lib/api.ts` into namespaced clients:
  - `bootstrap`
  - `superadmin`
  - `admin`
  - `workforce`
  - `hospitable`
- Add DTOs under `lib/types/*`.
- Prefer adapter/fallback mode while backend catches up.

### Phase 4 — superadmin console
- Build:
  - overview
  - businesses
  - locations
  - users
  - roles
  - permissions
  - feature flags
  - audit log
- Reuse shared table/filter/card primitives.

### Phase 5 — tenant admin
- Build:
  - overview
  - business settings
  - locations
  - members
  - roles
  - dashboards
- Gate actions with permissions.

### Phase 6 — workforce and hospitable completion
- Workforce: scheduling, shifts, assignments, timeclock.
- Hospitable: move current rooms, housekeeping, maintenance, inventory, property setup into their new workspace paths.

### Phase 7 — polish and testing
- Add theme tokens, light/dark/system toggle, and contrast cleanup.
- Make business selector show names everywhere, not IDs.
- Add tests for:
  - sidebar visibility by permission
  - at least one superadmin page
  - bootstrap/session fallback
  - route guards / unauthorized states

### Phase 8 — advanced
- Widget builder
- Feature flags
- Dashboard templates
- Visual room map
- Audit detail viewer

## Backend minimum contract for the shell
- `GET /api/v1/bootstrap/session`
  - user
  - permissions
  - active business
  - active location
  - available businesses
  - available locations
  - enabled workspaces/modules

## First patch scope
This first patch covers:
- shared shell scaffolding
- typed nav registry
- permission filtering
- workspace switcher
- current-user/session hook with mock fallback
- grouped `(console)` routes for `/superadmin`, `/admin`, `/workforce`, `/hospitable`, and `/system/preferences`

## What it intentionally does not do yet
- migrate existing root hospitable pages
- add redirects
- wire the real selectors to mutation/state persistence
- expand `lib/api.ts`
- add guards and page-level authorization components
- build data tables/forms
- implement feature flags or widget builder