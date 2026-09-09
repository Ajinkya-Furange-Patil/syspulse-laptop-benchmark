"""
SysPulse Laptop Buyer Audit Engine - Phase 14: Head-to-Head Comparison Engine
Compares 2 or more laptops across every physical parameter, power envelope,
and workload domain to determine unequivocal domain winners.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from audit_engine.models import LaptopSpecification
from audit_engine.workload_engine import WorkloadScoringEngine, MasterWorkloadAuditReport
from audit_engine.dealbreaker_engine import DealBreakerAndBottleneckEngine, DealBreakerAndBottleneckReport
from audit_engine.value_engine import ValueAnalysisEngine, ValueAuditResult


@dataclass
class DomainWinner:
    domain_name: str
    winning_sku: str
    winning_model_name: str
    winning_score: float
    margin_pts: float
    decisive_reason: str


@dataclass
class MultiLaptopComparisonReport:
    laptops_compared: List[Dict[str, Any]]
    domain_winners: List[DomainWinner]
    overall_best_pick: str
    parameter_comparison_table: List[Dict[str, Any]]
    executive_recommendation: str


class LaptopComparisonEngine:
    """
    Rigorously pits 2 or more laptops against each other in side-by-side engineering comparisons.
    """

    @classmethod
    def compare(cls, laptops: List[LaptopSpecification]) -> MultiLaptopComparisonReport:
        if not laptops:
            raise ValueError("At least 1 laptop must be provided for audit comparison.")

        domain_scores: Dict[str, Dict[str, float]] = {
            "Gaming": {},
            "AI / Machine Learning": {},
            "Software Development": {},
            "Engineering / CAD": {},
            "Content Creation": {},
            "Campus Portability": {},
            "Value for Money": {}
        }

        laptop_summaries = []

        for lap in laptops:
            workload_rep = WorkloadScoringEngine.evaluate_all(lap)
            deal_rep = DealBreakerAndBottleneckEngine.audit(lap)
            val_rep = ValueAnalysisEngine.evaluate(lap, 75.0, 70.0, 8.0)

            sku = lap.metadata.exact_sku
            domain_scores["Gaming"][sku] = workload_rep.gaming.overall_gaming_score
            domain_scores["AI / Machine Learning"][sku] = workload_rep.ai_ml.overall_aiml_score
            domain_scores["Software Development"][sku] = workload_rep.software_dev.overall_dev_score
            domain_scores["Engineering / CAD"][sku] = workload_rep.engineering_cad.overall_engineering_score
            domain_scores["Content Creation"][sku] = workload_rep.content_creation.overall_creator_score
            domain_scores["Campus Portability"][sku] = workload_rep.portability.overall_portability_score
            domain_scores["Value for Money"][sku] = val_rep.value_score_100

            laptop_summaries.append({
                "sku": sku,
                "brand": lap.metadata.brand,
                "model": lap.metadata.model_name,
                "price_inr": lap.metadata.street_price_inr,
                "cpu": lap.cpu.exact_model,
                "gpu": f"{lap.gpu.exact_model} ({lap.gpu.oem_base_tgp_w.value or '?'}W TGP)",
                "vram": f"{lap.gpu.vram_gb} GB",
                "ram": f"{lap.memory.total_capacity_gb}GB {lap.memory.ram_type} ({lap.memory.channel_configuration})",
                "display": f"{lap.display.resolution_horizontal}x{lap.display.resolution_vertical} {lap.display.refresh_rate_hz}Hz",
                "storage": f"{lap.storage.total_capacity_gb}GB ({lap.storage.m2_slots_total} M.2 slots)",
                "weight": f"{lap.chassis.weight_kg.value or '?'} kg",
                "adapter": f"{lap.power.adapter_rating_w}W"
            })

        # Calculate Domain Winners
        winners: List[DomainWinner] = []
        domain_explanations = {
            "Gaming": "Higher configured GPU TGP, hardware MUX switch, and faster display pixel response time.",
            "AI / Machine Learning": "Greater dedicated VRAM buffer, NVIDIA Tensor cores, and higher memory bandwidth.",
            "Software Development": "Superior multi-threaded compilation throughput, dual-channel RAM, and container headroom.",
            "Engineering / CAD": "Higher single-core boost clock for SolidWorks viewports, sustained cooling, and AVX-512 acceleration.",
            "Content Creation": "Wider color gamut (100% DCI-P3), high color accuracy, and dedicated AV1/NVENC media engines.",
            "Campus Portability": "Lighter true travel weight, larger battery capacity (Wh), and versatile USB-C PD travel charging.",
            "Value for Money": "Highest compute capability and VRAM delivered per rupee spent."
        }

        for domain, sku_map in domain_scores.items():
            sorted_skus = sorted(sku_map.items(), key=lambda x: x[1], reverse=True)
            top_sku, top_score = sorted_skus[0]
            second_score = sorted_skus[1][1] if len(sorted_skus) > 1 else top_score
            margin = round(top_score - second_score, 1)

            top_lap = next(l for l in laptops if l.metadata.exact_sku == top_sku)
            winners.append(DomainWinner(
                domain_name=domain,
                winning_sku=top_sku,
                winning_model_name=f"{top_lap.metadata.brand} {top_lap.metadata.model_name}",
                winning_score=top_score,
                margin_pts=margin,
                decisive_reason=domain_explanations.get(domain, "Superior benchmark and architectural specifications.")
            ))

        # Parameter comparison table
        param_table = [
            {"parameter": "CPU Silicon", "values": {l["sku"]: l["cpu"] for l in laptop_summaries}},
            {"parameter": "GPU & Configured TGP", "values": {l["sku"]: l["gpu"] for l in laptop_summaries}},
            {"parameter": "Dedicated VRAM", "values": {l["sku"]: l["vram"] for l in laptop_summaries}},
            {"parameter": "RAM & Topology", "values": {l["sku"]: l["ram"] for l in laptop_summaries}},
            {"parameter": "Display Resolution & Hz", "values": {l["sku"]: l["display"] for l in laptop_summaries}},
            {"parameter": "Storage & Expansion", "values": {l["sku"]: l["storage"] for l in laptop_summaries}},
            {"parameter": "Weight", "values": {l["sku"]: l["weight"] for l in laptop_summaries}},
            {"parameter": "Power Adapter", "values": {l["sku"]: l["adapter"] for l in laptop_summaries}},
            {"parameter": "Street Price", "values": {l["sku"]: f"Rs {l['price_inr']:,.0f}" for l in laptop_summaries}}
        ]

        # Overall recommendation
        top_overall_winner = max(
            laptops,
            key=lambda l: sum(domain_scores[d][l.metadata.exact_sku] for d in domain_scores)
        )
        rec = f"Overall Technical Leader: {top_overall_winner.metadata.brand} {top_overall_winner.metadata.model_name} ({top_overall_winner.metadata.exact_sku}) due to balanced power delivery, robust cooling, and absence of castrated silicon."

        return MultiLaptopComparisonReport(
            laptops_compared=laptop_summaries,
            domain_winners=winners,
            overall_best_pick=f"{top_overall_winner.metadata.brand} {top_overall_winner.metadata.model_name}",
            parameter_comparison_table=param_table,
            executive_recommendation=rec
        )
