# SysPulse Architecture & Engineering Design

This document details the internal architecture, hardware telemetry mechanisms, and benchmark workload designs in the **SysPulse** hardware benchmark and laptop evaluation engine.

---

## High-Level Architecture Diagram

```
                              ┌─────────────────────────────┐
                              │      run.bat / CLI          │
                              │  (Unified Master Runner)    │
                              └──────────────┬──────────────┘
                                             │
                                             ▼
                              ┌─────────────────────────────┐
                              │        src/main.cpp         │
                              │   Master Orchestration      │
                              └──────┬───────┬───────┬──────┘
                                     │       │       │
             ┌───────────────────────┘       │       └─────────────────────────┐
             ▼                               ▼                                 ▼
┌─────────────────────────┐    ┌───────────────────────────┐    ┌─────────────────────────┐
│     sys_detect.hpp      │    │       ram_bench.hpp       │    │     cuda_bench.cuh      │
│  • Win32 WMI Hardware   │    │  • Multi-Threaded Stream  │    │  • Native CUDA SGEMM    │
│  • CPUID SIMD Probing   │    │  • Bandwidth (Read/Write) │    │  • GELU & VRAM Copy     │
│  • PowrProf / Battery   │    │  • Latency & Channel Test │    │  • Cross-Load Stress    │
└────────────┬────────────┘    └─────────────┬─────────────┘    └────────────┬────────────┘
             │                               │                               │
             └───────────────────────┬───────┴───────────────────────────────┘
                                     ▼
                      ┌─────────────────────────────┐
                      │    bottleneck_engine.hpp    │
                      │    buyer_checklist.hpp      │
                      │  • 34-Point Rule Engine     │
                      │  • Cross-Throttle Analyzer  │
                      │  • Suitability Scorers      │
                      └──────────────┬──────────────┘
                                     │
                                     ▼
                      ┌─────────────────────────────┐
                      │    Interactive HTML & JSON  │
                      │  • laptop_buyer_inspection  │
                      │  • performance_report.html  │
                      │  • JSON Telemetry Exporter  │
                      └─────────────────────────────┘
```

---

## Core Engine Modules

### 1. Hardware Detection Engine (`include/sys_detect.hpp`)
- **Query Mechanism**: Interacts directly with Windows WMI (`IWbemServices`, `IWbemClassObject`) via COM APIs to query `Win32_Processor`, `Win32_PhysicalMemory`, `Win32_VideoController`, and `Win32_DiskDrive`.
- **CPUID Microarchitecture Probing**: Executes inline `__cpuid` and `__cpuidex` instructions to check for AVX, AVX2, FMA3, and AVX-512 extensions directly from CPU register flags (`EBX`, `ECX`).
- **Memory Topology**: Queries physical memory chips to detect whether memory is operating in **Single-Channel** (1x 64-bit bus) or **Dual-Channel** (2x 64-bit or 128-bit bus).

### 2. Memory Subsystem Benchmark (`include/ram_bench.hpp`)
- **Streaming AVX Workloads**: Allocates safety-bounded buffers to test sequential memory reads, sequential memory writes, and cross-buffer copies.
- **Cache vs DRAM Latency**: Measures pointer-chasing latency to test L1, L2, L3 cache boundary performance vs main system DRAM access latency.
- **Compiler Optimization Prevention**: Uses `RamBench::DoNotOptimize(value)` memory clobbers to guarantee that loops and memory accesses are not eliminated as dead code by the MSVC `/O2` optimizer.

### 3. GPU Acceleration & Cross-Throttling (`src/cuda_kernels.cu`)
- **Tiled Matrix Multiplication (SGEMM)**: Implements a 2D shared-memory tiled SGEMM kernel (`TILE_SIZE = 16`) to saturate streaming multiprocessors (SMs) and measure peak single-precision TFLOPs.
- **GELU Non-Linear Activation**: Measures memory-bound FP32 math typical in modern Transformer / LLM architectures.
- **Host-Device VRAM Streaming**: Tests bidirectional memory copy bandwidth between host DRAM and GPU GDDR6/LPDDR5 memory over PCIe.
- **Cross-Throttling Test**: Spawns simultaneous OpenMP CPU stress threads while looping the GPU SGEMM kernel. Compares isolated throughput against combined throughput to detect VRM power throttling and shared heat-pipe thermal choke.

### 4. Non-CUDA Universal Fallback (`src/cuda_stub.cpp`)
- For machines without an NVIDIA GPU or without the CUDA Toolkit installed (such as Intel Iris Xe or AMD Radeon laptops), `src/cuda_stub.cpp` provides transparent fallback implementations of `CudaCheckAvailability()` and `RunCudaBenchmarks()`.
- Allows the entire project to compile and run universally without crashing or linker failures.

### 5. Bottleneck Synthesis & 34-Point Buyer Audit (`include/buyer_checklist.hpp`)
- Ingests raw telemetry and microbenchmark metrics.
- Evaluates 34 strict hardware rules and compiles status indicators (`PASS`, `WARN`, `FAIL`).
- Generates categorized scorecard reports and exports both raw structured JSON data and self-contained interactive HTML dashboards with dark mode aesthetics and instant status filters.
