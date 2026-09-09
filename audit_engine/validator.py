"""
SysPulse Laptop Buyer Audit Engine - Specification Validator & Sanity Auditor
Validates laptop specification sheets against the engineering schema.
Extracts unknown values, enforces field provenance, and performs initial sanity audits.
"""

from typing import Dict, Any, List, Tuple
import json
from audit_engine.models import (
    LaptopSpecification, MetadataSpec, ChassisSpec, CPUSpec, GPUSpec,
    MemorySpec, StorageSubsystemSpec, StorageDriveSpec, DisplaySpec,
    CoolingSpec, PowerSpec, ConnectivitySpec, BenchmarkSpec,
    AuditField, FieldStatus, DataSource
)


class SpecValidationError(Exception):
    pass


def parse_audit_field(data: Any, default_val: Any = None) -> AuditField:
    """
    Parses an audit field from either a raw value or an explicit audit dict.
    Never guesses; sets UNKNOWN if value is null or missing.
    """
    if data is None:
        return AuditField.unknown()
    if isinstance(data, dict) and "status" in data:
        status_str = data.get("status", "UNKNOWN").upper()
        source_str = data.get("source", "UNKNOWN").upper()
        status = FieldStatus(status_str) if status_str in FieldStatus.__members__ else FieldStatus.UNKNOWN
        source = DataSource(source_str) if source_str in DataSource.__members__ else DataSource.UNKNOWN
        val = data.get("value")
        conf = float(data.get("confidence", 1.0 if status == FieldStatus.CONFIRMED else 0.0))
        return AuditField(value=val, status=status, source=source, confidence=conf)
    # If a raw literal is passed, default to CONFIRMED via OEM_SPEC
    return AuditField.confirmed(data, DataSource.OEM_SPEC)


