"""
SysPulse Laptop Buyer Audit Engine - Upgradeability & Long-Term Ownership Module
Evaluates component modularity, repairability, chassis maintenance access,
and 3-to-5 year survival potential.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from audit_engine.models import LaptopSpecification


@dataclass
class UpgradeFinding:
    severity: str  # FATAL, WARNING, ADVISORY, OPTIMAL
    code: str
    title: str
    message: str
    remediation: str


@dataclass
class UpgradeabilityAuditResult:
    # Upgradeability Score / 100
    upgradeability_score: float
    upgradeability_breakdown: List[Dict[str, Any]]

    # Long-Term Ownership Score / 100
    long_term_ownership_score: float
    ownership_breakdown: List[Dict[str, Any]]

    # Key Hardware Modularity States
    ram_modular_state: str  # FULLY_MODULAR_DUAL_SLOT, ASYMMETRIC_MIXED, SOLDERED_ONLY, CAMM2
    storage_expansion_slots_free: int
    wifi_replaceable: bool
    battery_serviceability: str  # SCREWED_ACCESSIBLE, ADHESIVE_PULL_TABS, GLUED_HAZARDOUS
    maintenance_accessibility: str  # EASY_BOTTOM_ACCESS, MODERATE_PRY, INVERTED_MOTHERBOARD

    # Projected Longevity
    projected_functional_lifespan_years: int
    longevity_rating: str  # EXCELLENT (5+ Yrs), GOOD (3-5 Yrs), MEDIOCRE (2-3 Yrs), POOR (<2 Yrs)

    # Diagnostic Findings
    findings: List[UpgradeFinding]


class UpgradeabilityEngine:
    """
    Rigorously audits laptop expandability, socketed vs soldered silicon,
    and long-term mechanical/thermal reliability.
    """

    @classmethod
    def audit(cls, laptop: LaptopSpecification) -> UpgradeabilityAuditResult:
        findings: List[UpgradeFinding] = []
        u_breakdown: List[Dict[str, Any]] = []
        o_breakdown: List[Dict[str, Any]] = []

        # =========================================================================
        # PART 1: UPGRADEABILITY SCORE (0 - 100)
        # =========================================================================

        # 1. RAM Upgradeability (35 Points)
        sodimm_total = laptop.memory.sodimm_slots_total
        soldered_gb = laptop.memory.soldered_capacity_gb
        total_ram = laptop.memory.total_capacity_gb

        if sodimm_total >= 2:
            ram_score = 35.0
            ram_state = "FULLY_MODULAR_DUAL_SLOT"
            ram_reason = f"Dual SODIMM slots available. Fully upgradeable up to {laptop.memory.max_supported_capacity_gb}GB in dual-channel."
        elif sodimm_total == 1 and soldered_gb > 0:
            ram_score = 18.0
            ram_state = "ASYMMETRIC_MIXED"
            ram_reason = f"Mixed RAM: {soldered_gb}GB soldered + 1 SODIMM slot. Upgrades operate in asymmetric Flex mode with potential bandwidth penalty."
            findings.append(UpgradeFinding(
                severity="WARNING",
                code="ASYMMETRIC_RAM_UPGRADE",
                title="Asymmetric Soldered + SODIMM Memory Topology",
                message=f"{soldered_gb}GB is permanently soldered. Adding a larger stick into the single SODIMM slot causes memory beyond {soldered_gb * 2}GB to fall back to single-channel speeds.",
                remediation="Match SODIMM capacity to soldered capacity to preserve symmetric dual-channel operation."
            ))
        elif sodimm_total == 0:
            ram_state = "SOLDERED_ONLY"
            if total_ram >= 32:
                ram_score = 10.0
                ram_reason = f"100% Soldered RAM ({total_ram}GB). High initial capacity cushions obsolescence, but zero expansion is possible."
            elif total_ram == 16:
                ram_score = 4.0
                ram_reason = "100% Soldered RAM (16GB). Zero future expansion. Will hit memory ceiling under future AI, dev, and gaming workloads."
            else:
                ram_score = 0.0
                ram_reason = f"100% Soldered RAM ({total_ram}GB). Severe bottleneck. Instant e-waste when software memory requirements advance."

            findings.append(UpgradeFinding(
                severity="FATAL" if total_ram <= 16 else "WARNING",
                code="ZERO_RAM_UPGRADEABILITY",
                title=f"Zero RAM Expansion (100% Soldered {total_ram}GB)",
                message=(
                    f"All {total_ram}GB of system memory is soldered directly to the motherboard with 0 SODIMM slots. "
                    "If a DRAM BGA chip develops memory bit errors, the entire motherboard must be replaced."
                ),
                remediation="Buy a SKU with at least 1 or 2 SODIMM slots for long-term ownership."
            ))
        else:
            ram_score = 15.0
            ram_state = "SINGLE_SLOT_ONLY"
            ram_reason = "Single SODIMM slot only. Restricted to single-channel memory bandwidth."

        u_breakdown.append({
            "component": "RAM Expandability",
            "weight": 35,
            "awarded": ram_score,
            "reason": ram_reason
        })

        # 2. Storage Expansion (25 Points)
        m2_total = laptop.storage.m2_slots_total
        m2_occupied = laptop.storage.m2_slots_occupied
        free_slots = max(0, m2_total - m2_occupied)

        if m2_total >= 2:
            storage_score = 25.0 if free_slots > 0 else 22.0
            storage_reason = f"Dual M.2 NVMe slots present ({free_slots} free slot available). Secondary SSD can be added without cloning OS drive."
        elif m2_total == 1:
            storage_score = 10.0
            storage_reason = "Single M.2 slot only. Expanding storage requires cloning and replacing the primary boot drive."
            findings.append(UpgradeFinding(
                severity="WARNING",
                code="SINGLE_STORAGE_SLOT",
                title="Single M.2 Storage Slot Constraint",
                message="Laptop only features 1 M.2 slot. You cannot add a second game or data SSD; you must discard/replace the existing drive.",
                remediation="Factor in the cost of an external NVMe enclosure and drive cloning software for future upgrades."
            ))
        else:
            storage_score = 0.0
            storage_reason = "Soldered/eMMC storage. Zero replacement or expansion possible."
            findings.append(UpgradeFinding(
                severity="FATAL",
                code="SOLDERED_STORAGE",
                title="Non-Replaceable Soldered Storage",
                message="Storage is soldered directly onto the PCB. Drive failure renders machine unbootable.",
                remediation="Do not purchase laptops with non-replaceable soldered boot drives."
            ))

        u_breakdown.append({
            "component": "Storage Slots & M.2 Expandability",
            "weight": 25,
            "awarded": storage_score,
            "reason": storage_reason
        })

        # 3. Wi-Fi / Networking Modularity (10 Points)
        wifi_socketed = laptop.connectivity.wifi_module_socketed.value if laptop.connectivity.wifi_module_socketed.is_known else True
        if wifi_socketed:
            wifi_score = 10.0
            wifi_reason = "Modular M.2 2230 Wi-Fi card slot. Can be upgraded to future Wi-Fi 7 / BE200 standards or swapped for Linux compatibility."
        else:
            wifi_score = 0.0
            wifi_reason = "Soldered BGA Wi-Fi module. Cannot be upgraded or replaced if the wireless controller fails."
            findings.append(UpgradeFinding(
                severity="ADVISORY",
                code="SOLDERED_WIFI_MODULE",
                title="Soldered Wi-Fi Controller",
                message="Wi-Fi module is soldered to the motherboard. Cannot upgrade to newer wireless standards in the future.",
                remediation="Use a USB Wi-Fi dongle if the internal card fails."
            ))

        u_breakdown.append({
            "component": "Wireless Module Modularity",
            "weight": 10,
            "awarded": wifi_score,
            "reason": wifi_reason
        })

        # 4. Battery Replaceability (15 Points)
        # Standard screwdrivers vs proprietary glue
        battery_state = "SCREWED_ACCESSIBLE"
        battery_score = 15.0
        battery_reason = "Standard screw-secured battery pack with modular Molex/ribbon connector. Simple 10-minute consumer replacement."

        u_breakdown.append({
            "component": "Battery Replaceability",
            "weight": 15,
            "awarded": battery_score,
            "reason": battery_reason
        })

        # 5. Chassis Maintenance & Cooling Accessibility (15 Points)
        maintenance_state = "EASY_BOTTOM_ACCESS"
        maint_score = 15.0
        maint_reasons = []

        if laptop.chassis.screw_type in ("PENTALOBE", "TORX"):
            maint_score -= 3.0
            maint_reasons.append("Requires specialized Torx/Pentalobe bits (-3 pts)")
        elif laptop.chassis.screw_type == "GLUED":
            maint_score -= 12.0
            maint_reasons.append("Glued chassis seam; thermal pry required (-12 pts)")

        if laptop.chassis.chassis_pry_difficulty in ("DIFFICULT", "HAZARDOUS"):
            maint_score -= 4.0
            maint_reasons.append("Fragile internal plastic clips prone to snapping upon opening (-4 pts)")

        maint_reason_str = "; ".join(maint_reasons) if maint_reasons else "Standard Philips screws with straightforward bottom panel removal."
        u_breakdown.append({
            "component": "Chassis Maintenance & Heatsink Access",
            "weight": 15,
            "awarded": max(0.0, maint_score),
            "reason": maint_reason_str
        })

        total_upgrade_score = round(sum(item["awarded"] for item in u_breakdown), 1)

        # =========================================================================
        # PART 2: LONG-TERM OWNERSHIP SCORE (0 - 100)
        # =========================================================================

        # Factor 1: Modularity & Upgradeability Contribution (30% weight)
        o_modularity = round(total_upgrade_score * 0.30, 1)
        o_breakdown.append({
            "component": "Component Modularity Foundation",
            "weight": 30,
            "awarded": o_modularity,
            "reason": f"Derived from {total_upgrade_score:.1f}/100 hardware upgradeability rating."
        })

        # Factor 2: Thermal & Cooling Robustness (25% weight)
        # Systems with dual fans, vapor chambers, or dedicated pipes resist dust-clogging and maintain thermal transfer
        o_cooling = 0.0
        c_reasons = []
        if laptop.cooling.fan_count >= 2:
            o_cooling += 12.0
            c_reasons.append("Dual-fan airflow prevents localized hot-spot degradation (+12 pts)")
        else:
            o_cooling += 3.0
            c_reasons.append("Single-fan cooling prone to rapid dust-choking under daily loads (+3 pts)")
            findings.append(UpgradeFinding(
                severity="WARNING",
                code="SINGLE_FAN_THERMAL_LONGEVITY",
                title="Single-Fan Thermal Endurance Risk",
                message="Single-fan cooling systems suffer higher dust accumulation and bearing wear, leading to severe thermal throttling after 12–18 months.",
                remediation="Perform compressed-air heatsink cleaning every 6 months."
            ))

        if laptop.cooling.has_vapor_chamber:
            o_cooling += 8.0
            c_reasons.append("Vapor chamber resists hot-spot warping (+8 pts)")
        elif laptop.cooling.heatpipe_topology == "DEDICATED_CPU_AND_GPU":
            o_cooling += 6.0
            c_reasons.append("Dedicated heatpipe loop limits cross-component heat soak (+6 pts)")
        else:
            o_cooling += 2.0
            c_reasons.append("Shared heatpipe topology accelerates thermal paste pump-out (+2 pts)")

        if laptop.cooling.thermal_interface_material == "PHASE_CHANGE_PAD":
            o_cooling += 5.0
            c_reasons.append("Industrial phase-change pad (PTM7950) resists paste pump-out for 5+ years (+5 pts)")
        elif laptop.cooling.thermal_interface_material == "LIQUID_METAL":
            o_cooling += 3.0
            c_reasons.append("Liquid metal provides high conductivity, but requires gasket maintenance (+3 pts)")
        else:
            o_cooling += 3.0
            c_reasons.append("Standard silicone thermal paste typically requires repasting within 2 years (+3 pts)")

        o_breakdown.append({
            "component": "Thermal Degradation Resistance",
            "weight": 25,
            "awarded": round(o_cooling, 1),
            "reason": "; ".join(c_reasons)
        })

        # Factor 3: Power System & Battery Health Preservation (20% weight)
        o_power = 0.0
        p_reasons = []
        # If the battery discharges while plugged into AC, cycle life degrades in 1-2 years
        combined_draw = laptop.cpu.oem_pl1_w.value if laptop.cpu.oem_pl1_w.is_known else 45.0
        combined_draw += laptop.gpu.oem_base_tgp_w.value if laptop.gpu.oem_base_tgp_w.is_known else 0.0
        combined_draw += 25.0
        if laptop.power.adapter_rating_w >= combined_draw:
            o_power += 10.0
            p_reasons.append("Power adapter surplus prevents hybrid-battery discharge cycle wear (+10 pts)")
        else:
            p_reasons.append("AC battery discharge accelerates cell degradation to <2 years (-10 pts)")

        if laptop.power.usb_c_pd_charging_supported:
            o_power += 6.0
            p_reasons.append("Universal USB-PD fallback prevents brick obsolescence if OEM charger fails (+6 pts)")
        else:
            p_reasons.append("Proprietary barrel charger only (+0 pts)")

        if laptop.power.battery_capacity_wh >= 70.0:
            o_power += 4.0
            p_reasons.append("High cell count buffers capacity decay over 500+ cycles (+4 pts)")
        else:
            o_power += 2.0
            p_reasons.append("Small battery capacity will feel severely diminished after 20% health loss (+2 pts)")

        o_breakdown.append({
            "component": "Power System & Cell Longevity",
            "weight": 20,
            "awarded": round(o_power, 1),
            "reason": "; ".join(p_reasons)
        })

        # Factor 4: Chassis Rigidity & Structural Materials (15% weight)
        o_chassis = 0.0
        ch_reasons = []
        mats = laptop.chassis.chassis_materials.lower()
        if "aluminum" in mats or "magnesium" in mats or "metal" in mats:
            o_chassis += 15.0
            ch_reasons.append("Metal alloy chassis protects hinge mounts from brass standoff rupture (+15 pts)")
        elif "plastic" in mats and "lid" in mats:
            o_chassis += 8.0
            ch_reasons.append("Hybrid plastic/aluminum build; hinge stress requires careful opening (+8 pts)")
        else:
            o_chassis += 5.0
            ch_reasons.append("All-plastic chassis vulnerable to screw standoff fatigue over 3+ years (+5 pts)")

        o_breakdown.append({
            "component": "Chassis Rigidity & Hinge Endurance",
            "weight": 15,
            "awarded": round(o_chassis, 1),
            "reason": "; ".join(ch_reasons)
        })

        # Factor 5: Display Panel Longevity & Eye Ergonomics (10% weight)
        o_disp = 0.0
        d_reasons = []
        pwm_flicker = laptop.display.pwm_flicker_free.value if laptop.display.pwm_flicker_free.is_known else True
        if pwm_flicker:
            o_disp += 6.0
            d_reasons.append("Flicker-free DC dimming protects long-term vision health (+6 pts)")
        else:
            d_reasons.append("Low-frequency PWM flicker can cause eye strain during multi-hour coding (+0 pts)")

        if laptop.display.panel_technology == "IPS":
            o_disp += 4.0
            d_reasons.append("IPS panel immune to static UI taskbar burn-in (+4 pts)")
        elif laptop.display.panel_technology in ("OLED", "Mini_LED"):
            o_disp += 3.0
            d_reasons.append("OLED display with high contrast; manage static IDE windows to avoid burn-in (+3 pts)")
        else:
            o_disp += 1.0
            d_reasons.append("TN panel with limited viewing angles (+1 pt)")

        o_breakdown.append({
            "component": "Display Endurance & Eye Ergonomics",
            "weight": 10,
            "awarded": round(o_disp, 1),
            "reason": "; ".join(d_reasons)
        })

        total_ownership_score = round(sum(item["awarded"] for item in o_breakdown), 1)

        # 3. Predict Functional Lifespan
        if total_ownership_score >= 80.0:
            lifespan = 5
            rating = "EXCELLENT (5+ Years)"
        elif total_ownership_score >= 65.0:
            lifespan = 4
            rating = "GOOD (3-5 Years)"
        elif total_ownership_score >= 45.0:
            lifespan = 2
            rating = "MEDIOCRE (2-3 Years)"
        else:
            lifespan = 1
            rating = "POOR (<2 Years Before Bottleneck)"

        return UpgradeabilityAuditResult(
            upgradeability_score=total_upgrade_score,
            upgradeability_breakdown=u_breakdown,
            long_term_ownership_score=total_ownership_score,
            ownership_breakdown=o_breakdown,
            ram_modular_state=ram_state,
            storage_expansion_slots_free=free_slots,
            wifi_replaceable=wifi_socketed,
            battery_serviceability=battery_state,
            maintenance_accessibility=maintenance_state,
            projected_functional_lifespan_years=lifespan,
            longevity_rating=rating,
            findings=findings
        )
