# Anti-Marketing Verification Rules

Retailer listings and manufacturer brochures use hyperbolic marketing claims to mask cost-cutting decisions. The Anti-Marketing Audit Engine detects and debunks these claims.

---

## 1. The Verification Workflow
```
Extract Promotional Buzzword → Query Physical Hardware Telemetry → Compare Against Reality → Issue Verdict
```

---

## 2. Canonical Marketing Traps & Physical Checks

### 1. "AI-Powered" / "Next-Gen AI Laptop"
- **Marketing Claim:** Laptop is ready for cutting-edge local artificial intelligence.
- **Physical Verification:**
  - Does the machine have a discrete NVIDIA GPU with Tensor Cores?
  - Is dedicated VRAM $\ge 8\text{ GB}$?
  - Does the NPU deliver meaningful TOPS ($\ge 40\text{ TOPS}$ for Copilot+)?
- **Verdict:**
  - `SUPPORTED`: $\ge 8\text{GB}$ VRAM with CUDA Tensor support.
  - `PARTIALLY_SUPPORTED`: Capable NPU for background webcam blur, but cannot run local LLMs.
  - `MISLEADING_MARKETING_TRAP`: 4GB VRAM (crashes with CUDA OOM) or marketing claim based purely on integrated graphics with no dedicated Tensor hardware.

### 2. "High-Performance Gaming"
- **Marketing Claim:** High framerate AAA gaming powerhouse.
- **Physical Verification:**
  - Is the GPU TGP castrated (e.g. $<60\%$ of silicon maximum)?
  - Is RAM single-channel or soldered?
  - Is a hardware MUX switch present?
- **Verdict:**
  - `MISLEADING_MARKETING_TRAP` if a 140W die is throttled to 45W or hobbled by single-channel RAM.

### 3. "Fast 144Hz / 240Hz Display"
- **Marketing Claim:** Ultra-responsive esports display.
- **Physical Verification:**
  - Does measured GTG response time exceed the frame time ($>15\text{ ms}$)?
- **Verdict:**
  - `MISLEADING_MARKETING_TRAP` if physical pixel transitions produce severe smearing and ghosting.
