"""
SysPulse Laptop Buyer Audit Engine - Phase 8 Verification Test
Tests the Hardware Unit Economics & Value Analysis Engine:
1. Capability per 10,000 INR
2. GPU Compute & VRAM per Rupee
3. Detection of Overpriced Marketing Traps vs Genuine Value
"""

import os
import sys
import json

# Ensure project root is on sys.path and stdout handles utf-8
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from audit_engine.validator import SpecificationValidator
from audit_engine.performance_engine import RealPerformanceEngine
from audit_engine.value_engine import ValueAnalysisEngine, ValueAuditResult


def run_phase8_test():
    print("=" * 90)
    print("       SYSPULSE LAPTOP BUYER AUDIT ENGINE - PHASE 8: VALUE & UNIT ECONOMICS          ")
    print("=" * 90)

    test_targets = [
        ("DECEPTIVE PAPER TIGER (COST-CUT HARDWARE)", "examples/deceptive_paper_tiger.json"),
        ("PROPERLY ENGINEERED WORKSTATION (FULL POWER)", "examples/engineered_workstation.json"),
        ("PHYSICAL HOST MACHINE (BUDGET LAB RIG)", "examples/host_physical_laptop.json"),
        ("SEVERE POWER DEFICIT TRAP (UNDERSIZED ADAPTER)", "examples/severe_power_deficit.json")
    ]

    for title, filepath in test_targets:
        print("\n" + "#" * 90)
        print(f"  TARGET AUDIT: {title}")
        print(f"  Specification File: {filepath}")
        print("#" * 90)

        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        laptop, _ = SpecificationValidator.validate_and_load(raw_data)
        perf_res = RealPerformanceEngine.audit_performance(laptop)

        val_res: ValueAuditResult = ValueAnalysisEngine.evaluate(
            laptop,
            perf_res.sustained_performance_score,
            perf_res.expected_metrics.cpu_multi_thread_index,
            perf_res.expected_metrics.gpu_fp32_tflops_expected
        )

        econ = val_res.unit_economics
        print(f"\n[+] Model Under Test: {laptop.metadata.brand} {laptop.metadata.model_name}")
        print(f"    Pricing         : Rs {econ.price:,.0f} ({val_res.market_tier})")
        print(f"    Value Rating    : [{val_res.value_rating}] ({val_res.value_score_100:.1f} / 100.0 pts)")
        print(f"    Justification   : {val_res.value_justification}")
        print(f"    Market Context  : {val_res.competing_market_context}")

        print("\n--- HARDWARE UNIT ECONOMICS (PER 10,000 INR) ---")
        print(f"    • Total Capability   : {econ.overall_capability_per_10k:>5.2f} pts / 10k INR")
        print(f"    • CPU Multi-Core     : {econ.cpu_performance_per_10k:>5.2f} pts / 10k INR")
        print(f"    • GPU FP32 Compute   : {econ.gpu_tflops_per_10k:>5.2f} TFLOPs / 10k INR")
        print(f"    • Dedicated VRAM     : {econ.vram_gb_per_10k:>5.2f} GB / 10k INR")
        print(f"    • System Memory (RAM): {econ.ram_gb_per_10k:>5.2f} GB / 10k INR")
        print(f"    • Solid-State Storage: {econ.storage_gb_per_10k:>5.1f} GB / 10k INR")

        print("\n--- COMPONENT RETURN ON INVESTMENT BREAKDOWN ---")
        for item in val_res.breakdown:
            print(f"    [{item['status']:<7}] {item['metric']:<32}: {item['value']}")

    print("\n" + "=" * 90)
    print("             PHASE 8 VALUE ANALYSIS TEST COMPLETED SUCCESSFULLY             ")
    print("=" * 90)


if __name__ == "__main__":
    run_phase8_test()
