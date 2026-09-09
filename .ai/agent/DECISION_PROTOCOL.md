# AI Agent Decision Protocol

When an AI agent faces ambiguity or architectural decisions, it must follow this deterministic protocol.

---

## 1. The Decision Hierarchy

1. **Physical Reality & Hardware Evidence:** Physical limits (vBIOS TGP, memory bus width, thermals) always supersede assumptions.
2. **The Project Constitution:** If a proposed change conflicts with [`.ai/constitution/PROJECT_CONSTITUTION.md`](file:///.ai/constitution/PROJECT_CONSTITUTION.md), reject the change.
3. **Existing Architectural Patterns:** Follow established code patterns in `audit_engine/` and `src/` rather than introducing alien design paradigms.
4. **Conservative Engineering Defaults:** If a manufacturer spec is omitted, choose the conservative floor rather than an optimistic guess.

---

## 2. Hypothesis Testing
Before committing to an optimization or algorithmic change:
- State the physical hypothesis.
- Measure the baseline before the change.
- Implement the change in an isolated module.
- Re-measure and compare delta.
- If no measurable improvement exists, discard the modification.
