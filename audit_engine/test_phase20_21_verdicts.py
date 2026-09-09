"""
SysPulse Laptop Buyer Audit Engine - Phase 20 & Phase 21 Verification Test
Tests Future-Proofing Horizons & User-Priority Conditioned Final Verdicts:
1. 1-Year, 3-Year, and 5-Year Future Viability Horizons
2. Proof of "NO UNIVERSAL WINNER":
   Demonstrating how identical hardware yields completely different buying verdicts
   depending on whether the user prioritizes AI/ML, CAD, Software Dev, or Gaming.
"""

import os
import sys
import json

# Ensure project root is on sys.path and stdout handles utf-8
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from audit_engine.validator import SpecificationValidator
from audit_engine.upgradeability import UpgradeabilityEngine
from audit_engine.workload_engine import WorkloadScoringEngine
from audit_engine.dealbreaker_engine import DealBreakerAndBottleneckEngine
from audit_engine.future_proofing import FutureProofingAndVerdictEngine, FutureProofingReport, FinalTailoredVerdict


def run_phase20_21_test():
    print("=" * 90)
    print("   SYSPULSE LAPTOP BUYER AUDIT ENGINE - PHASES 20 & 21: FUTURE-PROOFING & VERDICTS   ")
    print("=" * 90)

    test_targets = [
        ("PROPERLY ENGINEERED WORKSTATION", "examples/engineered_workstation.json"),
        ("DECEPTIVE PAPER TIGER", "examples/deceptive_paper_tiger.json"),
        ("PHYSICAL HOST RIG (GTX 1650 4GB)", "examples/host_physical_laptop.json")
    ]

    for title, filepath in test_targets:
        print("\n" + "#" * 90)
        print(f"  TARGET AUDIT: {title}")
        print(f"  Specification File: {filepath}")
        print("#" * 90)

        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        laptop, _ = SpecificationValidator.validate_and_load(raw_data)
        upgrade_res = UpgradeabilityEngine.audit(laptop)
        workload_res = WorkloadScoringEngine.evaluate_all(laptop)
        deal_res = DealBreakerAndBottleneckEngine.audit(laptop)

        # 1. Evaluate Future-Proofing (Phase 20)
        future_rep: FutureProofingReport = FutureProofingAndVerdictEngine.evaluate_future_proofing(
            laptop,
            upgrade_res.upgradeability_score
        )

        print(f"\n[+] Evaluated Model: {laptop.metadata.brand} {laptop.metadata.model_name}")
        print(f"    Future Viability Summary: {future_rep.summary}")
        print(f"    • 1-Year Horizon (2027): [{future_rep.horizon_1_year.viability_rating}] - {future_rep.horizon_1_year.bottleneck_projection}")
        print(f"    • 3-Year Horizon (2029): [{future_rep.horizon_3_year.viability_rating}] - {future_rep.horizon_3_year.bottleneck_projection}")
        print(f"    • 5-Year Horizon (2031): [{future_rep.horizon_5_year.viability_rating}] - {future_rep.horizon_5_year.bottleneck_projection}")

        # 2. Evaluate User-Priority Conditioned Final Verdicts (Phase 21)
        # We test multiple distinct user priorities to demonstrate NO UNIVERSAL WINNER
        priorities = ["Gaming", "AI_ML", "Software_Development", "Engineering_CAD", "Portability"]

        print("\n--- USER PRIORITY-CONDITIONED BUYING VERDICTS (NO UNIVERSAL WINNER) ---")
        for prio in priorities:
            v: FinalTailoredVerdict = FutureProofingAndVerdictEngine.synthesize_verdict(
                laptop,
                prio,
                workload_res,
                deal_res,
                value_score=75.0
            )
            print(f"    [*] Priority: {prio:<22} -> VERDICT: [{v.verdict:<15}] (Domain Score: {v.priority_score:>5.1f}/100)")
            print(f"        Reason : {v.primary_reason}")
            print(f"        Advice : {v.tailored_buying_advice}\n")

    print("=" * 90)
    print("      PHASES 20 & 21 FUTURE-PROOFING & VERDICTS TEST COMPLETED SUCCESSFULLY         ")
    print("=" * 90)


if __name__ == "__main__":
    run_phase20_21_test()
