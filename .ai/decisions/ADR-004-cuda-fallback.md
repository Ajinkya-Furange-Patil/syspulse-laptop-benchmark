# ADR-004: Native CUDA Execution with Universal CPU Fallback

## Status
Accepted

## Context
A substantial portion of target laptops do not feature discrete NVIDIA GPUs (e.g. Intel Iris Xe / Arc, AMD Radeon 680M/780M/890M, or systems where CUDA is uninstalled). If the master binary hard-depended on NVIDIA CUDA runtime DLLs, the executable would fail to launch on non-NVIDIA machines.

## Decision
1. The C++ benchmark codebase implements a modular dual-path strategy:
   - Dynamic CUDA runtime check via `CudaCheckAvailability()`.
   - Dedicated compilation paths for CUDA (`src/cuda_kernels.cu`) and host CPU fallback (`src/cuda_stub.cpp`).
2. If CUDA is not detected at runtime, the benchmark suite bypasses CUDA kernels gracefully and executes CPU-based multi-thread float/integer passes without crashing.

## Consequences
- The binary runs on 100% of modern x64 Windows machines.
- NVIDIA laptops receive deep hardware acceleration testing (SGEMM, Tensor TFLOPs), while non-NVIDIA laptops execute clean CPU benchmarks.
