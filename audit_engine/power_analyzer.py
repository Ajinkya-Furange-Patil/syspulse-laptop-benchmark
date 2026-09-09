"""
SysPulse Laptop Buyer Audit Engine - Dedicated Power Analysis Engine
Audits CPU power limits (PL1/PL2/Tau), GPU TGP (Base/Dynamic Boost),
System Auxiliary overhead, power adapter adequacy, battery charge headroom,
and cross-load power contention.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from audit_engine.models import LaptopSpecification, FieldStatus


@dataclass
class PowerAuditFinding:
    severity: str  # FATAL, WARNING, ADVISORY, OPTIMAL
    code: str
    title: str
    message: str
    remediation: str


@dataclass
class PowerAnalysisResult:
    # Demand metrics in Watts
    system_auxiliary_power_w: float
    cpu_sustained_power_w: float
    cpu_peak_power_w: float
    gpu_sustained_power_w: float
    gpu_peak_power_w: float
    total_sustained_demand_w: float
    total_peak_demand_w: float

    # Supply metrics in Watts
    adapter_rating_w: float
    sustained_headroom_w: float
    peak_headroom_w: float

    # Headroom Ratios
    sustained_headroom_ratio: float
    peak_headroom_ratio: float

    # Battery Drainage Metrics
    battery_drain_on_ac_expected: bool
    estimated_battery_drain_rate_w: float
    charging_speed_under_load: str  # FAST, SLOW, TRICKLE, DRAINING_WHILE_PLUGGED_IN

    # Power Delivery Audit Score (0 - 100)
    power_score: float
    score_breakdown: List[Dict[str, Any]]

    # Diagnostic Findings
    findings: List[PowerAuditFinding]


class PowerAnalysisEngine:
    """
    Evaluates system electrical balance, adapter adequacy,
    and power starvation bottlenecks under sustained cross-load.
    """

    @classmethod
    def estimate_auxiliary_power(cls, laptop: LaptopSpecification) -> float:
        """
        Estimates motherboard, display, fan, NVMe, Wi-Fi, and RAM auxiliary power draw.
        """
        # Baseline motherboard, chipset, and memory controller
        aux = 10.0

        # Display power based on diagonal, resolution, and brightness
        diag = laptop.display.diagonal_inches
        nits = laptop.display.advertised_brightness_nits
        hz = laptop.display.refresh_rate_hz
        # Larger screens and 500-nit high-refresh panels draw significantly more
        display_pwr = 4.0 + (diag / 15.6) * (nits / 300.0) * (1.0 + (hz - 60) * 0.003)
        aux += display_pwr

        # Storage (active PCIe Gen4/Gen5 NVMe)
        aux += 3.5 * min(laptop.storage.m2_slots_occupied, 2)

        # RAM power (DDR5 active channels)
        aux += 2.5 if laptop.memory.channel_configuration == "DUAL_CHANNEL" else 1.5

        # Fans active at 100% duty cycle
        aux += 2.0 * max(laptop.cooling.fan_count, 1)

        return round(aux, 1)

    @classmethod
    def analyze(cls, laptop: LaptopSpecification) -> PowerAnalysisResult:
        findings: List[PowerAuditFinding] = []
        score_breakdown: List[Dict[str, Any]] = []

        # 1. Determine CPU Power Envelopes
        cpu = laptop.cpu
        if cpu.oem_pl1_w.is_known and cpu.oem_pl1_w.value is not None:
            cpu_pl1 = cpu.oem_pl1_w.value
        else:
            cpu_pl1 = cpu.intel_amd_rated_base_power_w
            findings.append(PowerAuditFinding(
                severity="ADVISORY",
                code="CPU_PL1_UNSTATED",
                title="CPU Sustained Power (PL1) Unstated by OEM",
                message=f"OEM did not state PL1; estimated using Intel/AMD base TDP of {cpu_pl1}W.",
                remediation="Benchmark with SysPulse or Cinebench R23 sustained loop to measure true PL1."
            ))

        if cpu.oem_pl2_w.is_known and cpu.oem_pl2_w.value is not None:
            cpu_pl2 = cpu.oem_pl2_w.value
        else:
            cpu_pl2 = cpu.intel_amd_rated_max_turbo_w

        # 2. Determine GPU Power Envelopes
        gpu = laptop.gpu
        if gpu.is_discrete:
            if gpu.oem_base_tgp_w.is_known and gpu.oem_base_tgp_w.value is not None:
                gpu_base_tgp = gpu.oem_base_tgp_w.value
            else:
                # Conservative Floor Assumption: lowest bin
                gpu_base_tgp = 45.0 if "4060" in gpu.exact_model else 35.0
                findings.append(PowerAuditFinding(
                    severity="WARNING",
                    code="GPU_TGP_UNSTATED",
                    title="GPU TGP Unstated by OEM (Conservative Floor Applied)",
                    message=f"Manufacturer omitted exact TGP. Evaluated at worst-case {gpu_base_tgp}W floor.",
                    remediation="Verify actual TGP via NVIDIA Control Panel or SysPulse Telemetry."
                ))

            dyn_boost = gpu.oem_dynamic_boost_w.value if (gpu.oem_dynamic_boost_w.is_known and gpu.oem_dynamic_boost_w.value is not None) else 15.0
            gpu_peak_tgp = gpu_base_tgp + dyn_boost
        else:
            gpu_base_tgp = 0.0
            gpu_peak_tgp = 0.0

        # 3. Calculate System Auxiliary Power
        aux_w = cls.estimate_auxiliary_power(laptop)

        # 4. Cross-Load Demands
        # Under simultaneous full CPU+GPU load (e.g. gaming with ray-tracing, CUDA + OpenMP compilation, or simulation)
        sustained_demand = round(cpu_pl1 + gpu_base_tgp + aux_w, 1)
        peak_demand = round(cpu_pl2 + gpu_peak_tgp + aux_w, 1)

        adapter_w = laptop.power.adapter_rating_w
        sustained_headroom = round(adapter_w - sustained_demand, 1)
        peak_headroom = round(adapter_w - peak_demand, 1)

        sustained_ratio = round(adapter_w / sustained_demand, 2) if sustained_demand > 0 else 2.0
        peak_ratio = round(adapter_w / peak_demand, 2) if peak_demand > 0 else 2.0

        # 5. Deficit & Battery Drainage Diagnosis
        battery_drain = False
        drain_rate = 0.0
        charging_speed = "FAST"

        if sustained_headroom < 0:
            battery_drain = True
            drain_rate = abs(sustained_headroom)
            charging_speed = "DRAINING_WHILE_PLUGGED_IN"
            findings.append(PowerAuditFinding(
                severity="FATAL",
                code="AC_BATTERY_DRAIN_CROSSLOAD",
                title="Critical Power Adapter Deficit (Battery Discharge on AC)",
                message=(
                    f"Power adapter is {adapter_w}W, but sustained system crossload requires {sustained_demand}W. "
                    f"The laptop suffers a {drain_rate}W deficit and WILL discharge its battery while gaming or "
                    "rendering on AC power, leading to battery wear, micro-stutters, and thermal degradation."
                ),
                remediation="Avoid purchasing this SKU unless an upgraded OEM adapter (>="
                            f"{int(sustained_demand + 30)}W) is bundled or supported."
            ))
        elif sustained_headroom < 15.0:
            charging_speed = "TRICKLE"
            findings.append(PowerAuditFinding(
                severity="WARNING",
                code="MARGINAL_POWER_HEADROOM",
                title="Marginal Power Adapter Headroom",
                message=(
                    f"Power adapter provides only {sustained_headroom}W surplus above sustained load. "
                    "Battery charging while gaming or compiling will be extremely slow (trickle charge)."
                ),
                remediation="Ensure laptop is charged before starting heavy multi-hour rendering jobs."
            ))
        elif sustained_headroom < 35.0:
            charging_speed = "SLOW"
        else:
            charging_speed = "FAST"

        # Check Peak Surge Deficit
        if peak_headroom < -20.0 and not battery_drain:
            findings.append(PowerAuditFinding(
                severity="WARNING",
                code="TURBO_SURGE_DEFICIT",
                title="Peak Turbo Power Deficit (Aggressive PL2 Throttling Expected)",
                message=(
                    f"Peak combined boost demand ({peak_demand}W) exceeds adapter rating ({adapter_w}W) by {abs(peak_headroom)}W. "
                    "The system firmware will prematurely throttle CPU PL2 boost clocks or restrict GPU Dynamic Boost."
                ),
                remediation="Expect short burst performance to degrade rapidly to PL1 baseline."
            ))

        # Check GPU TGP Castration Ratio
        if gpu.is_discrete:
            tgp_ratio = gpu_base_tgp / gpu.silicon_max_possible_tgp_w
            if tgp_ratio < 0.55:
                findings.append(PowerAuditFinding(
                    severity="FATAL",
                    code="GPU_TGP_SEVERELY_CASTRATED",
                    title="GPU TGP Severely Castrated (<55% Silicon Envelope)",
                    message=(
                        f"{gpu.exact_model} is tuned to {gpu_base_tgp}W, which is only {tgp_ratio*100:.0f}% of its "
                        f"{gpu.silicon_max_possible_tgp_w}W silicon potential. Real-world gaming/AI performance is severely crippled."
                    ),
                    remediation="Look for alternative SKUs offering at least 80% of silicon max TGP."
                ))
            elif tgp_ratio >= 0.85:
                findings.append(PowerAuditFinding(
                    severity="OPTIMAL",
                    code="GPU_TGP_MAX_P_VERIFIED",
                    title="Full-Wattage Max-P GPU Configuration Verified",
                    message=(
                        f"{gpu.exact_model} is configured at {gpu_base_tgp}W ({tgp_ratio*100:.0f}% of silicon max). "
                        "Delivers maximum potential framerates and compute throughput for this GPU class."
                    ),
                    remediation="Optimal silicon power implementation."
                ))

        # Check USB-C PD Sink Limitation
        if laptop.power.usb_c_pd_charging_supported:
            pd_max = laptop.power.usb_c_pd_max_input_w or 100.0
            if pd_max < sustained_demand:
                findings.append(PowerAuditFinding(
                    severity="ADVISORY",
                    code="TYPE_C_PD_PERFORMANCE_DERATING",
                    title="Type-C Charging Performance Derating",
                    message=(
                        f"Laptop supports USB-C charging up to {pd_max}W, but maximum sustained demand is {sustained_demand}W. "
                        "When running on a Type-C travel charger, GPU or CPU power will automatically be throttled."
                    ),
                    remediation="Use OEM high-wattage barrel/GaN charger for full-power gaming and heavy compilation."
                ))

        # 6. Calculate Transparent Power Delivery Score (0 - 100)
        # Factor A: Sustained Power Margin (40 pts)
        if sustained_headroom_ratio := sustained_ratio:
            if sustained_headroom_ratio >= 1.25:
                score_a = 40.0
                reason_a = "Generous sustained adapter headroom (>=25% surplus for fast charging under full load)."
            elif sustained_headroom_ratio >= 1.05:
                score_a = 28.0 + (sustained_headroom_ratio - 1.05) / 0.20 * 12.0
                reason_a = f"Adequate sustained headroom ({sustained_headroom_ratio:.2f}x adapter margin)."
            elif sustained_headroom_ratio >= 1.0:
                score_a = 15.0
                reason_a = "Extremely narrow power margin (<=5% surplus; slow charging under load)."
            else:
                score_a = 0.0
                reason_a = f"POWER DEFICIT: Sustained demand exceeds adapter by {abs(sustained_headroom)}W (Battery drains on AC)."
        score_breakdown.append({
            "component": "Sustained Adapter Balance",
            "weight": 40,
            "awarded": round(score_a, 1),
            "reason": reason_a
        })

        # Factor B: Peak Burst Stability (20 pts)
        if peak_ratio >= 1.10:
            score_b = 20.0
            reason_b = "Adapter fully accommodates combined CPU PL2 turbo + GPU Dynamic Boost."
        elif peak_ratio >= 0.90:
            score_b = 12.0 + (peak_ratio - 0.90) / 0.20 * 8.0
            reason_b = "Slight peak power deficit; temporary battery assist or dynamic power-limit throttling expected."
        else:
            score_b = 4.0
            reason_b = f"Severe peak power deficit ({peak_ratio:.2f}x). Heavy thermal/power throttling on burst loads."
        score_breakdown.append({
            "component": "Peak Turbo Stability",
            "weight": 20,
            "awarded": round(score_b, 1),
            "reason": reason_b
        })

        # Factor C: GPU TGP Optimization (25 pts)
        if gpu.is_discrete:
            tgp_pct = gpu_base_tgp / gpu.silicon_max_possible_tgp_w
            score_c = round(min(25.0, max(0.0, (tgp_pct - 0.35) / 0.65 * 25.0)), 1)
            reason_c = f"GPU allocated {gpu_base_tgp}W ({tgp_pct*100:.0f}% of silicon max {gpu.silicon_max_possible_tgp_w}W)."
        else:
            score_c = 25.0
            reason_c = "Integrated graphics; no discrete TGP allocation required."
        score_breakdown.append({
            "component": "GPU TGP Allocation",
            "weight": 25,
            "awarded": score_c,
            "reason": reason_c
        })

        # Factor D: Power Portability & USB-PD Flexibility (15 pts)
        score_d = 0.0
        reasons_d = []
        if laptop.power.usb_c_pd_charging_supported:
            score_d += 8.0
            reasons_d.append("Supports USB-C PD travel charging (+8 pts)")
        if laptop.power.adapter_form_factor == "SLIM_GAN":
            score_d += 4.0
            reasons_d.append("Compact GaN power supply (+4 pts)")
        if laptop.power.battery_capacity_wh >= 75.0:
            score_d += 3.0
            reasons_d.append("High-capacity battery (>=75Wh, +3 pts)")
        elif laptop.power.battery_capacity_wh >= 55.0:
            score_d += 1.5
            reasons_d.append("Standard battery capacity (+1.5 pts)")
        reason_d = "; ".join(reasons_d) if reasons_d else "Standard barrel adapter; no USB-PD support."
        score_breakdown.append({
            "component": "Power Portability & USB-PD",
            "weight": 15,
            "awarded": round(score_d, 1),
            "reason": reason_d
        })

        total_score = round(score_a + score_b + score_c + score_d, 1)

        return PowerAnalysisResult(
            system_auxiliary_power_w=aux_w,
            cpu_sustained_power_w=cpu_pl1,
            cpu_peak_power_w=cpu_pl2,
            gpu_sustained_power_w=gpu_base_tgp,
            gpu_peak_power_w=gpu_peak_tgp,
            total_sustained_demand_w=sustained_demand,
            total_peak_demand_w=peak_demand,
            adapter_rating_w=adapter_w,
            sustained_headroom_w=sustained_headroom,
            peak_headroom_w=peak_headroom,
            sustained_headroom_ratio=sustained_ratio,
            peak_headroom_ratio=peak_ratio,
            battery_drain_on_ac_expected=battery_drain,
            estimated_battery_drain_rate_w=drain_rate,
            charging_speed_under_load=charging_speed,
            power_score=total_score,
            score_breakdown=score_breakdown,
            findings=findings
        )
