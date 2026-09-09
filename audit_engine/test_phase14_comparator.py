"""
SysPulse Laptop Buyer Audit Engine - Phase 14 Verification Test
Tests Multi-Laptop Head-to-Head Comparison Engine:
1. Side-by-Side Parameter Matrix
2. Domain-by-Domain Winner Calculation (Gaming, AI, Dev, CAD, Content, Portability, Value)
3. Decisive Engineering Rationale (Why one machine beats another)
"""

import os
import sys
import json

# Ensure project root is on sys.path and stdout handles utf-8
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from audit_engine.validator import SpecificationValidator
from audit_engine.comparator import LaptopComparisonEngine, MultiLaptopComparisonReport


def run_phase14_test():
    print("=" * 90)
    print("       SYSPULSE LAPTOP BUYER AUDIT ENGINE - PHASE 14: HEAD-TO-HEAD COMPARATOR        ")
    print("=" * 90)

    spec_files = [
        ("Engineered Workstation", "examples/engineered_workstation.json"),
        ("Deceptive Paper Tiger", "examples/deceptive_paper_tiger.json"),
        ("Severe Power Deficit", "examples/severe_power_deficit.json")
    ]

    laptops = []
    for label, path in spec_files:
        with open(path, "r", encoding="utf-8") as f:
            lap, _ = SpecificationValidator.validate_and_load(json.load(f))
            laptops.append(lap)

    report: MultiLaptopComparisonReport = LaptopComparisonEngine.compare(laptops)

    print(f"\n[+] PITTING {len(laptops)} MACHINES IN DIRECT HEAD-TO-HEAD AUDIT:")
    for l in report.laptops_compared:
        print(f"    - [{l['sku']}] {l['brand']} {l['model']}")
        print(f"      Price: Rs {l['price_inr']:,.0f} | CPU: {l['cpu']} | GPU: {l['gpu']} | VRAM: {l['vram']}")

    print("\n==========================================================================================")
    print("                               DOMAIN WINNERS & DECISIVE FACTORS                          ")
    print("==========================================================================================")
    for w in report.domain_winners:
        print(f"  * DOMAIN: {w.domain_name:<24}")
        print(f"    Winner: {w.winning_model_name} ({w.winning_sku})")
        print(f"    Score : {w.winning_score:.1f} pts (Margin: +{w.margin_pts:.1f} pts over runner-up)")
        print(f"    Why?  : {w.decisive_reason}\n")

    print("==========================================================================================")
    print("                               SIDE-BY-SIDE PARAMETER MATRIX                              ")
    print("==========================================================================================")
    skus = [l["sku"] for l in report.laptops_compared]
    header = f"  {'Parameter':<24}" + "".join(f"{sku:<26}" for sku in skus)
    print(header)
    print("  " + "-" * (len(header) - 2))

    for row in report.parameter_comparison_table:
        line = f"  {row['parameter']:<24}"
        for sku in skus:
            val_str = str(row['values'].get(sku, "N/A"))
            line += f"{val_str[:24]:<26}"
        print(line)

    print("\n------------------------------------------------------------------------------------------")
    print(f"  EXECUTIVE RECOMMENDATION: {report.executive_recommendation}")
    print("==========================================================================================")
    print("\n" + "=" * 90)
    print("             PHASE 14 HEAD-TO-HEAD COMPARISON TEST COMPLETED SUCCESSFULLY             ")
    print("=" * 90)


if __name__ == "__main__":
    run_phase14_test()
