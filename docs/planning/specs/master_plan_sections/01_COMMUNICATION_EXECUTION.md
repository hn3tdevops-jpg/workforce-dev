<!--
HN3T_MASTER_PLAN execution section — Communication module.

Status: draft, intended to be cut-and-pasted into the backend repo's
`docs/plans/HN3T_MASTER_PLAN.md` as a new top-level section. Authored from
`docs/planning/specs/COMMUNICATION_MODULE_SPEC.md`. Numbered "01" because
Communication is a precondition for the Studio AI integration section.
-->

# Communication Module — Execution Plan

**Spec reference:** [`../COMMUNICATION_MODULE_SPEC.md`](../COMMUNICATION_MODULE_SPEC.md)
**Workstream owner:** Communication
**Precedes:** Studio AI integration (cannot ship until at least M1 here is green)
**Depends on:** tenant + RBAC (existing), nothing new

## Goal

Land a canonical, transport-agnostic threaded-conversation module that any other
Workforce module can attach to its own objects (Studio designs first; CRM, Hospitable
Ops, Timeline later) without re-implementing threads, participants, attachments, or
read state.

## Non-goals (this section)

- No realtime / websocket layer. Polling is acceptable for M1.
- No OpenAI, prompts, or AI behaviour — that belongs to the AI Gateway section.
- No Studio-specific UI or domain objects.
- No email/SMS bridge. External transports are a later workstream.

## Scope

In-scope tables (new, tenant-scoped):

- `comm_threads` — id, tenant_id, subject_type, subject_id, title, created_by, created_at, last_message_at, closed_at
- `comm_messages` — id, thread_id, author_type ("user"|"ai_gateway"|"system"), author_id, body_markdown, parent_message_id, created_at, edited_at, deleted_at, ai_request_log_id (nullable FK, see AI Gateway section)
- `comm_participants` — thread_id, user_id, role ("owner"|"participant"|"observer"), added_by, added_at, last_read_message_id
- `comm_attachments` — id, message_id, filename, content_type, size_bytes, storage_key, uploaded_by, uploaded_at

In-scope API surface (under existing `/api/v1`):

- `POST   /api/v1/comm/threads`
- `GET    /api/v1/comm/threads?subject_type=&subject_id=`
- `GET    /api/v1/comm/threads/:id`
- `POST   /api/v1/comm/threads/:id/messages`
- `GET    /api/v1/comm/threads/:id/messages?after=&limit=`
- `POST   /api/v1/comm/threads/:id/participants`
- `POST   /api/v1/comm/messages/:id/attachments`
- `POST   /api/v1/comm/threads/:id/read` (sets `last_read_message_id`)

All endpoints enforce tenant scoping and RBAC. `subject_type` / `subject_id` are
opaque to Communication — they're just a polymorphic anchor the calling module
gives us. No FK enforcement on the subject side; the owning module manages cleanup.

## Milestones

### M1 — Read/write threads with messages (MVP, blocks Studio)

- Alembic migration for the four tables, with `(tenant_id, subject_type, subject_id)` index on threads.
- SQLAlchemy models + Marshmallow (or pydantic, repo-dependent) schemas.
- Services in `services/communication/` — no business logic in route handlers.
- Routes above except `participants` and `attachments`.
- Authorization: a user can read/write a thread iff they are a participant **or** they have read/write permission on the `(subject_type, subject_id)` they're scoping into. Communication asks the owning module via a `can_user_access(subject_type, subject_id, user, mode)` resolver registry; Studio is the first registrant.
- Pytest coverage: tenant isolation, RBAC denial, pagination, deletion (soft).
- DevHub: progress entry + audit log on every schema migration.

### M2 — Participants + read state

- Participants endpoint and per-user `last_read_message_id`.
- Unread-count aggregation endpoint: `GET /api/v1/comm/unread?subject_type=&subject_id=`.

### M3 — Attachments

- Storage backend abstraction (local disk in dev, S3-compatible in prod). Reuse existing storage helper if one exists; otherwise add `services/storage/`.
- Virus scan hook is a no-op pluggable interface for now.
- Mime-type whitelist enforced server-side.

### M4 — Subject deletion contract

- Owning modules call `comm.archive_for_subject(subject_type, subject_id)` on delete.
- Archived threads are read-only and excluded from default listings; never hard-deleted.

## Acceptance criteria (whole section)

- A Studio design object can host a thread, accept messages from a human user and from the AI Gateway (via `author_type="ai_gateway"` and the FK to `ai_request_logs`), and surface unread count to a workspace badge — without Communication code knowing anything about Studio or OpenAI.
- Tenant isolation: cross-tenant access on any endpoint returns 404 (not 403), verified by test.
- Removing the AI Gateway module entirely leaves Communication compiling and passing tests (the FK to `ai_request_logs` is nullable and Communication does not import from AI Gateway).

## Evidence / done-definition

- Migration applied on dev DB; rollback tested.
- Pytest green for `tests/communication/`.
- DevHub progress entry per milestone, with the relevant commit SHA.
- One curl-script smoke run captured in `docs/plans/PROGRESS_REPORT_API.md`.

## Open questions (do not block start of M1)

- Message edit history: keep `edited_at` only, or full revision table? — decide before M2.
- Markdown rendering: server-side sanitize, or trust client? — decide before any UI ships.
