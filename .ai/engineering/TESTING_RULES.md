# Testing & Validation Rules

Testing in SysPulse is mandatory. No feature, formula tweak, or bug fix is considered complete until it is validated across real hardware or verified test fixtures.

---

## 1. Core Testing Requirements

1. **Every Feature Must Have a Test:** When adding a new capability, add a corresponding test in `audit_engine/test_phase*.py` or the C++ benchmark suite.
2. **Every Bug Fix Must Have a Regression Test:** Ensure that the specific failure mode is tested and prevented from recurring.
3. **Continuous End-to-End Verification:** Always run [`test_all_phases.py`](file:///test_all_phases.py) to ensure all 22 phases execute cleanly with zero runtime exceptions.

---

## 2. Testing Edge Cases & Hardware Diversity

Test cases must evaluate diverse and extreme laptop configurations:
- **The Deceptive Paper Tiger:** High advertised specs (e.g. i7 + RTX 4060) crippled by 45W vBIOS, single-channel soldered RAM, and a 45% NTSC display. Must trigger deal-breakers and anti-marketing traps.
- **The Properly Engineered Workstation:** Balanced power delivery, Max-P TGP, dual SODIMM slots, vapor chamber cooling, and 100% DCI-P3 display. Must achieve high scores with clean engineering verification.
- **The Severe Power Deficit Machine:** High-draw silicon (Core i9 + RTX 4070) paired with an undersized power adapter (e.g. 135W). Must flag hybrid battery drain on AC power.
- **The Real Host Lab Machine:** Physical telemetry ingested from live C++/CUDA runs, verifying real-world sensor integration.

---

## 3. Prohibited Testing Practices
- **NEVER** weaken a test threshold simply to make a failing test pass.
- **NEVER** skip tests that expose architectural or hardware weaknesses.
- **NEVER** mock hardware sensor data in a way that produces misleadingly optimistic scores.
- **NEVER** commit tests that rely on external network calls or remote servers.
