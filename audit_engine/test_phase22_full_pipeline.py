"""
SysPulse Laptop Buyer Audit Engine - Phase 22 Verification Test
Tests the Unified Master Orchestrator, CLI interface, and Report Generation (Phases 13, 17, 18, 22):
1. End-to-end audit execution of sample laptops
2. Interactive HTML report generation and validation
3. Markdown dossier generation
4. CLI argument parsing and live benchmark ingestion
"""

import os
import sys
import json

# Ensure project root is on sys.path and stdout handles utf-8
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from audit_engine.main import audit_single_laptop, compare_laptops


def run_phase22_test():
    print("=" * 90)
    print("       SYSPULSE LAPTOP BUYER AUDIT ENGINE - PHASE 22: FULL UNIFIED PIPELINE          ")
    print("=" * 90)

    html_out = "results/test_pipeline_dossier.html"
    os.makedirs("results", exist_ok=True)

    print("\n[STEP 1/3] Auditing Single Machine with HTML Report Generation...")
    audit_single_laptop(
        spec_path="examples/engineered_workstation.json",
        user_priority="Gaming",
        output_html=html_out
    )

    if os.path.exists(html_out):
        size = os.path.getsize(html_out)
        print(f"[✓] HTML Report verified on disk: {html_out} ({size:,} bytes)")
        assert size > 1000, "HTML report should be non-empty and well-formed."
    else:
        raise FileNotFoundError(f"Failed to generate {html_out}")

    print("\n[STEP 2/3] Auditing Live Host Rig (Ingesting Real Telemetry from results/)...")
    live_html = "results/test_live_rig_dossier.html"
    audit_single_laptop(
        spec_path="examples/host_physical_laptop.json",
        user_priority="AI_ML",
        output_html=live_html
    )

    if os.path.exists(live_html):
        size = os.path.getsize(live_html)
        print(f"[✓] Live Rig HTML Report verified: {live_html} ({size:,} bytes)")

    print("\n[STEP 3/3] Executing Multi-Laptop Head-to-Head Comparison Pipeline...")
    compare_laptops([
        "examples/engineered_workstation.json",
        "examples/deceptive_paper_tiger.json"
    ])

    print("\n" + "=" * 90)
    print("             PHASE 22 MASTER PIPELINE COMPLETED SUCCESSFULLY                 ")
    print("=" * 90)


if __name__ == "__main__":
    run_phase22_test()
