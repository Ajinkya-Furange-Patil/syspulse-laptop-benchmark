"""
SysPulse Laptop Buyer Audit Engine - Data Models
Defines strongly typed, normalized data structures for all hardware subsystems.
Every critical parameter is tracked with provenance, status, and confidence.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, List, Dict, Any, TypeVar, Generic
import json


class FieldStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    ESTIMATED = "ESTIMATED"
    UNKNOWN = "UNKNOWN"


class DataSource(str, Enum):
    OEM_SPEC = "OEM_SPEC"
    BENCHMARK_MEASURED = "BENCHMARK_MEASURED"
    COMMUNITY_DATABASE = "COMMUNITY_DATABASE"
    USER_MANUAL_INPUT = "USER_MANUAL_INPUT"
    UNKNOWN = "UNKNOWN"


T = TypeVar("T")


@dataclass
class AuditField(Generic[T]):
    """
    Every audited parameter encapsulates the value, certainty status, origin,
    and confidence score [0.0 - 1.0].
    """
    value: Optional[T] = None
    status: FieldStatus = FieldStatus.UNKNOWN
    source: DataSource = DataSource.UNKNOWN
    confidence: float = 0.0

    @classmethod
    def confirmed(cls, val: T, source: DataSource = DataSource.OEM_SPEC) -> "AuditField[T]":
        return cls(value=val, status=FieldStatus.CONFIRMED, source=source, confidence=1.0)

    @classmethod
    def estimated(cls, val: T, confidence: float = 0.6, source: DataSource = DataSource.COMMUNITY_DATABASE) -> "AuditField[T]":
        return cls(value=val, status=FieldStatus.ESTIMATED, source=source, confidence=confidence)

    @classmethod
    def unknown(cls) -> "AuditField[T]":
        return cls(value=None, status=FieldStatus.UNKNOWN, source=DataSource.UNKNOWN, confidence=0.0)

    @property
    def is_known(self) -> bool:
        return self.status != FieldStatus.UNKNOWN and self.value is not None


# Subsystem Models

@dataclass
class ChassisSpec:
    weight_kg: AuditField[float] = field(default_factory=AuditField.unknown)
    thickness_mm: AuditField[float] = field(default_factory=AuditField.unknown)
    chassis_materials: str = "Plastic"
    screw_type: str = "PHILIPS"
    chassis_pry_difficulty: str = "MODERATE"
    easy_maintenance_hatch: bool = False


@dataclass
class CPUSpec:
    manufacturer: str = "Unknown"
    exact_model: str = "Unknown"
    architecture: str = "Unknown"
    generation: str = "Unknown"
    process_node_nm: Optional[float] = None
    total_physical_cores: int = 0
    p_cores: int = 0
    e_cores: int = 0
    total_threads: int = 0
    base_clock_ghz: float = 0.0
    boost_clock_ghz: float = 0.0
    all_core_boost_ghz: AuditField[float] = field(default_factory=AuditField.unknown)
    l2_cache_mb: Optional[float] = None
    l3_cache_mb: Optional[float] = None
    intel_amd_rated_base_power_w: float = 45.0
    intel_amd_rated_max_turbo_w: float = 115.0
    # Crucial OEM Power Envelopes:
    oem_pl1_w: AuditField[float] = field(default_factory=AuditField.unknown)
    oem_pl2_w: AuditField[float] = field(default_factory=AuditField.unknown)
    oem_tau_seconds: AuditField[float] = field(default_factory=AuditField.unknown)
    npu_present: bool = False
    npu_tops: AuditField[float] = field(default_factory=AuditField.unknown)
    avx2: bool = True
    avx512: bool = False
    igpu_model: str = "Unknown"
    pcie_gen: int = 4
    undervolting_supported: AuditField[bool] = field(default_factory=AuditField.unknown)


@dataclass
class GPUSpec:
    is_discrete: bool = True
    manufacturer: str = "NVIDIA"
    exact_model: str = "Unknown"
    chip_code: str = "Unknown"
    architecture: str = "Unknown"
    cuda_cores_or_shaders: int = 0
    tensor_cores: int = 0
    rt_cores: int = 0
    vram_gb: float = 0.0
    vram_type: str = "GDDR6"
    memory_bus_width_bit: AuditField[int] = field(default_factory=AuditField.unknown)
    memory_bandwidth_gbps: AuditField[float] = field(default_factory=AuditField.unknown)
    silicon_max_possible_tgp_w: float = 140.0
    # Crucial OEM GPU Envelopes:
    oem_base_tgp_w: AuditField[float] = field(default_factory=AuditField.unknown)
    oem_dynamic_boost_w: AuditField[float] = field(default_factory=AuditField.unknown)
    graphics_clock_base_mhz: AuditField[int] = field(default_factory=AuditField.unknown)
    graphics_clock_boost_mhz: AuditField[int] = field(default_factory=AuditField.unknown)
    has_mux_switch: AuditField[bool] = field(default_factory=AuditField.unknown)
    advanced_optimus: AuditField[bool] = field(default_factory=AuditField.unknown)
    gsync_support: AuditField[bool] = field(default_factory=AuditField.unknown)
    nvenc_generation: Optional[str] = None
    av1_encode_hardware: bool = False
    cuda_compute_capability: Optional[str] = None


@dataclass
class MemorySpec:
    total_capacity_gb: int = 16
    ram_type: str = "DDR5"
    speed_mts: int = 4800
    channel_configuration: str = "UNKNOWN"  # DUAL_CHANNEL, SINGLE_CHANNEL
    bus_width_bits: AuditField[int] = field(default_factory=AuditField.unknown)
    soldered_capacity_gb: int = 0
    sodimm_slots_total: int = 2
    sodimm_slots_occupied: int = 2
    max_supported_capacity_gb: int = 64
    cas_latency: AuditField[int] = field(default_factory=AuditField.unknown)
    measured_bandwidth_gbps: AuditField[float] = field(default_factory=AuditField.unknown)


@dataclass
class StorageDriveSpec:
    slot_number: int = 1
    exact_ssd_model: AuditField[str] = field(default_factory=AuditField.unknown)
    capacity_gb: int = 512
    form_factor: str = "M.2_2280"
    interface_type: str = "NVMe_PCIe"
    pcie_generation: int = 4
    pcie_lanes: int = 4
    nand_type: str = "TLC"  # SLC, MLC, TLC, QLC, UNKNOWN
    has_dram_cache: AuditField[bool] = field(default_factory=AuditField.unknown)
    sequential_read_mbps: AuditField[float] = field(default_factory=AuditField.unknown)
    sequential_write_mbps: AuditField[float] = field(default_factory=AuditField.unknown)
    sustained_write_throttle_observed: AuditField[bool] = field(default_factory=AuditField.unknown)


@dataclass
class StorageSubsystemSpec:
    total_capacity_gb: int = 512
    m2_slots_total: int = 2
    m2_slots_occupied: int = 1
    drives: List[StorageDriveSpec] = field(default_factory=list)


@dataclass
class DisplaySpec:
    diagonal_inches: float = 15.6
    aspect_ratio: str = "16:9"
    resolution_horizontal: int = 1920
    resolution_vertical: int = 1080
    refresh_rate_hz: int = 144
    panel_technology: str = "IPS"  # IPS, OLED, Mini_LED, TN, VA
    advertised_brightness_nits: float = 300.0
    measured_brightness_nits: AuditField[float] = field(default_factory=AuditField.unknown)
    contrast_ratio: AuditField[float] = field(default_factory=AuditField.unknown)
    response_time_gtg_ms: AuditField[float] = field(default_factory=AuditField.unknown)
    color_gamut_srgb_pct: AuditField[float] = field(default_factory=AuditField.unknown)
    color_gamut_dci_p3_pct: AuditField[float] = field(default_factory=AuditField.unknown)
    delta_e_accuracy: AuditField[float] = field(default_factory=AuditField.unknown)
    vrr_technology: str = "AdaptiveSync"  # G_SYNC, FreeSync, AdaptiveSync, None
    pwm_flicker_free: AuditField[bool] = field(default_factory=AuditField.unknown)
    pwm_frequency_hz: AuditField[float] = field(default_factory=AuditField.unknown)
    surface_finish: str = "MATTE_ANTI_GLARE"


@dataclass
class CoolingSpec:
    fan_count: int = 2
    heatpipe_count: AuditField[int] = field(default_factory=AuditField.unknown)
    heatpipe_topology: str = "HYBRID"  # DEDICATED_CPU_AND_GPU, SHARED_HEATPIPES, HYBRID
    has_vapor_chamber: bool = False
    thermal_interface_material: str = "STANDARD_PASTE"  # STANDARD_PASTE, PHASE_CHANGE_PAD, LIQUID_METAL
    exhaust_vents_count: int = 4
    vrm_actively_cooled: AuditField[bool] = field(default_factory=AuditField.unknown)
    vram_actively_cooled: AuditField[bool] = field(default_factory=AuditField.unknown)
    rated_thermal_dissipation_watts: AuditField[float] = field(default_factory=AuditField.unknown)
    measured_noise_dba_max_load: AuditField[float] = field(default_factory=AuditField.unknown)


@dataclass
class PowerSpec:
    battery_capacity_wh: float = 60.0
    adapter_rating_w: float = 180.0
    adapter_form_factor: str = "STANDARD_BARREL"
    usb_c_pd_charging_supported: bool = True
    usb_c_pd_max_input_w: Optional[float] = 100.0
    battery_discharge_under_ac_crossload: AuditField[bool] = field(default_factory=AuditField.unknown)


@dataclass
class ConnectivitySpec:
    thunderbolt_ports: int = 0
    usb4_ports: int = 0
    usb_c_total: int = 2
    usb_a_total: int = 2
    hdmi_version: str = "2.1"
    ethernet_rj45_speed_mbps: int = 1000
    sd_card_slot: str = "NONE"
    wifi_standard: str = "Wi-Fi 6"
    wifi_module_socketed: AuditField[bool] = field(default_factory=AuditField.unknown)


@dataclass
class BenchmarkSpec:
    test_ambient_temp_c: Optional[float] = None
    cinebench_r23_single: Optional[float] = None
    cinebench_r23_multi_initial: Optional[float] = None
    cinebench_r23_multi_sustained_10min: Optional[float] = None
    timespy_graphics_score: Optional[float] = None
    timespy_cpu_score: Optional[float] = None
    geekbench6_single: Optional[float] = None
    geekbench6_multi: Optional[float] = None
    blender_classroom_sec: Optional[float] = None
    cpu_peak_temp_c: Optional[float] = None
    cpu_sustained_temp_c: Optional[float] = None
    gpu_peak_temp_c: Optional[float] = None
    gpu_sustained_temp_c: Optional[float] = None
    sustained_performance_loss_percent: Optional[float] = None


@dataclass
class MetadataSpec:
    brand: str
    series: str
    model_name: str
    exact_sku: str
    release_year: int
    msrp_inr: float
    street_price_inr: float
    msrp_usd: float
    target_audience: str = "General"
    marketing_headline: str = ""


@dataclass
class LaptopSpecification:
    """
    Master Laptop Specification Data Structure.
    Contains complete subsystem specifications, provenance tracking,
    and automatic confidence calculations.
    """
    metadata: MetadataSpec
    chassis: ChassisSpec
    cpu: CPUSpec
    gpu: GPUSpec
    memory: MemorySpec
    storage: StorageSubsystemSpec
    display: DisplaySpec
    cooling: CoolingSpec
    power: PowerSpec
    connectivity: ConnectivitySpec = field(default_factory=ConnectivitySpec)
    benchmarks: Optional[BenchmarkSpec] = None

    def calculate_audit_confidence(self) -> Dict[str, Any]:
        """
        Calculates confidence scores per subsystem and overall.
        Identifies every single unknown parameter without guessing.
        """
        subsystem_fields: Dict[str, List[AuditField]] = {
            "CPU": [
                self.cpu.oem_pl1_w,
                self.cpu.oem_pl2_w,
                self.cpu.oem_tau_seconds,
                self.cpu.all_core_boost_ghz,
                self.cpu.undervolting_supported
            ],
            "GPU": [
                self.gpu.oem_base_tgp_w,
                self.gpu.oem_dynamic_boost_w,
                self.gpu.has_mux_switch,
                self.gpu.advanced_optimus,
                self.gpu.memory_bandwidth_gbps
            ],
            "Memory": [
                self.memory.bus_width_bits,
                self.memory.cas_latency,
                self.memory.measured_bandwidth_gbps
            ],
            "Storage": [
                self.storage.drives[0].has_dram_cache if self.storage.drives else AuditField.unknown(),
                self.storage.drives[0].sequential_read_mbps if self.storage.drives else AuditField.unknown(),
                self.storage.drives[0].sustained_write_throttle_observed if self.storage.drives else AuditField.unknown()
            ],
            "Display": [
                self.display.measured_brightness_nits,
                self.display.response_time_gtg_ms,
                self.display.color_gamut_srgb_pct,
                self.display.color_gamut_dci_p3_pct,
                self.display.pwm_flicker_free
            ],
            "Cooling": [
                self.cooling.heatpipe_count,
                self.cooling.vrm_actively_cooled,
                self.cooling.vram_actively_cooled,
                self.cooling.rated_thermal_dissipation_watts,
                self.cooling.measured_noise_dba_max_load
            ],
            "Power": [
                self.power.battery_discharge_under_ac_crossload
            ]
        }

        subsystem_confidence: Dict[str, float] = {}
        unknown_fields_by_subsystem: Dict[str, List[str]] = {}
        total_confidence_sum = 0.0
        total_subsystems = len(subsystem_fields)

        for sub_name, fields_list in subsystem_fields.items():
            if not fields_list:
                subsystem_confidence[sub_name] = 1.0
                continue
            conf_sum = sum(f.confidence for f in fields_list)
            avg_conf = conf_sum / len(fields_list)
            subsystem_confidence[sub_name] = round(avg_conf, 2)
            total_confidence_sum += avg_conf

            unknowns = [f"field_{i}" for i, f in enumerate(fields_list) if not f.is_known]
            if unknowns:
                unknown_fields_by_subsystem[sub_name] = unknowns

        overall_conf = round(total_confidence_sum / total_subsystems, 2)
        confidence_grade = "HIGH" if overall_conf >= 0.85 else ("MEDIUM" if overall_conf >= 0.65 else "LOW")

        return {
            "overall_confidence": overall_conf,
            "confidence_grade": confidence_grade,
            "subsystem_confidence": subsystem_confidence,
            "has_unknowns": bool(unknown_fields_by_subsystem)
        }
