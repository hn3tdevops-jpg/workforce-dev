# Studio AI Integration Spec

**Status:** Planning only. No code changes implied by this document.
**Owner workstream:** Studio.
**Depends on:**
- Workforce tenant + RBAC (existing, unchanged).
- [`COMMUNICATION_MODULE_SPEC.md`](COMMUNICATION_MODULE_SPEC.md)
- [`AI_GATEWAY_MODULE_SPEC.md`](AI_GATEWAY_MODULE_SPEC.md)

## Purpose

Studio is where humans (and the AI, on their behalf) shape **structured design objects**
inside Workforce — layouts, widget configurations, generated specs, and similar artifacts
that are richer than free-form text but smaller than full app code.

This spec describes how Studio integrates with the two adjacent modules:

- Studio uses **Communication** for human-readable, threaded interaction *about* a design
  object.
- Studio uses the **AI Gateway** to actually drive any LLM work (analysis, generation,
  refactor suggestions, parsing of user intent).

Studio is the **only** module in this pack that is allowed to compose Communication and AI
Gateway together. Communication and AI Gateway must not depend on each other and must not
depend on Studio.

## Boundaries

Studio **owns**:

- Studio design objects (the structured artifacts being authored) and their versions.
- The mapping from a design object → its Communication thread (one canonical thread per
  object, plus optional side threads).
- The mapping from a design object change → the AI Gateway request that produced or
  reviewed it.
- Studio-specific prompts, tools, and parsed-output schemas registered with the AI Gateway.
- Studio UI surfaces (canvas, inspector, side panel chat).

Studio **does not own**:

- Threads, messages, participants, attachments → Communication.
- OpenAI client, prompt templates as infrastructure, request logs → AI Gateway.
- Tenant / RBAC primitives → existing Workforce core.

## Object model (Studio side only)

| Object | Description |
|--------|-------------|
| `StudioObject` | The artifact being designed. Tenant-scoped. Has a kind, a current version, and a stable id. |
| `StudioObjectVersion` | An immutable snapshot of a `StudioObject` at a point in time. The structured payload lives here. |
| `StudioObjectThreadLink` | One-to-one mapping from a `StudioObject` to its canonical Communication `Thread`. Optional additional links for side conversations (review, decision log). |
| `StudioObjectAIAction` | A record that this `StudioObjectVersion` was produced or modified via an AI Gateway call. Stores the AI Gateway `Request` id, the calling prompt slug/version, and a short human label ("rename suggestion", "layout refactor"). |

Studio does **not** duplicate Communication data (no copy of messages) and does **not**
duplicate AI Gateway data (no copy of prompts or raw model responses). It only stores ids
that point at them.

## Flow: human asks the AI to do something to a Studio object

This is the canonical integration shape. It is the only path Studio uses to combine the two
modules.

1. **User posts in the Studio object's thread** via Communication (a normal `text` message
   authored by a `user` participant). Nothing AI-specific has happened yet.
2. **Studio reads the new message** and decides whether it represents an AI request. (This
   decision is Studio's, not Communication's.)
3. **Studio calls the AI Gateway** with a Studio-registered prompt slug, passing:
   - the current `StudioObjectVersion` payload,
   - the relevant slice of thread context,
   - the tools Studio wants to expose for this prompt.
4. **AI Gateway** runs the call, validates the parsed output against the prompt's declared
   schema, and returns a typed `Response` plus a `Request` id. It writes its own request log
   row independently.
5. **Studio applies the response**:
   - if it produced a new design state, Studio creates a new `StudioObjectVersion` and a
     matching `StudioObjectAIAction` linking to the AI Gateway `Request` id;
   - it then posts an `agent_response` message back into the same Communication thread,
     authored by an `agent` participant, with the rendered text body and a structured
     payload that references the AI Gateway `Request` id (and, when applicable, the new
     `StudioObjectVersion` id).
6. **User sees the reply in their thread** like any other message. The fact that the AI
   was involved is metadata on the message, not a separate UI surface.

### Import direction

```
studio/  ─► communication/   (allowed)
studio/  ─► ai_gateway/      (allowed)

communication/  ──╳──  ai_gateway/   (forbidden in either direction)
communication/  ──╳──  studio/       (forbidden)
ai_gateway/     ──╳──  studio/       (forbidden)
```

Any change that introduces an import in a forbidden direction is a spec violation and must
be reworked.

## Tools and prompts

- Studio registers its own prompts with the AI Gateway by slug, e.g.
  `studio.rename_object`, `studio.suggest_layout`, `studio.review_change`. Versioning,
  rendering, and validation are handled entirely by the AI Gateway per its own spec.
- Studio registers its own tool handlers (e.g. "fetch related Studio objects",
  "preview a proposed version") with the AI Gateway's tool registry. The tool's *handler
  code* lives in Studio, but the gateway is what offers it to the model and routes the call.
- Studio prompts must declare typed output schemas. Studio refuses to apply an AI response
  that does not parse — it surfaces the failure as an `agent_response` message with a clear
  error body, and does not create a new `StudioObjectVersion`.

## Tenancy & RBAC

- Every Studio object, thread link, and AI action is scoped to a tenant.
- A user can only trigger AI actions on a Studio object if they already have permission to
  edit that object under existing Workforce role checks. Studio is responsible for the
  permission check before calling the AI Gateway.
- The AI Gateway is responsible for tagging its own log row with the calling tenant /
  user / module; Studio is responsible for passing them.
- No new global roles are introduced by this spec.

## Audit story

For any change to a Studio object, the following chain must be reconstructible:

```
StudioObjectVersion
  └─► StudioObjectAIAction (optional, present iff AI was involved)
        └─► AI Gateway Request  (full prompt, model, tokens, parsed output)
  └─► Communication Message(s) on the linked Thread
        └─► (agent_response messages carry the AI Gateway Request id)
```

This is the explicit reason the three modules exist as separate concerns: any single row in
this chain can be retained, redacted, or expired according to its own module's policy
without breaking the others.

## Out of scope (explicit)

- Realtime collaborative editing on Studio objects. Separate spec when needed.
- Agent-initiated work that is not in response to a user message in a thread (e.g.
  scheduled "review my designs nightly"). Possible later, but must still go through the AI
  Gateway and post results via Communication; it does not get to bypass either module.
- External delivery of AI-produced Studio summaries (email digest, etc.). That belongs to a
  future delivery adapter on top of Communication.

## Non-goals

- Do **not** let Studio store a copy of prompts or raw model output. It stores the AI
  Gateway `Request` id and re-fetches when needed.
- Do **not** let Studio bypass Communication for "AI side-channel" messages. Every
  user-visible agent reply about a Studio object goes through Communication as a normal
  message authored by an `agent` participant.
- Do **not** introduce a "Studio-only" thread type inside Communication. The thread is a
  normal thread; the link from object → thread lives on the Studio side.

## Open questions (to resolve before execution section)

1. Whether every `StudioObjectVersion` change must be tied to a Communication message (for
   audit symmetry), or only those produced via the AI path.
2. How aggressively Studio batches AI calls when a user posts multiple messages quickly.
3. UI placement of the AI Gateway `Request` id (visible in agent message metadata only, or
   surfaced as a "view full prompt" affordance for admins).
4. Conflict policy when an AI action proposes a new version concurrent with a human edit.


---

**Execution plan draft:** [`master_plan_sections/03_STUDIO_AI_INTEGRATION_EXECUTION.md`](master_plan_sections/03_STUDIO_AI_INTEGRATION_EXECUTION.md) — milestone breakdown, scope, and acceptance criteria for cutting into HN3T_MASTER_PLAN.md.
