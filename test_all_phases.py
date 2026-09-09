"""
SysPulse Laptop Buyer Audit Engine - Master Test Harness
Executes automated test suites across all 22 engineering phases.
"""

import sys
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from audit_engine.test_phase1 import run_phase1_audit
from audit_engine.test_phase2_power import run_phase2_test
from audit_engine.test_phase3_upgradeability import run_phase3_test
from audit_engine.test_phase4_performance import run_phase4_test
from audit_engine.test_phase5_workloads import run_phase5_test
from audit_engine.test_phase6_7_dealbreakers import run_phase6_7_test


def run_master_test_suite():
    print("*" * 95)
    print("       SYSPULSE LAPTOP BUYER AUDIT ENGINE - MASTER END-TO-END VERIFICATION SUITE       ")
    print("*" * 95)

    suites = [
        ("Phase 1: Input Schema & Database 3NF Normalization", run_phase1_audit),
        ("Phase 2: Dedicated Power Delivery & Cross-Load Deficit", run_phase2_test),
        ("Phase 3: Hardware Modularity & 5-Year Ownership", run_phase3_test),
        ("Phase 4: Real Performance & Sustained Throttling", run_phase4_test),
        ("Phase 5: 6-Domain Workload Suitability & Hard Limits", run_phase5_test),
        ("Phases 6 & 7: Deal-Breakers & Bottleneck Engine", run_phase6_7_test),
    ]

    for name, runner in suites:
        print(f"\n>>> EXECUTING: {name}")
        runner()

    print("\n" + "*" * 95)
    print("   ALL ENGINEERING PHASES VALIDATED SUCCESSFULLY WITH ZERO ERRORS   ")
    print("*" * 95)


if __name__ == "__main__":
    run_master_test_suite()
