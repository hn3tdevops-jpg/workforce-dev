<!--
HN3T_MASTER_PLAN execution section — AI Gateway module.

Status: draft, intended to be cut-and-pasted into the backend repo's
`docs/plans/HN3T_MASTER_PLAN.md` as a new top-level section. Authored from
`docs/planning/specs/AI_GATEWAY_MODULE_SPEC.md`. Numbered "02" because it can
land in parallel with M1 of the Communication section but is required before
Studio AI integration can start.
-->

# AI Gateway Module — Execution Plan

**Spec reference:** [`../AI_GATEWAY_MODULE_SPEC.md`](../AI_GATEWAY_MODULE_SPEC.md)
**Workstream owner:** AI Gateway
**Precedes:** Studio AI integration (cannot ship without at least M1 + M2 here)
**Depends on:** tenant + RBAC (existing), `OPENAI_API_KEY` secret in env

## Goal

Be the single chokepoint for all LLM traffic out of Workforce. Other modules
(Studio first) get a typed, schema-validated, audited call surface; nobody else
imports the `openai` SDK.

## Non-goals (this section)

- No conversation/thread model — Communication owns that.
- No domain knowledge of Studio designs, CRM contacts, or Hospitable units.
- No model routing / cost optimisation logic in M1. Pinned single model is fine.
- No streaming responses in M1.

## Scope

In-scope tables (new, tenant-scoped):

- `ai_prompts` — id, slug, version, body_template, input_schema_json, output_schema_json, tools_json, created_at, created_by, retired_at. **Append-only** — new versions never overwrite.
- `ai_request_logs` — id, tenant_id, prompt_slug, prompt_version, caller_module, caller_subject_type, caller_subject_id, user_id, model, request_payload_json, response_payload_json, parsed_output_json, error_code, error_detail, latency_ms, prompt_tokens, completion_tokens, total_cost_usd, started_at, finished_at

In-scope service surface (Python, **not** HTTP — this is an internal module):

```python
# services/ai_gateway/__init__.py
def run_prompt(
    *,
    slug: str,
    version: int | None,        # None = latest non-retired
    input: dict,                # validated against prompt.input_schema_json
    tenant_id: int,
    user_id: int | None,
    caller_module: str,         # e.g. "studio"
    caller_subject_type: str | None,
    caller_subject_id: int | None,
) -> AIGatewayResult: ...
```

`AIGatewayResult` has: `parsed_output`, `request_log_id`, `model`, `usage`, `error` (None on success).

In-scope admin HTTP surface (`/api/v1/ai/admin/...`, superadmin-only):

- `GET  /prompts` — list slugs + versions
- `GET  /prompts/:slug` — current + history
- `POST /prompts` — register a new prompt version (body: template, input_schema, output_schema, tools)
- `POST /prompts/:slug/retire`
- `GET  /request-logs?caller_module=&prompt_slug=&since=&until=&limit=` — paginated audit

No general user-facing HTTP endpoint. Other modules call `run_prompt` in-process.

## Milestones

### M1 — Synchronous, single-prompt happy path

- Tables + migrations.
- `run_prompt` implementation that: validates input against schema → renders template → calls OpenAI → parses response against output schema → writes a row to `ai_request_logs` (success or failure) → returns result.
- Retries: 2 attempts with exponential backoff on rate-limit / 5xx; no retry on schema-validation failure.
- Failures are first-class: schema-violation, openai-error, parse-error, and timeout each get a distinct `error_code` in the log.
- Pytest with a mocked OpenAI client; no real network in CI.
- One canary prompt registered via migration: `slug="canary.echo"`, version 1, that round-trips a string. Used by the smoke-test endpoint below.

### M2 — Prompt registry + admin surface

- Admin HTTP endpoints above, superadmin-only.
- Prompt versions are immutable once written; "edit" = new version.
- DevHub progress entry on every prompt registration.

### M3 — Tool/function calling

- `tools_json` on prompts is now honoured.
- Tool handlers are registered in code via a decorator; the registry is checked at prompt-registration time so admins can't ship a prompt that references an unregistered tool.
- Tool calls + their results are captured inside `request_payload_json` / `response_payload_json` so the full trace is preserved.

### M4 — Cost and rate caps

- Per-tenant daily token + USD ceilings, configurable, enforced before the OpenAI call.
- Soft-warn at 80 %, hard-stop at 100 % with a `tenant_quota_exceeded` error.
- Surface remaining quota in the admin request-logs view.

## Acceptance criteria (whole section)

- A single `grep -rn "import openai" services/ apps/api/` returns exactly one hit: `services/ai_gateway/_openai_client.py`. No other module imports the SDK.
- Every successful and failed AI call is replayable from `ai_request_logs` (request payload + prompt version + parsed output stored).
- A Studio test calls `run_prompt(slug="studio.intent_to_layout", ...)` end-to-end against a mocked OpenAI client and inserts an `ai_request_logs` row in the same transaction it returned from.
- Removing Communication does not break AI Gateway compilation or tests.

## Evidence / done-definition

- Migration applied on dev DB; rollback tested.
- Pytest green for `tests/ai_gateway/`, including schema-violation and timeout paths.
- Admin UI (or curl scripts) demonstrated end-to-end: register prompt → call it → see the request log entry.
- DevHub progress entry per milestone.

## Open questions (do not block start of M1)

- Where do prompt templates live in source — DB-only, or also as files under `services/ai_gateway/prompts/` synced via management command? Decide before M2.
- Streaming: defer to a post-M4 milestone unless Studio explicitly needs it.
