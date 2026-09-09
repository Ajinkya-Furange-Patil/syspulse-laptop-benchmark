# Canonical Benchmark Metrics Dictionary

Every metric recorded or evaluated in SysPulse must adhere to these exact naming conventions and measurement units.

---

## 1. CPU Metrics
- `cpu_model_name` (string): Exact detected model string from CPUID/WMI.
- `cpu_physical_cores` (int): Count of physical CPU cores (combining P + E cores).
- `cpu_logical_threads` (int): Total OS hardware thread execution units.
- `cpu_base_clock_ghz` (float): Advertised manufacturer nominal frequency.
- `cpu_boost_clock_ghz` (float): Maximum single-core peak turbo frequency.
- `cpu_single_mops` (float): Single-core integer instruction throughput in Millions of Operations per second (MOps/s).
- `cpu_multi_gflops` (float): Multi-threaded OpenMP compute throughput in Giga-Floating Point Operations per second (GFLOPs).
- `cpu_sustained_drop_pct` (float): Percentage throughput decline from initial burst to steady state.
- `cpu_peak_temp_c` (float): Maximum observed package temperature in degrees Celsius (°C).

---

## 2. GPU & Graphics Metrics
- `gpu_name` (string): Discrete GPU model string reported by driver/NVML.
- `gpu_vram_mb` (float): Total dedicated video memory in Megabytes.
- `gpu_sm_count` (int): Number of Streaming Multiprocessors.
- `gpu_cuda_cores` (int): Number of active CUDA compute cores / shaders.
- `gpu_fp32_tflops` (float): Measured sustained single-precision floating point throughput in TFLOPs.
- `gpu_tgp_watts` (float): Configured total graphics power ceiling in Watts.
- `gpu_temp_c` (float): GPU edge / hotspot temperature in degrees Celsius (°C).

---

## 3. Memory & Storage Metrics
- `ram_total_mb` (float): Installed physical RAM capacity in Megabytes.
- `ram_speed_mts` (int): Memory transfer rate in Mega-Transfers per second (MT/s).
- `ram_channels` (string): `"SINGLE_CHANNEL"`, `"DUAL_CHANNEL"`, or `"QUAD_CHANNEL"`.
- `ram_bandwidth_gbps` (float): Measured continuous memory read/write throughput in Gigabytes per second (GB/s).
- `ssd_read_mbps` (float): Sustained sequential read throughput in Megabytes per second (MB/s).
- `ssd_write_mbps` (float): Sustained sequential write throughput in Megabytes per second (MB/s).
