<!-- Installed via DevHub feature-doc intake.
Original filename: Groundtruth_Workforce_AI_Collaboration_System.md
Installed at: 2026-05-15T15:24:26Z
This is a planning/reference document. Do not edit casually; revise via PR. -->

# Groundtruth Workforce AI Collaboration System

**Purpose:** Turn the Groundtruth Integration Brief into practical working assets for Workforce, Dev Hub, ChatGPT, and Copilot execution.

**Source note:** Adapted from Groundtruth Integration Brief - Human-AI Collaboration Protocol v1.0, prepared by Casey Patterson, May 2026.

**Operating principle:** The human brings clarity of intent; the AI collaborator brings precision of execution. Every session should continue the work rather than restart it.

---

## 1. Reusable AI Task Template

Use this template whenever you want a high-quality AI or Copilot handoff. It is designed to prevent vague outputs, lost context, and incomplete execution.

```text
GROUNDTRUTH TASK SUBMISSION

Context Frame:
- Project/workstream:
- Current state:
- Relevant files, URLs, repositories, screenshots, logs, or docs:
- Known constraints:
- Prior decisions that must be preserved:

Intent Statement:
- I want to accomplish:
- The reason this matters is:
- The final output should help me:

Success Criteria:
- Done means:
- Evidence I expect to see:
- Tests, checks, links, screenshots, commands, or files that should prove success:

Boundary Flags:
- Do not change:
- Do not assume:
- Scope limits:
- Tone/audience/format requirements:
- Security or permission limits:

Execution Request:
- First inspect the real current state.
- Make the smallest complete change that satisfies the success criteria.
- Preserve existing architecture and naming conventions.
- Report assumptions, exact files touched, exact commands run, and verification results.

Required Output:
1. Artifact or completed change
2. Brief rationale for key choices and trade-offs
3. Confidence signal with assumptions and remaining risks
4. Recommended next step
```

### Compact version

```text
Use Groundtruth mode. Context: [project/state/files]. Intent: [desired outcome and why]. Success: [observable done criteria]. Boundaries: [scope limits, no-go areas, format]. Execute with bias toward action, but inspect real files first, preserve existing architecture, and report artifact, rationale, confidence, evidence, and next step.
```

### Workforce example

```text
GROUNDTRUTH TASK SUBMISSION

Context Frame:
- Project/workstream: Workforce API auth and membership flow.
- Current state: Backend runs from /home/hn3t/workforce_api and frontend from /home/hn3t/workforce_frontend_app. Login problems have previously involved auth-success-but-no-workspace-context, not just password validation.
- Relevant files: apps/api/app/api/v1/endpoints/auth.py, apps/api/app/services/rbac_service.py, Alembic migrations, frontend auth context and API client.
- Known constraints: Preserve tenant, business, location, employee-file, and system-user separation.

Intent Statement:
- Identify and fix the real cause of the login/membership failure.
- The final result should make login and /auth/me work for a valid user with active membership data.

Success Criteria:
- Exact failing endpoint is identified.
- Exact condition producing the error is shown.
- Data-model requirement is documented.
- Migration or data fix is applied only if evidence supports it.
- Targeted tests pass.
- API reproduction commands and responses are reported.

Boundary Flags:
- Do not bypass RBAC.
- Do not treat it as a password issue unless evidence proves it.
- Do not silently change public API contracts.
- Do not conflate system users with employee files.

Required Output:
- Artifact/change summary, rationale, confidence, evidence, and next step.
```

---

## 2. Workforce Project Operating Protocol

### 2.1 Mission

The Workforce project operating protocol applies Groundtruth to ongoing engineering work across the Workforce backend, Workforce frontend, and Dev Hub. Its purpose is to keep AI-assisted development accurate, traceable, and continuous across sessions.

### 2.2 Scope

This protocol covers:

- Backend work in `/home/hn3t/workforce_api`
- Frontend work in `/home/hn3t/workforce_frontend_app`
- Dev Hub work in `/home/hn3t/dev_hub`
- Documentation, runbooks, Copilot prompts, progress reports, and project dashboards
- Auth, RBAC, employee linkage, business/location scoping, package management, and deployment workflows

### 2.3 Ownership model

| Area | Human operator owns | AI collaborator owns |
|---|---|---|
| Intent | Business goal, priority, acceptable trade-offs | Clarifying ambiguous goals when necessary |
| Architecture | Final approval of model and product direction | Implementation options and risk analysis |
| Execution | Permission to change scope, deploy, or use secrets | Code changes, tests, docs, and reports within boundaries |
| Quality | Acceptance of done state | Verification, evidence, and regression checks |
| Continuity | Correction of stored assumptions | Maintaining project context and decision history |

### 2.4 Non-negotiable project invariants

