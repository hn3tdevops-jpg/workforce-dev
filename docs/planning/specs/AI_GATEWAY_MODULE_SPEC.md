# AI Gateway Module Spec

**Status:** Planning only. No code changes implied by this document.
**Owner workstream:** AI Gateway.
**Depends on:** Workforce tenant + RBAC (existing, unchanged).
**Consumed by:** Studio today. Open to other modules later (CRM, Hospitable Ops, Timeline).

## Purpose

The AI Gateway is the **only** place in Workforce that talks to OpenAI (or any future LLM
provider). It exists so that:

- Prompt construction, tool/function-calling, response parsing, retries, and request logging
  all live in one module with one set of conventions.
- Other modules (Studio, future CRM, future Hospitable) can request structured AI work
  without each one re-implementing client wiring, schemas, error handling, or auditing.
- Cost, latency, and safety controls can be enforced in one place.

The AI Gateway is **conversation-agnostic and product-agnostic**:

- It does not own threads, messages, participants, or attachments — those are Communication.
- It does not own Studio's structured design objects — those are Studio.
- It does not decide *why* a prompt is being run; it just runs it correctly and logs it.

## Boundaries

AI Gateway **owns**:

- The OpenAI (and future provider) client wiring and credentials.
- Prompt templates and prompt assembly.
- Tool / function definitions exposed to the model.
- Parsing and validation of model output into typed Python objects.
- The request log (every call, its inputs, its outputs, its cost/latency, its outcome).
- Provider-level retries, backoff, and timeout policy.

AI Gateway **does not own**:

- Conversations or message history surfaces → Communication.
- Domain objects the AI is reasoning about → the calling module (Studio etc.).
- User-visible UI for chat → presentation layer of the calling module.

## Core objects

| Object | Description |
|--------|-------------|
| `Prompt` | A named, versioned template. Has a slug, version, role-structured template body, and declared input variables. |
| `Tool` | A function exposed to the model. Has a name, JSON schema for arguments, and a server-side handler reference. |
| `Request` | A single invocation of the gateway by a caller. Captures caller module, tenant, prompt slug/version, rendered inputs, tool list, raw model response, parsed output, status, error (if any), tokens, cost, latency. |
| `Response` | The parsed, validated, typed return value handed back to the caller. Stable shape per prompt version. |

## Public surface (conceptual)

The AI Gateway exposes a small, stable API to other modules:

- `run(prompt_slug, version, inputs, tools=..., output_schema=...) -> Response`
- `get_request(request_id)` — fetch an entry from the request log (for audit / linking).
- `list_prompts()` / `get_prompt(slug, version)` — for admin / planning surfaces.

Callers pass **typed inputs** and get back a **typed parsed object**. They never see the raw
HTTP wire format and never construct OpenAI request bodies themselves.

## Prompt + tool conventions

- Prompts are addressed by `(slug, version)`. Slug is stable; version bumps whenever the
  prompt body, tool surface, or expected output schema changes.
- A prompt declares its inputs explicitly. The gateway refuses to render a prompt with
  missing or unknown variables.
- A prompt declares the schema of its parsed output. The gateway validates against that
  schema before returning to the caller and records validation failures in the request log.
- Tools are global to the gateway, not per-prompt. A prompt opts in to a subset of tools.

## Request log

Every call produces exactly one `Request` row. The log records:

- Caller module (e.g. `studio`), tenant id, user id (if applicable).
- Prompt slug, prompt version.
- Rendered system / user / tool messages (or a hash + retention pointer, depending on
  retention policy decided later).
- Tools offered and tools actually invoked.
- Raw model response and parsed output (or parse error).
- Tokens, cost estimate, latency, provider, model.
- Status: `ok`, `parse_error`, `tool_error`, `provider_error`, `timeout`, `validation_error`.

The request log is the **only** source of truth for "what did the AI do and why" for the
whole product. Other modules that want to refer to an AI action store the request id, not a
copy of the prompt or response.

## Tenancy & RBAC

- Every request is scoped to the calling tenant. The gateway refuses requests without a
  tenant context.
- The gateway honors existing Workforce role checks via the caller: the caller is
  responsible for confirming the user is allowed to perform the action; the gateway is
  responsible for not leaking other tenants' data into prompts and for tagging the log row
  correctly.
- No new global roles are introduced by this spec. Admin-only surfaces (prompt management,
  request log viewer) reuse existing admin roles.

## Failure modes & policy

| Failure | Behavior |
|---------|----------|
| Provider timeout | Configurable retry with backoff, capped. Logged as `timeout` if exhausted. |
| Provider error (5xx, rate limit) | Retry with backoff. Logged with provider error code. |
| Tool invocation error | Returned to model up to a configurable max tool-loop depth. Logged as `tool_error` if the loop is exhausted without a final response. |
| Parse / schema validation error | Logged as `parse_error` / `validation_error`. Caller receives a typed error, **not** a partially-parsed response. |
| Missing prompt slug/version | Hard error; never silently falls back to a different version. |

## Out of scope (explicit)

- Storing user-visible chat history. The gateway logs *requests*, not conversations. If a
  caller wants the user to see the agent's reply, the caller persists an `agent_response`
  message via Communication and links it to a request id.
- UI for chatting with the model. That is the calling module's responsibility (e.g. Studio).
- Provider fan-out / model routing policy. v1 targets a single provider; multi-provider
  routing is a later spec.
- Embeddings / vector search. Separate spec when needed.

## Non-goals

- Do **not** let the AI Gateway import from Studio, Communication, or any product module.
  Imports flow inward only: Studio → AI Gateway.
- Do **not** model conversations inside the gateway. A multi-turn "conversation with the
  agent" is a sequence of `Request` rows linked from the outside by the caller (typically a
  Communication thread). The gateway itself is stateless across calls.

## Open questions (to resolve before execution section)

1. Retention policy for raw prompt/response payloads (full vs. hashed + redacted).
2. Per-tenant cost caps and how the gateway signals "over budget" to callers.
3. Whether tool handlers live inside the AI Gateway module or are registered by callers at
   startup (leaning toward registry, so Studio owns its own tool implementations).
4. Streaming responses — supported in v1 or deferred to a follow-up spec.


---

**Execution plan draft:** [`master_plan_sections/02_AI_GATEWAY_EXECUTION.md`](master_plan_sections/02_AI_GATEWAY_EXECUTION.md) — milestone breakdown, scope, and acceptance criteria for cutting into HN3T_MASTER_PLAN.md.
