# SysPulse Scope

## 1. IN SCOPE

### Hardware Inspection & Verification
- **CPU**: Cores, threads, base/boost clocks, microarchitecture IPC, AVX capabilities, sustained PL1 and peak PL2 envelopes.
- **GPU**: Silicon die, SM/CUDA counts, dedicated VRAM, memory bus width, bandwidth, OEM configured vBIOS TGP, dynamic boost, and MUX switch routing.
- **Memory**: Total capacity, transfer rate (MT/s), active channel topology (Single, Dual, Quad), and modularity (SODIMM slots vs soldered LPDDR).
- **Storage**: Interface (PCIe Gen 3/4/5 NVMe vs SATA), sustained sequential throughput, DRAM cache presence, and M.2 expansion slot count.
- **Display**: Resolution, refresh rate (Hz), measured GTG pixel response time, color gamut (sRGB, DCI-P3), brightness (nits), and aspect ratio.
- **Power Delivery**: OEM adapter wattage, combined cross-load power balance, and detection of battery drain while plugged into AC power.
- **Cooling & Thermals**: Rated dissipation watts, heatpipe/vapor chamber topology, fan count, exhaust vents, and thermal paste pump-out vulnerability.
- **Upgradeability & Longevity**: Fasteners (Philips vs Torx), glue usage, modular Wi-Fi, hinge mechanics, and 1/3/5-year ownership projections.

### Benchmarking & Stress Testing
- CPU single-thread raw instruction throughput (MOps/s) and multi-thread OpenMP floating-point throughput (GFLOPs).
- RAM memory bandwidth and cache latency curves.
- GPU compute via native CUDA kernels (AI SGEMM matrix multiplication and graphics simulation).
- Sustained multi-minute thermal stability and throttling drop percentages.
- Concurrent CPU + GPU cross-load stress behavior.

### Analysis & Evaluation
- Workload-specific suitability (Gaming, AI/LLMs, Software Dev, Engineering/CAD, Content Creation, Portability).
- Identification of fatal hardware deal-breakers and inter-subsystem bottlenecks with % loss estimation.
- Hardware unit economics and price-to-performance ROI (Performance/₹, VRAM/₹, GPU TFLOPs/₹).
- Anti-marketing audit cross-examining promotional buzzwords against silicon physical limits.
- Subsystem confidence tracking and multi-source conflict resolution.

### Reporting
- Machine-readable JSON telemetry and audit records.
- Executive Markdown dossiers.
- Self-contained, zero-external-dependency interactive HTML reports.

---

## 2. OUT OF SCOPE

Unless explicitly requested by the user, SysPulse will **NOT** be:
- An antivirus, malware scanner, or spyware detector
- A Windows registry "cleaner" or temporary file optimizer
- A game booster or background task killer
- An automated overclocking or undervolting tuning utility
- A BIOS modifier or firmware flasher
- A destructive hardware stress test that bypasses OEM safeguards
- A cryptocurrency miner or background compute network
- A cloud-based analytics engine requiring mandatory user telemetry
- A platform requiring mandatory internet connectivity or user accounts
- An ad-supported affiliate referral or sponsored ranking website
- A conversational AI chatbot or LLM frontend

---

## 3. PRIMARY PRODUCT DEFINITION

```
SysPulse = Hardware Evidence + Benchmarking + Audit + Explainable Analysis + Workload Verdicts
```
SysPulse is an engineering truth tool designed to protect users from deceptive laptop marketing and reveal true sustained hardware capability.
