"""
SysPulse Laptop Buyer Audit Engine - Database Module
Provides normalized 3NF SQLite schema initialization, table creation,
and insertion helpers for long-term laptop cataloging.
"""

import sqlite3
from typing import Dict, Any, Optional
import os

SCHEMA_DDL = """
PRAGMA foreign_keys = ON;

-- 1. CPU Silicon Entity (Reusable across laptops)
CREATE TABLE IF NOT EXISTS cpus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manufacturer TEXT NOT NULL,
    exact_model TEXT NOT NULL UNIQUE,
    architecture TEXT NOT NULL,
    generation TEXT,
    process_node_nm REAL,
    total_physical_cores INTEGER NOT NULL,
    p_cores INTEGER DEFAULT 0,
    e_cores INTEGER DEFAULT 0,
    total_threads INTEGER NOT NULL,
    base_clock_ghz REAL NOT NULL,
    boost_clock_ghz REAL NOT NULL,
    l2_cache_mb REAL,
    l3_cache_mb REAL,
    intel_amd_rated_base_power_w REAL,
    intel_amd_rated_max_turbo_w REAL,
    npu_present INTEGER DEFAULT 0,
    npu_tops REAL DEFAULT 0,
    avx2 INTEGER DEFAULT 1,
    avx512 INTEGER DEFAULT 0,
    igpu_model TEXT
);

-- 2. GPU Silicon Entity (Reusable across laptops)
CREATE TABLE IF NOT EXISTS gpus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manufacturer TEXT NOT NULL,
    exact_model TEXT NOT NULL,
    chip_code TEXT,
    architecture TEXT NOT NULL,
    cuda_cores_or_shaders INTEGER NOT NULL,
    tensor_cores INTEGER DEFAULT 0,
    rt_cores INTEGER DEFAULT 0,
    vram_gb REAL NOT NULL,
    vram_type TEXT NOT NULL,
    memory_bus_width_bit INTEGER,
    silicon_max_possible_tgp_w REAL,
    nvenc_generation TEXT,
    av1_encode INTEGER DEFAULT 0,
    cuda_compute_capability TEXT,
    UNIQUE(manufacturer, exact_model, vram_gb)
);

-- 3. Display Panel Entity
CREATE TABLE IF NOT EXISTS displays (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    diagonal_inches REAL NOT NULL,
    aspect_ratio TEXT NOT NULL,
    resolution_horizontal INTEGER NOT NULL,
    resolution_vertical INTEGER NOT NULL,
    refresh_rate_hz INTEGER NOT NULL,
    panel_technology TEXT NOT NULL,
    advertised_brightness_nits REAL NOT NULL,
    srgb_pct REAL,
    dci_p3_pct REAL,
    vrr_technology TEXT,
    surface_finish TEXT
);

-- 4. Cooling Design Entity
CREATE TABLE IF NOT EXISTS cooling_designs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fan_count INTEGER NOT NULL,
    heatpipe_count INTEGER,
    heatpipe_topology TEXT NOT NULL,
    has_vapor_chamber INTEGER DEFAULT 0,
    thermal_interface_material TEXT NOT NULL,
    exhaust_vents_count INTEGER DEFAULT 2
);

-- 5. Main Laptop SKU Entity
CREATE TABLE IF NOT EXISTS laptops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT NOT NULL,
    series TEXT,
    model_name TEXT NOT NULL,
    exact_sku TEXT NOT NULL UNIQUE,
    release_year INTEGER NOT NULL,
    msrp_inr REAL,
    street_price_inr REAL,
    msrp_usd REAL,
    weight_kg REAL,
    thickness_mm REAL,
    cpu_id INTEGER NOT NULL REFERENCES cpus(id),
    gpu_id INTEGER REFERENCES gpus(id),
    display_id INTEGER NOT NULL REFERENCES displays(id),
    cooling_id INTEGER NOT NULL REFERENCES cooling_designs(id),
    
    -- OEM Specific Tuning Limits (Distinguishes laptop implementation from raw silicon)
    oem_pl1_w REAL,
    oem_pl1_status TEXT DEFAULT 'UNKNOWN',
    oem_pl2_w REAL,
    oem_pl2_status TEXT DEFAULT 'UNKNOWN',
    oem_gpu_base_tgp_w REAL,
    oem_gpu_tgp_status TEXT DEFAULT 'UNKNOWN',
    oem_gpu_dynamic_boost_w REAL,
    has_mux_switch INTEGER,
    has_mux_switch_status TEXT DEFAULT 'UNKNOWN',
    advanced_optimus INTEGER,
    
    -- Memory Subsystem
    ram_total_gb INTEGER NOT NULL,
    ram_type TEXT NOT NULL,
    ram_speed_mts INTEGER NOT NULL,
    ram_channels TEXT NOT NULL,
    ram_soldered_gb INTEGER DEFAULT 0,
    ram_sodimm_slots_total INTEGER DEFAULT 2,
    ram_sodimm_slots_occupied INTEGER DEFAULT 2,
    ram_max_capacity_gb INTEGER,
    
    -- Power Envelope
    battery_capacity_wh REAL NOT NULL,
    adapter_rating_w REAL NOT NULL,
    usb_c_pd_supported INTEGER DEFAULT 0,
    
    -- Confidence & Metadata
    overall_confidence REAL DEFAULT 0.0,
    confidence_grade TEXT DEFAULT 'LOW',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Storage Drives per Laptop
CREATE TABLE IF NOT EXISTS laptop_storage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    laptop_id INTEGER NOT NULL REFERENCES laptops(id) ON DELETE CASCADE,
    slot_number INTEGER NOT NULL,
    capacity_gb INTEGER NOT NULL,
    form_factor TEXT NOT NULL,
    interface_type TEXT NOT NULL,
    pcie_generation INTEGER,
    nand_type TEXT,
    has_dram_cache INTEGER,
    sequential_read_mbps REAL,
    sequential_write_mbps REAL
);

-- 7. Verified Hardware Benchmarks
CREATE TABLE IF NOT EXISTS laptop_benchmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    laptop_id INTEGER NOT NULL REFERENCES laptops(id) ON DELETE CASCADE,
    cinebench_r23_single REAL,
    cinebench_r23_multi REAL,
    cinebench_r23_sustained_10min REAL,
    timespy_graphics_score REAL,
    timespy_cpu_score REAL,
    geekbench6_single REAL,
    geekbench6_multi REAL,
    blender_classroom_sec REAL,
    cpu_peak_temp_c REAL,
    cpu_sustained_temp_c REAL,
    gpu_peak_temp_c REAL,
    gpu_sustained_temp_c REAL,
    sustained_performance_loss_pct REAL
);

-- 8. Detected Deal-Breakers
CREATE TABLE IF NOT EXISTS deal_breakers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    laptop_id INTEGER NOT NULL REFERENCES laptops(id) ON DELETE CASCADE,
    severity TEXT NOT NULL, -- FATAL, WARNING, ADVISORY
    category TEXT NOT NULL, -- VRAM, RAM_TOPOLOGY, POWER_DEFICIT, DISPLAY_TRAP, THERMAL_LIMIT
    message TEXT NOT NULL,
    impact TEXT NOT NULL
);

-- 9. Workload Audit Scores
CREATE TABLE IF NOT EXISTS audit_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    laptop_id INTEGER NOT NULL REFERENCES laptops(id) ON DELETE CASCADE,
    overall_score REAL NOT NULL,
    gaming_score REAL NOT NULL,
    aiml_score REAL NOT NULL,
    dev_score REAL NOT NULL,
    cad_engineering_score REAL NOT NULL,
    content_creation_score REAL NOT NULL,
    portability_score REAL NOT NULL,
    upgradeability_score REAL NOT NULL,
    value_score REAL NOT NULL,
    verdict TEXT NOT NULL,
    audit_report_json TEXT
);

-- Indexes for lightning fast queries across large catalogs
CREATE INDEX IF NOT EXISTS idx_laptop_sku ON laptops(exact_sku);
CREATE INDEX IF NOT EXISTS idx_laptop_cpu ON laptops(cpu_id);
CREATE INDEX IF NOT EXISTS idx_laptop_gpu ON laptops(gpu_id);
CREATE INDEX IF NOT EXISTS idx_cpu_model ON cpus(exact_model);
CREATE INDEX IF NOT EXISTS idx_gpu_model ON gpus(exact_model);
"""


