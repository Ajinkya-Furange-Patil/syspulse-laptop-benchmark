"""
SysPulse Laptop Buyer Audit Engine - Workload & Use-Case Fit Scoring Engine
Evaluates 6 completely separate domain workloads:
1. Modern Gaming
2. AI / Machine Learning & Local LLMs (Enforces HARD VRAM Capacity Limits)
3. Programming & Software Development
4. Engineering & CAD / CAE
5. Content Creation & Video Production
6. Campus Portability & Battery Life
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import math
from audit_engine.models import LaptopSpecification


# -----------------------------------------------------------------------------
# Data Models for Domain Results
# -----------------------------------------------------------------------------

@dataclass
class GamingSuitability:
    score_1080p: float
    score_1440p_1600p: float
    score_high_refresh_esports: float
    score_aaa_heavy: float
    score_ray_tracing: float
    overall_gaming_score: float
    gaming_tier: str  # FLAGSHIP_4K, ENTHUSIAST_1440P, SOLID_1080P_HIGH, ENTRY_1080P_MED, ESPORTS_ONLY
    bottlenecks: List[str]
    breakdown: List[Dict[str, Any]]


@dataclass
class AiMlSuitability:
    vram_hard_limit_flag: Optional[str]  # e.g., "VRAM CAPACITY LIMIT: OOM ON SDXL & 8B LLMs"
    largest_local_llm_parameter_fit: str # "Llama-3 8B (Q4_K_M GGUF)", "None (<3B only)"
    lora_fine_tuning_viable: bool
    stable_diffusion_sdxl_viable: bool
    score_local_inference: float
    score_small_model_lora: float
    score_computer_vision_yolo: float
    score_cuda_development: float
    overall_aiml_score: float
    aiml_tier: str  # PRODUCTION_RESEARCH, RESEARCH_SWEETSPOT, ENTRY_INFERENCE, UNSUITABLE
    hard_limitations: List[str]
    breakdown: List[Dict[str, Any]]


@dataclass
class SoftwareDevSuitability:
    vm_and_docker_tier: str  # MULTI_VM_K8S_READY, DOCKER_CONTAINER_READY, TIGHT_MEMORY_CEILING
    linux_compatibility_rating: str # EXCELLENT, GOOD, TRICKY_OPTIMUS_DRIVERS
    code_compilation_speed_rating: str # BLAZING, FAST, MODERATE, SLOW
    score_compilation_multi_thread: float
    score_ram_capacity_headroom: float
    score_virtualization_dockers: float
    score_display_vertical_code_view: float
    overall_dev_score: float
    dev_tier: str
    breakdown: List[Dict[str, Any]]


@dataclass
class EngineeringCadSuitability:
    solidworks_cad_rating: str
    fea_cfd_simulation_rating: str
    score_cad_viewport_single_thread: float
    score_simulation_multi_thread: float
    score_sustained_thermal_stability: float
    overall_engineering_score: float
    engineering_tier: str
    breakdown: List[Dict[str, Any]]


@dataclass
class ContentCreationSuitability:
    video_editing_4k_timeline: str # SMOOTH_4K_MULTI_CAM, CAPABLE_SINGLE_STREAM, PROXY_WORKFLOW_ONLY
    color_accuracy_grade: str      # CALIBRATED_STUDIO, ACCEPTABLE, WASHED_OUT_TRAP
    hardware_encoders_available: List[str]
    score_timeline_scrubbing: float
    score_render_export_nvenc: float
    score_display_color_fidelity: float
    overall_creator_score: float
    creator_tier: str
    breakdown: List[Dict[str, Any]]


@dataclass
class PortabilitySuitability:
    true_travel_weight_kg: float   # Laptop weight + adapter weight
    estimated_office_runtime_hours: float
    usb_c_charging_flexibility: str
    score_chassis_weight: float
    score_battery_endurance: float
    score_charging_versatility: float
    overall_portability_score: float
    portability_tier: str
    breakdown: List[Dict[str, Any]]


@dataclass
class MasterWorkloadAuditReport:
    gaming: GamingSuitability
    ai_ml: AiMlSuitability
    software_dev: SoftwareDevSuitability
    engineering_cad: EngineeringCadSuitability
    content_creation: ContentCreationSuitability
    portability: PortabilitySuitability
    workload_winner_matrix: Dict[str, str]


# -----------------------------------------------------------------------------
# Workload Evaluation Engine
# -----------------------------------------------------------------------------

class WorkloadScoringEngine:
    """
    Rigorously audits suitability across individual distinct domains.
    Enforces non-linear utility curves, display aspect ratio benefits,
    and hard VRAM memory cliffs.
    """

    @classmethod
    def evaluate_all(cls, laptop: LaptopSpecification) -> MasterWorkloadAuditReport:
        gaming = cls.evaluate_gaming(laptop)
        ai_ml = cls.evaluate_ai_ml(laptop)
        software_dev = cls.evaluate_software_dev(laptop)
        engineering = cls.evaluate_engineering(laptop)
        creator = cls.evaluate_content_creation(laptop)
        portability = cls.evaluate_portability(laptop)

        # Winner analysis
        scores = {
            "Gaming": gaming.overall_gaming_score,
            "AI / Machine Learning": ai_ml.overall_aiml_score,
            "Software Development": software_dev.overall_dev_score,
            "Engineering / CAD": engineering.overall_engineering_score,
            "Content Creation": creator.overall_creator_score,
            "Portability / Mobility": portability.overall_portability_score
        }
        best_workload = max(scores, key=scores.get)
        worst_workload = min(scores, key=scores.get)

        winner_matrix = {
            "Strongest Domain": f"{best_workload} ({scores[best_workload]:.1f}/100)",
            "Weakest Domain": f"{worst_workload} ({scores[worst_workload]:.1f}/100)"
        }

        return MasterWorkloadAuditReport(
            gaming=gaming,
            ai_ml=ai_ml,
            software_dev=software_dev,
            engineering_cad=engineering,
            content_creation=creator,
            portability=portability,
            workload_winner_matrix=winner_matrix
        )

    # -------------------------------------------------------------------------
    # 1. GAMING WORKLOAD EVALUATION
    # -------------------------------------------------------------------------
    @classmethod
    def evaluate_gaming(cls, laptop: LaptopSpecification) -> GamingSuitability:
        breakdown = []
        bottlenecks = []

        gpu = laptop.gpu
        tgp = gpu.oem_base_tgp_w.value if gpu.oem_base_tgp_w.is_known else 45.0
        vram = gpu.vram_gb
        has_mux = gpu.has_mux_switch.value if gpu.has_mux_switch.is_known else False
        has_vrr = laptop.display.vrr_technology in ("G_SYNC", "FreeSync", "AdaptiveSync")
        resp_ms = laptop.display.response_time_gtg_ms.value if laptop.display.response_time_gtg_ms.is_known else 8.0
        hz = laptop.display.refresh_rate_hz

        if not gpu.is_discrete:
            return GamingSuitability(
                score_1080p=25.0, score_1440p_1600p=5.0, score_high_refresh_esports=30.0,
                score_aaa_heavy=5.0, score_ray_tracing=0.0, overall_gaming_score=15.0,
                gaming_tier="INTEGRATED_GRAPHICS_CASUAL_ONLY",
                bottlenecks=["No discrete GPU; shared system memory limits framerates."],
                breakdown=[{"factor": "iGPU Only", "score": 15.0, "reason": "Lacks dedicated VRAM & shaders."}]
            )

        # 1080p Suitability (0 - 100)
        s_1080p = min(100.0, (gpu.cuda_cores_or_shaders / 3072.0) * 50.0 + (tgp / 100.0) * 35.0 + (vram / 8.0) * 15.0)

        # 1440p / 1600p Suitability (Requires VRAM >= 8GB and TGP >= 85W)
        if vram < 6.0:
            s_1440p = 15.0
            bottlenecks.append(f"{vram}GB VRAM triggers catastrophic texture stutter at 1440p/1600p.")
        elif vram < 8.0:
            s_1440p = min(60.0, (tgp / 100.0) * 50.0)
        else:
            s_1440p = min(100.0, (gpu.cuda_cores_or_shaders / 4608.0) * 45.0 + (tgp / 120.0) * 35.0 + (vram / 12.0) * 20.0)

        # High-Refresh Esports Suitability (High Hz + MUX switch + fast GTG response)
        s_esports = min(100.0, (hz / 240.0) * 40.0 + (10.0 if has_mux else 0.0) + (10.0 if has_vrr else 0.0) + (40.0 if resp_ms <= 4.0 else (20.0 if resp_ms <= 10.0 else 5.0)))
        if resp_ms > 15.0 and hz >= 120:
            bottlenecks.append(f"Panel GTG response time is {resp_ms}ms; severe ghosting in fast shooters despite {hz}Hz.")

        # AAA Modern Heavies (Cyberpunk, Black Myth: Wukong, Alan Wake 2)
        s_aaa = min(100.0, (vram / 8.0) * 30.0 + (tgp / 120.0) * 40.0 + (gpu.cuda_cores_or_shaders / 3072.0) * 30.0)

        # Ray Tracing Suitability (Requires RT cores & Ada Lovelace DLSS 3)
        if gpu.rt_cores > 0 and "Ada" in gpu.architecture:
            s_rt = min(100.0, (gpu.rt_cores / 36.0) * 60.0 + (vram / 8.0) * 40.0)
        elif gpu.rt_cores > 0:
            s_rt = min(65.0, (gpu.rt_cores / 36.0) * 40.0 + (vram / 8.0) * 25.0)
        else:
            s_rt = 5.0
            bottlenecks.append("Lacks dedicated Ray Tracing acceleration cores.")

        if not has_mux:
            bottlenecks.append("No hardware MUX switch: 5–15% FPS penalty caused by routing frames through iGPU.")

        overall = round(s_1080p * 0.30 + s_1440p * 0.25 + s_esports * 0.20 + s_aaa * 0.15 + s_rt * 0.10, 1)

        if overall >= 85.0:
            tier = "ENTHUSIAST_1440P_READY"
        elif overall >= 70.0:
            tier = "SOLID_1080P_ULTRA"
        elif overall >= 50.0:
            tier = "ENTRY_1080P_MEDIUM"
        else:
            tier = "ESPORTS_720P_COMPROMISED"

        breakdown.append({"metric": "1080p Native Gaming", "score": round(s_1080p, 1), "weight": "30%"})
        breakdown.append({"metric": "1440p/1600p High-Res Gaming", "score": round(s_1440p, 1), "weight": "25%"})
        breakdown.append({"metric": "High-Refresh Esports Motion", "score": round(s_esports, 1), "weight": "20%"})
        breakdown.append({"metric": "AAA Heavy Titles", "score": round(s_aaa, 1), "weight": "15%"})
        breakdown.append({"metric": "Hardware Ray-Tracing & DLSS", "score": round(s_rt, 1), "weight": "10%"})

        return GamingSuitability(
            score_1080p=round(s_1080p, 1),
            score_1440p_1600p=round(s_1440p, 1),
            score_high_refresh_esports=round(s_esports, 1),
            score_aaa_heavy=round(s_aaa, 1),
            score_ray_tracing=round(s_rt, 1),
            overall_gaming_score=overall,
            gaming_tier=tier,
            bottlenecks=bottlenecks,
            breakdown=breakdown
        )

    # -------------------------------------------------------------------------
    # 2. AI & MACHINE LEARNING (HARD VRAM CAPACITY CLIFFS)
    # -------------------------------------------------------------------------
    @classmethod
    def evaluate_ai_ml(cls, laptop: LaptopSpecification) -> AiMlSuitability:
        breakdown = []
        hard_limits = []
        gpu = laptop.gpu
        vram = gpu.vram_gb
        has_cuda = gpu.manufacturer == "NVIDIA"
        tensor_cores = gpu.tensor_cores
        vram_bw = gpu.memory_bandwidth_gbps.value if gpu.memory_bandwidth_gbps.is_known else 256.0

        vram_flag = None
        lora_viable = False
        sdxl_viable = False

        # VRAM HARD RESOURCE CLIFF AUDIT
        if not has_cuda:
            vram_flag = "NON-CUDA PLATFORM: LACKS NATIVE TENSORRT & PYTORCH ACCELERATION"
            hard_limits.append("PyTorch and modern ML pipelines require extensive configuration or fall back to slow CPU inference.")
            largest_llm = "CPU Offload Only (Extremely Slow)"
            lora_viable = False
            sdxl_viable = False
            s_inf = 15.0
            s_lora = 0.0
            s_cv = 25.0
            s_cuda = 0.0
        elif vram < 6.0:
            vram_flag = "VRAM CAPACITY LIMIT: 4GB VRAM IS A DEAD-END FOR MODERN AI"
            hard_limits.append("OUT OF MEMORY: Cannot load Llama-3 8B even in 4-bit quantization without spilling to system RAM.")
            hard_limits.append("OUT OF MEMORY: Stable Diffusion XL (SDXL) will crash with CUDA OutOfMemoryError.")
            largest_llm = "TinyLlama 1.1B or Phi-2 2.7B (Q4 only)"
            lora_viable = False
            sdxl_viable = False
            s_inf = 20.0
            s_lora = 0.0
            s_cv = 40.0
            s_cuda = 25.0
        elif vram < 8.0:
            vram_flag = "VRAM CAPACITY CEILING: 6GB RESTRICTS LARGE MODELS"
            hard_limits.append("Can run 3B-7B models in aggressive 4-bit quantization, but zero headroom for context window expansion (>2k tokens).")
            largest_llm = "Mistral 7B (Q3_K_S) / Gemma 2B"
            lora_viable = False
            sdxl_viable = False
            s_inf = 48.0
            s_lora = 15.0
            s_cv = 60.0
            s_cuda = 45.0
        elif vram < 12.0:
            # 8GB VRAM (Sweet spot for students)
            largest_llm = "Llama-3 8B (Q4_K_M GGUF / AWQ) + 4k Context"
            lora_viable = True
            sdxl_viable = True
            s_inf = 78.0
            s_lora = 60.0  # QLoRA viable
            s_cv = 85.0
            s_cuda = 75.0
            hard_limits.append("Full 16-bit FP16 training not possible. Must use 4-bit QLoRA with gradient checkpointing.")
        elif vram < 16.0:
            largest_llm = "13B Models / Command-R / 8B Full FP16 Inference"
            lora_viable = True
            sdxl_viable = True
            s_inf = 90.0
            s_lora = 85.0
            s_cv = 95.0
            s_cuda = 90.0
        else:
            # 16GB+ VRAM (Workstation Class)
            largest_llm = "33B Quantized / 70B MoE Offload / Full LoRA"
            lora_viable = True
            sdxl_viable = True
            s_inf = 98.0
            s_lora = 95.0
            s_cv = 100.0
            s_cuda = 98.0

        # Memory bandwidth scaling factor
        bw_factor = min(1.0, vram_bw / 256.0)
        s_inf = round(s_inf * bw_factor, 1)

        overall = round(s_inf * 0.35 + s_lora * 0.25 + s_cv * 0.20 + s_cuda * 0.20, 1)

        if overall >= 85.0:
            tier = "PRODUCTION_RESEARCH_WORKSTATION"
        elif overall >= 65.0:
            tier = "ACADEMIC_STUDENT_SWEETSPOT (QLoRA & 8B LLMs)"
        elif overall >= 40.0:
            tier = "LIGHT_INFERENCE_ONLY (<7B Quantized)"
        else:
            tier = "UNSUITABLE_FOR_LOCAL_AI"

        breakdown.append({"metric": "Local LLM Inference", "score": s_inf, "weight": "35%", "note": f"Fit: {largest_llm}"})
        breakdown.append({"metric": "QLoRA Parameter Tuning", "score": s_lora, "weight": "25%", "note": "Viable" if lora_viable else "OUT OF MEMORY"})
        breakdown.append({"metric": "Computer Vision & YOLO", "score": s_cv, "weight": "20%", "note": "TensorRT Accelerated" if has_cuda else "CPU Only"})
        breakdown.append({"metric": "CUDA Compute Architecture", "score": s_cuda, "weight": "20%", "note": f"{tensor_cores} Tensor Cores"})

        return AiMlSuitability(
            vram_hard_limit_flag=vram_flag,
            largest_local_llm_parameter_fit=largest_llm,
            lora_fine_tuning_viable=lora_viable,
            stable_diffusion_sdxl_viable=sdxl_viable,
            score_local_inference=s_inf,
            score_small_model_lora=s_lora,
            score_computer_vision_yolo=s_cv,
            score_cuda_development=s_cuda,
            overall_aiml_score=overall,
            aiml_tier=tier,
            hard_limitations=hard_limits,
            breakdown=breakdown
        )

    # -------------------------------------------------------------------------
    # 3. PROGRAMMING & SOFTWARE DEVELOPMENT
    # -------------------------------------------------------------------------
    @classmethod
    def evaluate_software_dev(cls, laptop: LaptopSpecification) -> SoftwareDevSuitability:
        breakdown = []
        cpu = laptop.cpu
        ram_gb = laptop.memory.total_capacity_gb
        channels = laptop.memory.channel_configuration
        ssd_dram = laptop.storage.drives[0].has_dram_cache.value if laptop.storage.drives else False
        aspect = laptop.display.aspect_ratio

        # Compilation multi-threading
        s_compile = min(100.0, (cpu.total_threads / 24.0) * 60.0 + (cpu.boost_clock_ghz / 5.0) * 40.0)
        if channels == "SINGLE_CHANNEL":
            s_compile = round(s_compile * 0.72, 1)  # 28% compilation penalty on single-channel

        # RAM Headroom for Docker & VMs
        if ram_gb < 16:
            s_ram = 25.0
            vm_tier = "TIGHT_MEMORY_CEILING: IDE + Browser consumes baseline. Docker swapping to disk."
        elif ram_gb == 16:
            s_ram = 68.0
            vm_tier = "DOCKER_CONTAINER_READY: Supports 3-5 active containers alongside IDE."
        elif ram_gb <= 32:
            s_ram = 92.0
            vm_tier = "MULTI_VM_K8S_READY: Excellent capacity for local Kubernetes clusters."
        else:
            s_ram = 100.0
            vm_tier = "ENTERPRISE_WORKSTATION_GRADE: Massive virtualization headroom."

        # Virtualization & WSL2
        s_virt = min(100.0, (cpu.total_physical_cores / 12.0) * 50.0 + (s_ram * 0.50))

        # Vertical Code Viewport (16:10 / 3:2 displays show 12-18% more code lines than 16:9)
        if aspect in ("16:10", "3:2"):
            s_display_code = 95.0
        else:
            s_display_code = 70.0

        overall = round(s_compile * 0.35 + s_ram * 0.35 + s_virt * 0.20 + s_display_code * 0.10, 1)

        if overall >= 85.0:
            tier = "TIER-1_DEVELOPER_RIG (Heavy Compilation & Multi-VMs)"
        elif overall >= 70.0:
            tier = "PROFESSIONAL_FULL_STACK (Docker & IDEs)"
        else:
            tier = "ENTRY_LEVEL_SCRIPTING (Memory or Core Bound)"

        breakdown.append({"metric": "Parallel Build Compilation", "score": s_compile, "weight": "35%"})
        breakdown.append({"metric": "Memory Headroom for Containers", "score": s_ram, "weight": "35%"})
        breakdown.append({"metric": "Virtualization & WSL2", "score": s_virt, "weight": "20%"})
        breakdown.append({"metric": "Vertical Code Aspect Ratio", "score": s_display_code, "weight": "10%"})

        return SoftwareDevSuitability(
            vm_and_docker_tier=vm_tier,
            linux_compatibility_rating="GOOD" if laptop.gpu.is_discrete else "EXCELLENT (Native iGPU Kernel)",
            code_compilation_speed_rating="BLAZING" if s_compile >= 85 else ("FAST" if s_compile >= 65 else "MODERATE"),
            score_compilation_multi_thread=s_compile,
            score_ram_capacity_headroom=s_ram,
            score_virtualization_dockers=s_virt,
            score_display_vertical_code_view=s_display_code,
            overall_dev_score=overall,
            dev_tier=tier,
            breakdown=breakdown
        )

    # -------------------------------------------------------------------------
    # 4. ENGINEERING & CAD / SIMULATION
    # -------------------------------------------------------------------------
    @classmethod
    def evaluate_engineering(cls, laptop: LaptopSpecification) -> EngineeringCadSuitability:
        breakdown = []
        cpu = laptop.cpu
        gpu = laptop.gpu
        ram = laptop.memory.total_capacity_gb

        # CAD Viewport (SolidWorks, Inventor, AutoCAD) is heavily bound to Single-Core IPC + OpenGL/DirectX
        s_cad = min(100.0, (cpu.boost_clock_ghz / 5.2) * 55.0 + (35.0 if gpu.is_discrete else 10.0) + (10.0 if ram >= 16 else 0.0))

        # FEA / CFD Numerical Simulation (ANSYS, COMSOL, OpenFOAM) is bound to all-core sustained power & AVX-512
        avx512_bonus = 15.0 if cpu.avx512 else 0.0
        pl1 = cpu.oem_pl1_w.value if cpu.oem_pl1_w.is_known else 45.0
        s_sim = min(100.0, (cpu.total_threads / 20.0) * 45.0 + (pl1 / 90.0) * 30.0 + avx512_bonus + (10.0 if ram >= 32 else 0.0))

        # Sustained Thermal Stability
        cooling_watts = laptop.cooling.rated_thermal_dissipation_watts.value if laptop.cooling.rated_thermal_dissipation_watts.is_known else 100.0
        s_therm = min(100.0, (cooling_watts / 160.0) * 100.0)

        overall = round(s_cad * 0.40 + s_sim * 0.40 + s_therm * 0.20, 1)

        breakdown.append({"metric": "Single-Thread CAD Viewport", "score": round(s_cad, 1), "weight": "40%"})
        breakdown.append({"metric": "FEA/CFD Simulation Throughput", "score": round(s_sim, 1), "weight": "40%"})
        breakdown.append({"metric": "Continuous Thermal Endurance", "score": round(s_therm, 1), "weight": "20%"})

        return EngineeringCadSuitability(
            solidworks_cad_rating="SMOOTH_COMPLEX_ASSEMBLIES" if s_cad >= 80 else "ADEQUATE_STUDENT_PARTS",
            fea_cfd_simulation_rating="HIGH_SCALE_SOLVER" if s_sim >= 80 else "MODERATE_MESH_ONLY",
            score_cad_viewport_single_thread=round(s_cad, 1),
            score_simulation_multi_thread=round(s_sim, 1),
            score_sustained_thermal_stability=round(s_therm, 1),
            overall_engineering_score=overall,
            engineering_tier="WORKSTATION_CLASS" if overall >= 80 else ("SOLID_ENGINEERING_LAPTOP" if overall >= 60 else "ENTRY_ONLY"),
            breakdown=breakdown
        )

    # -------------------------------------------------------------------------
    # 5. CONTENT CREATION & VIDEO PRODUCTION
    # -------------------------------------------------------------------------
    @classmethod
    def evaluate_content_creation(cls, laptop: LaptopSpecification) -> ContentCreationSuitability:
        breakdown = []
        gpu = laptop.gpu
        disp = laptop.display
        srgb = disp.color_gamut_srgb_pct.value if disp.color_gamut_srgb_pct.is_known else 60.0
        dci_p3 = disp.color_gamut_dci_p3_pct.value if disp.color_gamut_dci_p3_pct.is_known else 45.0
        delta_e = disp.delta_e_accuracy.value if disp.delta_e_accuracy.is_known else 4.5

        # Display Color Grading Score (sRGB >= 100%, DCI-P3 >= 95%, Delta E < 2.0)
        if srgb <= 65.0:
            s_color = 20.0
            color_grade = "WASHED_OUT_TRAP: 45% NTSC / <=60% sRGB is completely unsuitable for color grading."
        elif srgb >= 99.0 and dci_p3 >= 90.0:
            s_color = 95.0 if delta_e <= 2.0 else 85.0
            color_grade = "CALIBRATED_STUDIO: Wide DCI-P3 cinema coverage with low Delta E."
        else:
            s_color = 65.0
            color_grade = "ACCEPTABLE_WEB_ONLY: 100% sRGB for YouTube/Web; partial DCI-P3."

        # Timeline Scrubbing (Requires Fast NVMe + RAM >= 16GB + QuickSync/NVDEC)
        s_scrub = min(100.0, (laptop.memory.total_capacity_gb / 32.0) * 45.0 + (gpu.vram_gb / 8.0) * 35.0 + 20.0)

        # Hardware Encoders
        encoders = []
        if gpu.is_discrete:
            if gpu.nvenc_generation:
                encoders.append(f"NVENC ({gpu.nvenc_generation})")
            else:
                encoders.append("NVENC Hardware")
            if gpu.av1_encode_hardware:
                encoders.append("AV1 Hardware Encode")
        if "Intel" in laptop.cpu.manufacturer:
            encoders.append("Intel QuickSync Video (4:2:2 10-bit HEVC)")

        s_encode = 95.0 if "AV1" in str(encoders) else (75.0 if encoders else 30.0)

        overall = round(s_color * 0.40 + s_scrub * 0.35 + s_encode * 0.25, 1)

        breakdown.append({"metric": "Display Color Gamut & Accuracy", "score": s_color, "weight": "40%"})
        breakdown.append({"metric": "4K Timeline Scrubbing & VRAM", "score": s_scrub, "weight": "35%"})
        breakdown.append({"metric": "Hardware Media Export (NVENC/AV1)", "score": s_encode, "weight": "25%"})

        return ContentCreationSuitability(
            video_editing_4k_timeline="SMOOTH_4K_MULTI_CAM" if s_scrub >= 80 else "CAPABLE_SINGLE_STREAM",
            color_accuracy_grade=color_grade,
            hardware_encoders_available=encoders,
            score_timeline_scrubbing=s_scrub,
            score_render_export_nvenc=s_encode,
            score_display_color_fidelity=s_color,
            overall_creator_score=overall,
            creator_tier="STUDIO_PRODUCTION_READY" if overall >= 80 else ("SOLID_CREATOR_MACHINE" if overall >= 60 else "WASHED_OUT_DISPLAY_RESTRICTED"),
            breakdown=breakdown
        )

    # -------------------------------------------------------------------------
    # 6. CAMPUS PORTABILITY & MOBILITY
    # -------------------------------------------------------------------------
    @classmethod
    def evaluate_portability(cls, laptop: LaptopSpecification) -> PortabilitySuitability:
        breakdown = []
        chassis_wt = laptop.chassis.weight_kg.value if laptop.chassis.weight_kg.is_known else 2.3
        adapter_wt = 0.35 if laptop.power.adapter_form_factor == "SLIM_GAN" else (0.85 if laptop.power.adapter_rating_w >= 200 else 0.55)
        true_travel_wt = round(chassis_wt + adapter_wt, 2)

        # Weight Score
        if true_travel_wt <= 1.8:
            s_wt = 95.0
        elif true_travel_wt <= 2.4:
            s_wt = 75.0
        elif true_travel_wt <= 3.0:
            s_wt = 50.0
        else:
            s_wt = 25.0

        # Battery Life Estimation
        wh = laptop.power.battery_capacity_wh
        has_dgpu = laptop.gpu.is_discrete
        # Idle/Office draw estimate: 8W for efficient iGPU/chassis; 14W for gaming chassis
        idle_draw = 14.0 if has_dgpu else 7.5
        est_hours = round(wh / idle_draw, 1)

        s_battery = min(100.0, (wh / 99.9) * 100.0)

        # Charging Versatility (USB-C PD)
        s_charge = 95.0 if laptop.power.usb_c_pd_charging_supported else 40.0

        overall = round(s_wt * 0.40 + s_battery * 0.40 + s_charge * 0.20, 1)

        breakdown.append({"metric": "Travel Weight (Chassis + Charger)", "score": s_wt, "weight": "40%", "note": f"{true_travel_wt} kg total"})
        breakdown.append({"metric": "Battery Capacity & Endurance", "score": s_battery, "weight": "40%", "note": f"{wh} Wh (~{est_hours} hrs light use)"})
        breakdown.append({"metric": "USB-C PD Travel Charging", "score": s_charge, "weight": "20%", "note": "Supported" if laptop.power.usb_c_pd_charging_supported else "Barrel only"})

        return PortabilitySuitability(
            true_travel_weight_kg=true_travel_wt,
            estimated_office_runtime_hours=est_hours,
            usb_c_charging_flexibility="VERSATILE_TYPE_C_PD" if laptop.power.usb_c_pd_charging_supported else "PROPRIETARY_BRICK_MANDATORY",
            score_chassis_weight=s_wt,
            score_battery_endurance=s_battery,
            score_charging_versatility=s_charge,
            overall_portability_score=overall,
            portability_tier="ULTRA_PORTABLE_ALL_DAY" if overall >= 80 else ("COMMUTER_FRIENDLY" if overall >= 60 else "DESKTOP_REPLACEMENT_HEAVY"),
            breakdown=breakdown
        )
