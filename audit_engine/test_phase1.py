"""
SysPulse Laptop Buyer Audit Engine - Phase 1 Verification Test
Loads both the Deceptive Paper Tiger and Engineered Workstation specs,
validates them against the schema, populates SQLite 3NF tables,
and executes the audit inspection.
"""

import os
import sys
import json

# Ensure project root is on sys.path and stdout handles utf-8
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from audit_engine.validator import SpecificationValidator
from audit_engine.db import DatabaseManager


def run_phase1_audit():
    print("=" * 80)
    print("       SYSPULSE LAPTOP BUYER AUDIT ENGINE - PHASE 1 VERIFICATION TEST       ")
    print("=" * 80)

    # 1. Initialize SQLite Database
    db_path = "syspulse_audit.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    db = DatabaseManager(db_path)
    print(f"[*] Initialized SQLite 3NF Relational Database: '{db_path}'")

    test_files = [
        ("DECEPTIVE PAPER TIGER LAPTOP", "examples/deceptive_paper_tiger.json"),
        ("PROPERLY ENGINEERED WORKSTATION", "examples/engineered_workstation.json")
    ]

    for label, filepath in test_files:
        print("\n" + "#" * 80)
        print(f"  AUDITING SPECIFICATION: {label}")
        print(f"  Source File: {filepath}")
        print("#" * 80)

        with open(filepath, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        # 2. Validate and Parse
        laptop, warnings = SpecificationValidator.validate_and_load(raw_data)
        confidence_report = laptop.calculate_audit_confidence()

        print(f"\n[+] Laptop Model: {laptop.metadata.brand} {laptop.metadata.model_name} ({laptop.metadata.exact_sku})")
        print(f"    Advertised Headline: \"{laptop.metadata.marketing_headline}\"")
        print(f"    Pricing: Rs {laptop.metadata.street_price_inr:,.0f} ($ {laptop.metadata.msrp_usd:,.0f})")

        print("\n--- SUBSYSTEM AUDIT STATUS & HARDWARE CONFIDENCE ---")
        print(f"    Overall Confidence: {confidence_report['overall_confidence'] * 100:.1f}% [{confidence_report['confidence_grade']}]")
        for sub, conf in confidence_report["subsystem_confidence"].items():
            print(f"    - {sub:<12}: {conf * 100:>5.1f}% confidence")

        print("\n--- SILICON VS. OEM CONFIGURATION AUDIT ---")
        print(f"    CPU Silicon       : {laptop.cpu.manufacturer} {laptop.cpu.exact_model} ({laptop.cpu.total_physical_cores}C / {laptop.cpu.total_threads}T)")
        print(f"    CPU Base / Boost  : {laptop.cpu.base_clock_ghz} GHz / {laptop.cpu.boost_clock_ghz} GHz")
        print(f"    OEM PL1 / PL2     : {laptop.cpu.oem_pl1_w.value}W / {laptop.cpu.oem_pl2_w.value}W")
        print(f"    GPU Silicon       : {laptop.gpu.manufacturer} {laptop.gpu.exact_model} ({laptop.gpu.cuda_cores_or_shaders} CUDA Cores)")
        print(f"    VRAM Subsystem    : {laptop.gpu.vram_gb}GB {laptop.gpu.vram_type} ({laptop.gpu.memory_bus_width_bit.value}-bit)")
        print(f"    Silicon Max TGP   : {laptop.gpu.silicon_max_possible_tgp_w}W")
        print(f"    OEM Configured TGP: {laptop.gpu.oem_base_tgp_w.value}W (Boost: +{laptop.gpu.oem_dynamic_boost_w.value}W)")
        print(f"    MUX Switch Present: {laptop.gpu.has_mux_switch.value}")
        print(f"    RAM Configuration : {laptop.memory.total_capacity_gb}GB {laptop.memory.ram_type}-{laptop.memory.speed_mts} MT/s ({laptop.memory.channel_configuration})")
        print(f"    RAM Topology      : {laptop.memory.soldered_capacity_gb}GB Soldered | {laptop.memory.sodimm_slots_total} SODIMM slots ({laptop.memory.sodimm_slots_occupied} occupied)")
        print(f"    Display Matrix    : {laptop.display.resolution_horizontal}x{laptop.display.resolution_vertical} @ {laptop.display.refresh_rate_hz}Hz ({laptop.display.panel_technology})")
        print(f"    Color Gamut / GTG : {laptop.display.color_gamut_srgb_pct.value}% sRGB | {laptop.display.response_time_gtg_ms.value}ms GTG")
        print(f"    Cooling Topology  : {laptop.cooling.fan_count} Fans | {laptop.cooling.heatpipe_topology} | Vapor Chamber: {laptop.cooling.has_vapor_chamber}")
        print(f"    Power Envelope    : {laptop.power.adapter_rating_w}W Adapter | {laptop.power.battery_capacity_wh}Wh Battery")

        print("\n--- PRE-AUDIT SANITY CHECKS & ANTI-MARKETING WARNINGS ---")
        if warnings:
            for i, w in enumerate(warnings, 1):
                print(f"    [!] WARNING {i}: {w}")
        else:
            print("    [OK] No fatal configuration traps detected in baseline specification.")

        # 3. Store into SQLite Database
        with db.get_connection() as conn:
            cpu_id = db.get_or_create_cpu(conn, raw_data["cpu"])
            gpu_id = db.get_or_create_gpu(conn, raw_data["gpu"])
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO displays (
                    diagonal_inches, aspect_ratio, resolution_horizontal, resolution_vertical,
                    refresh_rate_hz, panel_technology, advertised_brightness_nits, srgb_pct,
                    dci_p3_pct, vrr_technology, surface_finish
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                laptop.display.diagonal_inches, laptop.display.aspect_ratio,
                laptop.display.resolution_horizontal, laptop.display.resolution_vertical,
                laptop.display.refresh_rate_hz, laptop.display.panel_technology,
                laptop.display.advertised_brightness_nits, laptop.display.color_gamut_srgb_pct.value,
                laptop.display.color_gamut_dci_p3_pct.value, laptop.display.vrr_technology,
                laptop.display.surface_finish
            ))
            disp_id = cur.lastrowid

            cur.execute("""
                INSERT INTO cooling_designs (
                    fan_count, heatpipe_count, heatpipe_topology, has_vapor_chamber,
                    thermal_interface_material, exhaust_vents_count
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                laptop.cooling.fan_count, laptop.cooling.heatpipe_count.value,
                laptop.cooling.heatpipe_topology, 1 if laptop.cooling.has_vapor_chamber else 0,
                laptop.cooling.thermal_interface_material, laptop.cooling.exhaust_vents_count
            ))
            cool_id = cur.lastrowid

            cur.execute("""
                INSERT INTO laptops (
                    brand, series, model_name, exact_sku, release_year, msrp_inr,
                    street_price_inr, msrp_usd, weight_kg, thickness_mm, cpu_id, gpu_id,
                    display_id, cooling_id, oem_pl1_w, oem_pl2_w, oem_gpu_base_tgp_w,
                    oem_gpu_dynamic_boost_w, has_mux_switch, advanced_optimus,
                    ram_total_gb, ram_type, ram_speed_mts, ram_channels, ram_soldered_gb,
                    ram_sodimm_slots_total, ram_sodimm_slots_occupied, ram_max_capacity_gb,
                    battery_capacity_wh, adapter_rating_w, usb_c_pd_supported,
                    overall_confidence, confidence_grade
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                laptop.metadata.brand, laptop.metadata.series, laptop.metadata.model_name,
                laptop.metadata.exact_sku, laptop.metadata.release_year, laptop.metadata.msrp_inr,
                laptop.metadata.street_price_inr, laptop.metadata.msrp_usd, laptop.chassis.weight_kg.value,
                laptop.chassis.thickness_mm.value, cpu_id, gpu_id, disp_id, cool_id,
                laptop.cpu.oem_pl1_w.value, laptop.cpu.oem_pl2_w.value,
                laptop.gpu.oem_base_tgp_w.value, laptop.gpu.oem_dynamic_boost_w.value,
                1 if laptop.gpu.has_mux_switch.value else 0,
                1 if laptop.gpu.advanced_optimus.value else 0,
                laptop.memory.total_capacity_gb, laptop.memory.ram_type, laptop.memory.speed_mts,
                laptop.memory.channel_configuration, laptop.memory.soldered_capacity_gb,
                laptop.memory.sodimm_slots_total, laptop.memory.sodimm_slots_occupied,
                laptop.memory.max_supported_capacity_gb, laptop.power.battery_capacity_wh,
                laptop.power.adapter_rating_w, 1 if laptop.power.usb_c_pd_charging_supported else 0,
                confidence_report["overall_confidence"], confidence_report["confidence_grade"]
            ))
            laptop_db_id = cur.lastrowid
            conn.commit()
            print(f"\n[OK] Successfully cataloged into SQLite Database under Laptop ID: {laptop_db_id}")

    print("\n" + "=" * 80)
    print("       PHASE 1 VERIFICATION & HARDWARE AUDIT COMPLETED SUCCESSFULLY       ")
    print("=" * 80)


if __name__ == "__main__":
    run_phase1_audit()
