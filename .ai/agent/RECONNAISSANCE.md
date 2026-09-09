# Codebase Reconnaissance Guide

Before editing any file in SysPulse, perform reconnaissance to understand the exact structure and dependencies.

---

## 1. Reconnaissance Checklist

1. **Locate the True Authority:**
   - For native benchmark behavior: inspect `src/main.cpp`, `src/sys_detect.cpp`, and `src/cuda_kernels.cu`.
   - For analytical scoring: inspect `audit_engine/models.py`, `audit_engine/workload_engine.py`, and `audit_engine/dealbreaker_engine.py`.
   - For contract validation: inspect `schemas/laptop_schema.json` and `audit_engine/validator.py`.
2. **Check Call Sites:**
   - Search for function and symbol names using grep tools across the repository before renaming or deleting methods.
3. **Verify Build Scripts:**
   - Inspect `build.bat` and `package_portable.bat` to understand compiler flags and packaging steps.
4. **Inspect Test Fixtures:**
   - Check `examples/` for existing test JSON specifications (`deceptive_paper_tiger.json`, `engineered_workstation.json`, `host_physical_laptop.json`, `severe_power_deficit.json`).
