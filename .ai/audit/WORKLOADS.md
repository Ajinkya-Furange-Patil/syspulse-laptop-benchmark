# Workload Evaluation Domain Models

SysPulse explicitly models 6 discrete computing workloads. A laptop's suitability score is calculated independently for each domain.

---

## 1. Modern Gaming
- **Critical Resources:** GPU TGP, dedicated VRAM, hardware MUX switch, display refresh rate, GTG response time, and dual-channel memory interleaving.
- **Evaluation Criteria:**
  - High score requires Max-P TGP, $\ge 8\text{GB}$ VRAM, sub-5ms GTG response, and dual-channel memory.
  - Penalized heavily for single-channel RAM (-20 pts), castrated TGP, or absence of MUX switch.

---

## 2. AI / Machine Learning (Local LLMs & Diffusion)
- **Critical Resources:** Dedicated VRAM capacity, memory bus bandwidth, CUDA Tensor cores, and system RAM for offloading.
- **Evaluation Criteria:**
  - **Step Function for VRAM:**
    - $<4\text{ GB}$: Cap at 15.0 / 100 (Unusable for modern models).
    - $4\text{–}6\text{ GB}$: Cap at 35.0 / 100 (Quantized 3B models only).
    - $6\text{–}8\text{ GB}$: 60.0 / 100 (Standard 7B/8B Q4 models).
    - $8\text{–}12\text{ GB}$: 80.0 / 100 (7B/8B QLoRA fine-tuning viable).
    - $\ge 16\text{ GB}$: 95.0+ / 100 (Local workstation class).

---

## 3. Software Development
- **Critical Resources:** Multi-threaded CPU compile throughput, RAM capacity (minimum 16GB for IDEs, 32GB+ for Docker/VMs), dual-channel memory bandwidth, and display vertical canvas (16:10 aspect ratio).
- **Evaluation Criteria:**
  - Fast SSD random I/O and large core counts improve compilation scores.
  - Soldered 8GB/16GB RAM is heavily penalized for container workflows.

---

## 4. Engineering / CAD & Simulation
- **Critical Resources:** CPU single-core boost clock (paramount for SolidWorks viewport modeling), sustained cooling dissipation envelope, AVX-512 vector support, and ECC/workstation driver stability.
- **Evaluation Criteria:**
  - High single-core turbo (>4.8 GHz) + adequate thermal headroom yields high scores.

---

## 5. Content Creation & Video Production
- **Critical Resources:** Display color gamut (100% sRGB minimum, 100% DCI-P3 for HDR), hardware media encoders (NVENC 8th Gen, Intel QuickSync, AV1), and sustained NVMe write speeds.
- **Evaluation Criteria:**
  - Panels with 45% NTSC are clamped to low scores regardless of GPU power.

---

## 6. Campus Portability & Mobility
- **Critical Resources:** True travel weight (chassis weight + adapter weight), battery capacity (Wh), and USB-C Power Delivery charging flexibility.
- **Evaluation Criteria:**
  - Bulky 300W proprietary brick with no USB-C charging penalizes campus mobility.
