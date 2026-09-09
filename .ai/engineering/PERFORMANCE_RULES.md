# Performance Engineering Rules

SysPulse evaluates the performance of target laptops. Therefore, its own benchmark and analysis code must be engineered with high efficiency, zero measurement artifacts, and minimal runtime overhead.

---

## 1. Native Benchmark Hot Loops
- **Zero Allocations:** No heap allocation (`malloc`, `new`, `std::vector::push_back`, string formatting) inside tight inner benchmark loops.
- **Cache Eviction & Isolation:** RAM benchmarks must flush CPU caches or allocate working sets significantly larger than the L3 cache size (e.g. 2x to 4x L3 capacity) to measure true DRAM bandwidth rather than on-die cache throughput.
- **Prevent Dead-Code Optimization:** Use inline assembly or volatile memory sinks (`RamBench::DoNotOptimize()`) to ensure the compiler does not optimize away pure compute loops.
- **Warm-Up Runs:** Always execute an initial unmeasured warm-up cycle to populate instruction caches, spin up CPU power states, and avoid transient initialization jitter.

---

## 2. Python Audit Engine Efficiency
- Keep JSON parsing and database queries fast; load datasets using stream parsing or indexed SQLite lookups.
- Avoid redundant computations: calculate intensive metrics (e.g. IPC scaling or bottleneck search) once per audit run and pass results down the pipeline.
- Ensure report rendering completes in under 100 milliseconds for standard laptop dossiers.

---

## 3. Telemetry Overhead
- Hardware sensor polling must not exceed 1% CPU utilization during idle or benchmark monitoring.
- Use efficient WMI queries with specific column projections instead of `SELECT * FROM Win32_...`.