class SpecificationValidator:
    """
    Validates, normalizes, and performs sanity audit on raw laptop JSON inputs.
    """

    @classmethod
    def validate_and_load(cls, raw_dict: Dict[str, Any]) -> Tuple[LaptopSpecification, List[str]]:
        warnings: List[str] = []

        # 1. Validate mandatory blocks
        required_blocks = ["metadata", "chassis", "cpu", "gpu", "memory", "storage", "display", "cooling", "power"]
        for block in required_blocks:
            if block not in raw_dict:
                raise SpecValidationError(f"Missing mandatory specification block: '{block}'")

        # 2. Extract Metadata
        meta_d = raw_dict["metadata"]
        meta = MetadataSpec(
            brand=meta_d.get("brand", "Unknown"),
            series=meta_d.get("series", ""),
            model_name=meta_d.get("model_name", "Unknown"),
            exact_sku=meta_d.get("exact_sku", "SKU-UNKNOWN"),
            release_year=int(meta_d.get("release_year", 2024)),
            msrp_inr=float(meta_d.get("msrp_inr", 0.0)),
            street_price_inr=float(meta_d.get("street_price_inr", meta_d.get("msrp_inr", 0.0))),
            msrp_usd=float(meta_d.get("msrp_usd", 0.0)),
            target_audience=meta_d.get("target_audience", "General"),
            marketing_headline=meta_d.get("marketing_headline", "")
        )

        # 3. Extract Chassis
        chassis_d = raw_dict["chassis"]
        chassis = ChassisSpec(
            weight_kg=parse_audit_field(chassis_d.get("weight_kg")),
            thickness_mm=parse_audit_field(chassis_d.get("dimensions_mm", {}).get("thickness_max")),
            chassis_materials=chassis_d.get("chassis_materials", "Plastic"),
            screw_type=chassis_d.get("service_access", {}).get("screw_type", "PHILIPS"),
            chassis_pry_difficulty=chassis_d.get("service_access", {}).get("chassis_pry_difficulty", "MODERATE"),
            easy_maintenance_hatch=chassis_d.get("service_access", {}).get("easy_access_panel", False)
        )

        # 4. Extract CPU
        cpu_d = raw_dict["cpu"]
        cpu = CPUSpec(
            manufacturer=cpu_d.get("manufacturer", "Unknown"),
            exact_model=cpu_d.get("exact_model", "Unknown"),
            architecture=cpu_d.get("architecture", "Unknown"),
            generation=cpu_d.get("generation", "Unknown"),
            process_node_nm=cpu_d.get("process_node_nm"),
            total_physical_cores=int(cpu_d.get("total_physical_cores", 0)),
            p_cores=int(cpu_d.get("performance_cores", 0)),
            e_cores=int(cpu_d.get("efficiency_cores", 0)),
            total_threads=int(cpu_d.get("total_threads", 0)),
            base_clock_ghz=float(cpu_d.get("base_clock_ghz", 0.0)),
            boost_clock_ghz=float(cpu_d.get("boost_clock_ghz", 0.0)),
            all_core_boost_ghz=parse_audit_field(cpu_d.get("all_core_boost_ghz")),
            l2_cache_mb=cpu_d.get("cache", {}).get("l2_total_mb"),
            l3_cache_mb=cpu_d.get("cache", {}).get("l3_total_mb"),
            intel_amd_rated_base_power_w=float(cpu_d.get("intel_or_amd_spec_base_power_w", 45.0)),
            intel_amd_rated_max_turbo_w=float(cpu_d.get("intel_or_amd_spec_max_turbo_w", 115.0)),
            oem_pl1_w=parse_audit_field(cpu_d.get("oem_pl1_w")),
            oem_pl2_w=parse_audit_field(cpu_d.get("oem_pl2_w")),
            oem_tau_seconds=parse_audit_field(cpu_d.get("oem_tau_seconds")),
            npu_present=bool(cpu_d.get("npu_present", False)),
            npu_tops=parse_audit_field(cpu_d.get("npu_tops")),
            avx2=bool(cpu_d.get("instruction_extensions", {}).get("avx2", True)),
            avx512=bool(cpu_d.get("instruction_extensions", {}).get("avx512", False)),
            igpu_model=cpu_d.get("igpu_model", "Unknown"),
            pcie_gen=int(cpu_d.get("pcie_controller_gen", 4)),
            undervolting_supported=parse_audit_field(cpu_d.get("undervolting_supported"))
        )

        # 5. Extract GPU
        gpu_d = raw_dict["gpu"]
        gpu = GPUSpec(
            is_discrete=bool(gpu_d.get("is_discrete", True)),
            manufacturer=gpu_d.get("manufacturer", "NVIDIA"),
            exact_model=gpu_d.get("exact_model", "Unknown"),
            chip_code=gpu_d.get("chip_code", "Unknown"),
            architecture=gpu_d.get("architecture", "Unknown"),
            cuda_cores_or_shaders=int(gpu_d.get("cuda_cores_or_stream_processors", 0)),
            tensor_cores=int(gpu_d.get("tensor_cores", 0)),
            rt_cores=int(gpu_d.get("rt_cores", 0)),
            vram_gb=float(gpu_d.get("vram_gb", 0.0)),
            vram_type=gpu_d.get("vram_type", "GDDR6"),
            memory_bus_width_bit=parse_audit_field(gpu_d.get("memory_bus_width_bit")),
            memory_bandwidth_gbps=parse_audit_field(gpu_d.get("memory_bandwidth_gbps")),
            silicon_max_possible_tgp_w=float(gpu_d.get("silicon_max_possible_tgp_w", 140.0)),
            oem_base_tgp_w=parse_audit_field(gpu_d.get("oem_base_tgp_w")),
            oem_dynamic_boost_w=parse_audit_field(gpu_d.get("oem_dynamic_boost_w")),
            graphics_clock_base_mhz=parse_audit_field(gpu_d.get("graphics_clock_base_mhz")),
            graphics_clock_boost_mhz=parse_audit_field(gpu_d.get("graphics_clock_boost_mhz")),
            has_mux_switch=parse_audit_field(gpu_d.get("has_mux_switch")),
            advanced_optimus=parse_audit_field(gpu_d.get("advanced_optimus")),
            gsync_support=parse_audit_field(gpu_d.get("gsync_display_support")),
            nvenc_generation=gpu_d.get("video_encoders", {}).get("nvenc_version"),
            av1_encode_hardware=bool(gpu_d.get("video_encoders", {}).get("av1_encode_hardware", False)),
            cuda_compute_capability=gpu_d.get("cuda_compute_capability")
        )

        # 6. Extract Memory
        mem_d = raw_dict["memory"]
        memory = MemorySpec(
            total_capacity_gb=int(mem_d.get("total_capacity_gb", 16)),
            ram_type=mem_d.get("ram_type", "DDR5"),
            speed_mts=int(mem_d.get("speed_mts", 4800)),
            channel_configuration=mem_d.get("channel_configuration", "UNKNOWN"),
            bus_width_bits=parse_audit_field(mem_d.get("bus_width_bits")),
            soldered_capacity_gb=int(mem_d.get("soldered_capacity_gb", 0)),
            sodimm_slots_total=int(mem_d.get("sodimm_slots_total", 2)),
            sodimm_slots_occupied=int(mem_d.get("sodimm_slots_occupied", 2)),
            max_supported_capacity_gb=int(mem_d.get("max_supported_capacity_gb", 64)),
            cas_latency=parse_audit_field(mem_d.get("cas_latency_cl")),
            measured_bandwidth_gbps=parse_audit_field(mem_d.get("measured_read_bandwidth_gbps"))
        )

        # 7. Extract Storage
        stor_d = raw_dict["storage"]
        primary_d = stor_d.get("primary_drive", {})
        primary_drive = StorageDriveSpec(
            slot_number=1,
            exact_ssd_model=parse_audit_field(primary_d.get("exact_ssd_model")),
            capacity_gb=int(primary_d.get("capacity_gb", 512)),
            form_factor=primary_d.get("form_factor", "M.2_2280"),
            interface_type=primary_d.get("interface_type", "NVMe_PCIe"),
            pcie_generation=int(primary_d.get("pcie_generation", 4)),
            pcie_lanes=int(primary_d.get("pcie_lanes", 4)),
            nand_type=primary_d.get("nand_type", "UNKNOWN"),
            has_dram_cache=parse_audit_field(primary_d.get("has_dram_cache")),
            sequential_read_mbps=parse_audit_field(primary_d.get("sequential_read_mbps")),
            sequential_write_mbps=parse_audit_field(primary_d.get("sequential_write_mbps")),
            sustained_write_throttle_observed=parse_audit_field(primary_d.get("sustained_write_throttle_observed"))
        )
        storage = StorageSubsystemSpec(
            total_capacity_gb=int(stor_d.get("total_capacity_gb", 512)),
            m2_slots_total=int(stor_d.get("m2_slots_total", 2)),
            m2_slots_occupied=int(stor_d.get("m2_slots_occupied", 1)),
            drives=[primary_drive]
        )

        # 8. Extract Display
        disp_d = raw_dict["display"]
        display = DisplaySpec(
            diagonal_inches=float(disp_d.get("diagonal_inches", 15.6)),
            aspect_ratio=disp_d.get("aspect_ratio", "16:9"),
            resolution_horizontal=int(disp_d.get("resolution_horizontal", 1920)),
            resolution_vertical=int(disp_d.get("resolution_vertical", 1080)),
            refresh_rate_hz=int(disp_d.get("refresh_rate_hz", 60)),
            panel_technology=disp_d.get("panel_technology", "IPS"),
            advertised_brightness_nits=float(disp_d.get("advertised_brightness_nits", 300.0)),
            measured_brightness_nits=parse_audit_field(disp_d.get("measured_brightness_nits")),
            contrast_ratio=parse_audit_field(disp_d.get("contrast_ratio")),
            response_time_gtg_ms=parse_audit_field(disp_d.get("response_time_gtg_ms")),
            color_gamut_srgb_pct=parse_audit_field(disp_d.get("color_gamut_srgb_pct")),
            color_gamut_dci_p3_pct=parse_audit_field(disp_d.get("color_gamut_dci_p3_pct")),
            delta_e_accuracy=parse_audit_field(disp_d.get("delta_e_accuracy")),
            vrr_technology=disp_d.get("vrr_technology", "None"),
            pwm_flicker_free=parse_audit_field(disp_d.get("pwm_flicker_free")),
            pwm_frequency_hz=parse_audit_field(disp_d.get("pwm_frequency_hz")),
            surface_finish=disp_d.get("surface_finish", "MATTE_ANTI_GLARE")
        )

        # 9. Extract Cooling
        cool_d = raw_dict["cooling"]
        cooling = CoolingSpec(
            fan_count=int(cool_d.get("fan_count", 2)),
            heatpipe_count=parse_audit_field(cool_d.get("heatpipe_count")),
            heatpipe_topology=cool_d.get("heatpipe_topology", "HYBRID"),
            has_vapor_chamber=bool(cool_d.get("has_vapor_chamber", False)),
            thermal_interface_material=cool_d.get("thermal_interface_material", "STANDARD_PASTE"),
            exhaust_vents_count=int(cool_d.get("exhaust_vents_count", 2)),
            vrm_actively_cooled=parse_audit_field(cool_d.get("vrm_actively_cooled")),
            vram_actively_cooled=parse_audit_field(cool_d.get("vram_actively_cooled")),
            rated_thermal_dissipation_watts=parse_audit_field(cool_d.get("rated_thermal_dissipation_watts")),
            measured_noise_dba_max_load=parse_audit_field(cool_d.get("measured_noise_dba_max_load"))
        )

        # 10. Extract Power
        pwr_d = raw_dict["power"]
        power = PowerSpec(
            battery_capacity_wh=float(pwr_d.get("battery_capacity_wh", 60.0)),
            adapter_rating_w=float(pwr_d.get("adapter_rating_w", 180.0)),
            adapter_form_factor=pwr_d.get("adapter_form_factor", "STANDARD_BARREL"),
            usb_c_pd_charging_supported=bool(pwr_d.get("usb_c_pd_charging_supported", False)),
            usb_c_pd_max_input_w=pwr_d.get("usb_c_pd_max_input_w"),
            battery_discharge_under_ac_crossload=parse_audit_field(pwr_d.get("battery_discharge_under_ac_crossload"))
        )

        # 11. Extract Connectivity
        conn_d = raw_dict.get("connectivity_and_ports", {})
        connectivity = ConnectivitySpec(
            thunderbolt_ports=int(conn_d.get("thunderbolt_ports", 0)),
            usb4_ports=int(conn_d.get("usb4_ports", 0)),
            usb_c_total=int(conn_d.get("usb_c_total", 1)),
            usb_a_total=int(conn_d.get("usb_a_total", 2)),
            hdmi_version=conn_d.get("hdmi_version", "2.0"),
            ethernet_rj45_speed_mbps=int(conn_d.get("ethernet_rj45_speed_mbps", 1000)),
            sd_card_slot=conn_d.get("sd_card_slot", "NONE"),
            wifi_standard=conn_d.get("wifi_standard", "Wi-Fi 6"),
            wifi_module_socketed=parse_audit_field(conn_d.get("wifi_module_socketed"))
        )

        laptop = LaptopSpecification(
            metadata=meta,
            chassis=chassis,
            cpu=cpu,
            gpu=gpu,
            memory=memory,
            storage=storage,
            display=display,
            cooling=cooling,
            power=power,
            connectivity=connectivity
        )

        # Perform Pre-Audit Sanity & Anti-Marketing Checks
        cls._run_sanity_checks(laptop, warnings)

        return laptop, warnings

    @classmethod
    def _run_sanity_checks(cls, laptop: LaptopSpecification, warnings: List[str]):
        # 1. Check TGP castration
        if laptop.gpu.is_discrete and laptop.gpu.oem_base_tgp_w.is_known:
            tgp = laptop.gpu.oem_base_tgp_w.value
            max_silicon = laptop.gpu.silicon_max_possible_tgp_w
            if tgp is not None and tgp < (max_silicon * 0.60):
                warnings.append(
                    f"LOW-TGP WARNING: {laptop.gpu.exact_model} configured at {tgp}W base TGP "
                    f"(silicon maximum is {max_silicon}W). Severely lower performance than full-wattage implementations."
                )

        # 2. Check Single-Channel RAM
        if laptop.memory.channel_configuration == "SINGLE_CHANNEL":
            warnings.append(
                f"RAM CHANNEL BOTTLENECK: Single-channel {laptop.memory.ram_type} detected. "
                "Cuts CPU multi-core compilation and 1% low gaming framerates by up to 25-35%."
            )

        # 3. Check Soldered RAM
        if laptop.memory.sodimm_slots_total == 0 and laptop.memory.soldered_capacity_gb > 0:
            warnings.append(
                f"UPGRADEABILITY WARNING: 100% Soldered RAM ({laptop.memory.soldered_capacity_gb}GB). "
                "Zero future expansion possible. Non-repairable if memory fails."
            )

        # 4. Check Display Ghosting / Color Gamut Trap
        srgb_field = laptop.display.color_gamut_srgb_pct
        if srgb_field.is_known and srgb_field.value is not None and srgb_field.value <= 65.0:
            warnings.append(
                f"DISPLAY COLOR TRAP: Low color gamut ({srgb_field.value}% sRGB / 45% NTSC). "
                "Washed-out colors unsuitable for creative work and immersive media."
            )
        if laptop.display.refresh_rate_hz >= 120 and laptop.display.response_time_gtg_ms.is_known:
            resp = laptop.display.response_time_gtg_ms.value
            if resp is not None and resp > 15.0:
                warnings.append(
                    f"DISPLAY GHOSTING TRAP: Advertised {laptop.display.refresh_rate_hz}Hz refresh, but GTG response "
                    f"time is {resp}ms. Severe motion blur and ghosting in fast-paced games."
                )

        # 5. Check Power Adapter Deficit
        pl1 = laptop.cpu.oem_pl1_w.value if laptop.cpu.oem_pl1_w.is_known else laptop.cpu.intel_amd_rated_base_power_w
        tgp = laptop.gpu.oem_base_tgp_w.value if laptop.gpu.oem_base_tgp_w.is_known else 0.0
        combined_load = (pl1 or 0.0) + (tgp or 0.0) + 25.0  # +25W display, motherboard, fan auxiliary
        if laptop.power.adapter_rating_w < combined_load:
            warnings.append(
                f"POWER ADAPTER DEFICIT: Power adapter is {laptop.power.adapter_rating_w}W, but maximum concurrent "
                f"hardware load is ~{combined_load:.0f}W. Battery will discharge even when plugged in under load."
            )
