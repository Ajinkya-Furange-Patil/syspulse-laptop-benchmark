# SysPulse Data Flow Pipeline

This document details the exact end-to-end data transformation pipeline across SysPulse.

---

## 1. Pipeline Stages

```
[Raw Specification JSON / Native Sensors]
                   │
                   ▼ (1)
[SpecificationValidator.validate_and_load()]
                   │  - Validates against schemas/laptop_schema.json
                   │  - Checks physical sanity bounds
                   │  - Assigns AuditField[T] with provenance & confidence
                   │
                   ▼ (2)
[LaptopSpecification (Typed In-Memory Model)]
   │        │            │             │            │
   ▼ (3A)   ▼ (3B)       ▼ (3C)        ▼ (3D)       ▼ (3E)
[Power]  [Upgrade]  [Performance]  [Workload]  [Dealbreakers]
   │        │            │             │            │
   └────────┴────────────┼─────────────┴────────────┘
                         │
                         ▼ (4)
              [Value & Anti-Marketing]
                         │
                         ▼ (5)
              [Future-Proofing & Verdict]
                         │
                         ▼ (6)
          [Multi-Format Output Generation]
          ├─► JSON Machine Records
          ├─► Markdown Executive Dossier
          └─► Zero-Dependency HTML Report
```

---

## 2. Stage Details

### Stage 1: Validation & Provenance Ingestion
- Ingests raw JSON data (or telemetry-derived JSON).
- Validates against `schemas/laptop_schema.json` using Draft-07 syntax.
- Performs sanity checks: verifies $PL1 \le PL2$, that discrete GPUs define VRAM, that total storage matches drive capacity, and flags unconfirmed fields.

### Stage 2: Typed Model Construction
- Creates instances of `LaptopSpecification` with nested sub-models: `CPUSpecification`, `GPUSpecification`, `MemorySpecification`, `StorageSpecification`, `DisplaySpecification`, `PowerSpecification`, `CoolingSpecification`, `ChassisSpecification`, and `MetadataSpecification`.
- Every sensitive field is wrapped in `AuditField[T]` holding its value, unit, status (`CONFIRMED`, `ESTIMATED`, `UNKNOWN`), confidence (0.0 to 1.0), and data source (`BENCHMARK_MEASURED`, `OEM_SPEC`, etc.).

### Stage 3: Subsystem Domain Evaluation
- **Power Analysis:** Computes dynamic auxiliary draw $P_{\text{aux}}$, total cross-load demand, adapter balance, and flags battery drain on AC.
- **Modularity & Longevity:** Scores RAM upgradeability, M.2 expansion, fastener accessibility, and predicts 3-to-5-year lifespan.
- **Performance Modeling:** Evaluates sustained multi-core and single-core performance using microarchitecture IPC and sub-linear power scaling ($P^{0.68}$); blends live C++/CUDA telemetry if available.
- **Workload Scoring:** Calculates scores across 6 distinct domains independently: Gaming, AI/ML, Software Development, Engineering/CAD, Content Creation, and Campus Portability.
- **Deal-Breakers & Bottlenecks:** Detects fatal constraints (e.g. sub-6GB VRAM for AI, single-channel RAM, severe power deficits) and inter-subsystem bottlenecks with % throughput loss.

### Stage 4: Unit Economics & Marketing Audit
- Calculates capability-per-rupee (Performance/₹, VRAM/₹, GPU TFLOPs/₹) relative to the asking price.
- Scans promotional headline text for deceptive marketing buzzwords and contrasts them with physical measurements.

### Stage 5: Future-Proofing & Tailored Verdict Synthesis
- Evaluates 1-year, 3-year, and 5-year hardware viability.
- Generates a final tailored buying verdict conditioned directly on the user's primary priority.

### Stage 6: Report Generation & Persistence
- Writes output files to `results/` in structured JSON, console/Markdown, and interactive standalone HTML formats.
- Automatically launches the report in the default browser when running in native desktop mode.
