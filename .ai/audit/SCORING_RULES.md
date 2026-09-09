# Audit Scoring Rules & Weight Integrity

The scoring engine evaluates hardware objectively based on physics, electrical engineering, and microarchitecture.

---

## 1. Fundamental Scoring Axiom
> **The score is the RESULT of evidence. The score is NOT the target.**
>
> Never alter formulas or weight distributions merely because a machine scored lower or higher than expected.

---

## 2. Evaluation Layers
Scoring follows this strict cascade:
```
RAW SPECIFICATION / SENSOR METRICS
                 ↓
      PRE-AUDIT SANITY VALIDATION
                 ↓
   PHYSICAL THERMAL & POWER LIMITS
                 ↓
     WORKLOAD RESOURCE REQUIREMENTS
                 ↓
HARD CAPACITY CONSTRAINTS & DEAL-BREAKERS
                 ↓
   WEIGHTED DOMAIN & CATEGORY SCORING
                 ↓
        FINAL TAILORED VERDICT
```

---

## 3. Subsystem Weight Allocations
Baseline hardware categories are evaluated across 100 maximum points:
- **CPU Architecture & Multi-Core Scaling:** 20 points
- **GPU Silicon & Configured TGP:** 25 points
- **VRAM Capacity & AI Matrix Acceleration:** 15 points
- **RAM Capacity, Topology & Modularity:** 15 points
- **Storage Speed & Expansion Slots:** 10 points
- **Cooling Dissipation & Thermal Stability:** 15 points

---

## 4. Hard Constraints vs Weighted Averages
**Weighted averages MUST NEVER conceal fatal capacity limits.**
If a laptop has 4GB of VRAM and the user's workload is Local AI / LLMs:
- Do **not** report a "mediocre" score of 60/100 because the CPU is fast.
- The system must trigger a `FATAL_VRAM_SUB_6GB` deal-breaker and clamp the AI workload score to under 20/100, issuing a `HARD NO` verdict.