- Preserve strict separation between system user accounts and business-controlled employee files.
- Do not weaken RBAC, tenant scoping, business scoping, or location scoping.
- Keep backend authorization authoritative; do not rely only on frontend hiding or disabling UI.
- Use Alembic for schema changes; do not patch database structure ad hoc.
- Keep FastAPI routers thin and place business logic in services/modules.
- Preserve Pydantic v2 and SQLAlchemy async patterns already used by the backend.
- Do not silently change public API contracts without updating tests and dependent frontend code.
- Keep frontend build/deploy assumptions explicit, including API base URL, base path, and production-vs-dev behavior.
- Treat PythonAnywhere WSGI/ASGI deployment details as operational constraints, not incidental implementation details.

### 2.5 Standard work cycle

1. **Frame the task.** Capture context, intent, success criteria, and boundaries.
2. **Inspect the real state.** Read the actual code, logs, docs, current branch, and relevant tests.
3. **Plan the smallest complete change.** Avoid broad rewrites unless the user explicitly asks for a redesign.
4. **Execute safely.** Modify only the files required to satisfy the success criteria.
5. **Verify.** Run targeted tests, build checks, curl checks, or browser checks appropriate to the change.
6. **Report.** Provide artifact, rationale, confidence, evidence, risks, and next step.
7. **Update continuity.** Record important decisions in progress reports, state files, docs, or Dev Hub indices.

### 2.6 Required deliverable format for engineering tasks

```text
Artifact:
- What changed or what was produced.

Rationale:
- Brief decision summary explaining why this approach was chosen.

Evidence:
- Files inspected.
- Files changed.
- Commands run.
- Tests/checks performed.
- Key outputs or status codes.

Confidence:
- High / Medium / Low.
- Assumptions.
- Remaining risks.

Next Step:
- One recommended follow-on action.
```

### 2.7 Continuity records

Use these continuity anchors when a task affects the broader project:

- Backend plan/progress: `docs/plans/HN3T_MASTER_PLAN.md`, `docs/plans/PROGRESS_REPORT_API.md`, `.copilot_exec/state.json`
- Frontend plan/progress: `docs/plans/HN3T_MASTER_PLAN.md`, `docs/ADMIN/frontend/PROGRESS_REPORT_FRONTEND.md`, `.copilot_frontend/state.json`
- Dev Hub state/docs: `/home/hn3t/dev_hub`, generated docs indices, dashboards, progress reports, and script library indices
- Deployment evidence: curl outputs, logs, screenshots, Playwright reports, build logs, and PythonAnywhere web-tab/WSGI observations

---

## 3. Polished Groundtruth Integration Document

### 3.1 Purpose

Groundtruth is a structured collaboration protocol for human-directed AI work. It defines how the human operator and AI collaborator share context, divide responsibilities, preserve continuity, and produce traceable output.

For Workforce, Groundtruth should function as the operating layer that connects project planning, code execution, documentation, testing, deployment, and Dev Hub organization.

### 3.2 Input protocol

Every task should include four inputs:

1. **Context Frame** - background, constraints, active workstream, relevant artifacts, and prior decisions.
2. **Intent Statement** - the desired outcome and why it matters.
3. **Success Criteria** - measurable or observable markers that define done.
4. **Boundary Flags** - explicit limits on scope, tone, format, audience, permissions, security, or architecture.

### 3.3 Output protocol

Every AI deliverable should include four outputs:

1. **Artifact** - the completed answer, document, code change, prompt, report, or instruction block.
2. **Brief rationale** - a concise explanation of key choices and trade-offs. This should summarize decisions, not expose private chain-of-thought.
3. **Confidence signal** - certainty level, assumptions, incomplete information, and remaining risks.
4. **Next-step suggestion** - one practical follow-on action.

### 3.4 Five-layer architecture

| Layer | Function | Workforce application |
|---|---|---|
| L1 - Identity | Defines collaborator role and operating stance | AI acts as precise engineering/project collaborator, not an unconstrained code generator |
| L2 - Context | Captures history, constraints, and active workstreams | Uses repo paths, architecture rules, deployment state, and prior debugging evidence |
| L3 - Execution | Governs decomposition, tool selection, sequencing, and autonomy | Inspect files first, change minimally, test, report evidence |
| L4 - Quality | Enforces standards for accuracy, formatting, citations, and consistency | Preserve RBAC, update tests/docs, cite sources, verify builds and endpoints |
| L5 - Memory | Manages durable facts and continuity | Maintain plan/progress/state docs and carry decisions forward across sessions |

### 3.5 Collaboration rules

- **Bias toward action.** Proceed with reasonable assumptions when the risk is low, and state the assumptions.
- **Single-pass clarity.** Every output should be usable on first read.
- **Escalate consequential uncertainty.** Ask or flag uncertainty before making high-impact decisions.
- **Scope discipline.** Deliver exactly what was requested; keep optional expansions separate.
- **Transparent decision support.** Provide evidence and concise rationale for conclusions.
- **Continuity by default.** Treat each new session as a continuation of the project, not a blank slate.

