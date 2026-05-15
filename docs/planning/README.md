# Workforce Planning Docs

This directory holds **planning-only** material for the Workforce project. Nothing here
is implementation; nothing here changes the running services. These files exist so that
future work can be lifted cleanly into `HN3T_MASTER_PLAN.md` execution sections without
re-deriving the architecture each time.

## Layout

```
docs/planning/
  README.md                                    ← this file
  WORKFORCE_CONSOLIDATED_MASTER_PLAN_2026-04-17.md   ← top-level synthesis
  specs/        ← module-level architecture specs (one per workstream)
  roadmaps/     ← time-ordered implementation roadmaps
  deployment/   ← server / runtime boundary plans (PythonAnywhere etc.)
  groundtruth/  ← human↔AI collaboration protocol, Copilot prompts
```

## Top-level reference

- [`WORKFORCE_CONSOLIDATED_MASTER_PLAN_2026-04-17.md`](WORKFORCE_CONSOLIDATED_MASTER_PLAN_2026-04-17.md) —
  consolidated synthesis of the canonical master plan, UI roadmap, identity/RBAC
  reference, planning-pack reference, AI widget plan, server-boundary reference, and
  prompt-pack guidance. Use as the entry point for new contributors and as the source
  of truth when an open module spec needs platform-level grounding.

## Specs (module architecture, planning-only)

The three specs below cover closely related but **independent** workstreams. They must
stay separate — Communication, AI Gateway, and Studio are different modules with
different owners and different lifecycles.

- [`specs/COMMUNICATION_MODULE_SPEC.md`](specs/COMMUNICATION_MODULE_SPEC.md) — threads,
  messages, participants, attachments. Transport- and AI-agnostic.
  - [`specs/master_plan_sections/01_COMMUNICATION_EXECUTION.md`](specs/master_plan_sections/01_COMMUNICATION_EXECUTION.md) — Communication module rollout (M1–M4). Precondition for Studio AI.
- [`specs/AI_GATEWAY_MODULE_SPEC.md`](specs/AI_GATEWAY_MODULE_SPEC.md) — the only
  module allowed to talk to OpenAI. Owns prompts, tools, parsing, and request logs.
  Conversation- and product-agnostic.
  - [`specs/master_plan_sections/02_AI_GATEWAY_EXECUTION.md`](specs/master_plan_sections/02_AI_GATEWAY_EXECUTION.md) — AI Gateway rollout (M1–M4). Can land in parallel with Communication M1.
- [`specs/STUDIO_AI_INTEGRATION_SPEC.md`](specs/STUDIO_AI_INTEGRATION_SPEC.md) —
  structured design objects. Consumes Communication and AI Gateway. Only module
  allowed to compose them.
  - [`specs/master_plan_sections/03_STUDIO_AI_INTEGRATION_EXECUTION.md`](specs/master_plan_sections/03_STUDIO_AI_INTEGRATION_EXECUTION.md) — Studio AI integration (M1–M4). Depends on Communication M1 + AI Gateway M1+M2.

**Dependency direction (do not violate):**
`studio → communication`, `studio → ai_gateway`. No other crossings allowed.

### Master-plan execution sections (drafts)

Drafts of HN3T_MASTER_PLAN sections derived from the specs above. Cut-and-paste
into the backend repo's `docs/plans/HN3T_MASTER_PLAN.md` when ready; they are
intentionally self-contained so they survive the move.

- [`specs/master_plan_sections/01_COMMUNICATION_EXECUTION.md`](specs/master_plan_sections/01_COMMUNICATION_EXECUTION.md) — Communication module rollout (M1–M4). Precondition for Studio AI.
- [`specs/master_plan_sections/02_AI_GATEWAY_EXECUTION.md`](specs/master_plan_sections/02_AI_GATEWAY_EXECUTION.md) — AI Gateway rollout (M1–M4). Can land in parallel with Communication M1.
- [`specs/master_plan_sections/03_STUDIO_AI_INTEGRATION_EXECUTION.md`](specs/master_plan_sections/03_STUDIO_AI_INTEGRATION_EXECUTION.md) — Studio AI integration (M1–M4). Depends on Communication M1 + AI Gateway M1+M2.

## Roadmaps

- [`roadmaps/WORKFORCE_UI_MERGED_ROADMAP.md`](roadmaps/WORKFORCE_UI_MERGED_ROADMAP.md) —
  merged UI implementation roadmap (April 2026). Defines phase order (Phase 0 stabilise
  → Phase 8 advanced widget builder), the `app/(console)/*` route-group resolution, the
  `/api/v1/bootstrap/session` contract, and the first-patch scope. Pair with the
  consolidated master plan's "Workforce Web UI Plan" section.

## Deployment / runtime boundaries

- [`deployment/PYTHONANYWHERE_SERVER_REORG.md`](deployment/PYTHONANYWHERE_SERVER_REORG.md) —
  Copilot prompt for the PythonAnywhere host reorganisation. Establishes backend / frontend /
  admin-dev tooling boundaries, the `wf-hn3t.pythonanywhere.com` frontend responsibility,
  and OpenAI/Copilot placement rules. Six-phase procedure with explicit non-negotiables.
- Companion script: [`scripts/admin/pa_inventory.sh`](../../scripts/admin/pa_inventory.sh) —
  read-only Phase 1 inventory generator. Copy to PythonAnywhere and run there; writes a
  timestamped Markdown report into `~/dev_hub/reports/server_reorg/`. Never moves or
  deletes anything.

## Groundtruth — human↔AI collaboration

- [`groundtruth/GROUNDTRUTH_AI_COLLABORATION_SYSTEM.md`](groundtruth/GROUNDTRUTH_AI_COLLABORATION_SYSTEM.md) —
  full collaboration system: reusable task template, Workforce operating protocol,
  ownership model, project invariants, five-layer architecture (Identity / Context /
  Execution / Quality / Memory), continuity layer, and Dev Hub page concept.
- [`groundtruth/COPILOT_INSTRUCTION_BLOCK.md`](groundtruth/COPILOT_INSTRUCTION_BLOCK.md) —
  canonical Copilot execution-mode block. Paste this into a Copilot task or repo
  instruction file when you want Groundtruth-style execution.
- [`/.github/copilot-instructions.md`](../../.github/copilot-instructions.md) — repo-level
  mirror so GitHub Copilot picks it up automatically. If you edit either copy, mirror
  the other.

## Conventions

1. **Planning only.** Nothing in this tree implies code, migrations, or runtime changes.
   Implementation happens via `HN3T_MASTER_PLAN.md` execution sections elsewhere.
2. **Tenant / RBAC inherited.** Every spec assumes the existing Workforce tenant +
   business + location scoping and the existing role system. No new auth surfaces
   introduced here.
3. **Boundaries are load-bearing.** Module specs explicitly enumerate what they do
   **not** own. Future modules should add their own spec rather than collapsing into a
   neighbour.
4. **Additive edits.** Prefer adding a sibling document over rewriting an existing one;
   revoke or supersede explicitly when the project direction changes.
