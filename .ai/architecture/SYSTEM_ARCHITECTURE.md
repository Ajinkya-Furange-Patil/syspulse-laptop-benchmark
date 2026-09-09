# SysPulse System Architecture

## 1. High-Level Architecture Pipeline

```
┌───────────────────────────────────────────────────────────────┐
│                    Physical Hardware & OS                     │
│               Firmware (vBIOS, ACPI, DMI, MSR)                │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                  Native Hardware Probing                      │
│            WMI / CPUID / Win32 APIs / NVML / OpenMP           │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                   Native Benchmark Engine                     │
│         CPU (Single/Multi/Sustained) • RAM • CUDA GPU         │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                     Physical Telemetry                        │
│            Clocks, Temperatures, Watts, Drop %                │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│               Analytical Buyer Audit Engine                   │
│         Power Delivery • Upgradeability • Performance         │
│           Workload Suitability • Unit Economics • Values       │
└───────────────────────────────┬───────────────────────────────┘
                                │
               ┌────────────────┴────────────────┐
               ▼                                 ▼
┌───────────────────────────────┐ ┌─────────────────────────────┐
│    Deal-Breakers & Traps      │ │     Confidence Engine       │
│  Hard constraints & capacity  │ │ Evidence provenance & decay │
└──────────────┬────────────────┘ └──────────────┬──────────────┘
               └────────────────┬────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│           User-Priority Conditioned Final Verdict             │
│                  (NO UNIVERSAL WINNER)                        │
└───────────────────────────────┬───────────────────────────────┘
                                │
                                ▼
┌───────────────────────────────────────────────────────────────┐
│              Multi-Format Reporting Pipeline                  │
│       Machine JSON • Executive Markdown • Standalone HTML     │
└───────────────────────────────────────────────────────────────┘
```

---

## 2. Architectural Layers

### Layer 1: Hardware Probing & Calibration (`src/sys_detect.cpp`, `include/sys_detect.hpp`)
- Extracts exact processor model, core topology (P-cores vs E-cores), logical thread count, base and turbo limits via CPUID and WMI.
- Inspects physical memory topology: installed modules, speed in MT/s, active channels (Single vs Dual vs Quad), and safe benchmark allocation ceilings.
- Detects GPU hardware: checks CUDA driver and runtime presence, querying SM counts, CUDA core allocations, and physical VRAM capacity.

### Layer 2: Real-Silicon Benchmark Engine (`src/main.cpp`, `src/cuda_kernels.cu`, `include/ram_bench.hpp`)
- **Quick Single-Core**: Memory-independent 64-bit integer mix loop to assess pure single-thread instruction throughput.
- **Multi-Core Throughput**: OpenMP reduction across all logical processors performing double-precision floating point calculations.
- **Sustained Thermal Check**: Multi-second saturated load to observe clock degradation, package temperatures, and sustained drop percentages.
- **RAM Subsystem**: Read/write/copy bandwidth and latency measurements avoiding OS cache contamination.
- **CUDA AI & Graphics**: SGEMM matrix multiplication measuring FP32 TFLOPs and latency under sustained GPU draw.

### Layer 3: Analytical Buyer Audit Engine (`audit_engine/`)
- Pure Python 3.10+ analytical suite operating either on live telemetry or standardized specification JSON sheets.
- Models physical silicon scaling: microarchitecture IPC tables, sub-linear power scaling ($P^{0.68}$), cooling dissipation limits, and dynamic auxiliary system draw ($P_{\text{aux}}$).
- Assesses 6 separate workload domains independently with zero weight distortion.
- Scans promotional marketing headlines for deceptive buzzwords and compares them to physical realities.

### Layer 4: Reporting & Output (`audit_engine/report_generator.py`, `src/buyer_checklist.cpp`)
- Emits structured telemetry in `results/laptop_buyer_audit.json` and `results/performance_report.html`.
- Renders rich, dark-mode, zero-CDN, standalone HTML dossiers with transparent deduction trees.
