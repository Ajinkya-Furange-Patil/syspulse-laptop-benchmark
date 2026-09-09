"""
SysPulse Laptop Buyer Audit Engine - Phase 6 & Phase 7 Verification Test
Tests Hard Deal-Breakers and Bottleneck Prediction Engine across distinct hardware configurations.
"""

import os
import sys
import json

# Ensure project root is on sys.path and stdout handles utf-8
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from audit_engine.validator import SpecificationValidator
from audit_engine.dealbreaker_engine import DealBreakerAndBottleneckEngine, DealBreakerAndBottleneckReport
from audit_engine.db import DatabaseManager


def run_phase6_7_test():
    print("=" * 90)
    print("      SYSPULSE LAPTOP BUYER AUDIT ENGINE - PHASES 6 & 7: DEAL-BREAKERS & BOTTLENECK ENGINE      ")
    print("=" * 90)

    test_targets = [
        ("DECEPTIVE PAPER TIGER", "examples/deceptive_paper_tiger.json"),
        ("PROPERLY ENGINEERED WORKSTATION", "examples/engineered_workstation.json"),
        ("PHYSICAL LAB RIG (GTX 1650 4GB)", "examples/host_physical_laptop.json"),
        ("SEVERE POWER DEFICIT TRAP", "examples/severe_power_deficit.json")
    ]

    for title, filepath in test_targets:
        print("\n" + "#" * 90)
        print(f"  TARGET AUDIT: {title}")
        print(f"  Specification File: {filepath}")
        print("#" * 90)

        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        laptop, _ = SpecificationValidator.validate_and_load(raw_data)
        report: DealBreakerAndBottleneckReport = DealBreakerAndBottleneckEngine.audit(laptop)

        print(f"\n[+] Evaluated Model  : {laptop.metadata.brand} {laptop.metadata.model_name} ({laptop.metadata.exact_sku})")
        print(f"    Hardware Verdict : {report.overall_hardware_sanity_verdict}")
        print(f"    Fatal Blockers   : {report.fatal_dealbreakers_count} Detected")
        print(f"    Critical Warnings: {report.critical_warnings_count} Detected")

        print("\n--- DETECTED HARD DEAL-BREAKERS & HARDWARE TRAPS ---")
        if report.dealbreakers:
            for i, d in enumerate(report.dealbreakers, 1):
                print(f"    [{d.severity}] #{i} ({d.code}) - Subsystem: {d.subsystem}")
                print(f"          Title       : {d.title}")
                print(f"          Details     : {d.description}")
                print(f"          Impacts     : {', '.join(d.affected_workloads)}")
                print(f"          Fix/Advice  : {d.remediation_or_alternative}")
        else:
            print("    [OK] Flawless architectural design. Zero deal-breakers or traps identified.")

        print("\n--- HARDWARE BOTTLENECK PREDICTIONS & THROUGHPUT LOSS ---")
        if report.bottlenecks:
            for i, b in enumerate(report.bottlenecks, 1):
                print(f"    [!] #{i} BOTTLENECK ON: {b.subsystem_affected} [{b.bottleneck_severity}]")
                print(f"          Constraining Component: {b.constraining_component}")
                print(f"          Estimated Perf Loss   : ~{b.estimated_performance_loss_pct:.1f}%")
                print(f"          Bottleneck Mechanism  : {b.mechanism}")
                print(f"          Technical Explanation : {b.technical_explanation}")
        else:
            print("    [OK] Balanced component synergy. No severe inter-subsystem bottlenecks detected.")

    print("\n" + "=" * 90)
    print("             PHASE 6 & 7 DEAL-BREAKER & BOTTLENECK TEST COMPLETED             ")
    print("=" * 90)


if __name__ == "__main__":
    run_phase6_7_test()
