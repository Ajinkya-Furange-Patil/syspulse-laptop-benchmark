"""
SysPulse Laptop Buyer Audit Engine - Real Performance & Sustained Throttling Engine
Combines:
1. Expected Specification Performance Model (Architecture IPC, Power Curves, TGP, Memory Bus)
2. Empirical Real Hardware Telemetry Ingestion (SysPulse C++/CUDA benchmarks, Cinebench, TimeSpy, Geekbench)
3. Sustained Throttling & Thermal Degradation Penalty Engine
Mandatory Distinction: SPECIFICATION SCORE vs. MEASURED PERFORMANCE SCORE.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import math
from audit_engine.models import LaptopSpecification, BenchmarkSpec


@dataclass
class PerformanceFinding:
    severity: str  # FATAL, WARNING, ADVISORY, OPTIMAL
    code: str
    title: str
    message: str
    remediation: str


@dataclass
class ExpectedPerformanceMetrics:
    # CPU Theoretical
    cpu_single_thread_index: float  # Normalized to Core i9-13900K = 100.0
    cpu_multi_thread_index: float   # Normalized to Ryzen 9 7950X = 100.0
    cpu_expected_all_core_ghz: float
    cpu_power_scaling_factor: float

    # GPU Theoretical
    gpu_fp32_tflops_expected: float
    gpu_tensor_tflops_expected: float
    gpu_memory_bandwidth_expected_gbps: float
    gpu_tgp_efficiency_factor: float

    # Subsystem Expected
    ram_expected_bandwidth_gbps: float
    storage_expected_read_mbps: float


@dataclass
class MeasuredPerformanceMetrics:
    source: str
    cinebench_r23_single: Optional[float] = None
    cinebench_r23_multi_initial: Optional[float] = None
    cinebench_r23_multi_sustained: Optional[float] = None
    timespy_graphics: Optional[float] = None
    timespy_cpu: Optional[float] = None
    geekbench6_single: Optional[float] = None
    geekbench6_multi: Optional[float] = None
    blender_classroom_sec: Optional[float] = None
    syspulse_single_mops: Optional[float] = None
    syspulse_multi_gflops: Optional[float] = None
    syspulse_cuda_tflops: Optional[float] = None
    syspulse_vram_bandwidth_gbps: Optional[float] = None
    syspulse_ram_bandwidth_gbps: Optional[float] = None
    syspulse_ram_latency_ns: Optional[float] = None
    crystaldisk_read_mbps: Optional[float] = None
    cpu_peak_temp_c: Optional[float] = None
    cpu_sustained_temp_c: Optional[float] = None
    gpu_peak_temp_c: Optional[float] = None
    gpu_sustained_temp_c: Optional[float] = None


@dataclass
class SustainedThrottlingResult:
    cpu_retention_pct: float         # e.g., 95.0% sustained (5.0% drop)
    gpu_cross_throttle_pct: float    # e.g., 0.5% GPU throttle under concurrent CPU stress
    thermal_retention_grade: str     # EXCELLENT (>=92%), ACCEPTABLE (85-91%), HEAVY_THROTTLE (75-84%), SEVERE (<75%)
    thermal_penalty_points: float


@dataclass
class PerformanceAuditResult:
    # Mandatory Distinction
    specification_score: float                  # Theoretical potential based on silicon & limits (0 - 100)
    measured_performance_score: Optional[float] # Empirical score from real hardware benchmarks (0 - 100)
    sustained_performance_score: float          # Real continuous performance under load (0 - 100)

    # Breakdown components
    expected_metrics: ExpectedPerformanceMetrics
    measured_metrics: Optional[MeasuredPerformanceMetrics]
    throttling: SustainedThrottlingResult

    # Detailed Explainability Trees
    spec_score_breakdown: List[Dict[str, Any]]
    measured_score_breakdown: List[Dict[str, Any]]
    discrepancy_analysis: List[str]

    findings: List[PerformanceFinding]


class RealPerformanceEngine:
    """
    Rigorously bridges theoretical hardware capabilities with empirical physical benchmarks.
    """

    # Microarchitectural IPC Weights relative to Zen 3 / Tiger Lake baseline (1.00)
    ARCH_IPC_TABLE: Dict[str, float] = {
        "Zen 3": 1.00,
        "Zen 4": 1.15,
        "Zen 5": 1.30,
        "Tiger Lake": 1.00,
        "Alder Lake": 1.18,
        "Raptor Lake": 1.25,
        "Raptor Lake Refresh": 1.27,
        "Meteor Lake": 1.22,
        "Arrow Lake": 1.34,
        "Lunar Lake": 1.35,
        "Apple M1": 1.15,
        "Apple M2": 1.25,
        "Apple M3": 1.38,
        "Apple M4": 1.50
    }

    # GPU Architecture FP32 Efficiency relative to Turing (1.00)
    GPU_ARCH_EFFICIENCY: Dict[str, float] = {
        "Turing": 1.00,
        "Ampere": 1.35,
        "Ada Lovelace": 1.85,
        "Blackwell": 2.20,
        "RDNA 2": 1.10,
        "RDNA 3": 1.40,
        "RDNA 3.5": 1.45,
        "Battlemage": 1.30
    }

    @classmethod
    def calculate_expected_performance(cls, laptop: LaptopSpecification) -> ExpectedPerformanceMetrics:
        cpu = laptop.cpu
        gpu = laptop.gpu

        # 1. CPU IPC Index
        ipc = cls.ARCH_IPC_TABLE.get(cpu.architecture, 1.10)
        p_cores = cpu.p_cores if cpu.p_cores > 0 else cpu.total_physical_cores
        e_cores = cpu.e_cores

        # Power Scaling: Mobile CPUs under PL1 scale sub-linearly with power (diminishing returns)
        pl1 = cpu.oem_pl1_w.value if cpu.oem_pl1_w.is_known else cpu.intel_amd_rated_base_power_w
        # Power scaling curve: 45W is baseline 1.0. 15W is ~0.55. 90W is ~1.38. 140W is ~1.55.
        power_scale = math.pow(pl1 / 45.0, 0.45)

        # Single-Core index (boost clock * IPC)
        single_index = round((cpu.boost_clock_ghz * ipc / 5.5) * 100.0, 1)

        # All-Core expected clock
        all_core_clk = cpu.all_core_boost_ghz.value if cpu.all_core_boost_ghz.is_known else (cpu.base_clock_ghz + (cpu.boost_clock_ghz - cpu.base_clock_ghz) * 0.55)

        # Multi-Core throughput index: (P-cores * clk + E-cores * clk * 0.65) * IPC * power_scale
        raw_core_sum = (p_cores * all_core_clk) + (e_cores * (all_core_clk * 0.75) * 0.65)
        multi_index = round((raw_core_sum * ipc * power_scale / 110.0) * 100.0, 1)

        # 2. GPU Theoretical Compute
        if gpu.is_discrete:
            gpu_eff = cls.GPU_ARCH_EFFICIENCY.get(gpu.architecture, 1.30)
            tgp_base = gpu.oem_base_tgp_w.value if gpu.oem_base_tgp_w.is_known else 45.0
            # TGP scaling factor relative to 100W baseline
            tgp_scale = math.pow(tgp_base / 100.0, 0.52)
            clk_boost_ghz = (gpu.graphics_clock_boost_mhz.value or 1800) / 1000.0
            fp32_tflops = round((gpu.cuda_cores_or_shaders * 2 * clk_boost_ghz / 1000.0) * (tgp_base / gpu.silicon_max_possible_tgp_w), 2)
            tensor_tflops = round(fp32_tflops * (4.0 if gpu.tensor_cores > 0 else 1.0) * gpu_eff, 1)
            vram_bw = gpu.memory_bandwidth_gbps.value if gpu.memory_bandwidth_gbps.is_known else 256.0
        else:
            gpu_eff = 0.5
            tgp_scale = 0.2
            fp32_tflops = 1.5
            tensor_tflops = 2.0
            vram_bw = 40.0

        # 3. RAM Expected Bandwidth
        channels = 2 if laptop.memory.channel_configuration == "DUAL_CHANNEL" else 1
        bus_width = 128 if channels == 2 else 64
        # MT/s * bytes per transfer * efficiency
        ram_bw = round((laptop.memory.speed_mts * (bus_width / 8.0) / 1000.0) * 0.85, 1)

        # 4. Storage Expected Read
        storage_read = 7000.0 if laptop.storage.drives and laptop.storage.drives[0].pcie_generation >= 4 else 3500.0

        return ExpectedPerformanceMetrics(
            cpu_single_thread_index=single_index,
            cpu_multi_thread_index=multi_index,
            cpu_expected_all_core_ghz=round(all_core_clk, 2),
            cpu_power_scaling_factor=round(power_scale, 2),
            gpu_fp32_tflops_expected=fp32_tflops,
            gpu_tensor_tflops_expected=tensor_tflops,
            gpu_memory_bandwidth_expected_gbps=round(vram_bw, 1),
            gpu_tgp_efficiency_factor=round(tgp_scale, 2),
            ram_expected_bandwidth_gbps=ram_bw,
            storage_expected_read_mbps=storage_read
        )

    @classmethod
    def audit_performance(
        cls,
        laptop: LaptopSpecification,
        measured: Optional[MeasuredPerformanceMetrics] = None
    ) -> PerformanceAuditResult:
        findings: List[PerformanceFinding] = []
        spec_breakdown: List[Dict[str, Any]] = []
        measured_breakdown: List[Dict[str, Any]] = []
        discrepancies: List[str] = []

        # 1. Compute Expected Theoretical Metrics
        exp = cls.calculate_expected_performance(laptop)

        # 2. SPECIFICATION SCORE (0 - 100)
        # Component A: CPU Theoretical Score (30 pts)
        cpu_spec_score = min(30.0, (exp.cpu_multi_thread_index * 0.22) + (exp.cpu_single_thread_index * 0.08))
        spec_breakdown.append({
            "component": "CPU Silicon & Power Scaling",
            "weight": 30,
            "awarded": round(cpu_spec_score, 1),
            "reason": f"IPC Index ({laptop.cpu.architecture}) + PL1 {laptop.cpu.oem_pl1_w.value or 45}W power ceiling."
        })

        # Component B: GPU Silicon & TGP Allocation (35 pts)
        if laptop.gpu.is_discrete:
            gpu_tgp = laptop.gpu.oem_base_tgp_w.value if laptop.gpu.oem_base_tgp_w.is_known else 45.0
            tgp_ratio = gpu_tgp / laptop.gpu.silicon_max_possible_tgp_w
            vram_pts = min(10.0, (laptop.gpu.vram_gb / 16.0) * 10.0)
            compute_pts = min(25.0, (exp.gpu_fp32_tflops_expected / 15.0) * 20.0 * tgp_ratio)
            gpu_spec_score = round(min(35.0, vram_pts + compute_pts), 1)
            reason_gpu = f"{laptop.gpu.exact_model} at {gpu_tgp}W TGP ({tgp_ratio*100:.0f}% of max); {laptop.gpu.vram_gb}GB VRAM."
        else:
            gpu_spec_score = 10.0
            reason_gpu = "Integrated graphics baseline."
        spec_breakdown.append({
            "component": "GPU Silicon, TGP & VRAM Envelope",
            "weight": 35,
            "awarded": gpu_spec_score,
            "reason": reason_gpu
        })

        # Component C: Memory Subsystem Topology (20 pts)
        if laptop.memory.channel_configuration == "DUAL_CHANNEL":
            ram_spec_score = min(20.0, 14.0 + (laptop.memory.total_capacity_gb / 32.0) * 6.0)
            reason_ram = f"Dual-channel 128-bit bus active ({exp.ram_expected_bandwidth_gbps} GB/s theoretical throughput)."
        else:
            ram_spec_score = min(10.0, 6.0 + (laptop.memory.total_capacity_gb / 32.0) * 4.0)
            reason_ram = "PENALIZED: Single-channel 64-bit bus halves memory bandwidth."
            findings.append(PerformanceFinding(
                severity="WARNING",
                code="MEMORY_BANDWIDTH_STARVATION",
                title="Memory Bandwidth Halved by Single-Channel Bus",
                message=f"Single-channel {laptop.memory.ram_type} chokes CPU data feeding under parallel OpenMP/build workloads.",
                remediation="Populate the second SODIMM slot with a matching module."
            ))
        spec_breakdown.append({
            "component": "Memory Bus Bandwidth & Channels",
            "weight": 20,
            "awarded": round(ram_spec_score, 1),
            "reason": reason_ram
        })

        # Component D: Storage Interface & Expansion (15 pts)
        storage_pts = 10.0 if laptop.storage.drives and laptop.storage.drives[0].pcie_generation >= 4 else 6.0
        if laptop.storage.drives and laptop.storage.drives[0].has_dram_cache.value is True:
            storage_pts += 5.0
            reason_ssd = "PCIe Gen4 NVMe with dedicated DRAM cache buffer (+5 pts)."
        else:
            storage_pts += 1.0
            reason_ssd = "DRAM-less SSD; sustained writes vulnerable to controller saturation."
        spec_breakdown.append({
            "component": "Storage Speed & Controller Hierarchy",
            "weight": 15,
            "awarded": round(storage_pts, 1),
            "reason": reason_ssd
        })

        spec_total = round(sum(item["awarded"] for item in spec_breakdown), 1)

        # 3. SUSTAINED THERMAL THROTTLING EVALUATION
        # Calculate retention drop based on cooling capacity vs heat generation
        combined_load = (laptop.cpu.oem_pl1_w.value or 45.0) + (laptop.gpu.oem_base_tgp_w.value or 0.0)
        cooling_capacity = laptop.cooling.rated_thermal_dissipation_watts.value if laptop.cooling.rated_thermal_dissipation_watts.is_known else (60.0 * max(1, laptop.cooling.fan_count))

        if measured and measured.cinebench_r23_multi_initial and measured.cinebench_r23_multi_sustained:
            # Physical measured loop retention
            retention_pct = round((measured.cinebench_r23_multi_sustained / measured.cinebench_r23_multi_initial) * 100.0, 1)
        elif measured and measured.syspulse_multi_gflops:
            # SysPulse empirical quick retention
            retention_pct = 95.0
        else:
            # Model cooling deficit
            if cooling_capacity >= combined_load:
                retention_pct = 95.0
            else:
                deficit_pct = (combined_load - cooling_capacity) / combined_load
                retention_pct = round(max(60.0, 95.0 - (deficit_pct * 40.0)), 1)

        if retention_pct >= 92.0:
            ret_grade = "EXCELLENT"
            ret_penalty = 0.0
        elif retention_pct >= 85.0:
            ret_grade = "ACCEPTABLE"
            ret_penalty = 5.0
        elif retention_pct >= 75.0:
            ret_grade = "HEAVY_THROTTLE"
            ret_penalty = 18.0
            findings.append(PerformanceFinding(
                severity="WARNING",
                code="SUSTAINED_THERMAL_THROTTLE",
                title="Sustained Thermal Drop-Off Exceeds 15%",
                message=f"Performance drops to {retention_pct}% of burst speeds during continuous multi-minute rendering.",
                remediation="Elevate laptop rear or apply high-performance thermal pad (PTM7950)."
            ))
        else:
            ret_grade = "SEVERE_THROTTLE"
            ret_penalty = 35.0
            findings.append(PerformanceFinding(
                severity="FATAL",
                code="THERMAL_WALL_COLLAPSE",
                title="Thermal Dissipation Deficit (Severe Throttle Wall)",
                message=f"System collapses by {100.0 - retention_pct:.0f}% under sustained load. Severe heatsink inadequacy.",
                remediation="Avoid for long multi-threaded compilation, 3D rendering, or training."
            ))

        gpu_throttle = 0.5
        if laptop.cooling.heatpipe_topology == "SHARED_HEATPIPES" and laptop.gpu.is_discrete:
            gpu_throttle = 8.5
            findings.append(PerformanceFinding(
                severity="ADVISORY",
                code="SHARED_PIPE_CROSS_THROTTLE",
                title="Shared Heatpipe Cross-Thermal Contention",
                message="Shared CPU/GPU heatpipes transfer CPU heat spikes onto the GPU cold plate, inducing clock jitter.",
                remediation="Lock framerates to avoid concurrent 100% CPU+GPU saturation."
            ))

        throttling_res = SustainedThrottlingResult(
            cpu_retention_pct=retention_pct,
            gpu_cross_throttle_pct=gpu_throttle,
            thermal_retention_grade=ret_grade,
            thermal_penalty_points=ret_penalty
        )

        sustained_score = round(max(10.0, spec_total - ret_penalty), 1)

        # 4. MEASURED REAL PERFORMANCE SCORE (If physical benchmarks exist)
        measured_total = None
        if measured:
            # Normalize empirical real benchmark data:
            # Cinebench Multi: 25,000 pts = 100; 10,000 pts = 40
            # TimeSpy Graphics: 12,000 pts = 100; 5,000 pts = 42
            m_cpu = 0.0
            if measured.cinebench_r23_multi_sustained:
                m_cpu = min(35.0, (measured.cinebench_r23_multi_sustained / 25000.0) * 35.0)
            elif measured.syspulse_multi_gflops:
                m_cpu = min(35.0, (measured.syspulse_multi_gflops / 6000.0) * 35.0)

            m_gpu = 0.0
            if measured.timespy_graphics:
                m_gpu = min(35.0, (measured.timespy_graphics / 12000.0) * 35.0)
            elif measured.syspulse_cuda_tflops:
                m_gpu = min(35.0, (measured.syspulse_cuda_tflops / 0.50) * 35.0)

            m_ram = 0.0
            if measured.syspulse_ram_bandwidth_gbps:
                m_ram = min(15.0, (measured.syspulse_ram_bandwidth_gbps / 50.0) * 15.0)
            else:
                m_ram = 10.0

            m_storage = 0.0
            if measured.crystaldisk_read_mbps:
                m_storage = min(15.0, (measured.crystaldisk_read_mbps / 7000.0) * 15.0)
            else:
                m_storage = 10.0

            measured_total = round(m_cpu + m_gpu + m_ram + m_storage, 1)

            # Detect Paper Spec vs Real World Benchmark Discrepancy
            delta = spec_total - measured_total
            if delta > 15.0:
                discrepancies.append(
                    f"MARKETING DEFICIT: Specification Score ({spec_total}) is {delta:.1f} points higher than "
                    f"Measured Score ({measured_total}). Firmware power limits or thermal throttling are cutting into real performance!"
                )
            elif delta < -10.0:
                discrepancies.append(
                    f"OVER-PERFORMANCE: Measured Score ({measured_total}) exceeded paper expectations by {abs(delta):.1f} points. "
                    "Excellent OEM thermal engineering and silicon binning."
                )
            else:
                discrepancies.append(
                    f"CONSISTENT AUDIT: Measured hardware throughput ({measured_total}) aligns within {abs(delta):.1f} points of theoretical design."
                )

        return PerformanceAuditResult(
            specification_score=spec_total,
            measured_performance_score=measured_total,
            sustained_performance_score=sustained_score,
            expected_metrics=exp,
            measured_metrics=measured,
            throttling=throttling_res,
            spec_score_breakdown=spec_breakdown,
            measured_score_breakdown=measured_breakdown,
            discrepancy_analysis=discrepancies,
            findings=findings
        )
