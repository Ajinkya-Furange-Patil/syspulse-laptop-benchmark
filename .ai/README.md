# SysPulse AI Guardrails

This directory contains the persistent engineering rules, architectural constraints, and quality standards used by AI coding agents working on **SysPulse**.

---

## 1. Purpose

Prevent AI agents from:
- Hallucinating hardware specifications or vBIOS limits
- Converting unknown values into zeros or misleading assumptions
- Changing project scope or turning SysPulse into a generic web scraper/chatbot
- Redesigning working architecture unnecessarily
- Manipulating benchmark methodology or warm-up periods to inflate scores
- Tweaking scoring weights after the fact to artificially flatter a test machine
- Hiding uncertainty or presenting weak evidence as confirmed physical fact
- Adding unnecessary runtime or network dependencies
- Breaking single-binary offline portability
- Weakening unit/integration tests to force a pass
- Making workload-independent hardware judgments (*"No Universal Winner"*)

---

## 2. Directory Hierarchy

```
AGENTS.md (Master Entrypoint)
    ↓
.ai/
├── README.md               # Overview and directory index
├── constitution/           # Inviolable philosophical and scope boundaries
│   ├── PROJECT_CONSTITUTION.md
│   ├── NON_NEGOTIABLES.md
│   ├── SCOPE.md
│   └── TERMINOLOGY.md
├── architecture/           # System topology and component boundaries
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── COMPONENT_BOUNDARIES.md
│   ├── DATA_FLOW.md
│   └── DEPENDENCY_POLICY.md
├── engineering/            # Implementation and coding hygiene
│   ├── CODING_RULES.md
│   ├── CHANGE_POLICY.md
│   ├── TESTING_RULES.md
│   ├── PERFORMANCE_RULES.md
│   └── ERROR_HANDLING.md
├── benchmark/              # Native C++/CUDA benchmark rules
│   ├── BENCHMARK_PHILOSOPHY.md
│   ├── METRICS.md
│   ├── TELEMETRY.md
│   ├── STRESS_SAFETY.md
│   └── REPRODUCIBILITY.md
├── audit/                  # Analytical scoring and buyer evaluation
│   ├── AUDIT_PHILOSOPHY.md
│   ├── SCORING_RULES.md
│   ├── DEALBREAKERS.md
│   ├── CONFIDENCE.md
│   ├── ANTI_MARKETING.md
│   ├── WORKLOADS.md
│   └── FUTURE_PROOFING.md
├── agent/                  # AI agent workflow and decision protocols
│   ├── WORKFLOW.md
│   ├── RECONNAISSANCE.md
│   ├── DECISION_PROTOCOL.md
│   ├── STOP_CONDITIONS.md
│   └── COMPLETION_CHECKLIST.md
├── decisions/              # Architectural Decision Records (ADRs)
│   ├── README.md
│   ├── ADR-001-scoring-model.md
│   ├── ADR-002-unknown-values.md
│   ├── ADR-003-workload-verdicts.md
│   ├── ADR-004-cuda-fallback.md
│   └── ADR-005-offline-portability.md
└── tasks/                  # Task templates and execution audit logs
    ├── TASK_TEMPLATE.md
    └── AI_CHANGELOG.md
```

---

## 3. Important Notice

These files are **NOT** a replacement for source code documentation or the human-facing engineering specs under `docs/`.
They define how an **AI agent must behave** while inspecting, planning, and modifying the codebase.

---

## 4. The Golden Rule

> **A higher score is NOT the goal. A more truthful result is the goal.**
>
> If an AI agent does not know: **DO NOT GUESS**.
> Inspect the repository. Measure where possible. Verify assumptions. Then implement.
