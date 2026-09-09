"""
SysPulse Laptop Buyer Audit Engine - Phase 4 Verification Test
Tests the Real Performance & Sustained Throttling Engine:
1. Deceptive Paper Tiger (Theoretical vs Throttled Sustained Score)
2. Engineered Workstation (High-Performance Sustained Scaling)
3. Physical Host Machine Audited with LIVE Measured C++ & CUDA Telemetry
"""

import os
import sys
import json

# Ensure project root is on sys.path and stdout handles utf-8
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from audit_engine.validator import SpecificationValidator
from audit_engine.performance_engine import RealPerformanceEngine, PerformanceAuditResult
from audit_engine.benchmark_connector import BenchmarkConnector
from audit_engine.db import DatabaseManager


def run_phase4_test():
    print("=" * 90)
    print("       SYSPULSE LAPTOP BUYER AUDIT ENGINE - PHASE 4: REAL PERFORMANCE & THROTTLING       ")
    print("=" * 90)

    db = DatabaseManager("syspulse_audit.db")

    # Ingest live empirical benchmark data generated on this physical lab machine
    live_measured = BenchmarkConnector.load_from_syspulse_results("results")
    if live_measured:
        print(f"[*] Successfully connected to physical test results: [{live_measured.source}]")
        print(f"    - Measured CPU Multi-Throughput: {live_measured.syspulse_multi_gflops:.1f} GFLOPs")
        print(f"    - Measured CUDA SGEMM Compute  : {live_measured.syspulse_cuda_tflops:.2f} TFLOPs")
        print(f"    - Measured RAM Bandwidth       : {live_measured.syspulse_ram_bandwidth_gbps:.1f} GB/s")
        print(f"    - Measured NVMe Read Speed     : {live_measured.crystaldisk_read_mbps:.1f} MB/s")
        print(f"    - Measured Peak CPU Temp       : {live_measured.cpu_peak_temp_c:.1f} °C")

    test_targets = [
        ("DECEPTIVE PAPER TIGER", "examples/deceptive_paper_tiger.json", None),
        ("PROPERLY ENGINEERED WORKSTATION", "examples/engineered_workstation.json", None),
        ("PHYSICAL HOST MACHINE (LIVE MEASURED RUN)", "examples/host_physical_laptop.json", live_measured)
    ]

    for title, filepath, measured_data in test_targets:
        print("\n" + "#" * 90)
        print(f"  PERFORMANCE AUDIT TARGET: {title}")
        print(f"  Specification File: {filepath}")
        if measured_data:
            print(f"  Live Telemetry Data Ingested: YES (Source: {measured_data.source})")
        else:
            print("  Live Telemetry Data Ingested: NO (Theoretical Specification Simulation Only)")
        print("#" * 90)

        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        laptop, _ = SpecificationValidator.validate_and_load(raw_data)
        res: PerformanceAuditResult = RealPerformanceEngine.audit_performance(laptop, measured_data)

        print(f"\n[+] Target Model      : {laptop.metadata.brand} {laptop.metadata.model_name} ({laptop.metadata.exact_sku})")
        print(f"    CPU Architecture  : {laptop.cpu.architecture} ({laptop.cpu.exact_model})")
        print(f"    Expected All-Core : {res.expected_metrics.cpu_expected_all_core_ghz} GHz (Power Scale: {res.expected_metrics.cpu_power_scaling_factor}x)")
        print(f"    GPU Compute Rating: {res.expected_metrics.gpu_fp32_tflops_expected} FP32 TFLOPs | {res.expected_metrics.gpu_tensor_tflops_expected} Tensor TFLOPs")
        print(f"    Expected RAM B/W  : {res.expected_metrics.ram_expected_bandwidth_gbps} GB/s ({laptop.memory.channel_configuration})")

        print("\n--- PERFORMANCE SCORES: SPECIFICATION VS MEASURED VS SUSTAINED ---")
        print(f"    1. SPECIFICATION AUDIT SCORE     : {res.specification_score:>5.1f} / 100.0 (Theoretical Architectural Potential)")
        if res.measured_performance_score is not None:
            print(f"    2. MEASURED BENCHMARK SCORE      : {res.measured_performance_score:>5.1f} / 100.0 (Empirical Hardware Execution)")
        else:
            print(f"    2. MEASURED BENCHMARK SCORE      : [UNMEASURED / LAB DATA REQUIRED]")
        print(f"    3. SUSTAINED PERFORMANCE SCORE   : {res.sustained_performance_score:>5.1f} / 100.0 (Continuous Real-World Output)")

        print("\n--- SUSTAINED THERMAL RETENTION & THROTTLING AUDIT ---")
        print(f"    Sustained Retention Rate : {res.throttling.cpu_retention_pct:.1f}% [{res.throttling.thermal_retention_grade}]")
        print(f"    GPU Crossload Throttling : {res.throttling.gpu_cross_throttle_pct:.1f}% clock drop")
        print(f"    Thermal Penalty Applied  : -{res.throttling.thermal_penalty_points:.1f} points")

        print("\n--- SPECIFICATION SCORE BREAKDOWN ---")
        for item in res.spec_score_breakdown:
            print(f"    - {item['component']:<36}: {item['awarded']:>4.1f} / {item['weight']} pts | {item['reason']}")

        if res.discrepancy_analysis:
            print("\n--- SPECIFICATION VS. REALITY DISCREPANCY AUDIT ---")
            for disc in res.discrepancy_analysis:
                print(f"    [!] {disc}")

        print("\n--- PERFORMANCE BOTTLENECKS & FINDINGS ---")
        if res.findings:
            for i, f in enumerate(res.findings, 1):
                print(f"    [{f.severity}] #{i} ({f.code}): {f.title}")
                print(f"          Details    : {f.message}")
                print(f"          Action/Fix : {f.remediation}")
        else:
            print("    [OK] No severe performance bottlenecks detected. System delivers expected silicon throughput.")

        # Persist to database
        with db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM laptops WHERE exact_sku = ?", (laptop.metadata.exact_sku,))
            row = cur.fetchone()
            if row:
                lap_id = row["id"]
                for f in res.findings:
                    if f.severity in ("FATAL", "WARNING"):
                        cur.execute("""
                            INSERT INTO deal_breakers (laptop_id, severity, category, message, impact)
                            VALUES (?, ?, ?, ?, ?)
                        """, (lap_id, f.severity, "PERFORMANCE_BOTTLENECK", f.title, f.message))
                conn.commit()

    print("\n" + "=" * 90)
    print("         PHASE 4 PERFORMANCE & SUSTAINED THROTTLING AUDIT COMPLETE          ")
    print("=" * 90)


if __name__ == "__main__":
    run_phase4_test()
