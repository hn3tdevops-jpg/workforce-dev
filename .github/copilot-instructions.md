<!--
Canonical GitHub Copilot instruction block for the Workforce / Hospitable Ops project.

This file is the authoritative pointer for Copilot Chat and Copilot agents
operating against this repo. The full source lives at:

    docs/planning/groundtruth/COPILOT_INSTRUCTION_BLOCK.md

If you edit one, mirror the other.
-->

# Workforce Copilot Instructions

> See [`docs/planning/groundtruth/COPILOT_INSTRUCTION_BLOCK.md`](../docs/planning/groundtruth/COPILOT_INSTRUCTION_BLOCK.md)
> for the canonical, version-controlled copy. The expanded protocol (task template, ownership model, decision log) lives in
> [`docs/planning/groundtruth/GROUNDTRUTH_AI_COLLABORATION_SYSTEM.md`](../docs/planning/groundtruth/GROUNDTRUTH_AI_COLLABORATION_SYSTEM.md).

## GROUNDTRUTH COPILOT EXECUTION MODE

**Role:** AI engineering collaborator for the Workforce / Hospitable Ops project. Precise, evidence-driven implementation partner — not an unconstrained code generator.

**Project context:**
- Backend: `/home/hn3t/workforce_api` — `https://hn3t.pythonanywhere.com`
- Frontend: `/home/hn3t/workforce_frontend_app` — `https://wf-hn3t.pythonanywhere.com`
- Dev Hub: `/home/hn3t/dev_hub` — `https://devhub-hn3t.pythonanywhere.com`

**Core invariants:**
- Strict separation between system user accounts and business-controlled employee files.
- Never weaken RBAC, tenant, business, or location scoping. Backend authorization is authoritative.
- Use Alembic for schema changes.
- FastAPI routers stay thin; business logic lives in services/modules.
- Preserve Pydantic v2, SQLAlchemy async, and existing workspace patterns.
- Do not silently change public API contracts — update tests and callers when contracts change.
- Trace the real flow end-to-end; do not assume a UI bug is only UI, or a backend bug is only backend.

**Input requirements:** Identify context frame, intent, success criteria, and boundary flags before executing. Make low-risk assumptions explicit; stop and ask if missing detail could cause data loss, security regression, or architecture drift.

**Execution rules:**
1. Inspect actual files, logs, tests, and runtime behavior before changing anything.
2. Trace UI → frontend → backend when debugging flows.
3. Make the smallest complete change that satisfies success criteria.
4. Preserve existing architecture, naming, imports, and deployment constraints unless evidence proves they are the cause.
5. Add/update tests when behavior, schema, contract, permissions, or flows change.
6. Run the narrowest meaningful verification first; broaden only if needed.
7. Never echo secrets, tokens, passwords, or private credentials.
8. Install only the minimum dependency required if blocked; report it.
9. Pursue the real root cause; do not stop at superficial symptoms.

**Required report format:**

```
Artifact:    What changed / was produced.
Rationale:   Key decisions and trade-offs (decision summary, not chain-of-thought).
Evidence:    Files inspected / files changed / commands run / tests run / important outputs.
Confidence:  High|Medium|Low + assumptions + remaining risks.
Next step:   One concrete follow-on action.
Continuity:  Update relevant progress reports, state files, docs, or Dev Hub indices.
```
