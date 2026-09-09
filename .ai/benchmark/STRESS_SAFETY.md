# Stress Testing Safety Protocols

Laptop thermal and power management is sensitive. Sub-optimal cooling or degraded thermal paste can cause rapid heat accumulation. SysPulse must enforce strict safety bounds during all stress phases.

---

## 1. Safety Bounds & Safeguards

1. **Explicit Duration Limits:**
   - Default quick stress runs must be capped at 15 to 60 seconds.
   - Long-duration sustained tests must never run indefinitely; they must require an explicit `--duration <seconds>` parameter.
2. **Thermal Trip Interception:**
   - If CPU package temperature reaches 100°C or GPU hotspot reaches 95°C, log an immediate `THERMAL_THROTTLE_DETECTED` warning.
   - Never attempt to disable or bypass hardware PROCHOT or TjMax throttling mechanisms.
3. **Graceful Cancellation:**
   - All benchmark loops must poll for user cancellation (e.g. `Ctrl+C` or standard signals) and cleanly terminate without leaving worker threads spinning in the background.
4. **Memory Allocation Safety Ceilings:**
   - Never allocate more than 75% of available physical RAM to prevent triggering aggressive Windows pagefile thrashing or OutOfMemory crashes of the host OS.
