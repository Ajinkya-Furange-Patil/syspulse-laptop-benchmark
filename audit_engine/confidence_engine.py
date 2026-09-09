"""
SysPulse Laptop Buyer Audit Engine - Phase 9 & Phase 15:
Confidence System & Multi-Source Conflict Resolution Engine
Audits input data quality, provenance decay, and resolves conflicting vendor claims.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from audit_engine.models import LaptopSpecification, FieldStatus, DataSource


@dataclass
class SpecificationConflict:
    field_name: str
    subsystem: str
    source_a_name: str
    source_a_value: Any
    source_a_confidence: float
    source_b_name: str
    source_b_value: Any
    source_b_confidence: float
    resolved_value: Any
    resolution_rationale: str


@dataclass
class SystemConfidenceAuditReport:
    overall_confidence: float        # 0.0 - 1.0 (e.g. 0.94 = 94%)
    confidence_tier: str             # HIGH (>=0.85), MEDIUM (0.65-0.84), LOW (<0.65)
    confirmed_parameters_count: int
    estimated_parameters_count: int
    unknown_parameters_count: int
    subsystem_confidence_scores: Dict[str, float]
    unknown_fields_flagged: List[str]
    conflicts_detected: List[SpecificationConflict]
    audit_reliability_verdict: str


class ConfidenceAndConflictEngine:
    """
    Rigorously tracks the provenance of every hardware metric.
    Prevents false certainty when manufacturers omit critical tuning specifications.
    """

    # Hierarchy of Source Authority
    SOURCE_PRIORITY: Dict[DataSource, int] = {
        DataSource.BENCHMARK_MEASURED: 100,  # Physical lab measurement is ground truth
        DataSource.OEM_SPEC: 80,             # Official technical specification document
        DataSource.COMMUNITY_DATABASE: 60,   # Tested by community / teardowns
        DataSource.USER_MANUAL_INPUT: 40,    # Entered manually by user
        DataSource.UNKNOWN: 0
    }

    @classmethod
    def audit_laptop_confidence(cls, laptop: LaptopSpecification) -> SystemConfidenceAuditReport:
        subsystem_map = {
            "CPU Power Envelopes": [
                ("oem_pl1_w", laptop.cpu.oem_pl1_w),
                ("oem_pl2_w", laptop.cpu.oem_pl2_w),
                ("all_core_boost_ghz", laptop.cpu.all_core_boost_ghz),
                ("undervolting_supported", laptop.cpu.undervolting_supported)
            ],
            "GPU Silicon & TGP": [
                ("oem_base_tgp_w", laptop.gpu.oem_base_tgp_w),
                ("oem_dynamic_boost_w", laptop.gpu.oem_dynamic_boost_w),
                ("has_mux_switch", laptop.gpu.has_mux_switch),
                ("memory_bandwidth_gbps", laptop.gpu.memory_bandwidth_gbps)
            ],
            "Memory Subsystem": [
                ("bus_width_bits", laptop.memory.bus_width_bits),
                ("measured_bandwidth_gbps", laptop.memory.measured_bandwidth_gbps)
            ],
            "Storage Architecture": [
                ("has_dram_cache", laptop.storage.drives[0].has_dram_cache if laptop.storage.drives else laptop.cpu.oem_pl1_w),
                ("sequential_read_mbps", laptop.storage.drives[0].sequential_read_mbps if laptop.storage.drives else laptop.cpu.oem_pl1_w)
            ],
            "Display Metrics": [
                ("measured_brightness_nits", laptop.display.measured_brightness_nits),
                ("response_time_gtg_ms", laptop.display.response_time_gtg_ms),
                ("color_gamut_srgb_pct", laptop.display.color_gamut_srgb_pct),
                ("color_gamut_dci_p3_pct", laptop.display.color_gamut_dci_p3_pct)
            ],
            "Cooling & Thermals": [
                ("heatpipe_count", laptop.cooling.heatpipe_count),
                ("rated_thermal_dissipation_watts", laptop.cooling.rated_thermal_dissipation_watts)
            ]
        }

        subsystem_conf = {}
        confirmed_cnt = 0
        estimated_cnt = 0
        unknown_cnt = 0
        unknown_list = []
        total_fields = 0
        conf_sum_total = 0.0

        for sub_name, field_tuples in subsystem_map.items():
            sub_sum = 0.0
            for name, af in field_tuples:
                total_fields += 1
                sub_sum += af.confidence
                conf_sum_total += af.confidence

                if af.status == FieldStatus.CONFIRMED:
                    confirmed_cnt += 1
                elif af.status == FieldStatus.ESTIMATED:
                    estimated_cnt += 1
                else:
                    unknown_cnt += 1
                    unknown_list.append(f"{sub_name}: {name}")

            subsystem_conf[sub_name] = round(sub_sum / len(field_tuples), 2)

        overall_conf = round(conf_sum_total / max(1, total_fields), 2)

        if overall_conf >= 0.85:
            tier = "HIGH"
            verdict = "AUDIT_RELIABLE: High data integrity. Critical OEM limits confirmed."
        elif overall_conf >= 0.65:
            tier = "MEDIUM"
            verdict = "CAVEAT_CONDITIONAL: Several metrics estimated. Moderate confidence."
        else:
            tier = "LOW"
            verdict = "SPECIFICATION_DEFICIT: Key tuning parameters unknown. Audit forced to use conservative floors."

        return SystemConfidenceAuditReport(
            overall_confidence=overall_conf,
            confidence_tier=tier,
            confirmed_parameters_count=confirmed_cnt,
            estimated_parameters_count=estimated_cnt,
            unknown_parameters_count=unknown_cnt,
            subsystem_confidence_scores=subsystem_conf,
            unknown_fields_flagged=unknown_list,
            conflicts_detected=[],
            audit_reliability_verdict=verdict
        )

    @classmethod
    def resolve_spec_conflict(
        cls,
        field_name: str,
        subsystem: str,
        source_a: str, val_a: Any, conf_a: float, type_a: DataSource,
        source_b: str, val_b: Any, conf_b: float, type_b: DataSource
    ) -> SpecificationConflict:
        """
        Transparently resolves conflicts when retailers or spec sheets disagree.
        Example: Retailer listing says "140W RTX 4060", but OEM spec sheet says "45W".
        """
        prio_a = cls.SOURCE_PRIORITY.get(type_a, 50)
        prio_b = cls.SOURCE_PRIORITY.get(type_b, 50)

        if prio_a > prio_b:
            winner_val = val_a
            rationale = f"Selected {source_a} ({val_a}) over {source_b} ({val_b}) because physical measurement / official OEM source has higher authority."
        elif prio_b > prio_a:
            winner_val = val_b
            rationale = f"Selected {source_b} ({val_b}) over {source_a} ({val_a}) because physical measurement / official OEM source has higher authority."
        else:
            # Conservative principle: pick lower value to avoid marketing overestimation
            winner_val = min(val_a, val_b) if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)) else val_a
            rationale = f"Identical authority; applied conservative engineering floor ({winner_val}) to prevent false marketing expectations."

        return SpecificationConflict(
            field_name=field_name,
            subsystem=subsystem,
            source_a_name=source_a,
            source_a_value=val_a,
            source_a_confidence=conf_a,
            source_b_name=source_b,
            source_b_value=val_b,
            source_b_confidence=conf_b,
            resolved_value=winner_val,
            resolution_rationale=rationale
        )
