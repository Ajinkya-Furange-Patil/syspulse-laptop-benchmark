# ⚡ SysPulse: All-in-One PC Benchmark & 34-Point Laptop Buyer Inspection Suite

<div align="center">

[![C++20](https://img.shields.io/badge/Language-C%2B%2B20-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)](https://en.wikipedia.org/wiki/C%2B%2B20)
[![CUDA](https://img.shields.io/badge/GPU%20Compute-CUDA%2012%2F13-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](https://developer.nvidia.com/cuda-toolkit)
[![Platform](https://img.shields.io/badge/Platform-Windows%20x64-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg?style=for-the-badge)](CONTRIBUTING.md)

**A single zero-dependency tool to audit, benchmark, and stress-test your PC hardware before buying or tuning.**

[Quick Start](#-quick-start-60-seconds) • [What It Audits](#-what-it-audits-the-34-point-checklist) • [Reports](#-interactive-html-reports) • [Architecture](#-architecture--how-it-works) • [Roadmap & Suggestions](#-roadmap--suggestions-for-students) • [Contributing](#-contributing)

</div>

---

## 🎯 The Problem This Solves

When students and developers buy a laptop or evaluate their PC, **OEM specification sheets often hide the truth**:
- Did the manufacturer solder **single-channel RAM** (strangling gaming 1% lows and compilation speeds by up to 35%)?
- Does the discrete GPU have an anemic **35W TGP** or a full **95W+ power limit**?
- Does the laptop **thermal throttle** after just 30 seconds of heavy compilation or CAD rendering?
- Will the GPU VRAM fit modern local AI models (**Llama 3 8B, Phi-3, Stable Diffusion**)?
- Do the CPU and GPU choke each other over a **shared heat-pipe and VRM power budget**?

**SysPulse answers every single one of these questions with a single tool.** In under 60 seconds, it runs low-level hardware probes, microbenchmarks, and cross-stress workloads, delivering an overall score out of 100 alongside an **interactive HTML inspection report**.

---

## ✨ Key Features & Capabilities

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 SYSPULSE BENCHMARK ENGINE                              │
├───────────────────┬───────────────────┬───────────────────┬────────────────────────────┤
│  ⚡ CPU & SIMD    │  🧠 MEMORY SYSTEM │  🚀 GPU & AI      │  🔥 THERMAL & POWER        │
│  • Core Topology  │  • Dual-Channel   │  • SGEMM TFLOPs   │  • Sustained Drop %        │
│  • AVX2 & AVX-512 │  • Bandwidth GB/s │  • GELU & VRAM BW │  • CPU+GPU Cross-Throttle  │
│  • Multi-Scaling  │  • DRAM Latency   │  • LLM Ceiling    │  • TjMax Safety Headroom   │
└───────────────────┴───────────────────┴───────────────────┴────────────────────────────┘
```

- 🔬 **Zero-Hardcoding Dynamic Hardware Probing**: Reads CPU topology, physical vs logical cores, cache, PCIe generation, and RAM bus channels directly via Win32 WMI and CPUID register flags.
- ⚡ **AVX2 & AVX-512 Vector Engine**: Measures raw FP32/FP64 mathematical throughput and detects microarchitectural SIMD acceleration.
- 🧠 **RAM Dual-Channel Verification**: Stream tests memory bandwidth (GB/s) and flags single-channel bandwidth bottlenecks.
- 🤖 **Native CUDA AI & Gaming Workloads**: Runs 2D shared-memory tiled SGEMM matrix multiplication and activation kernels to calculate real TFLOPs, VRAM bandwidth, and local LLM parameter ceilings.
- 🔌 **Universal CPU Fallback**: Automatically compiles and executes on **any Windows PC** (including Intel Iris Xe and AMD Radeon systems) even if CUDA is not installed.
- ⚖️ **Simultaneous Cross-Throttling Stress**: Runs CPU OpenMP workers alongside GPU compute kernels simultaneously to reveal shared thermal and VRM power-starvation limits.
- 📋 **34-Point Buyer Inspection**: Translates technical measurements into a plain-English scorecard with **Strengths (Pros)**, **Cautions**, and **Red Flag Dealbreakers**.
- 📊 **Zero-Dependency Interactive HTML Reports**: Generates self-contained dashboards with dark mode aesthetics and instant status filters for offline viewing and sharing.

---

## 🚀 Quick Start (60 Seconds)

### Method 1: The One-Click Launcher (Easiest)
Just clone or download the repository, then double-click:
```cmd
run.bat
```
> **What happens automatically**:
> 1. Detects your MSVC C++ compiler and CUDA Toolkit.
> 2. Compiles the project into `bin\laptop_benchmark.exe` (if not already built).
> 3. Executes the full hardware evaluation suite.
> 4. Launches the generated interactive HTML report in your default web browser!

---

### Method 2: Command-Line Interface (CLI)

#### 1. Compile the Suite
```cmd
build.bat
```
*(If NVIDIA CUDA is detected, native GPU kernels are compiled; otherwise, it builds with universal CPU fallback mode automatically!)*

#### 2. Run the Benchmark
```cmd
bin\laptop_benchmark.exe
```

#### 3. Custom Flags
```cmd
# Run a 30-second sustained stress test with 4096x4096 AI matrix
bin\laptop_benchmark.exe --duration 30 --matrix 4096

# Display help and options
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

## 📊 Interactive HTML Reports

Upon completion, SysPulse automatically exports and opens:
- 📄 **`results/laptop_buyer_inspection.html`**: Complete 34-point scorecard with interactive category and status filter buttons (`[All]`, `[Pass]`, `[Caution]`, `[Dealbreaker]`), pros/cons lists, and upgrade advice.
- 📄 **`results/performance_report.html`**: Technical benchmark report detailing compute TFLOPs, memory bandwidth, latency, and thermal curves.
- 💾 **`results/laptop_buyer_audit.json`**: Machine-readable JSON telemetry for automated analysis or comparisons.

---

## 📁 Repository Structure

```
SysPulse/
├── .gitattributes              # Line-ending and Git normalization
├── .gitignore                  # Clean repository filter (ignores bins/objs/dumps)
├── LICENSE                     # MIT Open Source License
├── README.md                   # This documentation
├── CONTRIBUTING.md             # Developer & student contribution guide
├── CMakeLists.txt              # Cross-IDE CMake configuration
├── build.bat                   # Master 1-click intelligent compiler (MSVC + CUDA / CPU)
├── run.bat                     # Master 1-click runner (auto-builds + opens report)
├── clean.bat                   # Utility script to clean bin/ and build/ folders
├── docs/                       # Detailed guides and specifications
│   ├── ARCHITECTURE.md         # Engine architecture, WMI prober & kernel design
│   ├── BUYER_AUDIT_SPEC.md     # In-depth breakdown of all 34 hardware checkpoints
│   └── GITHUB_PUBLISH_GUIDE.md # Step-by-step guide to push this repo to GitHub
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
│   └── phases/                 # Granular individual test modules
│       ├── phase0_audit/       # Hardware topology probe binary
│       ├── phase1_baseline/    # System idle calibration
│       ├── phase2_cpu_single/  # AVX-512 single-core microbenchmark
│       ├── phase3_cpu_multi/   # OpenMP multi-thread scalability benchmark
│       └── phase4_cpu_sustained/# 60-second thermal degradation test
├── scripts/                    # Modular build scripts for individual phases
│   └── build_phases/           # Individual phase build runners (Phase 0 to 4)
└── results/                    # Output directory for HTML and JSON reports
    └── .gitkeep
```

---

## 💡 Roadmap & Suggestions for Students

If you are a student or developer looking to expand this project or build high-impact portfolio features, here are 7 recommended enhancements:

1. 🌐 **DirectX 12 / DirectML GPU Support**:
   - *Goal*: Add a fallback compute kernel using DirectML or DirectCompute so AMD Radeon and Intel Arc / Iris Xe GPUs can be benchmarked for TFLOPs without NVIDIA CUDA.
2. 💾 **CrystalDiskMark-Style Disk Stress**:
   - *Goal*: Benchmark sequential and 4K random read/write speeds, verify NVMe cache endurance, and check for SLC cache drop-offs during prolonged file transfers.
3. 🔋 **Battery Drain & Efficiency Benchmark**:
   - *Goal*: Query battery discharge rate (in milliwatts via `GetSystemPowerStatus`) during active stress to compute a **Performance-per-Watt (PPW)** score and estimate real campus battery life.
4. 🖥️ **Display & Peripherals QA Helper**:
   - *Goal*: Include an interactive full-screen dead-pixel checker, screen refresh rate validator, and keyboard ghosting diagnostic (ideal for students buying second-hand laptops).
5. 🖨️ **1-Click PDF Report Export**:
   - *Goal*: Add a print-ready CSS stylesheet and PDF generation trigger in the HTML report so students can attach inspection reports when negotiating prices or claiming warranties.
6. 🌍 **Community Benchmark Leaderboard**:
   - *Goal*: Allow users to voluntarily upload anonymized JSON telemetry to a public GitHub Discussions thread or web API to compare scores against identical laptop models globally.
7. 🎛️ **Lightweight Native GUI (ImGui / Tauri)**:
   - *Goal*: Build a modern desktop GUI showing live real-time graphs of CPU/GPU clock speeds, fan speeds, temperatures, and power draw during testing.

---

## 💻 System Requirements

| Component | Minimum | Recommended |
| :--- | :--- | :--- |
| **Operating System** | Windows 10 / 11 (64-bit) | Windows 11 (64-bit) |
| **Compiler** | Visual Studio 2019 / 2022 Build Tools (with C++ Desktop workload) | Visual Studio 2022 Community / Build Tools |
| **GPU Acceleration** | Any integrated or discrete GPU (Universal CPU mode enabled) | NVIDIA GeForce / RTX GPU with CUDA Toolkit 12.x or 13.x |
| **RAM** | 4 GB | 16 GB+ |

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on code style, submitting issues, and opening pull requests.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

Developed with ❤️ by **Ajinkya Patil** for students, developers, and hardware enthusiasts worldwide.
