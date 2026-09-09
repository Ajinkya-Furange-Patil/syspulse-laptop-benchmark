# 34-Point Laptop Technical Buyer's Inspection Specification

The **34-Point Laptop Inspection Engine** evaluates hardware before purchase, benchmark validation, or tuning. Unlike generic synthetic benchmarks that only produce an abstract score, this checklist audits the fundamental engineering parameters that dictate real-world longevity, gaming performance, AI model capability, and developer productivity.

---

## Checklist Categories Overview

| Category | Total Weight | Key Parameters Audited |
| :--- | :--- | :--- |
| **1. CPU Architecture & Multi-Core** | 20 Points | Physical cores, thread scaling, AVX-512 / AVX2 vector extensions, base vs boost frequency |
| **2. GPU Silicon & TGP Power** | 25 Points | Discrete vs Integrated GPU, CUDA core count, SM architecture, TGP wattage envelope |
| **3. GPU VRAM Capacity & AI Ceilings** | 15 Points | Dedicated VRAM (GB), memory bus width, LLM parameter ceiling (Q4/Q8/FP16), Stable Diffusion compatibility |
| **4. RAM Subsystem & Topology** | 15 Points | Dual-channel vs Single-channel bus width (128-bit vs 64-bit), MT/s speed, capacity headroom for VMs/Docker |
| **5. Storage Speed & Expansion** | 10 Points | NVMe PCIe Generation (Gen3/Gen4/Gen5), sequential read throughput, secondary M.2 expansion capability |
| **6. Cooling, Thermals & Cross-Load** | 15 Points | Peak load temperatures, TjMax safety margin, frequency drop-off over sustained load, CPU+GPU shared power throttling |

---

## Detailed Checkpoint Breakdown

### Category 1: CPU Architecture (Checkpoints 1 - 6)
1. **Physical Core Count**: Distinguishes true hardware execution units from logical threads (SMT/HyperThreading). Minimum recommended for engineering: 6 cores.
2. **Logical Thread Count**: Verifies full multi-threading utilization for parallel build jobs (Ninja, MSBuild, GCC).
3. **AVX-512 Vectorization**: Detects hardware 512-bit vector registers. Critical for accelerated matrix operations, scientific simulations, and quantized CPU inference (`llama.cpp`).
4. **AVX2 / FMA3 Vector Pipeline**: Verifies standard 256-bit SIMD baseline for modern gaming engines and multimedia workloads.
5. **Base Clock Frequency**: Validates thermal design power (TDP) floor under non-boost conditions.
6. **Sustained Multi-Core Scaling**: Measures real multi-threaded efficiency compared to theoretical linear core scaling.

### Category 2: GPU Silicon & Power (Checkpoints 7 - 12)
7. **Discrete vs Integrated Detection**: Flags systems relying solely on shared system RAM for graphics.
8. **Streaming Multiprocessors (SMs)**: Audits active compute units on the GPU silicon die.
9. **CUDA Cores / Compute Units**: Gauges raw parallel compute capabilities.
10. **GPU Clock Frequency**: Validates GPU boost state under sustained gaming/compute loads.
11. **TGP Power Limit**: Detects whether a laptop GPU is a low-power Max-Q variant (e.g. 35W) vs a full-power variant (e.g. 95W–140W).
12. **PCIe Link Generation & Width**: Validates host-to-device bus throughput (e.g., PCIe Gen4 x8 or x16).

### Category 3: VRAM Capacity & Local AI Ceilings (Checkpoints 13 - 17)
13. **Dedicated VRAM Size**:
    - `< 4 GB`: Unsuitable for modern AAA gaming and modern LLMs.
    - `4 GB - 6 GB`: Entry-level gaming (1080p medium); small quantized models (<3.8B parameters) or Stable Diffusion 1.5.
    - `8 GB - 12 GB`: Sweet spot for college AI research (Llama 3 8B Q4/Q8, LoRA fine-tuning) and 1080p/1440p gaming.
    - `16 GB+`: Workstation class; capable of running 70B quantized models and local deep learning training.
14. **VRAM Bus Width**: Detects 64-bit, 128-bit, 192-bit, or 256-bit memory buses.
15. **VRAM Bandwidth (GB/s)**: Measures real memory copy throughput directly on GPU VRAM.
16. **Local LLM Model Compatibility**: Automatically predicts the largest GGUF/AWQ model that fits into VRAM without CPU offload paging.
17. **Fine-Tuning Capability**: Evaluates whether LoRA / QLoRA parameter tuning is viable on the hardware.

### Category 4: RAM Subsystem (Checkpoints 18 - 22)
18. **Dual-Channel vs Single-Channel**: Audits memory bus channels. Single-channel RAM drops CPU gaming 1% low framerates and memory-intensive compilation by **up to 35%**.
19. **Memory Speed (MT/s)**: Detects DDR4 (2400–3200 MT/s) vs DDR5/LPDDR5 (4800–7500 MT/s).
20. **Total Physical RAM Capacity**:
    - `< 8 GB`: Severe dealbreaker for development.
    - `8 GB - 16 GB`: Baseline for students and casual gaming.
    - `32 GB+`: Ideal for heavy virtualization, Docker containers, Android Studio, and local LLMs.
21. **Measured Read/Write Bandwidth**: AVX stream throughput in GB/s.
22. **Memory Subsystem Latency**: Memory access time in nanoseconds.

### Category 5: Storage & Expansion (Checkpoints 23 - 27)
23. **Drive Interface**: NVMe PCIe vs SATA SSD vs HDD.
24. **PCIe Link Speed**: PCIe Gen3 (up to 3,500 MB/s) vs Gen4 (up to 7,500 MB/s) vs Gen5.
25. **Sequential Read Throughput**: Measured sequential read velocity.
26. **Thermal Throttling on Sustained Writes**: Detects if the SSD drops to HDD speeds when SLC cache saturates.
27. **Secondary Drive / Slot Presence**: Expansion headroom for secondary game/data drives.

### Category 6: Cooling, Thermals & Cross-Load (Checkpoints 28 - 34)
28. **Peak CPU Temperature**: Under 100% all-core AVX stress.
29. **TjMax Safety Delta**: Degrees remaining before CPU emergency thermal throttling (100°C).
30. **Sustained Frequency Degradation**: Compares performance in seconds 1–5 vs seconds 30–60. Degradation > 15% indicates inadequate heatsink/fan capacity.
31. **Simultaneous CPU+GPU Cross-Load**: Runs both CPU OpenMP workers and GPU CUDA SGEMM concurrently.
32. **CPU Cross-Throttle Percentage**: Measures CPU speed reduction caused by GPU power draw.
33. **GPU Cross-Throttle Percentage**: Measures GPU speed reduction caused by CPU thermal soak.
34. **Shared Power Budget Engineering Verdict**: Delivers final diagnosis of VRM/cooling design.

---

## Target Use-Case Suitability Scoring

The engine maps the 34 raw hardware metrics into 4 student-centric application tiers:

1. **Modern Gaming (0 - 100)**: Weighted towards GPU TFLOPs, dedicated VRAM, dual-channel RAM, and thermal headroom.
2. **AI & Local LLMs (0 - 100)**: Weighted heavily towards VRAM capacity, Tensor compute throughput, and AVX-512 CPU support.
3. **Engineering, VMs & Software Dev (0 - 100)**: Weighted towards physical core count, RAM capacity (16GB/32GB), and NVMe read/write speeds.
4. **Campus Portability & Thermal Stability (0 - 100)**: Weighted towards thermal dissipation, low power contention, and sustained efficiency.
