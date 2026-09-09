# ADR-005: Standalone Zero-Dependency Offline Distribution

## Status
Accepted

## Context
When inspecting laptops in physical retail stores or testing air-gapped lab systems, users cannot install complex dependencies, run `npm install`, configure Python virtual environments, or connect to the internet.

## Decision
SysPulse maintains an automated portable distribution packager ([`package_portable.bat`](file:///package_portable.bat)) that generates:
1. `SysPulse_Portable/`: A clean standalone folder containing:
   - `SysPulse.exe` (Signed 64-bit benchmark executable).
   - `vcomp140.dll` (Bundled OpenMP runtime).
   - `results/` (Local output folder).
2. `SysPulse_Portable.zip`: A compact archive that can be extracted to a USB thumbdrive and executed via double-click, automatically opening the resulting inspection report in the default browser.

## Consequences
- Zero-friction retail evaluation.
- No network or administrative setup required.
- Keeps portable folder clean and isolated from development artifacts.
