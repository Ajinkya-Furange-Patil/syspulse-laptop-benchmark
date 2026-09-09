# ⚡ SysPulse: All-in-One PC Benchmark & 34-Point Laptop Buyer Inspection Suite

<div align="center">

[![C++20](https://img.shields.io/badge/Language-C%2B%2B20-00599C?style=for-the-badge&logo=c%2B%2B&logoColor=white)](https://en.wikipedia.org/wiki/C%2B%2B20)
[![CUDA](https://img.shields.io/badge/GPU%20Compute-CUDA%2012%2F13-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](https://developer.nvidia.com/cuda-toolkit)
[![Platform](https://img.shields.io/badge/Platform-Windows%20x64-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg?style=for-the-badge)](CONTRIBUTING.md)

**A single zero-dependency tool to audit, benchmark, and stress-test your PC hardware before buying or tuning.**

### 📥 [Click Here to Download Standalone Executable (SysPulse_Portable.zip)](https://github.com/Ajinkya-Furange-Patil/syspulse-laptop-benchmark/releases/latest/download/SysPulse_Portable.zip)
*⚡ Zero Setup • No Visual Studio • No Python • No CUDA SDK • No Admin Rights • Runs Completely Offline on Any Laptop!*

[Direct Download](#-download-and-test-in-retail-shops-zero-setup) • [Quick Start](#-quick-start) • [What It Audits](#-what-it-audits-the-34-point-checklist) • [Reports](#-interactive-html-reports) • [Roadmap](#-roadmap--suggestions-for-students)

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

## 🎒 Download and Test in Retail Shops (Zero Setup)

If you are visiting a laptop showroom (e.g. Croma, Reliance Digital, Best Buy, or checking a refurbished laptop from OLX), **you do not have time to install Visual Studio, C++ compilers, or Python**. 

**You can run SysPulse directly from a USB flash drive with ZERO external setup!**

### 📦 3-Step Testing Walkthrough:
1. **Download the Portable Bundle**:
   - Download **[SysPulse_Portable.zip](https://github.com/Ajinkya-Furange-Patil/syspulse-laptop-benchmark/releases/latest/download/SysPulse_Portable.zip)** (only ~360 KB!).
2. **Copy to Any USB Drive**:
   - Extract the `.zip` archive and copy the folder onto your USB pendrive.
3. **Plug & Run on the Demo / New Laptop**:
   - Plug your USB drive into the laptop in the store.
   - Double-click **`run_portable.bat`** (or `laptop_benchmark.exe`).
   - Wait **30 to 60 seconds** as it stress-tests CPU, RAM, GPU, thermals, and storage.
   - The interactive **34-point Laptop Buyer Inspection Report** will automatically pop up in Microsoft Edge / Chrome!

### 🛡️ Why It Runs 100% Independently:
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
---

## 🔬 SysPulse Laptop Buyer Audit Engine (Phases 1 – 22)

In addition to physical hardware benchmarking, SysPulse includes a **Laptop Buyer Audit Engine** designed to answer:
> *"Is this laptop actually engineered for your specific workload, or is it a paper tiger being sold with misleading headline specifications?"*

### 💡 Core Capabilities:
1. **Dynamic Architecture & Zero Hardcoding**: Every metric is calculated dynamically from silicon data, OEM firmware limits (PL1/PL2/TGP), and physics curves.
2. **Dedicated Power Delivery & Battery Crossload Engine**: Detects when high-end CPUs and GPUs are throttled by undersized power adapters ($P_{\text{adapter}} < \text{PL1} + \text{TGP} + \text{Aux}$), causing battery drain on AC power.
3. **Hardware Modularity & 5-Year Ownership**: Audits soldered vs SODIMM RAM, M.2 expansion slots, screw types, and predicts 3-to-5 year functional lifespans.
4. **Hard Deal-Breaker & Bottleneck Engine**: Evaluates non-negotiable capacity cliffs (e.g. 4GB VRAM hard stop for AI/LLMs, single-channel RAM compile bottlenecks, 24ms display ghosting traps).
5. **Multi-Domain Workload Scoring**:
   - 🎮 **Gaming**: 1080p, 1440p, High-Hz Esports, Ray Tracing, and MUX switch verification.
   - 🤖 **AI & Local LLMs**: Hard VRAM capacity limits, Llama-3 8B parameter fit, QLoRA fine-tuning viability, Stable Diffusion XL feasibility.
   - 💻 **Software Development**: Multi-core build compilation, Docker/VM RAM headroom, vertical code display aspect ratio.
   - ⚙️ **Engineering & CAD**: SolidWorks single-thread viewport, FEA/CFD simulation, AVX-512 acceleration.
   - 🎨 **Content Creation**: 100% DCI-P3 color gamut, hardware AV1/NVENC dual encoders, 4K timeline scrubbing.
   - 🔋 **Campus Portability**: True travel weight (chassis + charger), off-charger battery hours, USB-C PD travel charging.
6. **Anti-Marketing Audit**: Automatically flags buzzwords like *"AI-Powered"* or *"Gaming Beast"* and cross-examines them against cold physical hardware realities.
7. **Head-to-Head Comparison Engine**: Compares multiple laptops side-by-side across every parameter to declare domain winners.
8. **Explainable "WHY?" Trees**: Every deduction logs its exact formula, impact, and remediation.

### 🚀 Audit Engine Quick Run Commands:

```powershell
# 1. Audit the physical machine currently running SysPulse (Live Hardware Mode)
python audit_engine/main.py --live --priority Software_Development --html results/audit_dossier.html

# 2. Audit a specific laptop specification sheet (e.g. for AI research)
python audit_engine/main.py --file examples/engineered_workstation.json --priority AI_ML

# 3. Compare multiple laptops side-by-side
python audit_engine/main.py --compare examples/deceptive_paper_tiger.json examples/engineered_workstation.json examples/host_physical_laptop.json

# 4. Run the master end-to-end test suite across all 22 engineering phases
python test_all_phases.py
```

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
