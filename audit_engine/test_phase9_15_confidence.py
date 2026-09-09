"""
SysPulse Laptop Buyer Audit Engine - Phase 9 & Phase 15 Verification Test
Tests Confidence Scoring, Provenance Tracking, and Multi-Source Conflict Resolution:
1. Provenance Confidence per Subsystem (CPU, GPU, RAM, Storage, Display, Cooling)
2. Authority-Ranked Conflict Resolution (Benchmark > OEM Spec > Community > Retailer)
3. Detection of Missing OEM Tuning Limits
"""

import os
import sys
import json

# Ensure project root is on sys.path and stdout handles utf-8
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from audit_engine.validator import SpecificationValidator
from audit_engine.confidence_engine import ConfidenceAndConflictEngine, SystemConfidenceAuditReport, SpecificationConflict
from audit_engine.models import DataSource


def run_phase9_15_test():
    print("=" * 90)
    print("   SYSPULSE LAPTOP BUYER AUDIT ENGINE - PHASES 9 & 15: CONFIDENCE & RESOLUTION       ")
    print("=" * 90)

    test_targets = [
        ("HIGH-CONFIDENCE AUDITED WORKSTATION", "examples/engineered_workstation.json"),
        ("DECEPTIVE SPECIFICATION SHEET (OMITTED LIMITS)", "examples/deceptive_paper_tiger.json"),
        ("PHYSICAL HOST RIG (LIVE SENSORS)", "examples/host_physical_laptop.json")
    ]

    for title, filepath in test_targets:
        print("\n" + "#" * 90)
        print(f"  TARGET AUDIT: {title}")
        print(f"  Specification File: {filepath}")
        print("#" * 90)

        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        laptop, warnings = SpecificationValidator.validate_and_load(raw_data)
        conf_report: SystemConfidenceAuditReport = ConfidenceAndConflictEngine.audit_laptop_confidence(laptop)

        print(f"\n[+] Laptop Evaluated    : {laptop.metadata.brand} {laptop.metadata.model_name}")
        print(f"    Overall Confidence  : {conf_report.overall_confidence * 100:.1f}% [{conf_report.confidence_tier} TIER]")
        print(f"    Data Integrity State: {conf_report.audit_reliability_verdict}")
        print(f"    Parameter Breakdown : {conf_report.confirmed_parameters_count} Confirmed, "
              f"{conf_report.estimated_parameters_count} Estimated, {conf_report.unknown_parameters_count} Unknown")

        print("\n--- SUBSYSTEM CONFIDENCE RATINGS ---")
        for sub, score in conf_report.subsystem_confidence_scores.items():
            print(f"    • {sub:<24}: {score * 100:>5.1f}%")

        if conf_report.unknown_fields_flagged:
            print("\n--- UNKNOWN / OMITTED FIELDS FORCED TO CONSERVATIVE FLOORS ---")
            for field_name in conf_report.unknown_fields_flagged:
                print(f"    [!] {field_name}")

    print("\n" + "=" * 90)
    print("       MULTI-SOURCE CONFLICT RESOLUTION SIMULATION (PHASE 15)       ")
    print("=" * 90)

    # Simulation 1: Retailer vs OEM Spec on GPU TGP
    # Retailer advertises 140W, but OEM specification confirms 45W Max-Q
    c1 = ConfidenceAndConflictEngine.resolve_spec_conflict(
        field_name="GPU Base TGP",
        subsystem="GPU / Power",
        source_a="Retailer Product Page (Amazon)",
        val_a=140.0,
        conf_a=0.50,
        type_a=DataSource.USER_MANUAL_INPUT,
        source_b="Official OEM Technical Whitepaper",
        val_b=45.0,
        conf_b=0.95,
        type_b=DataSource.OEM_SPEC
    )
    print(f"\n[Conflict #1] Field: {c1.field_name} ({c1.subsystem})")
    print(f"    Source A: {c1.source_a_name} -> {c1.source_a_value}W (Confidence: {c1.source_a_confidence})")
    print(f"    Source B: {c1.source_b_name} -> {c1.source_b_value}W (Confidence: {c1.source_b_confidence})")
    print(f"    ==> RESOLUTION: Accepted {c1.resolved_value}W")
    print(f"    ==> RATIONALE : {c1.resolution_rationale}")

    # Simulation 2: Measured Benchmark vs OEM Spec on Boost Clock
    # OEM claims 5.0 GHz boost, but physical stress test proves 4.2 GHz sustained ceiling
    c2 = ConfidenceAndConflictEngine.resolve_spec_conflict(
        field_name="Sustained All-Core Boost",
        subsystem="CPU Thermal/Clock",
        source_a="OEM Marketing Brochure",
        val_a=5.0,
        conf_a=0.80,
        type_a=DataSource.OEM_SPEC,
        source_b="SysPulse Physical Benchmark Telemetry",
        val_b=4.2,
        conf_b=1.00,
        type_b=DataSource.BENCHMARK_MEASURED
    )
    print(f"\n[Conflict #2] Field: {c2.field_name} ({c2.subsystem})")
    print(f"    Source A: {c2.source_a_name} -> {c2.source_a_value} GHz (Confidence: {c2.source_a_confidence})")
    print(f"    Source B: {c2.source_b_name} -> {c2.source_b_value} GHz (Confidence: {c2.source_b_confidence})")
    print(f"    ==> RESOLUTION: Accepted {c2.resolved_value} GHz")
    print(f"    ==> RATIONALE : {c2.resolution_rationale}")

    print("\n" + "=" * 90)
    print("      PHASES 9 & 15 CONFIDENCE & CONFLICT TEST COMPLETED SUCCESSFULLY       ")
    print("=" * 90)


if __name__ == "__main__":
    run_phase9_15_test()
