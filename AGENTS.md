# AGENTS.md
# SysPulse AI Engineering Contract

This repository is **SysPulse**: an offline-first laptop/PC benchmarking, hardware inspection, bottleneck analysis, and buyer-audit system.

This file is the mandatory entrypoint for any AI coding agent working inside this repository. The AI **MUST** read this file before modifying code. For detailed rules, read the relevant files under `.ai/`.

---

# 1. CORE DIRECTIVE

You are an engineering agent working **INSIDE** an existing system.
Your job is:
```
UNDERSTAND → VERIFY → PLAN → MODIFY → TEST → REPORT
```
Your job is **NOT**:
```
INVENT → REWRITE → GUESS → ADD RANDOM FEATURES
```

Never redesign the project merely because you would personally architect it differently. Preserve the existing architecture unless the task explicitly requires architectural change.

---

# 2. PROJECT IDENTITY

SysPulse exists to:
- Benchmark real hardware
- Inspect real laptop hardware constraints
- Measure sustained performance vs short-burst boost
- Identify inter-subsystem bottlenecks
- Detect thermal and power delivery limitations
- Evaluate hardware modularity and upgradeability
- Evaluate workload suitability across 6 discrete domains
- Identify non-negotiable hardware deal-breakers
- Produce explainable, evidence-grounded buyer recommendations

SysPulse is **NOT**:
- A generic PC optimizer
- An overclocking utility
- A game booster
- A synthetic score generator
- A marketing/specification scraper
- An AI chatbot
- A generic laptop affiliate website

