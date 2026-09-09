# Benchmark Philosophy & Physical Rigor

A benchmark is only valid if it measures the physical capabilities of hardware rather than measuring the quirks of the benchmark harness itself.

---

## 1. Core Tenets

### 1. Distinguish Peak vs Sustained
Most modern laptop CPUs can deliver impressive numbers for 10 to 30 seconds while drawing PL2 power (e.g. 115W) and dumping heat into a cold copper heatsink. Once the copper saturates, power drops to PL1 (e.g. 45W) and clocks plummet by 25–40%.
**SysPulse prioritizes sustained steady-state capability over short-burst peak vanity numbers.**

### 2. Measure Real Workload Equivalents
- **CPU Single-Thread:** Real-world execution involves irregular branching, pointer chasing, and integer bit manipulation. Synthetic vector loops that stay in L1 cache do not represent desktop application responsiveness.
- **CPU Multi-Core:** Multi-threaded throughput must measure scalable floating point computations across all physical and logical threads using standard OpenMP scheduling.
- **RAM Subsystem:** Memory latency and bandwidth must be evaluated across realistic buffer sizes that exceed cache hierarchies.
- **GPU AI Matrix Multiplications:** Deep learning and LLM inference rely heavily on GEMM (General Matrix Multiply) throughput and tensor core execution, not just 3D rasterization.

---

## 2. Validity Criteria for New Benchmarks

A benchmark workload in SysPulse is considered **INVALID** if:
1. The compiler can compute the result at compile time (constant folding / dead code elimination).
2. The dataset fits entirely in L1/L2 cache when measuring main memory (RAM).
3. The measurement timer includes setup time, memory allocation, or disk I/O.
4. The test runs for less than the CPU Tau limit when claiming to measure sustained thermal behavior.
5. The result cannot be replicated within a 5% variance margin under identical thermal conditions.
