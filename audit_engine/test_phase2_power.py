"""
SysPulse Laptop Buyer Audit Engine - Phase 2 Verification Test
Tests the dedicated Power Analysis Engine across three distinct hardware tiers:
1. Deceptive Paper Tiger (Marginal/Deficit power design)
2. Properly Engineered Workstation (Surplus GaN power design)
3. Severe Power Deficit (Flagship CPU/GPU paired with cost-cut adapter)
"""

import os
import sys
import json

# Ensure project root is on sys.path and stdout handles utf-8
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from audit_engine.validator import SpecificationValidator
from audit_engine.power_analyzer import PowerAnalysisEngine, PowerAnalysisResult
from audit_engine.db import DatabaseManager


def run_phase2_test():
    print("=" * 85)
    print("          SYSPULSE LAPTOP BUYER AUDIT ENGINE - PHASE 2: POWER AUDIT          ")
    print("=" * 85)

    test_cases = [
        ("DECEPTIVE PAPER TIGER", "examples/deceptive_paper_tiger.json"),
        ("PROPERLY ENGINEERED WORKSTATION", "examples/engineered_workstation.json"),
        ("SEVERE POWER DEFICIT TRAP", "examples/severe_power_deficit.json")
    ]

    db = DatabaseManager("syspulse_audit.db")

    for title, filepath in test_cases:
        print("\n" + "#" * 85)
        print(f"  POWER AUDIT TARGET: {title}")
        print(f"  Specification File: {filepath}")
        print("#" * 85)

        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        laptop, _ = SpecificationValidator.validate_and_load(raw_data)
        pwr_result: PowerAnalysisResult = PowerAnalysisEngine.analyze(laptop)

        print(f"\n[+] Target SKU      : {laptop.metadata.brand} {laptop.metadata.model_name} ({laptop.metadata.exact_sku})")
        print(f"    CPU Silicon     : {laptop.cpu.exact_model} (PL1: {pwr_result.cpu_sustained_power_w}W | PL2 Turbo: {pwr_result.cpu_peak_power_w}W)")
        print(f"    GPU Silicon     : {laptop.gpu.exact_model} (TGP Base: {pwr_result.gpu_sustained_power_w}W | Peak Boost: {pwr_result.gpu_peak_power_w}W)")
        print(f"    Power Adapter   : {pwr_result.adapter_rating_w}W ({laptop.power.adapter_form_factor})")
        print(f"    Battery Pack    : {laptop.power.battery_capacity_wh}Wh")

        print("\n--- ELECTRICAL DEMAND & POWER BALANCE MATRIX ---")
        print(f"    System Aux Overhead: {pwr_result.system_auxiliary_power_w:>5.1f}W (Motherboard, Display, Fans, NVMe, RAM)")
        print(f"    Sustained Crossload: {pwr_result.total_sustained_demand_w:>5.1f}W (CPU PL1 + GPU TGP + Aux)")
        print(f"    Peak Turbo Crossload: {pwr_result.total_peak_demand_w:>5.1f}W (CPU PL2 + GPU Dynamic Boost + Aux)")
        print(f"    Sustained Headroom : {pwr_result.sustained_headroom_w:>+5.1f}W (Headroom Ratio: {pwr_result.sustained_headroom_ratio:.2f}x)")
        print(f"    Peak Turbo Headroom: {pwr_result.peak_headroom_w:>+5.1f}W (Peak Ratio: {pwr_result.peak_headroom_ratio:.2f}x)")
        print(f"    Charging Speed     : {pwr_result.charging_speed_under_load}")

        if pwr_result.battery_drain_on_ac_expected:
            print(f"    [!] AC DISCHARGE DETECTED: Battery drains at ~{pwr_result.estimated_battery_drain_rate_w:.1f}W while plugged into wall under heavy load!")
        else:
            print(f"    [OK] AC Stability Verified: Surplus wattage ensures steady battery charging under full load.")

        print("\n--- POWER DELIVERY SCORE & TRANSPARENT FACTOR BREAKDOWN ---")
        print(f"    Total Power Score: {pwr_result.power_score:>5.1f} / 100.0")
        for item in pwr_result.score_breakdown:
            print(f"    - {item['component']:<26}: {item['awarded']:>4.1f} / {item['weight']} pts | {item['reason']}")

        print("\n--- DIAGNOSTIC FINDINGS & REMEDIATIONS ---")
        if pwr_result.findings:
            for i, f in enumerate(pwr_result.findings, 1):
                print(f"    [{f.severity}] #{i} ({f.code}): {f.title}")
                print(f"          Details    : {f.message}")
                print(f"          Action/Fix : {f.remediation}")
        else:
            print("    [OK] Clean electrical audit. No design compromises or power starvation detected.")

        # Sync detected deal-breakers to SQLite database
        with db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM laptops WHERE exact_sku = ?", (laptop.metadata.exact_sku,))
            row = cur.fetchone()
            if row:
                lap_id = row["id"]
                for f in pwr_result.findings:
                    if f.severity in ("FATAL", "WARNING"):
                        cur.execute("""
                            INSERT INTO deal_breakers (laptop_id, severity, category, message, impact)
                            VALUES (?, ?, ?, ?, ?)
                        """, (lap_id, f.severity, "POWER_ANALYSIS", f.title, f.message))
                conn.commit()

    print("\n" + "=" * 85)
    print("               PHASE 2 POWER AUDIT TEST COMPLETED SUCCESSFULLY               ")
    print("=" * 85)


if __name__ == "__main__":
    run_phase2_test()