class DatabaseManager:
    def __init__(self, db_path: str = "syspulse_audit.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self) -> None:
        with self.get_connection() as conn:
            conn.executescript(SCHEMA_DDL)

    def get_or_create_cpu(self, conn: sqlite3.Connection, cpu_data: Dict[str, Any]) -> int:
        cur = conn.cursor()
        cur.execute("SELECT id FROM cpus WHERE exact_model = ?", (cpu_data["exact_model"],))
        row = cur.fetchone()
        if row:
            return row["id"]
        cur.execute("""
            INSERT INTO cpus (
                manufacturer, exact_model, architecture, generation, process_node_nm,
                total_physical_cores, p_cores, e_cores, total_threads, base_clock_ghz,
                boost_clock_ghz, l2_cache_mb, l3_cache_mb, intel_amd_rated_base_power_w,
                intel_amd_rated_max_turbo_w, npu_present, npu_tops, avx2, avx512, igpu_model
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cpu_data.get("manufacturer", "Unknown"),
            cpu_data["exact_model"],
            cpu_data.get("architecture", "Unknown"),
            cpu_data.get("generation"),
            cpu_data.get("process_node_nm"),
            cpu_data.get("total_physical_cores", 0),
            cpu_data.get("performance_cores", 0),
            cpu_data.get("efficiency_cores", 0),
            cpu_data.get("total_threads", 0),
            cpu_data.get("base_clock_ghz", 0.0),
            cpu_data.get("boost_clock_ghz", 0.0),
            cpu_data.get("cache", {}).get("l2_total_mb"),
            cpu_data.get("cache", {}).get("l3_total_mb"),
            cpu_data.get("intel_or_amd_spec_base_power_w", 45.0),
            cpu_data.get("intel_or_amd_spec_max_turbo_w", 115.0),
            1 if cpu_data.get("npu_present") else 0,
            cpu_data.get("npu_tops", {}).get("value") if isinstance(cpu_data.get("npu_tops"), dict) else 0,
            1 if cpu_data.get("instruction_extensions", {}).get("avx2", True) else 0,
            1 if cpu_data.get("instruction_extensions", {}).get("avx512", False) else 0,
            cpu_data.get("igpu_model", "Unknown")
        ))
        return cur.lastrowid

    def get_or_create_gpu(self, conn: sqlite3.Connection, gpu_data: Dict[str, Any]) -> Optional[int]:
        if not gpu_data.get("is_discrete", False):
            return None
        cur = conn.cursor()
        cur.execute("SELECT id FROM gpus WHERE exact_model = ? AND vram_gb = ?", 
                    (gpu_data["exact_model"], gpu_data.get("vram_gb", 0)))
        row = cur.fetchone()
        if row:
            return row["id"]
        cur.execute("""
            INSERT INTO gpus (
                manufacturer, exact_model, chip_code, architecture,
                cuda_cores_or_shaders, tensor_cores, rt_cores, vram_gb,
                vram_type, memory_bus_width_bit, silicon_max_possible_tgp_w,
                cuda_compute_capability
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            gpu_data.get("manufacturer", "NVIDIA"),
            gpu_data["exact_model"],
            gpu_data.get("chip_code", ""),
            gpu_data.get("architecture", "Unknown"),
            gpu_data.get("cuda_cores_or_stream_processors", 0),
            gpu_data.get("tensor_cores", 0),
            gpu_data.get("rt_cores", 0),
            gpu_data.get("vram_gb", 0),
            gpu_data.get("vram_type", "GDDR6"),
            gpu_data.get("memory_bus_width_bit", {}).get("value") if isinstance(gpu_data.get("memory_bus_width_bit"), dict) else None,
            gpu_data.get("silicon_max_possible_tgp_w", 140.0),
            gpu_data.get("cuda_compute_capability", "")
        ))
        return cur.lastrowid