Do not turn SysPulse into any of these. Read:
- [`.ai/constitution/SCOPE.md`](file:///.ai/constitution/SCOPE.md)
- [`.ai/constitution/PROJECT_CONSTITUTION.md`](file:///.ai/constitution/PROJECT_CONSTITUTION.md)

---

# 3. ABSOLUTE RULES

The following rules are **NON-NEGOTIABLE**:

1. **Never invent hardware specifications.**
2. **Never silently assume unknown hardware values.**
3. **Never convert an unknown value into zero.**
4. **Never fabricate benchmark results.**
5. **Never fabricate thermal measurements.**
6. **Never fabricate TGP/TDP values.**
7. **Never fabricate VRAM capacity.**
8. **Never fabricate CPU/GPU clocks.**
9. **Never treat marketing claims as physical measurements.**
10. **Never hide uncertainty.**
11. **Never modify scoring weights merely to make a result look better.**
12. **Never optimize for a higher final score.**
13. **Never make a benchmark easier merely to improve performance numbers.**
14. **Never remove a test because it exposes a weakness.**
15. **Never hardcode one laptop's specifications into general logic.**
16. **Never make one vendor/model the implicit reference standard.**
17. **Never assume NVIDIA hardware exists.**
18. **Never assume CUDA is available.**
19. **Never assume administrator privileges.**
20. **Never require internet access unless explicitly designed as an optional feature.**
21. **Never introduce a large dependency for a small feature.**
22. **Never rewrite unrelated modules.**
23. **Never delete existing tests without replacement justification.**
24. **Never change public output formats without considering compatibility.**
25. **Never claim a change is complete without testing it.**

---

# 4. SOURCE OF TRUTH

When information conflicts, enforce this strict authority hierarchy:

1. **Actual measured hardware telemetry** (Physical lab run / sensors)
2. **Direct OS/hardware API results** (WMI, CPUID, NVML, Win32 APIs)
3. **Verified benchmark measurements** (Repeatable, sustained test output)
4. **Firmware/driver-reported limits** (vBIOS TGP tables, MSR PL1/PL2)
5. **Manufacturer technical whitepapers & service manuals**
6. **Reputable third-party teardown measurements** (Notebookcheck, etc.)
7. **User-provided manual specifications**
8. **Generic conservative assumptions**

*Generic assumptions MUST NEVER override actual measurements.*

---

# 5. UNKNOWN DATA POLICY

`UNKNOWN` is a completely valid and necessary state.
Use:
```
UNKNOWN
```
instead of:
```
0, false, minimum value, guessed value
```
unless the metric's semantics explicitly require another representation.
Every important measurement must carry:
- `value`
- `unit`
- `source`
- `confidence` (0.0 to 1.0)
- `timestamp`
- `measurement_method`

---

# 6. BENCHMARK INTEGRITY

Benchmark code must measure physical silicon rather than accidentally measuring the benchmark implementation.
Before modifying benchmark logic, answer:
- What hardware resource is being exercised?
- What is the workload?
- What is the expected physical bottleneck?
- What is the measurement unit?
- What is the warm-up behavior?
- What is the steady-state thermal behavior?
- What background OS interference exists?
- Can the result be reproduced independently?
- Can the result be independently sanity-checked?

*Never manipulate workload parameters simply to obtain a better score.*

---

# 7. SCORE INTEGRITY

SysPulse must rigorously separate:
```
RAW MEASUREMENTS
      ↓
DERIVED METRICS
      ↓
EVIDENCE
      ↓
WORKLOAD EVALUATION
      ↓
DEALBREAKERS
      ↓
SCORE
      ↓
VERDICT
```
Do **NOT** collapse these layers. A score is an interpretation of evidence; a score is **NOT** evidence itself.

---

# 8. DEALBREAKERS

A dealbreaker is a hard, workload-specific limitation.
*Example:* 4GB VRAM is a hard dealbreaker for modern Local LLMs and AAA gaming textures, but perfectly viable for basic 2D CAD and standard software development.
Therefore:
**DO NOT produce universal statements such as "4 GB VRAM = bad laptop".**
**PREFER: "4 GB VRAM creates a hard capacity limitation for AI/LLM workloads."**

Every dealbreaker must specify:
- `affected_workload`
- `physical_reason`
- `threshold`
- `evidence`
- `confidence`
- `is_upgradeable`
- `possible_workaround`

---

# 9. WORKLOAD-FIRST EVALUATION

Never assume that one single score represents every user. There is **NO UNIVERSAL WINNER**.
At minimum evaluate:
- Modern Gaming
- AI / Machine Learning (Local LLMs & Diffusion)
- Software Development (Compilation & Containers)
- Engineering / CAD & Simulation
- Content Creation & Video Editing
- Campus Portability & Battery

A laptop may score:
- 95 / 100 for Software Development
- 40 / 100 for Gaming
- 15 / 100 for Local AI

That is a **VALID, ACCURATE** result.

---

# 10. ANTI-MARKETING PRINCIPLE

Marketing language is not hardware evidence.
Phrases like:
`"AI-Powered"`, `"Gaming Beast"`, `"Studio Display"`, `"Ultra Performance"`, `"Military-Grade"`
must **never** directly contribute to a technical score.
Only measurable physical properties (silicon die, vBIOS TGP, measured GTG response time, color gamut, heatsink dissipation envelope) may affect evaluation.

---

# 11. ARCHITECTURE BOUNDARIES

Respect existing module boundaries. Before modifying a module:
1. Read its implementation.
2. Read its interface/header.
3. Find callers.
4. Find tests.
5. Understand its output contract.
6. Check related documentation.

Do not modify a component solely because another component could theoretically do the same job.

---

# 12. CHANGE SIZE & HYGIENE

Prefer the **smallest correct change** over the largest possible redesign.
Avoid:
- Drive-by refactors
- Unnecessary renaming
- Formatting entire untouched files
- Unsolicited dependency replacements
- Architecture rewrites

---

# 13. VALIDATION & TESTING

After modifying code:
1. Compile cleanly with MSVC / C++20.
2. Run relevant unit and integration test runners.
3. Run [`test_all_phases.py`](file:///test_all_phases.py).
4. Inspect output for regressions.
5. Never claim "tested" unless the command actually ran and completed with code 0.

---

# 14. HARDWARE SAFETY

Benchmark and stress functionality must remain safely bounded.
Never intentionally:
- Damage hardware
- Bypass CPU/GPU thermal protection
- Bypass firmware safety limits
- Disable OS emergency safeguards
- Create unbounded infinite memory loops
- Intentionally cause destructive overheating

Stress tests must have hard duration limits, responsive cancellation paths, and resource cleanups.

---

# 15. STOP CONDITIONS

**STOP** and ask for clarification if:
- User requirements contradict each other.
- Changing system architecture appears necessary but was not requested.
- A critical hardware value is unknown and materially affects the outcome.
- A scoring formula is mathematically ambiguous.
- An API behavior cannot be verified offline.
- A change breaks backward compatibility of output JSON/HTML schemas.

---

# 16. REQUIRED READING INDEX

Before making non-trivial modifications, read:
- [`.ai/constitution/PROJECT_CONSTITUTION.md`](file:///.ai/constitution/PROJECT_CONSTITUTION.md)
- [`.ai/constitution/NON_NEGOTIABLES.md`](file:///.ai/constitution/NON_NEGOTIABLES.md)
- [`.ai/architecture/SYSTEM_ARCHITECTURE.md`](file:///.ai/architecture/SYSTEM_ARCHITECTURE.md)
- [`.ai/architecture/COMPONENT_BOUNDARIES.md`](file:///.ai/architecture/COMPONENT_BOUNDARIES.md)
- [`.ai/agent/WORKFLOW.md`](file:///.ai/agent/WORKFLOW.md)

For benchmark work:
- [`.ai/benchmark/BENCHMARK_PHILOSOPHY.md`](file:///.ai/benchmark/BENCHMARK_PHILOSOPHY.md)
- [`.ai/benchmark/METRICS.md`](file:///.ai/benchmark/METRICS.md)
- [`.ai/benchmark/REPRODUCIBILITY.md`](file:///.ai/benchmark/REPRODUCIBILITY.md)

For audit & scoring work:
- [`.ai/audit/AUDIT_PHILOSOPHY.md`](file:///.ai/audit/AUDIT_PHILOSOPHY.md)
- [`.ai/audit/SCORING_RULES.md`](file:///.ai/audit/SCORING_RULES.md)
- [`.ai/audit/DEALBREAKERS.md`](file:///.ai/audit/DEALBREAKERS.md)
- [`.ai/audit/CONFIDENCE.md`](file:///.ai/audit/CONFIDENCE.md)
- [`.ai/audit/WORKLOADS.md`](file:///.ai/audit/WORKLOADS.md)

---

# 17. FINAL PRINCIPLE

> **A higher score is NOT the goal. A more truthful result is the goal.**

When uncertain: **DO NOT GUESS. Inspect. Measure. Verify. Then change.**
SysPulse must remain a hardware-evidence-driven engineering system.
