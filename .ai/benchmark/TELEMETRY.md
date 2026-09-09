# Hardware Telemetry Acquisition Rules

Telemetry is the bridge between physical hardware and the analytical audit engine. It must be sampled accurately without introducing measurement noise.

---

## 1. Sensor Ingestion Strategy

1. **WMI (Windows Management Instrumentation):**
   - Query `Win32_Processor`, `Win32_PhysicalMemory`, `Win32_VideoController`, and `MSAcpi_ThermalZoneTemperature` (under `root/wmi`).
   - Wrap COM initialization (`CoInitializeEx`) and WMI calls in exception handlers.
2. **Direct Win32 System APIs:**
   - Use `GlobalMemoryStatusEx` for accurate instantaneous physical and virtual memory allocation ceilings.
   - Use `GetSystemInfo` and `GetLogicalProcessorInformationEx` for cache and core topology maps.
3. **NVML / CUDA Driver APIs:**
   - Query GPU core clock, memory clock, temperature, fan speed, and power draw directly via NVML when available.

---

## 2. Sampling Frequency & Overhead
- Poll telemetry at reasonable intervals (e.g. 500ms to 1000ms) during sustained runs.
- Aggregate samples into minimum, maximum, and average values.
- If a sensor read times out or reports an invalid value (e.g. 0°C or 255°C), discard the reading as an outlier and increment the error counter.
