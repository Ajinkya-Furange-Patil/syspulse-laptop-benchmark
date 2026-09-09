# SysPulse Canonical Terminology

To prevent semantic drift, ambiguity, and AI hallucinations, all modules, schemas, and reports must use this canonical technical vocabulary:

---

## 1. Power & Thermal Terms
- **PL1 (Power Limit 1):** The maximum sustained power limit (in Watts) a CPU is permitted to consume continuously after the Tau duration expires.
- **PL2 (Power Limit 2):** The short-duration burst power ceiling (in Watts) allowed for transient high-demand tasks.
- **Tau:** The duration (in seconds) the processor is allowed to sustain PL2 before dropping to PL1.
- **TGP (Total Graphics Power):** The total electrical power (in Watts) allocated by the vBIOS to the discrete GPU die and its VRAM subsystem.
- **Dynamic Boost:** Power budget shifting between CPU and GPU managed by OEM firmware (NVIDIA Dynamic Boost / AMD SmartShift).
- **$P_{\text{aux}}$ (Auxiliary System Power):** The combined power drawn by display backlight, motherboard VRMs, memory controller, SSD controllers, Wi-Fi card, and cooling fans.
- **Cross-Load:** A concurrent heavy workload placing maximum simultaneous demand on both the CPU and GPU (e.g. gaming, rendering, simulation).
- **TjMax (Thermal Junction Maximum):** The maximum silicon junction temperature (typically 95°C–105°C for CPUs, 87°C for GPUs) before emergency hardware downclocking or shutdown.
- **Thermal Throttling:** Clock speed reduction enforced by the silicon to prevent exceeding TjMax.
- **Power Throttling:** Clock speed reduction enforced by the firmware power limiter (PL1/TGP clamp).

---

## 2. Silicon & Memory Architecture Terms
- **Max-P:** The maximum permissible TGP variant of a mobile GPU (e.g., RTX 4060 at 140W).
- **Max-Q:** A severely power-constrained variant of a mobile GPU (e.g., RTX 4060 clamped to 45W).
- **VRAM Capacity Limit:** A hard capacity ceiling where an entire model or game texture set cannot fit inside dedicated GDDR memory, triggering catastrophic host PCIe swapping or application crashes.
- **Channel Configuration:**
  - `SINGLE_CHANNEL`: A single 64-bit (or 32-bit LPDDR) memory bus. Cuts memory bandwidth in half; severely degrades 1% low frame rates.
  - `DUAL_CHANNEL`: Dual 64-bit symmetric memory channels. Baseline requirement for modern multi-core CPUs.
  - `QUAD_CHANNEL`: 4-channel configuration (common in LPDDR5x 128-bit arrangements or desktop workstation platforms).
- **Modularity:**
  - `SODIMM`: User-upgradeable small-outline dual in-line memory module socket.
  - `SOLDERED`: Non-upgradeable memory chips surface-mounted directly to the motherboard.
- **MUX Switch:** A physical hardware multiplexer that routes display output directly from the discrete GPU to the internal laptop screen, bypassing the integrated GPU.
- **Advanced Optimus:** Dynamic display switching (DRRS) via hardware MUX without requiring an OS restart.

---

## 3. Display Terms
- **GTG (Grey-to-Grey) Response Time:** The time (in milliseconds) required for a pixel to transition between two color shades. Must be under the frame time (e.g. <6.94ms for 144Hz) to prevent ghosting.
- **Ghosting / Smearing:** Visual motion blur trailing high-contrast moving objects caused by pixel response times that are slower than the refresh rate interval.
- **Color Gamut:** The range of colors a display can reproduce:
  - `45% NTSC`: Sub-budget gamut (~58-65% sRGB). Washed out, desaturated colors.
  - `100% sRGB`: Standard web and sRGB content creation baseline.
  - `100% DCI-P3`: Wide color gamut required for professional video production and HDR.

---

## 4. Evaluation & Scorecard Terms
- **Deal-Breaker:** A severe physical or architectural limitation that makes a laptop genuinely unsuitable for a specific workload domain, regardless of its overall average score.
- **Bottleneck:** A subsystem whose throughput ceiling prevents another, more capable subsystem from operating at its potential, resulting in an estimated percentage throughput loss.
- **No Universal Winner:** The core principle that hardware merit is conditioned on the user's workload; identical hardware can be an "EXCELLENT BUY" for CAD while being a "HARD NO" for local AI.
- **Marketing Trap:** A configuration where high-headline specifications (e.g. "Core i7", "RTX 4060") are crippled by hidden cost-cutting measures (e.g. 45W vBIOS, single-channel soldered RAM, washed-out 45% NTSC screen, or undersized adapter).
