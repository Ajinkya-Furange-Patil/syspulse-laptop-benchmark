# ⚡ SysPulse: All-in-One PC Benchmark & 34-Point Laptop Buyer Inspection Suite

<div align="center">

[![Version: v1.1.0](https://img.shields.io/badge/Release-v1.1.0-blueviolet?style=for-the-badge&logo=github)](https://github.com/Ajinkya-Furange-Patil/syspulse-laptop-benchmark/releases/tag/v1.1.0)
[![C++20](https://img.shields.io/badge/Language-C%2B%2B20-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)](https://en.wikipedia.org/wiki/C%2B%2B20)
[![CUDA](https://img.shields.io/badge/GPU%20Compute-CUDA%2012%2F13-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](https://developer.nvidia.com/cuda-toolkit)
[![Platform](https://img.shields.io/badge/Platform-Windows%20x64-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg?style=for-the-badge)](CONTRIBUTING.md)

**A single zero-dependency tool to audit, benchmark, and stress-test PC hardware before buying or tuning.**

### 📥 [Click Here to Download Standalone Executable (SysPulse_Portable.zip)](https://github.com/Ajinkya-Furange-Patil/syspulse-laptop-benchmark/releases/latest/download/SysPulse_Portable.zip)
*⚡ Zero Setup • No Visual Studio • No Python • No CUDA SDK • No Admin Rights • Runs Completely Offline on Any Laptop!*

[Direct Download](#-download-and-test-in-retail-shops-zero-setup) • [Quick Start](#-quick-start-for-developers--students-building-from-source) • [What It Audits](#-what-it-audits-the-34-point-checklist) • [Buyer Audit Engine](#-syspulse-laptop-buyer-audit-engine-phases-1--22) • [AI Guardrail System](#-ai-operating-manual--guardrail-system-agentsmd--ai) • [Reports](#-interactive-html-reports)

</div>

---

## 🎯 The Problem This Solves

When students and developers buy a laptop or evaluate their PC, **OEM specification sheets often hide the truth**:
- Did the manufacturer solder **single-channel RAM** (strangling gaming 1% lows and compilation speeds by up to 35%)?
- Does the discrete GPU have an anemic **35W–45W TGP** or a full **95W–140W power limit**?
- Does the laptop **thermal throttle** after just 30 seconds of heavy compilation or CAD rendering?
- Will the GPU VRAM fit modern local AI models (**Llama 3 8B, Phi-3, Stable Diffusion XL**)?
- Do the CPU and GPU choke each other over a **shared heat-pipe and VRM power budget**?
- Does the laptop **actively discharge its battery while plugged into the wall** due to an undersized AC adapter?

**SysPulse answers every single one of these questions with a single tool.** In under 60 seconds, it runs low-level hardware probes, microbenchmarks, and cross-stress workloads, delivering an overall score out of 100 alongside an **interactive HTML inspection report**.

---

## 🎒 Download and Test in Retail Shops (Zero Setup)

If you are visiting a laptop showroom (e.g. Croma, Reliance Digital, Best Buy, or checking a refurbished laptop from OLX), **you do not have time to install Visual Studio, C++ compilers, or Python**. 

**You can run SysPulse directly from a USB flash drive with ZERO external setup!**

### 📦 3-Step Testing Walkthrough:
1. **Download the Portable Bundle**:
   - Download **[SysPulse_Portable.zip](https://github.com/Ajinkya-Furange-Patil/syspulse-laptop-benchmark/releases/latest/download/SysPulse_Portable.zip)** (only ~360 KB!).
2. **Copy to Any USB Drive**:
   - Extract the `.zip` archive onto your USB thumbdrive.
3. **Plug & Run on the Demo / New Laptop**:
   - Plug your USB drive into the laptop in the store.
   - Double-click **`SysPulse.exe`**.
   - Wait **30 to 60 seconds** as it stress-tests CPU, RAM, GPU, thermals, and storage.
   - The interactive **34-point Laptop Buyer Inspection Report** will automatically pop up in Microsoft Edge / Chrome!

### 🛡️ Why It Runs 100% Independently:
- **Digitally Signed Standalone Binary**: `SysPulse.exe` is signed with the official developer Authenticode certificate (`Ajinkya Furange`) and contains embedded Windows Version Resource metadata.
- **No External Runtimes Needed**: Relies strictly on native Windows OS libraries (`kernel32.dll`, `user32.dll`, `ole32.dll`, `advapi32.dll`) that exist on **all Windows 10 & 11 PCs**. The OpenMP runtime (`vcomp140.dll`) is bundled side-by-side.
- **Hardware-Agnostic Fallback**:
  - If the laptop has an **NVIDIA GPU**, it automatically runs native CUDA SGEMM AI and VRAM bandwidth benchmarks.
  - If the laptop has an **Intel Iris Xe, Intel UHD, or AMD Radeon** iGPU, it automatically skips CUDA and runs CPU, RAM, thermal throttling, storage, and buyer checklist tests without errors.
- **No Administrator Elevation (UAC) Required**: Standard user permissions are sufficient for all WMI telemetry, CPUID probes, and memory benchmarks.
- **No Internet Required**: Completely self-contained offline evaluation.

---

## 🚀 Quick Start (For Developers & Students Building from Source)

If you have Visual Studio 2019/2022 or Build Tools installed and want to build from source:

### Method 1: The One-Click Runner
```cmd
# Clone the repository
git clone https://github.com/Ajinkya-Furange-Patil/syspulse-laptop-benchmark.git
cd syspulse-laptop-benchmark

# Auto-compiles and launches the benchmark + browser report
run.bat
```

### Method 2: Manual Build & CLI Flags
```cmd
# 1. Compile the master suite (auto-detects MSVC and CUDA with CPU fallback)
build.bat

# 2. Package your own standalone portable USB distribution
package_portable.bat

# 3. Run with custom benchmark durations
bin\laptop_benchmark.exe --duration 30 --matrix 4096

# 4. Display help
bin\laptop_benchmark.exe --help
```

---

## 📋 What It Audits (The 34-Point Checklist)

The suite evaluates 34 strict hardware rules across 6 core categories:

| Category | Weight | What It Tests |
| :--- | :---: | :--- |
| **1. CPU Architecture & Multi-Core** | 20 pts | Physical cores, SMT scaling, AVX-512 / AVX2 vector flags, base vs boost clocks |
| **2. GPU Silicon & TGP Power** | 25 pts | Discrete vs Integrated GPU, SM count, CUDA cores, TGP power headroom |
| **3. GPU VRAM & Local AI Ceilings** | 15 pts | Dedicated VRAM (GB), memory bus width, LLM model fit (Llama-3, Phi-3, Gemma) |
| **4. RAM Subsystem & Topology** | 15 pts | Dual-channel (128-bit) vs single-channel (64-bit), MT/s speed, GB capacity |
| **5. Storage Speed & Expansion** | 10 pts | NVMe PCIe Gen3/Gen4/Gen5 detection, sequential read throughput (MB/s) |
| **6. Cooling, Thermals & Cross-Load** | 15 pts | Peak temperatures, TjMax distance, sustained drop %, CPU+GPU cross-throttling |

### 🎯 Target Use-Case Suitability Scores
Every audit translates raw numbers into scores (0–100) and tiers for:
- 🎮 **Modern Gaming**: Esports / 1080p Medium / 1440p High / 4K Ultra
- 🤖 **AI & Local LLM Research**: Entry Quantized (<3.8B) / Capable (7B–8B) / Workstation (70B)
- 💻 **Programming, VMs & Docker**: Light coding / Full-stack / Multi-VM & Heavy compilation
- 🔋 **Campus Portability & Efficiency**: Battery balance, cooling noise, and thermal stability

---

## 🔬 SysPulse Laptop Buyer Audit Engine (Phases 1 – 22)

In addition to physical hardware benchmarking, SysPulse includes a **22-Phase Laptop Buyer Audit Engine** designed to answer:
> *"Is this laptop actually engineered for your specific workload, or is it being sold with misleading headline specifications?"*

### 💡 Core Engineering Capabilities:
1. **Dynamic Architecture & Zero Hardcoding**: Every metric is calculated dynamically from silicon data, OEM firmware limits (PL1/PL2/TGP), microarchitecture IPC tables, and sub-linear power scaling curves ($P^{0.68}$).
2. **Dedicated Power Delivery & Battery Crossload Engine**: Detects when high-end CPUs and GPUs are throttled by undersized power adapters ($P_{\text{adapter}} < \text{PL1} + \text{TGP} + P_{\text{aux}}$), causing active hybrid battery drain on AC power.
3. **Hardware Modularity & 5-Year Ownership**: Audits soldered vs SODIMM RAM, M.2 expansion slots, chassis fasteners (Philips vs Torx), glue usage, and predicts 3-to-5 year functional lifespans.
4. **Hard Deal-Breaker & Bottleneck Engine**: Evaluates non-negotiable capacity cliffs (e.g. 4GB VRAM hard stop for AI/LLMs, single-channel RAM compile bottlenecks, 18ms display ghosting traps) and computes inter-subsystem throughput loss percentages.
5. **Multi-Domain Workload Scoring (6 Domains)**:
   - 🎮 **Gaming**: 1080p, 1440p, High-Hz Esports, Ray Tracing, and MUX switch verification.
   - 🤖 **AI & Local LLMs**: Hard VRAM capacity limits, Llama-3 8B parameter fit, QLoRA fine-tuning viability, Stable Diffusion XL feasibility.
   - 💻 **Software Development**: Multi-core build compilation, Docker/VM RAM headroom, vertical code display aspect ratio.
   - ⚙️ **Engineering & CAD**: SolidWorks single-thread viewport, FEA/CFD simulation, AVX-512 acceleration.
   - 🎨 **Content Creation**: 100% DCI-P3 color gamut, hardware AV1/NVENC dual encoders, 4K timeline scrubbing.
   - 🔋 **Campus Portability**: True travel weight (chassis + charger), off-charger battery hours, USB-C PD travel charging.
6. **Anti-Marketing Audit**: Automatically scans promotional headlines for deceptive buzzwords (e.g. *"AI-Powered"*, *"Gaming Beast"*) and cross-examines them against physical hardware realities.
7. **Hardware Unit Economics & True Value Analysis**: Calculates capability delivered per 10,000 INR (Performance/₹, VRAM/₹, GPU TFLOPs/₹) and identifies overpriced marketing traps.
8. **Subsystem Confidence & Conflict Resolution**: Ranks data authority (Benchmark > OEM Spec > Teardowns > User Input) and prevents false zero values for missing data.
9. **Head-to-Head Comparison Engine**: Compares multiple laptops side-by-side across every parameter to declare domain winners.
10. **Explainable "WHY?" Trees**: Every deduction logs its exact formula, impact, and remediation.
11. **User-Priority Tailored Final Verdicts**: Enforces the **No Universal Winner** rule—identical hardware can be an `EXCELLENT BUY` for CAD while being a `HARD NO` for local AI.

### 🚀 Audit Engine CLI Commands:

```powershell
# 1. Audit the physical machine currently running SysPulse (Live Hardware Mode)
python audit_engine/main.py --live --priority Software_Development --html results/audit_dossier.html

# 2. Audit a specific laptop specification sheet (e.g. for AI research)
python audit_engine/main.py --file examples/engineered_workstation.json --priority AI_ML

# 3. Compare multiple laptops side-by-side in head-to-head competition
python audit_engine/main.py --compare examples/deceptive_paper_tiger.json examples/engineered_workstation.json examples/host_physical_laptop.json

# 4. Run the master end-to-end test suite across all 22 engineering phases
python test_all_phases.py
```

---

## 🛡️ AI Operating Manual & Guardrail System (`AGENTS.md` & `.ai/`)

SysPulse includes a **strict AI operating contract and guardrail system** to ensure that AI coding assistants operating in this repository preserve architectural rigor, never invent specifications, and adhere to physical evidence:

- [**`AGENTS.md`**](file:///AGENTS.md): The mandatory master entrypoint for AI agents defining non-negotiables, the source-of-truth hierarchy, unknown data policies, and definition of done.
- [**`.ai/constitution/`**](file:///.ai/constitution): Inviolable engineering principles ([`PROJECT_CONSTITUTION.md`](file:///.ai/constitution/PROJECT_CONSTITUTION.md), [`NON_NEGOTIABLES.md`](file:///.ai/constitution/NON_NEGOTIABLES.md), [`SCOPE.md`](file:///.ai/constitution/SCOPE.md), [`TERMINOLOGY.md`](file:///.ai/constitution/TERMINOLOGY.md)).
- [**`.ai/architecture/`**](file:///.ai/architecture): Component boundaries, system data flow, and zero-network dependency policies.
- [**`.ai/engineering/`**](file:///.ai/engineering): Coding standards for C++20 and typed Python, change management, testing rules, and performance engineering.
- [**`.ai/benchmark/`**](file:///.ai/benchmark): Benchmark validity rules, canonical metric dictionaries, telemetry acquisition, and stress safety.
- [**`.ai/audit/`**](file:///.ai/audit): Scoring philosophy, deal-breaker rules, confidence tracking, anti-marketing verification, and workload models.
- [**`.ai/agent/`**](file:///.ai/agent): Step-by-step agent workflow, reconnaissance checklists, and mandatory stop conditions.
- [**`.ai/decisions/`**](file:///.ai/decisions): Architectural Decision Records ([ADR-001](file:///.ai/decisions/ADR-001-scoring-model.md) through [ADR-005](file:///.ai/decisions/ADR-005-offline-portability.md)).
- [**`.ai/tasks/`**](file:///.ai/tasks): Task specification templates and persistent AI engineering changelog ([`AI_CHANGELOG.md`](file:///.ai/tasks/AI_CHANGELOG.md)).

---

## 📊 Interactive HTML Reports

Upon completion, SysPulse exports rich, zero-external-CDN standalone reports:
- 📄 **`results/laptop_buyer_inspection.html`**: Complete 34-point native scorecard with interactive category filter buttons (`[All]`, `[Pass]`, `[Caution]`, `[Dealbreaker]`), pros/cons lists, and upgrade advice.
- 📄 **`results/audit_dossier.html`**: Complete technical buyer dossier with domain scorecards, deal-breaker cards, anti-marketing audits, and future-proofing projections.
- 📄 **`results/performance_report.html`**: Technical benchmark report detailing compute TFLOPs, memory bandwidth, latency, and thermal curves.
- 💾 **`results/laptop_buyer_audit.json`**: Machine-readable JSON telemetry for automated analysis or comparisons.

---

## 📁 Repository Structure

```
SysPulse/
├── AGENTS.md                   # Canonical AI engineering contract (Master Entrypoint)
├── CLAUDE.md                   # Anthropic Claude compatibility pointer
├── GEMINI.md                   # Google Gemini compatibility pointer
├── .github/
│   └── copilot-instructions.md # GitHub Copilot compatibility pointer
├── .ai/                        # AI Operating Manual & Guardrail System
│   ├── README.md               # Guardrail overview and index
│   ├── constitution/           # Inviolable philosophy & non-negotiables
│   ├── architecture/           # Component boundaries & dependency policy
│   ├── engineering/            # C++20 & Python coding rules, change policy
│   ├── benchmark/              # Benchmark philosophy, metrics & telemetry
│   ├── audit/                  # Scoring rules, deal-breakers & confidence
│   ├── agent/                  # 8-phase workflow & stop conditions
│   ├── decisions/              # Architecture Decision Records (ADR-001 to 005)
│   └── tasks/                  # Task templates & persistent AI changelog
├── audit_engine/               # 22-Phase Python Laptop Buyer Audit Engine
│   ├── models.py               # Strongly typed data models with AuditField[T]
│   ├── validator.py            # Draft-07 schema validator & sanity auditor
│   ├── db.py                   # 3NF relational SQLite catalog manager
│   ├── power_analyzer.py       # Crossload power deficit & battery drain model
│   ├── upgradeability.py       # RAM/SSD modularity & 5-year ownership predictor
│   ├── performance_engine.py   # IPC microarch scaling & sustained throttling
│   ├── benchmark_connector.py  # Ingestion connector for native results/ telemetry
│   ├── workload_engine.py      # 6-domain suitability scoring (Gaming, AI, Dev...)
│   ├── dealbreaker_engine.py   # Fatal blocker & bottleneck throughput loss
│   ├── value_engine.py         # Hardware unit economics (Perf/₹, VRAM/₹)
│   ├── confidence_engine.py    # Provenance tracking & conflict resolution
│   ├── anti_marketing.py       # Buzzword scan vs silicon reality cross-examination
│   ├── future_proofing.py      # 1/3/5-year horizons & tailored verdicts
│   ├── comparator.py           # Multi-laptop head-to-head comparison
│   ├── report_generator.py     # Markdown & standalone interactive HTML dossiers
│   ├── main.py                 # Master CLI orchestrator
│   └── test_phase*.py          # Granular phase test harnesses
├── schemas/
│   └── laptop_schema.json      # Draft-07 JSON specification schema contract
├── examples/                   # Audited laptop specification test fixtures
│   ├── deceptive_paper_tiger.json
│   ├── engineered_workstation.json
│   ├── host_physical_laptop.json
│   └── severe_power_deficit.json
├── include/                    # Core C++ header modules
│   ├── sys_detect.hpp          # Win32 WMI & CPUID hardware probing
│   ├── ram_bench.hpp           # Streaming memory bandwidth & latency benchmarks
│   ├── cuda_bench.cuh          # CUDA AI GEMM & GPU workload header
│   ├── bottleneck_engine.hpp   # Bottleneck detection and scoring algorithms
│   └── buyer_checklist.hpp     # 34-Point buyer audit rules & HTML generator
├── src/                        # Implementation files
│   ├── main.cpp                # Master unified benchmark runner
│   ├── cuda_kernels.cu         # Native CUDA kernels (SGEMM, GELU, VRAM streaming)
│   ├── cuda_stub.cpp           # Transparent fallback for systems without CUDA
│   └── version.rc              # Windows PE Version resource (v1.1.0 metadata)
├── SysPulse_Portable/          # Clean retail USB distribution folder
│   ├── SysPulse.exe            # Digitally signed 64-bit benchmark executable
│   ├── vcomp140.dll            # Bundled OpenMP runtime DLL
│   └── results/                # Output directory for HTML and JSON reports
├── SysPulse_Portable.zip       # Standalone ~360 KB portable USB archive
├── test_all_phases.py          # Master verification suite across all 22 phases
├── build.bat                   # Master intelligent compiler (MSVC + CUDA / CPU)
├── run.bat                     # Master 1-click runner (auto-builds + opens report)
├── clean.bat                   # Clean bin/ and build/ folders
├── package_portable.bat        # Automated portable packager and code signer
├── CMakeLists.txt              # Cross-IDE CMake configuration
├── CONTRIBUTING.md             # Developer & student contribution guide
├── LICENSE                     # MIT Open Source License
└── results/                    # Runtime benchmark output folder (.gitkeep)
```

---

## 💻 System Requirements

| Component | Minimum | Recommended |
| :--- | :--- | :--- |
| **Operating System** | Windows 10 / 11 (64-bit) | Windows 11 (64-bit) |
| **Compiler (From Source)** | Visual Studio 2019 / 2022 Build Tools (with C++ Desktop workload) | Visual Studio 2022 Community / Build Tools |
| **GPU Acceleration** | Any integrated or discrete GPU (Universal CPU mode enabled) | NVIDIA GeForce / RTX GPU with CUDA Toolkit 12.x or 13.x |
| **RAM** | 4 GB | 16 GB+ |
| **Portable Binary** | Standalone `SysPulse.exe` (Runs on any Windows 10/11 x64 PC with zero dependencies) |

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md) for guidelines on code style, submitting issues, and opening pull requests.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

Developed with ❤️ by **Ajinkya Furange** for students, developers, and hardware enthusiasts worldwide.
