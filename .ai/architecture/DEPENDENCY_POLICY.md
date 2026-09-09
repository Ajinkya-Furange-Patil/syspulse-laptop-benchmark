# Dependency & Portability Policy

SysPulse prioritizes absolute offline portability, zero external runtime friction, and long-term stability.

---

## 1. Core Principles

1. **Zero Mandatory Runtime Internet Access:** SysPulse must operate flawlessly in air-gapped environments, clean retail laptops without Wi-Fi, and lab test rigs.
2. **Single-Binary Portability:** The native benchmark tool must compile to a standalone binary (`SysPulse.exe`) that executes on any x64 Windows 10/11 machine with only the bundled `vcomp140.dll`.
3. **Standard Library Preference:** Favor native Win32 APIs and standard Python libraries (`json`, `sqlite3`, `argparse`, `dataclasses`, `typing`) before even considering external dependencies.

---

## 2. Permitted Dependencies

### Native C++ Stack:
- **C++ Standard Library (C++20):** `<iostream>`, `<chrono>`, `<vector>`, `<string>`, `<cmath>`, `<algorithm>`, `<cstdint>`, `<memory>`.
- **Windows System APIs:** `Powrprof.lib`, `wbemuuid.lib` (WMI), `ole32.lib`, `oleaut32.lib`, `Advapi32.lib`, `Shell32.lib`.
- **OpenMP Runtime:** `/openmp` bundled with `vcomp140.dll`.
- **NVIDIA CUDA Toolkit (Optional Runtime):** `cudart.lib`, with automatic fallback to CPU/host mode when CUDA is absent.

### Analytical Python Engine:
- Python 3.10+ Standard Library only.
- Zero external `pip` requirements for the core audit engine.

---

## 3. Forbidden Dependencies

Unless explicitly approved in an Architecture Decision Record (ADR), do **NOT** add:
- Heavy cross-platform UI frameworks (Qt, Electron, Chromium Embedded Framework).
- Heavy machine learning runtimes (PyTorch, TensorFlow, ONNX Runtime) inside the lightweight distribution package.
- External telemetry reporting SDKs (Sentry, Google Analytics, Segment).
- Mandatory cloud license verification or remote APIs.
- External CSS/JS CDNs (Bootstrap, Tailwind CDN, Google Fonts) in generated HTML reports; all styles and scripts must be 100% self-contained inline.

---

## 4. Requirements for Introducing Any New Dependency

Before proposing any new dependency, the AI agent must document:
1. **Technical Necessity:** Why is the feature impossible or excessively complex with existing APIs?
2. **Size Impact:** How many megabytes does it add to `SysPulse_Portable.zip`?
3. **License Compatibility:** Is it MIT, BSD, or Apache 2.0 compatible?
4. **Offline Viability:** Does it function completely without internet access?
5. **Platform Support:** Does it run on clean Windows 10/11 x64 systems without requiring administrative installation?