### 3.6 Continuity layer

Groundtruth continuity preserves:

- Durable facts and preferences from the human operator
- Project-specific context anchors such as naming conventions, repo paths, style guides, active workstreams, and deployment details
- Decision logs that record important choices and their rationale
- Corrections, revocations, and updates made by the operator

Continuity should be additive. New context layers onto the existing project record unless the operator explicitly replaces or revokes it.

### 3.7 Collaboration contract

I will bring clarity of intent. You will bring precision of execution. Together we will build work that neither of us could produce alone. We iterate in the open, flag uncertainty early, and treat every session as a continuation - not a restart.

---

## 4. Copilot Instruction Block

Paste this into a Copilot task, repo instruction file, or Dev Hub execution prompt when you want Groundtruth-style execution.

```text
GROUNDTRUTH COPILOT EXECUTION MODE

Role:
You are an AI engineering collaborator for the Workforce / Hospitable Ops project. Operate as a precise, evidence-driven implementation partner. Do not act as an unconstrained code generator.

Project context:
- Backend: /home/hn3t/workforce_api
- Frontend: /home/hn3t/workforce_frontend_app
- Dev Hub: /home/hn3t/dev_hub
- Backend deployment: https://hn3t.pythonanywhere.com
- Frontend deployment: https://wf-hn3t.pythonanywhere.com
- Dev Hub deployment: https://devhub-hn3t.pythonanywhere.com

Core invariants:
- Preserve strict separation between system user accounts and business-controlled employee files.
- Do not weaken RBAC, tenant, business, or location scoping.
- Backend authorization must remain authoritative.
- Use Alembic for schema changes.
- Keep FastAPI routers thin and business logic in services/modules.
- Preserve Pydantic v2, SQLAlchemy async, and existing package/workspace patterns.
- Do not silently change public API contracts; update tests and callers when contracts change.
- Do not assume frontend issues are only frontend issues or backend issues are only backend issues; trace the real flow.

Input requirements:
Before executing, identify the task's context frame, intent statement, success criteria, and boundary flags. If the user did not provide one of these and the missing detail is not consequential, make a reasonable assumption and state it. If the missing detail could cause data loss, security regression, or broad architecture drift, stop and ask.

Execution rules:
1. Inspect the actual current files, logs, tests, and runtime behavior before changing anything.
2. Trace from UI action to frontend code to backend endpoint when debugging flows.
3. Make the smallest complete change that satisfies the success criteria.
4. Preserve existing architecture, naming conventions, imports, and deployment constraints unless evidence proves they are the cause.
5. Add or update tests when behavior, schema, contract, permissions, or user flows change.
6. Run the narrowest meaningful verification first, then broader checks if needed.
7. Do not use secrets in output. Do not print tokens, passwords, or private credentials.
8. If blocked by missing dependency or environment setup, install only the minimum required dependency and report it.
9. Continue through the real root cause; do not stop at the first superficial symptom.

Required report format:
Artifact:
- Summarize the change, fix, document, or instruction produced.

Rationale:
- Briefly explain key decisions and trade-offs. Do not provide private chain-of-thought; provide a concise decision summary.

Evidence:
- Files inspected:
- Files changed:
- Commands run:
- Tests/checks run:
- Important outputs, status codes, or logs:

Confidence:
- High / Medium / Low:
- Assumptions:
- Remaining risks:

Next step:
- Recommend one concrete next action.

Progress/continuity update:
- Update relevant progress reports, state files, docs, or Dev Hub indices when the task changes project state.
```

---

## Appendix A. Dev Hub page concept

Create a Dev Hub page named **Groundtruth Protocol** with these sections:

- Overview: what Groundtruth is and why the project uses it
- Submit a Task: reusable template with copy button
- Copilot Mode: copy-ready instruction block
- Workforce Invariants: architecture and security rules
- Evidence Standards: commands, tests, screenshots, logs, status codes
- Decision Log: table of date, decision, rationale, affected workstream, owner, and follow-up
- Progress Links: backend, frontend, Dev Hub, deployment, and CI validation records

---

## Appendix B. Decision log template

| Date | Workstream | Decision | Rationale | Evidence | Owner | Follow-up |
|---|---|---|---|---|---|---|
| YYYY-MM-DD | Backend / Frontend / Dev Hub | What changed or was decided | Why this was chosen | Link, command output, test, or doc | Human / AI / Both | Next action |

---

## Appendix C. AI output checklist

Before accepting an AI output, confirm:

- The artifact directly answers the request.
- The rationale explains the important trade-offs without unnecessary internal reasoning.
- The confidence signal names assumptions and risks.
- The next step is concrete and useful.
- Any code task includes files changed, commands run, and test evidence.
- Any project-state change updates the right continuity record.
