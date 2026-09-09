# SysPulse Non-Negotiable Rules

These rules override convenience, deadlines, and aesthetics. Any violation constitutes a critical failure of the engineering contract.

---

## 1. Hardware Data & Telemetry
- **NEVER** fabricate hardware specifications.
- **NEVER** invent TGP or power ratings.
- **NEVER** invent VRAM capacity or bus width.
- **NEVER** invent RAM topology (SODIMM vs soldered).
- **NEVER** invent CPU base or boost clocks.
- **NEVER** invent thermal limits or dissipation capacity.
- **NEVER** infer missing values as zero.
- **NEVER** silently discard unavailable metrics.

---

## 2. Benchmarking Integrity
- **NEVER** modify workload intensity to inflate benchmark numbers.
- **NEVER** remove warm-up loops when thermal stabilization is required.
- **NEVER** compare incomparable workloads (e.g. comparing FP32 SGEMM to INT8 inference).
- **NEVER** compare results produced under materially different thermal/power states without explicit disclosure.
- **NEVER** report a benchmark result without its physical unit (GFLOPs, MB/s, ms, °C, Watts).

---

## 3. Scoring & Verdicts
- **NEVER** tune weights after seeing a test result simply to improve the verdict.
- **NEVER** assign a higher score merely because a laptop is expensive or has premium branding.
- **NEVER** use marketing buzzwords as technical scoring inputs.
- **NEVER** hide fatal deal-breakers inside a blended weighted average score.
- **NEVER** optimize formulas to increase scores; optimize formulas only for physical accuracy.

---

## 4. Architecture & Dependencies
- **NEVER** rewrite the whole system to implement a localized feature.
- **NEVER** replace a functioning native subsystem without documented technical justification.
- **NEVER** introduce heavy third-party dependencies or external Python libraries casually.
- **NEVER** introduce mandatory network calls into an offline-first tool.
- **NEVER** duplicate existing logic across disparate modules.

---

## 5. AI Agent Behavior
- **NEVER** assume unverified facts.
- **NEVER** hallucinate hardware capabilities.
- **NEVER** claim execution or test runs that did not actually take place.
- **NEVER** claim hardware platform support without verifying physical APIs.
- **NEVER** silently alter project scope or engineering philosophy.

---

## 6. Safety & Operating System
- **NEVER** bypass CPU/GPU thermal trip points (TjMax).
- **NEVER** create unbounded, runaway stress workloads without a timeout or cancellation path.
- **NEVER** intentionally cause destructive hardware conditions.
- **NEVER** require administrator privileges without explicit, documented architectural justification.
