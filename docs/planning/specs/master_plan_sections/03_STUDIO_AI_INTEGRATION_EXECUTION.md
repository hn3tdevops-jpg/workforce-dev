<!--
HN3T_MASTER_PLAN execution section — Studio AI integration.

Status: draft, intended to be cut-and-pasted into the backend repo's
`docs/plans/HN3T_MASTER_PLAN.md` as a new top-level section. Authored from
`docs/planning/specs/STUDIO_AI_INTEGRATION_SPEC.md`. Numbered "03" because it
depends on Communication M1 and AI Gateway M1+M2 being green.
-->

# Studio AI Integration — Execution Plan

**Spec reference:** [`../STUDIO_AI_INTEGRATION_SPEC.md`](../STUDIO_AI_INTEGRATION_SPEC.md)
**Workstream owner:** Studio
**Depends on:**
- Communication module section, **M1 minimum** (threads + messages).
- AI Gateway module section, **M1 + M2 minimum** (`run_prompt` + prompt registry).
- Existing Studio design-object tables (no migration in this section to those tables).

## Goal

Wire Studio's structured design objects to the two adjacent modules so a user
can: open a design, chat about it in a real thread, and ask the AI to propose
structured changes to the design — without Studio ever calling OpenAI directly
or re-implementing threading.

## Non-goals (this section)

- No new core design-object schema. Studio's own model stays as-is.
- No new transport (still HTTP/polling).
- No multi-design batch operations.
- No "agent" that runs unattended — every AI action is initiated by an explicit user message.

## Scope

In-scope tables (new, scoped to Studio):

- `studio_design_threads` — design_id, thread_id (FK to `comm_threads`), created_at. Enforces 1:1 between a design and its conversation thread.
- `studio_ai_proposals` — id, design_id, request_log_id (FK to `ai_request_logs`), proposed_patch_json, status ("pending"|"applied"|"rejected"|"superseded"), reviewed_by, reviewed_at, applied_revision_id

In-scope prompts (registered in AI Gateway, owned by Studio):

- `studio.intent_to_layout` — v1. Input: design snapshot + user message. Output: a JSON patch against the design schema, plus a short natural-language summary.
- `studio.explain_design` — v1. Input: design snapshot + user question. Output: a markdown answer; no patch.

In-scope HTTP surface (under existing `/api/v1`):

- `GET  /api/v1/studio/designs/:id/thread` — returns or lazily creates the linked thread; delegates to Communication for the actual messages.
- `POST /api/v1/studio/designs/:id/ai/propose` — body: `{ user_message_id }`. Calls AI Gateway `run_prompt(slug="studio.intent_to_layout", ...)`. Writes a `studio_ai_proposals` row. Posts a Communication message with `author_type="ai_gateway"` and `ai_request_log_id` set. Returns the proposal id.
- `POST /api/v1/studio/designs/:id/ai/proposals/:pid/apply` — applies the patch atomically; creates a new design revision; marks the proposal `applied`.
- `POST /api/v1/studio/designs/:id/ai/proposals/:pid/reject` — marks the proposal `rejected`.

## Milestones

### M1 — Thread per design (no AI yet)

- Migration for `studio_design_threads`.
- `GET /thread` endpoint lazily creates a thread via Communication's service API the first time it's hit.
- Communication's permission resolver is registered to consult Studio's existing design-level RBAC for `subject_type="studio_design"`.
- Pytest: two users with different design access see appropriately scoped threads (or 404).

### M2 — AI propose, no apply

- `studio.intent_to_layout` v1 and `studio.explain_design` v1 registered via migration data.
- `/ai/propose` endpoint wired through AI Gateway. The AI's response shows up in the thread as a normal message; the patch lives on the proposal row, not in the message body.
- UI (or scripted) check: a human user types a message, hits "Ask AI", sees the AI's reply + a "Review proposal" affordance.

### M3 — Apply / reject with revision history

- `apply` performs the patch inside a single DB transaction with a new design-revision row; on schema-validation failure it rolls back and marks the proposal `superseded` with the validation error captured.
- `reject` is a one-shot state change.
- A second `propose` call against the same design supersedes any still-pending proposal (only one pending at a time).

### M4 — Explain-only flow

- `/ai/propose` routes to `studio.explain_design` when the request body has `mode="explain"`; no proposal row, just a thread message.

## Acceptance criteria (whole section)

- `grep -rn "import openai" apps/api/studio/ services/studio/` returns zero hits.
- A design can be deleted and:
  - the linked Communication thread is archived (not hard-deleted) via `comm.archive_for_subject`,
  - the `ai_request_logs` rows referenced by its proposals stay intact (audit is preserved),
  - `studio_ai_proposals` rows survive but cannot be applied (design is gone).
- Replaying an AI proposal from `ai_request_logs` alone produces an identical `proposed_patch_json` (modulo timestamps), proving Studio holds no hidden AI state.
- Communication and AI Gateway test suites both stay green when run without Studio installed.

## Evidence / done-definition

- Migration applied; rollback tested.
- Pytest green for `tests/studio/ai_integration/`.
- One end-to-end captured trace in `docs/plans/PROGRESS_REPORT_API.md`: user message → `/ai/propose` → AI Gateway log row → Communication message → proposal row → `/apply` → new design revision.
- DevHub progress entry per milestone.

## Open questions (do not block start of M1)

- Proposal preview UI vs. inline diff in the thread — Studio frontend decision, doesn't gate backend M2.
- Should `studio.intent_to_layout` v1 be allowed to call tools (e.g. `lookup_component`), or is v1 strictly schema-out? Decide before registering the prompt — defaulting to **no tools in v1** unless a clear need surfaces.
