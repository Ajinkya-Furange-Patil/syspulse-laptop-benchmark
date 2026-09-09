# Mandatory Stop Conditions

The AI agent **MUST STOP IMMEDIATELY** and ask the user for clarification when any of the following conditions are encountered:

---

## 1. Ambiguity & Contradiction
1. User requirements directly contradict existing project non-negotiables (e.g. asking to fabricate scores or remove deal-breakers).
2. Two specification documents or schema requirements directly contradict each other.
3. A requested scoring formula is mathematically undefined or ambiguous.

---

## 2. Safety & Scope
4. A requested stress test could bypass CPU/GPU safety protections or cause unbounded memory loops.
5. The request would convert SysPulse into a commercial affiliate website, registry cleaner, or cloud service.

---

## 3. Destructive Operations & Architecture
6. The proposed solution requires a wholesale rewrite of functioning subsystems without user instruction.
7. A requested change would break backward compatibility of public JSON telemetry schemas.
8. The agent is tempted to guess or fabricate unknown hardware specifications.
