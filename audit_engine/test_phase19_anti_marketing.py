"""
SysPulse Laptop Buyer Audit Engine - Phase 19 Verification Test
Tests the Anti-Marketing Audit Engine:
1. Extraction of Headline Promotional Buzzwords
2. Cross-Examination Against Physical Hardware Realities
3. Output Classification: SUPPORTED, PARTIALLY_SUPPORTED, or MISLEADING_MARKETING_TRAP
4. Marketing Honesty Score Calculation
"""

import os
import sys
import json

# Ensure project root is on sys.path and stdout handles utf-8
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from audit_engine.validator import SpecificationValidator
from audit_engine.anti_marketing import AntiMarketingAuditEngine, AntiMarketingReport


def run_phase19_test():
    print("=" * 90)
    print("       SYSPULSE LAPTOP BUYER AUDIT ENGINE - PHASE 19: ANTI-MARKETING AUDIT           ")
    print("=" * 90)

    test_targets = [
        ("DECEPTIVE PAPER TIGER (BUZZWORD OVERLOAD)", "examples/deceptive_paper_tiger.json"),
        ("HONESTLY ENGINEERED WORKSTATION", "examples/engineered_workstation.json"),
        ("SEVERE POWER DEFICIT (MISLEADING ULTRA-SLIM)", "examples/severe_power_deficit.json")
    ]

    for title, filepath in test_targets:
        print("\n" + "#" * 90)
        print(f"  TARGET AUDIT: {title}")
        print(f"  Specification File: {filepath}")
        print("#" * 90)

        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        laptop, _ = SpecificationValidator.validate_and_load(raw_data)
        report: AntiMarketingReport = AntiMarketingAuditEngine.audit_claims(laptop)

        print(f"\n[+] Laptop Evaluated    : {laptop.metadata.brand} {laptop.metadata.model_name}")
        print(f"    Advertised Headline : \"{laptop.metadata.marketing_headline}\"")
        print(f"    Marketing Honesty   : {report.marketing_honesty_score:.1f} / 100.0 pts")
        print(f"    Traps Detected      : {report.misleading_traps_count} Deceptive Traps out of {report.total_claims_scanned} Claims Scanned")
        print(f"    Summary Verdict     : {report.executive_summary}")

        print("\n--- DETAILED PROMOTIONAL CLAIMS CROSS-EXAMINATION ---")
        for i, claim in enumerate(report.claims, 1):
            tag = f"[{claim.audit_verdict}]"
            print(f"    Claim #{i}: \"{claim.claim_phrase}\" -> {tag}")
            print(f"      • Physical Reality : {claim.physical_hardware_reality}")
            print(f"      • Engineering Truth: {claim.engineering_explanation}\n")

    print("=" * 90)
    print("             PHASE 19 ANTI-MARKETING AUDIT COMPLETED SUCCESSFULLY             ")
    print("=" * 90)


if __name__ == "__main__":
    run_phase19_test()
