"""
SysPulse Laptop Buyer Audit Engine - Phase 8: Value Analysis Engine
Calculates true hardware ROI (Performance/₹, VRAM/₹, RAM/₹, CPU/₹, GPU/₹).
Rejects superficial pricing; distinguishes honest engineering from overpriced marketing traps.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from audit_engine.models import LaptopSpecification


@dataclass
class HardwareUnitEconomics:
    currency: str  # "INR" or "USD"
    price: float
    overall_capability_per_10k: float
    cpu_performance_per_10k: float
    gpu_tflops_per_10k: float
    vram_gb_per_10k: float
    ram_gb_per_10k: float
    storage_gb_per_10k: float


@dataclass
class ValueAuditResult:
    unit_economics: HardwareUnitEconomics
    market_tier: str  # ENTRY_BUDGET (<60K), VALUE_MIDRANGE (60K-100K), UPPER_PERFORMANCE (100K-150K), FLAGSHIP_WORKSTATION (>150K)
    value_rating: str # EXCELLENT_VALUE, GOOD_VALUE, FAIR_VALUE, OVERPRICED, OVERPRICED_MARKETING_TRAP
    value_score_100: float
    value_justification: str
    price_to_capability_index: float
    competing_market_context: str
    breakdown: List[Dict[str, Any]]


class ValueAnalysisEngine:
    """
    Rigorously audits price-to-performance economics with zero marketing bias.
    """

    @classmethod
    def evaluate(
        cls,
        laptop: LaptopSpecification,
        overall_score: float,
        cpu_multi_index: float,
        gpu_fp32_tflops: float
    ) -> ValueAuditResult:
        price_inr = laptop.metadata.street_price_inr or laptop.metadata.msrp_inr or 80000.0
        price_usd = laptop.metadata.msrp_usd or (price_inr / 83.0)

        # Baseline units per 10,000 INR
        price_units_10k = max(1.0, price_inr / 10000.0)

        cap_per_10k = round(overall_score / price_units_10k, 2)
        cpu_per_10k = round(cpu_multi_index / price_units_10k, 2)
        gpu_per_10k = round(gpu_fp32_tflops / price_units_10k, 2)
        vram_per_10k = round(laptop.gpu.vram_gb / price_units_10k, 2)
        ram_per_10k = round(laptop.memory.total_capacity_gb / price_units_10k, 2)
        storage_per_10k = round(laptop.storage.total_capacity_gb / price_units_10k, 1)

        econ = HardwareUnitEconomics(
            currency="INR",
            price=price_inr,
            overall_capability_per_10k=cap_per_10k,
            cpu_performance_per_10k=cpu_per_10k,
            gpu_tflops_per_10k=gpu_per_10k,
            vram_gb_per_10k=vram_per_10k,
            ram_gb_per_10k=ram_per_10k,
            storage_gb_per_10k=storage_per_10k
        )

        # Market Segment Classification
        if price_inr < 60000:
            tier = "ENTRY_BUDGET (< 60,000 INR)"
            baseline_cap = 6.5
        elif price_inr <= 100000:
            tier = "VALUE_MIDRANGE (60,000 - 100,000 INR)"
            baseline_cap = 7.5
        elif price_inr <= 150000:
            tier = "UPPER_PERFORMANCE (100,000 - 150,000 INR)"
            baseline_cap = 6.0
        else:
            tier = "FLAGSHIP_WORKSTATION (> 150,000 INR)"
            baseline_cap = 4.8

        # Value Index relative to price class expectations
        value_ratio = cap_per_10k / baseline_cap
        val_score = round(min(100.0, max(10.0, value_ratio * 75.0)), 1)

        # Check for specific price-to-feature traps
        breakdown = []
        is_castrated_gpu = laptop.gpu.is_discrete and (laptop.gpu.oem_base_tgp_w.value or 45.0) < (laptop.gpu.silicon_max_possible_tgp_w * 0.60)
        is_soldered_single_channel = laptop.memory.channel_configuration == "SINGLE_CHANNEL" and laptop.memory.sodimm_slots_total == 0

        if price_inr >= 95000 and (is_castrated_gpu or is_soldered_single_channel):
            rating = "OVERPRICED_MARKETING_TRAP"
            val_score = min(val_score, 38.0)
            justification = (
                f"Sellers are demanding premium pricing (Rs {price_inr:,.0f}) for cost-cut components: "
                f"{'Castrated ' + str(laptop.gpu.oem_base_tgp_w.value) + 'W GPU TGP; ' if is_castrated_gpu else ''}"
                f"{'Soldered single-channel RAM; ' if is_soldered_single_channel else ''}"
                "Competing laptops in this price bracket offer full-power Max-P GPUs and dual upgradeable SODIMM slots."
            )
        elif val_score >= 85.0:
            rating = "EXCELLENT_VALUE"
            justification = f"Exceptional capability-per-rupee ({cap_per_10k} pts / 10k INR). Outperforms market segment baseline by {((value_ratio-1)*100):.0f}%."
        elif val_score >= 70.0:
            rating = "GOOD_VALUE"
            justification = f"Strong price-to-performance ratio ({cap_per_10k} pts / 10k INR). Solid hardware allocation for the asking price."
        elif val_score >= 50.0:
            rating = "FAIR_VALUE"
            justification = f"Average market value ({cap_per_10k} pts / 10k INR). Hardware capabilities align standardly with segment pricing."
        else:
            rating = "OVERPRICED"
            justification = f"Poor return on investment ({cap_per_10k} pts / 10k INR). Hardware configuration falls below expectations for Rs {price_inr:,.0f}."

        breakdown.append({"metric": "Hardware Capability / 10k INR", "value": f"{cap_per_10k} pts", "status": "OPTIMAL" if cap_per_10k >= 7.0 else "SUBPAR"})
        breakdown.append({"metric": "GPU Compute / 10k INR", "value": f"{gpu_per_10k} TFLOPs", "status": "PASS" if gpu_per_10k >= 0.5 else "LOW"})
        breakdown.append({"metric": "VRAM Allocation / 10k INR", "value": f"{vram_per_10k} GB", "status": "PASS" if vram_per_10k >= 0.7 else "LOW"})
        breakdown.append({"metric": "RAM Allocation / 10k INR", "value": f"{ram_per_10k} GB", "status": "PASS" if ram_per_10k >= 1.5 else "LOW"})
        breakdown.append({"metric": "Storage Allocation / 10k INR", "value": f"{storage_per_10k} GB", "status": "PASS"})

        context = f"In the {tier} segment, expected hardware baseline is {baseline_cap} capability points per 10,000 INR."

        return ValueAuditResult(
            unit_economics=econ,
            market_tier=tier,
            value_rating=rating,
            value_score_100=val_score,
            value_justification=justification,
            price_to_capability_index=cap_per_10k,
            competing_market_context=context,
            breakdown=breakdown
        )
