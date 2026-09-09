# Error Handling & Resilience Rules

SysPulse will encounter missing hardware sensors, non-standard OEM ACPI implementations, broken drivers, incomplete retailer spec sheets, and unprivileged user environments. It must handle all anomalies gracefully.

---

## 1. Principles of Resilient Handling

1. **Graceful Degradation:** A missing hardware sensor or unavailable API must never crash the entire application.
2. **Never Fabricate on Failure:** If a sensor query fails, record `UNKNOWN` with confidence `0.0`. Never substitute a default value (such as 0 or 100) that could distort the audit.
3. **Explicit Diagnostic Logging:** Emit clear, informative warnings explaining why a sensor could not be polled (e.g. *"WMI thermal query requires administrator privilege; falling back to package power estimates"*).

---

## 2. Specific Failure Modes

### Missing NVIDIA GPU / CUDA Runtime
- Check availability via `CudaCheckAvailability()`.
- If CUDA initialization fails or device count is 0, gracefully skip GPU compute kernels and log an informational message. The CPU benchmark and audit pipeline must continue without interruption.

### Missing OEM Power Envelopes (PL1 / PL2 / TGP)
- When evaluating a specification file where OEM limits were omitted, set field status to `UNKNOWN`.
- The audit engine must apply conservative historical floors (e.g. 45W baseline for mobile dGPUs) while visibly decaying the audit confidence score.

### Unreadable Storage Sensors
- If disk sequential throughput cannot be measured due to permissions or read-only filesystem locks, fall back to interface rating (e.g. PCIe Gen 4x4 specification limit) marked as `ESTIMATED`.
