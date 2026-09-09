"""
SysPulse Laptop Buyer Audit Engine - Master Unified CLI & Engine Orchestrator
Executes the complete end-to-end 22-phase laptop buyer audit pipeline.
Zero hardcoding: every single metric is calculated dynamically from silicon data & physics models.
"""

import os
import sys
import json
import argparse
from typing import List, Optional

# Ensure project root is on sys.path and stdout handles utf-8
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from audit_engine.models import LaptopSpecification
from audit_engine.validator import SpecificationValidator
from audit_engine.power_analyzer import PowerAnalysisEngine
from audit_engine.upgradeability import UpgradeabilityEngine
from audit_engine.performance_engine import RealPerformanceEngine
from audit_engine.benchmark_connector import BenchmarkConnector
from audit_engine.workload_engine import WorkloadScoringEngine
from audit_engine.dealbreaker_engine import DealBreakerAndBottleneckEngine
from audit_engine.value_engine import ValueAnalysisEngine
from audit_engine.anti_marketing import AntiMarketingAuditEngine
from audit_engine.future_proofing import FutureProofingAndVerdictEngine
from audit_engine.comparator import LaptopComparisonEngine
from audit_engine.report_generator import ReportGenerator
from audit_engine.db import DatabaseManager


def audit_single_laptop(spec_path: str, user_priority: str, output_html: Optional[str] = None):
    print("=" * 90)
    print("                SYSPULSE: PROFESSIONAL LAPTOP BUYER AUDIT DOSSIER                ")
    print("=" * 90)

    if not os.path.exists(spec_path):
        print(f"[-] Error: Specification file not found: {spec_path}")
        return

    with open(spec_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # 1. Validation & Pre-Audit Sanity
    laptop, warnings = SpecificationValidator.validate_and_load(raw_data)
    confidence = laptop.calculate_audit_confidence()

    # 2. Power Analysis
    power_res = PowerAnalysisEngine.analyze(laptop)

    # 3. Upgradeability & Longevity
    upgrade_res = UpgradeabilityEngine.audit(laptop)

    # 4. Real Performance & Throttling
    measured_data = None
    if "host_physical" in spec_path:
        measured_data = BenchmarkConnector.load_from_syspulse_results("results")
    perf_res = RealPerformanceEngine.audit_performance(laptop, measured_data)

    # 5. Workload Scoring
    workload_res = WorkloadScoringEngine.evaluate_all(laptop)

    # 6. Deal-Breakers & Bottlenecks
    deal_res = DealBreakerAndBottleneckEngine.audit(laptop)

    # 7. Value Analysis
    val_res = ValueAnalysisEngine.evaluate(
        laptop,
        perf_res.sustained_performance_score,
        perf_res.expected_metrics.cpu_multi_thread_index,
        perf_res.expected_metrics.gpu_fp32_tflops_expected
    )

    # 8. Anti-Marketing Audit
    market_res = AntiMarketingAuditEngine.audit_claims(laptop)

    # 9. Future-Proofing
    future_res = FutureProofingAndVerdictEngine.evaluate_future_proofing(
        laptop,
        upgrade_res.upgradeability_score
    )

    # 10. Final Tailored Verdict
    verdict = FutureProofingAndVerdictEngine.synthesize_verdict(
        laptop,
        user_priority,
        workload_res,
        deal_res,
        val_res.value_score_100
    )

    # 11. Print Console Dossier
    md_report = ReportGenerator.generate_markdown(
        laptop, power_res, upgrade_res, perf_res, workload_res,
        deal_res, val_res, market_res, future_res, verdict
    )
    print(md_report)

    # 12. Save HTML Report
    if output_html:
        os.makedirs(os.path.dirname(os.path.abspath(output_html)), exist_ok=True)
        ReportGenerator.generate_html(
            output_html,
            laptop, power_res, upgrade_res, perf_res, workload_res,
            deal_res, val_res, market_res, future_res, verdict
        )
        print(f"\n[✓] Interactive HTML Report successfully exported to: {output_html}")


def compare_laptops(spec_paths: List[str]):
    print("=" * 90)
    print("         SYSPULSE: HEAD-TO-HEAD LAPTOP SPECIFICATION & HARDWARE COMPARISON         ")
    print("=" * 90)

    laptops = []
    for p in spec_paths:
        if not os.path.exists(p):
            print(f"[-] Warning: File not found: {p}")
            continue
        with open(p, "r", encoding="utf-8") as f:
            lap, _ = SpecificationValidator.validate_and_load(json.load(f))
            laptops.append(lap)

    if len(laptops) < 2:
        print("[-] Error: At least 2 valid specification files are required for comparison.")
        return

    comp_report = LaptopComparisonEngine.compare(laptops)

    print(f"\n[+] COMPARING {len(laptops)} MACHINES:")
    for l in comp_report.laptops_compared:
        print(f"    - {l['brand']} {l['model']} ({l['sku']}): Rs {l['price_inr']:,.0f} | {l['cpu']} | {l['gpu']}")

    print("\n==========================================================================================")
    print("                               DOMAIN WINNERS & VERDICTS                                  ")
    print("==========================================================================================")
    for w in comp_report.domain_winners:
        print(f"  * WINNER FOR {w.domain_name:<24}: {w.winning_model_name} ({w.winning_score:.1f} pts, +{w.margin_pts:.1f} margin)")
        print(f"    Decisive Rationale: {w.decisive_reason}\n")
    print("------------------------------------------------------------------------------------------")
    print(f"  {comp_report.executive_recommendation}")
    print("==========================================================================================")


def main():
    parser = argparse.ArgumentParser(
        description="SysPulse Professional Laptop Buyer Audit Engine"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        help="Path to laptop JSON specification sheet."
    )
    parser.add_argument(
        "--priority", "-p",
        type=str,
        choices=["Gaming", "AI_ML", "Software_Development", "Engineering_CAD", "Content_Creation", "Portability"],
        default="Gaming",
        help="User's primary workload priority."
    )
    parser.add_argument(
        "--compare", "-c",
        nargs="+",
        help="Compare multiple laptop specification JSON files side-by-side."
    )
    parser.add_argument(
        "--html",
        type=str,
        default="results/audit_dossier.html",
        help="Output filepath for interactive HTML report."
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Audit the physical machine currently executing SysPulse benchmarks."
    )

    args = parser.parse_args()

    if args.compare:
        compare_laptops(args.compare)
    elif args.live:
        audit_single_laptop("examples/host_physical_laptop.json", args.priority, args.html)
    elif args.file:
        audit_single_laptop(args.file, args.priority, args.html)
    else:
        # Default run on engineered workstation vs paper tiger
        print("[INFO] No file specified. Running demonstration audit on Engineered Workstation...")
        audit_single_laptop("examples/engineered_workstation.json", args.priority, args.html)


if __name__ == "__main__":
    main()
