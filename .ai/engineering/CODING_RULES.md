# Coding Rules & Language Standards

SysPulse uses a dual-language architecture: **C++20** for native hardware execution and benchmarking, and **Python 3.10+** for analytical auditing, scoring, and data modeling.

---

## 1. C++20 Standards (Native Engine)

### Compiler & Standards
- MSVC 2022 / Clang with `/std:c++20` or `/std:c++latest`.
- Zero compiler warnings at `/W3` level.
- Must compile cleanly with standard Microsoft build tools (`cl.exe`, `nvcc.exe`).

### Memory & Concurrency
- Use RAII (Resource Acquisition Is Initialization) for all system handles (`HMODULE`, `IWbemServices`, `HANDLE`).
- Never perform dynamic heap allocations (`new`, `malloc`, `std::vector::reserve`) inside tight benchmark measurement loops.
- Use `std::chrono::high_resolution_clock` for all timing; never use low-resolution `GetTickCount()` or `time()`.
- Use OpenMP `#pragma omp parallel for` for multi-threaded workloads with explicit reduction clauses.
- Prevent compiler dead-code elimination using benchmark memory fences (e.g. `RamBench::DoNotOptimize()`).

### Windows Interoperability
- Define `#define WIN32_LEAN_AND_MEAN` and `#define NOMINMAX` before including `<windows.h>`.
- Use UTF-8 / wide string conversion safely; avoid buffer overflows by passing explicit lengths to Win32 functions.

---

## 2. Python Standards (Audit Engine)

### Typing & Code Style
- Strongly typed: Use `typing` and `dataclasses` for all data transfer objects.
- Python 3.10+ compatibility (use `typing.Optional`, `typing.List`, `typing.Dict`, `typing.Union`).
- Zero external dependencies: rely exclusively on standard library modules.
- Preserve Windows console encoding compatibility: enforce UTF-8 reconfiguration on `sys.stdout` if available.

### Immutability & Math
- Mathematical modeling formulas must be transparent, documented, and deterministic.
- Avoid hidden magic numbers: declare domain thresholds as named class constants.
- Round user-facing floating point numbers to 1 or 2 decimal places for clean formatting.

---

## 3. CUDA & GPU Standards

### Kernel Design
- Every CUDA kernel must check for device availability before execution.
- Maintain a CPU fallback path (`src/cuda_stub.cpp`) when NVIDIA drivers or CUDA runtimes are not present.
- Use standard SGEMM / tile-based shared memory multiplication for matrix compute benchmarks.
- Clean up all GPU memory allocations via `cudaFree()` upon benchmark completion or error.
