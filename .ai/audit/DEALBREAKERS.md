# Deal-Breakers & Hardware Traps

A deal-breaker is a physical hardware constraint that makes a machine technically incapable of satisfying a specific workload.

---

## 1. Severity Classifications
1. **FATAL:** Workload cannot function or crashes due to physical resource exhaustion (e.g. CUDA OutOfMemory, battery draining on AC).
2. **WARNING:** Workload functions but suffers severe compromises (e.g. washed-out 45% NTSC color gamut, slow GTG ghosting display).
3. **ADVISORY:** Noticeable architectural trade-off (e.g. lack of MUX switch in an esports laptop).

---

## 2. Canonical Deal-Breakers in SysPulse

### `FATAL_VRAM_SUB_6GB`
- **Subsystem:** GPU / Dedicated Memory
- **Condition:** Discrete GPU dedicated VRAM < 6.0 GB.
- **Physical Reason:** Modern quantized LLMs (Llama-3 8B, Mistral 7B) and Stable Diffusion XL require $\ge 6\text{–}8\text{ GB}$ VRAM. 4GB triggers immediate OutOfMemory crashes or massive PCIe host memory swapping.
- **Impacted Workloads:** AI / Machine Learning, Modern AAA Gaming.

### `FATAL_POWER_ADAPTER_DEFICIT`
- **Subsystem:** Power Delivery
- **Condition:** Included adapter wattage < $\text{PL1} + \text{TGP} + P_{\text{aux}}$.
- **Physical Reason:** Combined hardware draw exceeds power supply output, forcing hybrid battery discharge while connected to AC power. Accelerates battery cycle wear and causes severe thermal throttling when battery drops below 30%.
- **Impacted Workloads:** Sustained Gaming, Compiling, 3D Rendering.

### `FATAL_SINGLE_CHANNEL_SOLDERED_RAM`
- **Subsystem:** Memory Topology
- **Condition:** Single-channel memory with 0 SODIMM expansion slots.
- **Physical Reason:** Memory bandwidth is cut by 50% permanently with no physical path to enable dual-channel interleaving.
- **Impacted Workloads:** Multi-core compilation, 1% low gaming stability.

### `WARN_DISPLAY_GHOSTING_TRAP`
- **Subsystem:** Display Panel
- **Condition:** Display refresh rate $\ge 120\text{ Hz}$ with measured GTG response time $> 15\text{ ms}$.
- **Physical Reason:** Pixel transition time exceeds frame window, causing severe smearing and ghosting.
- **Impacted Workloads:** Esports, Fast-Paced Action Gaming.
