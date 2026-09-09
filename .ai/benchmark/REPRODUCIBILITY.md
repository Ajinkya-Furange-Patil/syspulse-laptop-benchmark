# Benchmark Reproducibility Rules

Benchmarking results are meaningless if they cannot be replicated independently under identical conditions.

---

## 1. Controlling for Environmental Variance

1. **Power Profile Logging:**
   - Always record whether the laptop is operating on AC Power (`PluggedIn`) or DC Battery (`Discharging`).
   - Log the active Windows Power Scheme (e.g. `High Performance`, `Balanced`, `Best Power Efficiency`).
2. **Thermal Baseline Calibration:**
   - Record baseline idle temperature before initiating heavy compute passes.
   - If a benchmark run begins when the heatsink is already heat-soaked at 85°C, sustained scores will appear lower than a cold run; this must be explicitly noted in the telemetry artifact.
3. **Fixed Pseudo-Random Seeds:**
   - Memory mix loops and matrix initialization must use deterministic pseudo-random seeds (e.g. `0x9E3779B97F4A7C15ULL`) to ensure every test run executes identical mathematical operations.
