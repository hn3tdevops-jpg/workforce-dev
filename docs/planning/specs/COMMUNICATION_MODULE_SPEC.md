# Communication Module Spec

**Status:** Planning only. No code changes implied by this document.
**Owner workstream:** Communication.
**Depends on:** Workforce tenant + RBAC (existing, unchanged).
**Consumed by:** Studio. May also be consumed by future CRM, Hospitable Ops, and Timeline modules.

## Purpose

The Communication module is the canonical home for **human-readable, threaded interaction**
inside Workforce. It exists so that any other module (Studio today, CRM/Hospitable/Timeline
later) can attach a conversation to one of its objects without re-implementing threads,
participants, attachments, or read state.

Communication is **transport-agnostic and AI-agnostic**:

- It does not know about OpenAI, prompts, tools, or model parsing — that is the AI Gateway.
- It does not know about Studio design objects — Studio links to Communication, not the other way around.
- It does not own external delivery (email/SMS/push). Those are adapters layered on top later.

## Boundaries

Communication **owns**:

- Threads (a conversation).
- Messages (an utterance in a thread).
- Participants (who can see / post in a thread).
- Attachments (files associated with a message).
- Read state and basic thread metadata (title, last activity).

Communication **does not own**:

- AI calls or prompt logic → AI Gateway.
- Structured design artifacts (Studio nodes, layouts, generated specs) → Studio.
- Tenant accounts, roles, or auth → existing Workforce core.

## Core objects

| Object | Description |
|--------|-------------|
| `Thread` | A bounded conversation. Belongs to a tenant. Has a title, a kind, optional foreign references back to the owner module (e.g. a Studio object id), and timestamps. |
| `Participant` | A `(thread, actor)` membership. Actor can be a human user or a non-human agent (see "Author kinds" below). Carries role and read state. |
| `Message` | A single post in a thread. Has an author participant, a body, an optional structured payload, a kind, and timestamps. Immutable by default after a short edit window. |
| `Attachment` | A file linked to a message. Stored via the existing Workforce file storage layer. Mime/type, size, and a stable handle. |

## Author kinds

A `Participant` represents one of:

| Kind | Example |
|------|---------|
| `user` | A logged-in Workforce user. |
| `agent` | An AI assistant message inserted on behalf of a user/tenant (the AI Gateway is the producer, but the *participant* lives here). |
| `system` | Workforce itself posting an event into the thread (e.g. "Studio object renamed"). |

Communication stores the participant; it does **not** store why an agent message was
produced or which model produced it. That metadata lives in the AI Gateway request log and
is referenced by id from the message's structured payload when relevant.

## Message kinds

Communication is intentionally simple about what a message *is*:

| Kind | Body | Structured payload |
|------|------|--------------------|
| `text` | Markdown / plain text | none |
| `system_event` | Short human summary | optional event dict (e.g. `{"event":"renamed","from":"a","to":"b"}`) |
| `agent_response` | Rendered text from the agent | optional reference id to an AI Gateway request log entry |

Communication does **not** define new kinds for every consumer. Studio-specific semantics
(e.g. "design decision adopted") are encoded by the consumer via the structured payload, not
by inventing module-specific message kinds inside Communication.

## Public surface (conceptual)

The Communication module exposes a small, stable API to other modules:

- Create / list / get threads (scoped to tenant + participant).
- Post a message to a thread (text, system_event, or agent_response).
- Add / remove participants.
- Upload / attach a file to a message.
- Mark a thread read for a participant.

Other modules **must not** read or write Communication tables directly — they go through
this surface so that future delivery, indexing, and retention policies can change in one
place.

## Tenancy & RBAC

- Every thread, message, participant, and attachment is scoped to a tenant.
- Visibility of a thread is controlled by `Participant` membership, layered on top of
  existing Workforce role checks. A user must both have the tenant role to see the owning
  resource *and* be a participant on the thread.
- No new global roles are introduced by this spec.

## Out of scope (explicit)

- External delivery (email-out, SMS-out, push). Future adapter modules will subscribe to
  Communication events; the core module does not call out.
- Realtime transport (websockets). Communication is request/response in this spec; realtime
  is a delivery concern.
- AI behavior of any kind. The Communication module never instantiates an OpenAI client.
- Long-term message search ranking and analytics — folded into existing Workforce search /
  reporting later, not into this module.

## Non-goals

- Do **not** model "the AI conversation" as a special thread type. An agent message is just
  a message authored by an `agent` participant. The interesting AI state lives in the AI
  Gateway request log, referenced by id.
- Do **not** let Communication import from Studio or AI Gateway. Imports flow inward only:
  Studio → Communication, Studio → AI Gateway.

## Open questions (to resolve before execution section)

1. Edit / delete policy for messages (hard delete vs. tombstone).
2. Whether attachments inherit thread-level ACLs or carry their own.
3. Whether `system_event` messages count toward "unread" state.
4. Pagination contract (cursor vs. offset) for the public surface.


---

**Execution plan draft:** [`master_plan_sections/01_COMMUNICATION_EXECUTION.md`](master_plan_sections/01_COMMUNICATION_EXECUTION.md) — milestone breakdown, scope, and acceptance criteria for cutting into HN3T_MASTER_PLAN.md.
