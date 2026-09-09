# Component Boundaries & Ownership

To preserve clean separation of concerns, every directory in SysPulse has strict, non-overlapping ownership responsibilities:

---

## 1. `include/` — Native Public Interfaces & Utilities
- **Ownership:** C++ header declarations, data structures, and cross-platform native utility classes.
- **Allowed Contents:**
  - `sys_detect.hpp`: Hardware topology definitions.
  - `ram_bench.hpp`: Memory benchmarking routines and cache-flushing helpers.
  - `cuda_bench.cuh`: CUDA kernel interfaces and device structures.
  - `bottleneck_engine.hpp`: C++ telemetry correlation data types.
  - `buyer_checklist.hpp`: C++ 34-point native audit structures.
- **Strict Prohibition:** Do NOT embed high-level buyer recommendation logic, external web dependencies, or market pricing assumptions here.

---

## 2. `src/` — Native Benchmark Implementation & Telemetry
- **Ownership:** Native execution engine (C++20 and CUDA).
- **Allowed Contents:**
  - Hardware probing implementation (WMI, CPUID, Win32).
  - OpenMP parallel benchmark loops.
  - CUDA GPU compute and SGEMM kernels.
  - `main.cpp`: The unified CLI runner for `SysPulse.exe` / `laptop_benchmark.exe`.
  - Windows resource files (`version.rc`) containing author/publisher metadata.
- **Strict Prohibition:** Do NOT introduce Python interpreters or external network libraries into the native benchmark executable.

---

## 3. `audit_engine/` — Analytical Evaluation & Audit Suite
- **Ownership:** Technical evaluation, physics scaling, deal-breaker logic, value economics, and reporting.
- **Allowed Contents:**
  - `models.py`: Strongly typed data models and provenance confidence tracking.
  - `validator.py`: Input schema validation and pre-audit sanity checks.
  - `power_analyzer.py`: Cross-load power deficit and battery discharge models.
  - `upgradeability.py`: Serviceability, modularity, and 5-year longevity scoring.
  - `performance_engine.py`: IPC modeling, sustained throttling, and benchmark telemetry ingestion.
  - `workload_engine.py`: 6-domain workload suitability calculations.
  - `dealbreaker_engine.py`: Hard capacity limit and hardware trap detection.
  - `value_engine.py`: Hardware unit economics (Performance/₹, VRAM/₹).
  - `anti_marketing.py`: Buzzword scan vs silicon reality cross-examination.
  - `future_proofing.py`: 1/3/5-year horizons and user-priority tailored verdicts.
  - `comparator.py`: Multi-laptop head-to-head comparison engine.
  - `report_generator.py`: Markdown and self-contained interactive HTML dossiers.
  - `main.py`: Master CLI orchestrator.
- **Strict Prohibition:** Do NOT hardcode laptop models or specifications as universal truths; all scoring must be dynamically derived from physics formulas and input data.

---

## 4. `schemas/` — Machine-Readable Contracts
- **Ownership:** Formal JSON Schemas (Draft-07) governing laptop hardware specifications.
- **Allowed Contents:**
  - `schemas/laptop_schema.json`: The single source of truth for specification validation.
- **Strict Prohibition:** Never introduce breaking schema changes without updating `validator.py` and all test fixtures in `examples/`.

---

## 5. `results/` — Runtime Output Artifacts
- **Ownership:** Generated benchmark telemetry, audit records, and HTML dossiers.
- **Allowed Contents:**
  - `.gitkeep` (tracked to preserve directory structure).
- **Strict Prohibition:** Never commit generated result files (`.json`, `.html`, `.csv`) into source control; they are strictly ignored by `.gitignore`.

---

## 6. `docs/` — Human-Facing Documentation
- **Ownership:** Architectural whitepapers, engineering specifications, and user manuals.
- **Allowed Contents:**
  - `ARCHITECTURE.md`, `BUYER_AUDIT_SPEC.md`, `QUICKSTART.md`.

---

## 7. `SysPulse_Portable/` — Standalone Distribution Bundle
- **Ownership:** Packaged retail distribution for end-users running on target laptops.
- **Allowed Contents:**
  - `SysPulse.exe` (Digitally signed standalone binary).
  - `vcomp140.dll` (Bundled OpenMP runtime).
  - `results/` (Local output folder).
- **Strict Prohibition:** Never add source files, scripts, or debug artifacts into `SysPulse_Portable/`.
