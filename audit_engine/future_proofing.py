"""
SysPulse Laptop Buyer Audit Engine - Phase 20 & Phase 21:
Future-Proofing Prediction & Priority-Centric Final Verdict Engine
Projects 1-Year, 3-Year, and 5-Year viability, and issues tailored verdicts
based directly on the user's workload priorities. NO UNIVERSAL WINNER.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from audit_engine.models import LaptopSpecification
from audit_engine.workload_engine import MasterWorkloadAuditReport
from audit_engine.dealbreaker_engine import DealBreakerAndBottleneckReport


class VerdictTier:
    EXCELLENT_BUY = "EXCELLENT BUY"
    GOOD_BUY = "GOOD BUY"
    CONDITIONAL_BUY = "CONDITIONAL BUY"
    WAIT_COMPARE = "WAIT / COMPARE"
    NOT_RECOMMENDED = "NOT RECOMMENDED"
    HARD_NO = "HARD NO"


@dataclass
class FutureProofingHorizon:
    horizon_years: int
    viability_rating: str     # HIGH, MEDIUM, LOW
    confidence_level: str     # HIGH, MEDIUM, LOW
    bottleneck_projection: str
    recommended_upgrade_window: str


@dataclass
class FutureProofingReport:
    horizon_1_year: FutureProofingHorizon
    horizon_3_year: FutureProofingHorizon
    horizon_5_year: FutureProofingHorizon
    upgrade_pathway_viable: bool
    summary: str


@dataclass
class FinalTailoredVerdict:
    user_primary_priority: str  # "Gaming", "AI_ML", "Software_Development", "Engineering_CAD", "Content_Creation", "Portability"
    verdict: str                # One of VerdictTier
    priority_score: float       # Score for their selected priority (0 - 100)
    overall_hardware_score: float
    is_dealbreaker_present_for_user: bool
    primary_reason: str
    tailored_buying_advice: str
    alternative_suggestion: str


class FutureProofingAndVerdictEngine:
    """
    Evaluates hardware viability over 1, 3, and 5 years,
    and produces user-priority conditioned buying verdicts.
    """

    @classmethod
    def evaluate_future_proofing(
        cls,
        laptop: LaptopSpecification,
        upgrade_score: float
    ) -> FutureProofingReport:
        vram = laptop.gpu.vram_gb
        ram = laptop.memory.total_capacity_gb
        is_soldered_ram = laptop.memory.sodimm_slots_total == 0
        threads = laptop.cpu.total_threads

        # 1-Year Viability
        # Almost all new machines survive 1 year, unless VRAM < 4GB or RAM < 8GB
        if vram < 4.0 or ram < 8:
            h1 = FutureProofingHorizon(1, "LOW", "HIGH", "Memory ceiling already exceeded by modern OS and software.", "Immediate")
        else:
            h1 = FutureProofingHorizon(1, "HIGH", "HIGH", "Hardware easily handles present generation workloads.", "None required")

        # 3-Year Viability (2026 -> 2029)
        # In 3 years, 16GB will be baseline; 8GB VRAM will be minimum for standard AAA gaming; 8B LLMs will be standard OS assistants
        if ram <= 16 and is_soldered_ram:
            h3 = FutureProofingHorizon(3, "LOW", "HIGH", "16GB soldered memory ceiling prevents adapting to 2029 software memory baselines.", "Motherboard replacement needed")
        elif vram < 6.0:
            h3 = FutureProofingHorizon(3, "LOW", "HIGH", f"{vram}GB VRAM cannot run future game texture packs or OS AI models.", "External eGPU or laptop upgrade")
        elif ram >= 32 and (vram >= 8.0 or not laptop.gpu.is_discrete):
            h3 = FutureProofingHorizon(3, "HIGH", "HIGH", "Strong core and memory headroom will remain fully competitive.", "None required")
        else:
            h3 = FutureProofingHorizon(3, "MEDIUM", "MEDIUM", "Adequate for medium settings, but expect minor graphical/memory trade-offs.", "Populate second SSD slot")

        # 5-Year Viability (2026 -> 2031)
        # 5 years requires modular RAM (32GB+), strong physical cooling, and robust chassis
        if is_soldered_ram or upgrade_score < 60.0 or vram < 8.0:
            h5 = FutureProofingHorizon(5, "LOW", "MEDIUM", "Non-upgradeable components and thermal paste pump-out will render machine slow or obsolete.", "Replace laptop before year 5")
        elif threads >= 16 and ram >= 32 and vram >= 8.0 and upgrade_score >= 85.0:
            h5 = FutureProofingHorizon(5, "HIGH", "MEDIUM", "Workstation-class modularity allows swapping RAM/SSD/Wi-Fi to survive past 2031.", "Repaste heatsink at Year 3")
        else:
            h5 = FutureProofingHorizon(5, "MEDIUM", "LOW", "Usable for general productivity, but unviable for AAA gaming or heavy simulation.", "Upgrade RAM to maximum capacity")

        upgrade_viable = laptop.memory.sodimm_slots_total > 0 or laptop.storage.m2_slots_total > 1
        summary = (
            f"Hardware future-proofing is rated {h3.viability_rating} for a 3-year horizon, "
            f"and {h5.viability_rating} for a 5-year horizon based on component modularity and VRAM capacity."
        )

        return FutureProofingReport(
            horizon_1_year=h1,
            horizon_3_year=h3,
            horizon_5_year=h5,
            upgrade_pathway_viable=upgrade_viable,
            summary=summary
        )

    @classmethod
    def synthesize_verdict(
        cls,
        laptop: LaptopSpecification,
        user_priority: str,
        workload_report: MasterWorkloadAuditReport,
        dealbreaker_report: DealBreakerAndBottleneckReport,
        value_score: float
    ) -> FinalTailoredVerdict:
        """
        Calculates the FINAL BUY / CONDITIONAL BUY / DON'T BUY verdict.
        Prioritizes the USER'S PRIMARY WORKLOAD over generic averages.
        """
        # Map user priority to domain score
        priority_map = {
            "Gaming": (workload_report.gaming.overall_gaming_score, dealbreaker_report.is_fatal_for_gaming),
            "AI_ML": (workload_report.ai_ml.overall_aiml_score, dealbreaker_report.is_fatal_for_ai),
            "Software_Development": (workload_report.software_dev.overall_dev_score, dealbreaker_report.is_fatal_for_dev),
            "Engineering_CAD": (workload_report.engineering_cad.overall_engineering_score, False),
            "Content_Creation": (workload_report.content_creation.overall_creator_score, False),
            "Portability": (workload_report.portability.overall_portability_score, False)
        }

        domain_score, is_fatal = priority_map.get(user_priority, (workload_report.gaming.overall_gaming_score, False))
        overall_avg = round(sum(s for s, _ in priority_map.values()) / len(priority_map), 1)

        # 1. HARD FATAL BLOCKER CHECK
        if is_fatal:
            verdict = VerdictTier.HARD_NO if domain_score < 30 else VerdictTier.NOT_RECOMMENDED
            reason = f"FATAL HARDWARE LIMITATION: A non-negotiable deal-breaker prevents this laptop from executing your {user_priority} workload."
            advice = f"Do NOT buy this machine for {user_priority}. Even with high headline specs, hardware ceilings make it unsuitable."
            alt = "Look for a machine with higher dedicated VRAM, dual-channel RAM, or proper power delivery."

        # 2. SEVERE POWER DEFICIT CHECK
        elif any(d.code == "FATAL_POWER_ADAPTER_DEFICIT" for d in dealbreaker_report.dealbreakers):
            verdict = VerdictTier.NOT_RECOMMENDED
            reason = "POWER DEFICIT: The included power supply cannot sustain concurrent hardware load, draining battery on AC."
            advice = "Only buy if you can negotiate an upgraded, higher-wattage power adapter from the OEM."
            alt = "Check competing SKUs in this price tier with properly sized power supplies."

        # 3. HIGH PERFORMANCE IN TARGET DOMAIN
        elif domain_score >= 85.0 and value_score >= 65.0 and dealbreaker_report.fatal_dealbreakers_count == 0:
            verdict = VerdictTier.EXCELLENT_BUY
            reason = f"EXCEPTIONAL FIT: Scores {domain_score:.1f}/100 for {user_priority} with clean engineering and fair pricing."
            advice = f"Highly recommended. Fully satisfies all hardware requirements for {user_priority} with strong headroom."
            alt = "Proceed to purchase with confidence."

        elif domain_score >= 70.0:
            if dealbreaker_report.critical_warnings_count > 0 or value_score < 50.0:
                verdict = VerdictTier.CONDITIONAL_BUY
                reason = f"SOLID PERFORMANCE WITH CAVEATS: Scores {domain_score:.1f}/100 for {user_priority}, but has minor engineering trade-offs."
                advice = "Suitable if you are aware of the noted bottlenecks and plan minor upgrades (e.g. secondary SSD or RAM module)."
                alt = "Compare pricing against models with zero warnings before committing."
            else:
                verdict = VerdictTier.GOOD_BUY
                reason = f"GOOD FIT: Solid {domain_score:.1f}/100 capability for {user_priority} with dependable execution."
                advice = "Recommended purchase for this workload tier."
                alt = "Good balance of capability and price."

        elif domain_score >= 50.0:
            verdict = VerdictTier.WAIT_COMPARE
            reason = f"MEDIOCRE FIT: Achieves only {domain_score:.1f}/100 for {user_priority}. Hardware will feel constrained under heavy workloads."
            advice = "Wait for seasonal sales or consider saving slightly more for the next hardware tier."
            alt = "Consider previous-generation flagship models on clearance."

        else:
            verdict = VerdictTier.NOT_RECOMMENDED
            reason = f"UNSUITABLE FOR TARGET WORKLOAD: Low capability score ({domain_score:.1f}/100) for {user_priority}."
            advice = f"This laptop is not engineered for {user_priority}. You will quickly encounter frustrating performance bottlenecks."
            alt = "Reallocate budget towards models optimized specifically for your primary workload."

        return FinalTailoredVerdict(
            user_primary_priority=user_priority,
            verdict=verdict,
            priority_score=domain_score,
            overall_hardware_score=overall_avg,
            is_dealbreaker_present_for_user=is_fatal,
            primary_reason=reason,
            tailored_buying_advice=advice,
            alternative_suggestion=alt
        )
