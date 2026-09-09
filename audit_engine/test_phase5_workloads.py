"""
SysPulse Laptop Buyer Audit Engine - Phase 5 Verification Test
Tests the multi-domain Workload & Use-Case Fit Scoring Engine:
1. Modern Gaming
2. AI / Machine Learning (Enforces Hard VRAM Limits)
3. Programming / Software Development
4. Engineering / CAD & Simulation
5. Content Creation & Video Production
6. Campus Portability & Mobility
"""

import os
import sys
import json

# Ensure project root is on sys.path and stdout handles utf-8
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from audit_engine.validator import SpecificationValidator
from audit_engine.workload_engine import WorkloadScoringEngine, MasterWorkloadAuditReport
from audit_engine.db import DatabaseManager


def run_phase5_test():
    print("=" * 90)
    print("       SYSPULSE LAPTOP BUYER AUDIT ENGINE - PHASE 5: WORKLOAD-SPECIFIC AUDIT        ")
    print("=" * 90)

    test_targets = [
        ("DECEPTIVE PAPER TIGER", "examples/deceptive_paper_tiger.json"),
        ("PROPERLY ENGINEERED WORKSTATION", "examples/engineered_workstation.json"),
        ("PHYSICAL LAB MACHINE (GTX 1650 4GB)", "examples/host_physical_laptop.json")
    ]

    db = DatabaseManager("syspulse_audit.db")

    for title, filepath in test_targets:
        print("\n" + "#" * 90)
        print(f"  DOMAIN SUITABILITY AUDIT: {title}")
        print(f"  Specification File: {filepath}")
        print("#" * 90)

        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        laptop, _ = SpecificationValidator.validate_and_load(raw_data)
        report: MasterWorkloadAuditReport = WorkloadScoringEngine.evaluate_all(laptop)

        print(f"\n[+] Target Model: {laptop.metadata.brand} {laptop.metadata.model_name} ({laptop.metadata.exact_sku})")
        print(f"    Silicon Core: {laptop.cpu.exact_model} | {laptop.gpu.exact_model} ({laptop.gpu.vram_gb}GB VRAM)")
        print(f"    RAM & Screen: {laptop.memory.total_capacity_gb}GB ({laptop.memory.channel_configuration}) | {laptop.display.aspect_ratio} {laptop.display.panel_technology}")

        print("\n==========================================================================================")
        print("                           MULTI-DOMAIN WORKLOAD SCORECARD                                ")
        print("==========================================================================================")
        print(f"  1. [GAMING]           : {report.gaming.overall_gaming_score:>5.1f} / 100.0  [{report.gaming.gaming_tier}]")
        print(f"  2. [AI & LOCAL LLMS]  : {report.ai_ml.overall_aiml_score:>5.1f} / 100.0  [{report.ai_ml.aiml_tier}]")
        print(f"  3. [SOFTWARE DEV]     : {report.software_dev.overall_dev_score:>5.1f} / 100.0  [{report.software_dev.dev_tier}]")
        print(f"  4. [ENGINEERING/CAD]  : {report.engineering_cad.overall_engineering_score:>5.1f} / 100.0  [{report.engineering_cad.engineering_tier}]")
        print(f"  5. [CONTENT CREATION] : {report.content_creation.overall_creator_score:>5.1f} / 100.0  [{report.content_creation.creator_tier}]")
        print(f"  6. [PORTABILITY]      : {report.portability.overall_portability_score:>5.1f} / 100.0  [{report.portability.portability_tier}]")
        print("------------------------------------------------------------------------------------------")
        print(f"  * {report.workload_winner_matrix['Strongest Domain']}")
        print(f"  * {report.workload_winner_matrix['Weakest Domain']}")
        print("==========================================================================================")

        # Detailed Drilldowns for Critical Workloads
        print("\n--- AI / MACHINE LEARNING HARD LIMIT AUDIT ---")
        if report.ai_ml.vram_hard_limit_flag:
            print(f"    [!] HARD LIMIT ALERT : {report.ai_ml.vram_hard_limit_flag}")
        else:
            print(f"    [OK] VRAM Capacity   : {laptop.gpu.vram_gb}GB VRAM accommodates standard academic models.")
        print(f"    - Largest Local LLM  : {report.ai_ml.largest_local_llm_parameter_fit}")
        print(f"    - QLoRA Fine-Tuning  : {'VIABLE' if report.ai_ml.lora_fine_tuning_viable else 'OUT OF MEMORY (FATAL LIMIT)'}")
        print(f"    - Stable Diffusion XL: {'VIABLE' if report.ai_ml.stable_diffusion_sdxl_viable else 'OUT OF MEMORY (FATAL LIMIT)'}")
        for lim in report.ai_ml.hard_limitations:
            print(f"      * {lim}")

        print("\n--- SOFTWARE DEVELOPMENT & CONTAINER HEADROOM ---")
        print(f"    - Container Readiness: {report.software_dev.vm_and_docker_tier}")
        print(f"    - Linux Compatibility: {report.software_dev.linux_compatibility_rating}")
        print(f"    - Build Compilation  : {report.software_dev.code_compilation_speed_rating} ({report.software_dev.score_compilation_multi_thread:.1f} pts)")
        print(f"    - Vertical Code View : {laptop.display.aspect_ratio} Aspect Ratio ({report.software_dev.score_display_vertical_code_view:.1f} pts)")

        print("\n--- CONTENT CREATION & COLOR ACCURACY AUDIT ---")
        print(f"    - Panel Color Status : {report.content_creation.color_accuracy_grade}")
        print(f"    - 4K Video Timeline  : {report.content_creation.video_editing_4k_timeline}")
        print(f"    - Hardware Encoders  : {', '.join(report.content_creation.hardware_encoders_available) if report.content_creation.hardware_encoders_available else 'None'}")

        print("\n--- CAMPUS PORTABILITY & MOBILITY ---")
        print(f"    - True Travel Weight : {report.portability.true_travel_weight_kg} kg (Chassis + Power Supply)")
        print(f"    - Off-Charger Runtime: ~{report.portability.estimated_office_runtime_hours} hours light office use")
        print(f"    - Travel Charging    : {report.portability.usb_c_charging_flexibility}")

        if report.gaming.bottlenecks:
            print("\n--- DETECTED GAMING BOTTLENECKS ---")
            for b in report.gaming.bottlenecks:
                print(f"    [!] {b}")

        # Update SQLite audit scores
        with db.get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM laptops WHERE exact_sku = ?", (laptop.metadata.exact_sku,))
            row = cur.fetchone()
            if row:
                lap_id = row["id"]
                cur.execute("""
                    INSERT INTO audit_scores (
                        laptop_id, overall_score, gaming_score, aiml_score, dev_score,
                        cad_engineering_score, content_creation_score, portability_score,
                        upgradeability_score, value_score, verdict, audit_report_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    lap_id,
                    round((report.gaming.overall_gaming_score + report.software_dev.overall_dev_score) / 2.0, 1),
                    report.gaming.overall_gaming_score,
                    report.ai_ml.overall_aiml_score,
                    report.software_dev.overall_dev_score,
                    report.engineering_cad.overall_engineering_score,
                    report.content_creation.overall_creator_score,
                    report.portability.overall_portability_score,
                    80.0, 75.0,
                    report.gaming.gaming_tier,
                    json.dumps(report.workload_winner_matrix)
                ))
                conn.commit()

    print("\n" + "=" * 90)
    print("               PHASE 5 WORKLOAD AUDIT COMPLETED SUCCESSFULLY               ")
    print("=" * 90)


if __name__ == "__main__":
    run_phase5_test()
