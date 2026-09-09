# SysPulse Project Constitution

## 1. Mission
SysPulse exists to determine what a computer can actually do, what limits its performance, and whether its hardware configuration is appropriate for a specific workload. The project prioritizes physical reality over marketing specifications.

---

## 2. Engineering Philosophy
SysPulse strictly follows this sequence:
```
Measure first. Interpret second. Score third. Recommend last.
```
Never reverse this order.

---

## 3. Reality Over Specifications
- A **specification** says what a component is advertised to be.
- A **benchmark** says what it can do in isolation.
- **Telemetry** says what it is doing right now under power/thermal limits.
- **Sustained testing** says what it can continue doing indefinitely.

SysPulse must always distinguish all four states.

---

## 4. No Universal Laptop Score
There is no single universally correct laptop. Evaluation depends on:
- Primary workload
- Thermal dissipation headroom
- Sustained power envelope (PL1/TGP vs Adapter wattage)
- Modularity and upgradeability
- Memory capacity requirements
- Portability and battery discharge behavior
- Price-to-capability unit economics

Therefore, **workload-specific results are mandatory**.

---

## 5. Capacity vs Performance
Do **not** confuse:
- *"Slow"* (sub-optimal performance, low framerates, high latency) with:
- *"Cannot fit"* (fatal capacity constraint, OutOfMemory crash, PCIe asset thrashing).

*Example:* A GPU may have sufficient compute throughput but insufficient VRAM for a particular AI model. That is a **hard capacity limit**, not merely a performance deficit.

---

## 6. Peak vs Sustained
Short-duration burst performance is insufficient for evaluating sustained capability. SysPulse distinguishes:
- **Peak / Instantaneous:** Transient turbo boost (PL2 / Dynamic Boost)
- **Short-Duration:** 10-30 second burst (Cinebench single run)
- **Sustained:** Steady-state after heatsink saturation (PL1 / Base TGP)
- **Thermal-Limited:** Forced downclocking due to TjMax (95-100°C)
- **Power-Limited:** Clamped by vBIOS or undersized AC adapter
- **Cross-Load:** Concurrent CPU + GPU load causing thermal bleed or battery discharge

---

## 7. Hardware Bottleneck Philosophy
A bottleneck is **not** merely a component with low utilization. Correct bottleneck analysis requires correlation:
Low GPU utilization may signify:
- CPU single-thread bottleneck
- Workload synchronization barrier
- Thermal throttling on the VRM
- Memory bus saturation
- Driver/API overhead

*Never infer an inter-subsystem bottleneck from one metric alone.*

---

## 8. Evidence Chain
Every important conclusion must be deterministically traceable:
```
Raw Sensor / Spec → Derived Metric → Engineering Rule → Workload Impact → Verdict
```
A user or engineer must always be able to ask: *"Why did SysPulse conclude this?"* and receive a clear physical explanation.

---

## 9. Reproducibility
Results must be reproducible within reasonable variance. Every benchmark and audit artifact must record:
- Hardware topology
- OS build and power plan
- Driver version
- Ambient/thermal state
- Benchmark duration and iteration count
- Measurement method and confidence level

---

## 10. Honest Failure
A failed measurement is vastly preferable to a fabricated measurement.
If SysPulse cannot determine a parameter: **report `UNKNOWN` rather than guessing.**

---

## 11. Anti-Optimization Bias
SysPulse must never alter its methodology to make a particular machine appear better. The evaluation framework must remain completely independent of the commercial outcome.

---

## 12. Long-Term Goal
SysPulse should be a trustworthy, scientifically grounded computer systems inspection framework, not merely a benchmark score generator.
