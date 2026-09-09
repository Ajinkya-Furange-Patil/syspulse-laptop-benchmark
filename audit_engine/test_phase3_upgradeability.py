"""
SysPulse Laptop Buyer Audit Engine - Phase 3 Verification Test
Tests the dedicated Upgradeability & Long-Term Ownership Engine.
Audits RAM modularity, storage expansion, repairability, chassis hinge robustness,
and 3-to-5 year survival potential.
"""

import os
import sys
import json

# Ensure project root is on sys.path and stdout handles utf-8
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from audit_engine.validator import SpecificationValidator
from audit_engine.upgradeability import UpgradeabilityEngine, UpgradeabilityAuditResult
from audit_engine.db import DatabaseManager


def run_phase3_test():
    print("=" * 85)
    print("      SYSPULSE LAPTOP BUYER AUDIT ENGINE - PHASE 3: UPGRADEABILITY & OWNERSHIP      ")
    print("=" * 85)

    test_cases = [
        ("DECEPTIVE PAPER TIGER", "examples/deceptive_paper_tiger.json"),
        ("PROPERLY ENGINEERED WORKSTATION", "examples/engineered_workstation.json"),
        ("BUDGET POWER DEFICIT SKU", "examples/severe_power_deficit.json")
    ]

    db = DatabaseManager("syspulse_audit.db")

    for title, filepath in test_cases:
        print("\n" + "#" * 85)
        print(f"  UPGRADEABILITY AUDIT TARGET: {title}")
        print(f"  Specification File: {filepath}")
        print("#" * 85)

        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        laptop, _ = SpecificationValidator.validate_and_load(raw_data)
        result: UpgradeabilityAuditResult = UpgradeabilityEngine.audit(laptop)

        print(f"\n[+] Target SKU         : {laptop.metadata.brand} {laptop.metadata.model_name} ({laptop.metadata.exact_sku})")
        print(f"    RAM Topology       : {result.ram_modular_state} ({laptop.memory.total_capacity_gb}GB, {laptop.memory.soldered_capacity_gb}GB Soldered, {laptop.memory.sodimm_slots_total} SODIMMs)")
        print(f"    Storage Layout     : {laptop.storage.m2_slots_total} M.2 Slots Total ({result.storage_expansion_slots_free} Free)")
        print(f"    Wi-Fi Modularity   : {'Socketed M.2 2230' if result.wifi_replaceable else 'Soldered BGA'}")
        print(f"    Chassis Access     : {result.maintenance_accessibility} (Screws: {laptop.chassis.screw_type}, Pry: {laptop.chassis.chassis_pry_difficulty})")
        print(f"    Chassis Materials  : {laptop.chassis.chassis_materials}")

        print("\n--- UPGRADEABILITY SCORE / 100 ---")
        print(f"    Total Upgradeability Score: {result.upgradeability_score:>5.1f} / 100.0")
        for item in result.upgradeability_breakdown:
            print(f"    - {item['component']:<36}: {item['awarded']:>4.1f} / {item['weight']} pts | {item['reason']}")

        print("\n--- LONG-TERM OWNERSHIP SCORE / 100 ---")
        print(f"    Total Long-Term Ownership: {result.long_term_ownership_score:>5.1f} / 100.0")
        print(f"    Projected Functional Lifespan: {result.projected_functional_lifespan_years} Years [{result.longevity_rating}]")
        for item in result.ownership_breakdown:
            print(f"    - {item['component']:<36}: {item['awarded']:>4.1f} / {item['weight']} pts | {item['reason']}")

        print("\n--- DIAGNOSTIC UPGRADE FINDINGS & TRAPS ---")
        if result.findings:
            for i, f in enumerate(result.findings, 1):
                print(f"    [{f.severity}] #{i} ({f.code}): {f.title}")
                print(f"          Details    : {f.message}")
                print(f"          Action/Fix : {f.remediation}")
        else:
            print("    [OK] Outstanding modularity and repairability. No planned obsolescence detected.")

        # Persist findings to database
        with db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM laptops WHERE exact_sku = ?", (laptop.metadata.exact_sku,))
            row = cur.fetchone()
            if row:
                lap_id = row["id"]
                for f in result.findings:
                    if f.severity in ("FATAL", "WARNING"):
                        cur.execute("""
                            INSERT INTO deal_breakers (laptop_id, severity, category, message, impact)
                            VALUES (?, ?, ?, ?, ?)
                        """, (lap_id, f.severity, "UPGRADEABILITY", f.title, f.message))
                conn.commit()

    print("\n" + "=" * 85)
    print("          PHASE 3 UPGRADEABILITY AUDIT TEST COMPLETED SUCCESSFULLY          ")
    print("=" * 85)


if __name__ == "__main__":
    run_phase3_test()
