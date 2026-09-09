# AI Agent Workflow Protocol

Every AI coding agent operating inside the SysPulse codebase must execute tasks using this structured 8-phase protocol.

---

## Phase 0: STOP & DO NOT EDIT
Do **NOT** immediately start modifying files or proposing code diffs upon receiving a prompt. First inspect the existing state.

---

## Phase 1: Understand
- Read [`AGENTS.md`](file:///AGENTS.md) and the relevant specialized documents under [`.ai/`](file:///.ai/).
- Clarify the user's technical objective.
- Identify which subsystems are involved (Native C++, Audit Engine, Schemas, Reporting).

---

## Phase 2: Reconnaissance
- Inspect the codebase using search and file viewing tools.
- Identify call sites, interfaces, header files, and existing test coverage.
- Check recent commits and existing documentation.

---

## Phase 3: Problem Definition
Synthesize the task internally:
- What is currently happening?
- Why is it sub-optimal or broken?
- What exact physical behavior or data flow should change?
- What existing behavior **must not** break?

---

## Phase 4: Implementation Plan
Formulate a minimal, cohesive implementation plan:
- Group changes logically (schemas first, core engine second, tests third).
- Identify risks and backward compatibility implications.

---

## Phase 5: Implement
- Apply the smallest correct change.
- Follow [`CODING_RULES.md`](file:///.ai/engineering/CODING_RULES.md).
- Avoid drive-by refactorings or formatting untouched files.

---

## Phase 6: Validate
- Compile the native codebase (`build.bat` or MSVC).
- Run affected phase tests (`audit_engine/test_phase*.py`).
- Run the master verification suite (`test_all_phases.py`).
- Verify that exit codes are 0 and no regressions occurred.

---

## Phase 7: Review
- Confirm that no hardware data was fabricated.
- Confirm that no scoring formulas were distorted.
- Verify that the portable distribution package remains clean.

---

## Phase 8: Report & Commit
- Document what changed, what was tested, and any remaining limitations.
- Commit using standard Conventional Commits formatting.
