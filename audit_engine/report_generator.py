"""
SysPulse Laptop Buyer Audit Engine - Phase 13 & Phase 18:
Professional Audit Report Generator
Produces:
1. Executive Markdown Dossier
2. Machine-Readable JSON Audit Record
3. Self-Contained Interactive HTML Report with Rich Aesthetics & Explainable "WHY?" Trees
"""

import os
import json
from typing import Dict, Any, List, Optional
from audit_engine.models import LaptopSpecification
from audit_engine.power_analyzer import PowerAnalysisResult
from audit_engine.upgradeability import UpgradeabilityAuditResult
from audit_engine.performance_engine import PerformanceAuditResult
from audit_engine.workload_engine import MasterWorkloadAuditReport
from audit_engine.dealbreaker_engine import DealBreakerAndBottleneckReport
from audit_engine.value_engine import ValueAuditResult
from audit_engine.anti_marketing import AntiMarketingReport
from audit_engine.future_proofing import FutureProofingReport, FinalTailoredVerdict


class ReportGenerator:
    """
    Renders professional audit dossiers with transparent deductions and zero black-box scoring.
    """

    @classmethod
    def generate_markdown(
        cls,
        laptop: LaptopSpecification,
        power: PowerAnalysisResult,
        upgrade: UpgradeabilityAuditResult,
        perf: PerformanceAuditResult,
        workload: MasterWorkloadAuditReport,
        dealbreakers: DealBreakerAndBottleneckReport,
        value: ValueAuditResult,
        marketing: AntiMarketingReport,
        future: FutureProofingReport,
        verdict: FinalTailoredVerdict
    ) -> str:
        md = []
        md.append("=" * 80)
        md.append(f"# LAPTOP BUYER AUDIT DOSSIER: {laptop.metadata.brand} {laptop.metadata.model_name}")
        md.append(f"**Exact SKU:** `{laptop.metadata.exact_sku}` | **Release Year:** {laptop.metadata.release_year}")
        md.append(f"**Street Price:** Rs {laptop.metadata.street_price_inr:,.0f} ($ {laptop.metadata.msrp_usd:,.0f})")
        md.append(f"**Headline Claim:** *\"{laptop.metadata.marketing_headline}\"*")
        md.append("=" * 80)
        md.append("")

        md.append("## 1. EXECUTIVE VERDICT")
        md.append(f"### Final Verdict: **{verdict.verdict}** (User Priority: {verdict.user_primary_priority})")
        md.append(f"- **Target Domain Score:** {verdict.priority_score:.1f} / 100.0")
        md.append(f"- **Overall Hardware Capability:** {verdict.overall_hardware_score:.1f} / 100.0")
        md.append(f"- **Primary Reason:** {verdict.primary_reason}")
        md.append(f"- **Buying Advice:** {verdict.tailored_buying_advice}")
        md.append(f"- **Alternative Recommendation:** {verdict.alternative_suggestion}")
        md.append("")

        md.append("## 2. DOMAIN SUITABILITY SCORECARD")
        md.append("| Workload Domain | Score | Status / Tier | Why? (Key Architectural Factor) |")
        md.append("| :--- | :---: | :--- | :--- |")
        md.append(f"| **Modern Gaming** | **{workload.gaming.overall_gaming_score:.1f}/100** | {workload.gaming.gaming_tier} | TGP: {laptop.gpu.oem_base_tgp_w.value or '?'}W; MUX: {laptop.gpu.has_mux_switch.value}; VRAM: {laptop.gpu.vram_gb}GB |")
        md.append(f"| **AI / Machine Learning** | **{workload.ai_ml.overall_aiml_score:.1f}/100** | {workload.ai_ml.aiml_tier} | Fit: {workload.ai_ml.largest_local_llm_parameter_fit} |")
        md.append(f"| **Software Development** | **{workload.software_dev.overall_dev_score:.1f}/100** | {workload.software_dev.dev_tier} | {laptop.memory.total_capacity_gb}GB RAM ({laptop.memory.channel_configuration}); {laptop.cpu.total_threads} Threads |")
        md.append(f"| **Engineering / CAD** | **{workload.engineering_cad.overall_engineering_score:.1f}/100** | {workload.engineering_cad.engineering_tier} | Single-core boost: {laptop.cpu.boost_clock_ghz} GHz; AVX-512: {laptop.cpu.avx512} |")
        md.append(f"| **Content Creation** | **{workload.content_creation.overall_creator_score:.1f}/100** | {workload.content_creation.creator_tier} | Gamut: {laptop.display.color_gamut_srgb_pct.value or '?'}% sRGB; NVENC: {laptop.gpu.nvenc_generation or 'Yes'} |")
        port_wt = round((laptop.chassis.weight_kg.value or 2.3) + 0.5, 1)
        md.append(f"| **Campus Portability** | **{workload.portability.overall_portability_score:.1f}/100** | {workload.portability.portability_tier} | Travel Wt: {port_wt} kg; {laptop.power.battery_capacity_wh}Wh |")
        md.append(f"| **Modular Upgradeability** | **{upgrade.upgradeability_score:.1f}/100** | {upgrade.ram_modular_state} | SODIMM slots: {laptop.memory.sodimm_slots_total}; M.2 slots: {laptop.storage.m2_slots_total} |")
        md.append(f"| **5-Year Ownership** | **{upgrade.long_term_ownership_score:.1f}/100** | {upgrade.longevity_rating} | Lifespan: ~{upgrade.projected_functional_lifespan_years} Years |")
        md.append(f"| **Value for Money** | **{value.value_score_100:.1f}/100** | {value.value_rating} | {value.price_to_capability_index} capability pts per 10k INR |")
        md.append("")

        md.append("## 3. HARD DEAL-BREAKERS & TRAPS")
        if dealbreakers.dealbreakers:
            for i, d in enumerate(dealbreakers.dealbreakers, 1):
                md.append(f"### {i}. [{d.severity}] {d.title}")
                md.append(f"- **Subsystem:** {d.subsystem}")
                md.append(f"- **Impacted Workloads:** {', '.join(d.affected_workloads)}")
                md.append(f"- **Engineering Reality:** {d.description}")
                md.append(f"- **Action / Fix:** {d.remediation_or_alternative}")
                md.append("")
        else:
            md.append("- *No fatal hardware deal-breakers or configuration traps detected.*")
            md.append("")

        md.append("## 4. HARDWARE BOTTLENECK ANALYSIS")
        if dealbreakers.bottlenecks:
            for i, b in enumerate(dealbreakers.bottlenecks, 1):
                md.append(f"- **Bottleneck #{i}:** `{b.subsystem_affected}` constrained by `{b.constraining_component}` (~{b.estimated_performance_loss_pct:.1f}% throughput loss)")
                md.append(f"  * *Mechanism:* {b.mechanism}")
        else:
            md.append("- *Balanced hardware synergy. No severe bottlenecks detected.*")
        md.append("")

        md.append("## 5. ANTI-MARKETING AUDIT")
        md.append(f"**Marketing Honesty Score: {marketing.marketing_honesty_score:.1f} / 100.0** — {marketing.executive_summary}")
        for c in marketing.claims:
            md.append(f"- **Claim:** \"{c.claim_phrase}\" -> **[{c.audit_verdict}]**")
            md.append(f"  * *Hardware Reality:* {c.physical_hardware_reality}")
            md.append(f"  * *Explanation:* {c.engineering_explanation}")
        md.append("")

        md.append("## 6. FUTURE-PROOFING PROJECTION")
        md.append(f"- **1-Year Outlook:** {future.horizon_1_year.viability_rating} ({future.horizon_1_year.bottleneck_projection})")
        md.append(f"- **3-Year Outlook:** {future.horizon_3_year.viability_rating} ({future.horizon_3_year.bottleneck_projection})")
        md.append(f"- **5-Year Outlook:** {future.horizon_5_year.viability_rating} ({future.horizon_5_year.bottleneck_projection})")
        md.append(f"- **Summary:** {future.summary}")
        md.append("")

        md.append("=" * 80)
        md.append("*Generated by SysPulse Laptop Buyer Audit Engine v1.1.0 — Zero Marketing Bias.*")
        md.append("=" * 80)

        return "\n".join(md)

    @classmethod
    def generate_html(
        cls,
        output_filepath: str,
        laptop: LaptopSpecification,
        power: PowerAnalysisResult,
        upgrade: UpgradeabilityAuditResult,
        perf: PerformanceAuditResult,
        workload: MasterWorkloadAuditReport,
        dealbreakers: DealBreakerAndBottleneckReport,
        value: ValueAuditResult,
        marketing: AntiMarketingReport,
        future: FutureProofingReport,
        verdict: FinalTailoredVerdict
    ) -> None:
        """
        Generates a visually stunning, responsive, dark-mode, zero-external-dependency HTML report.
        """
        # Color badge helper
        def score_color(s: float) -> str:
            if s >= 80:
                return "#10b981" # green
            if s >= 60:
                return "#3b82f6" # blue
            if s >= 45:
                return "#f59e0b" # amber
            return "#ef4444"    # red

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SysPulse Laptop Buyer Audit - {laptop.metadata.brand} {laptop.metadata.model_name}</title>
<style>
  :root {{
    --bg-primary: #0a0e17;
    --bg-secondary: #131b2e;
    --bg-card: #1c2640;
    --accent-cyan: #06b6d4;
    --accent-blue: #3b82f6;
    --accent-green: #10b981;
    --accent-red: #ef4444;
    --accent-amber: #f59e0b;
    --text-main: #f1f5f9;
    --text-muted: #94a3b8;
    --border: #2e3d63;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background: var(--bg-primary);
    color: var(--text-main);
    line-height: 1.6;
    padding: 24px;
  }}
  .container {{ max-width: 1200px; margin: 0 auto; }}
  .header {{
    background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-card) 100%);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
  }}
  .header h1 {{ font-size: 24px; font-weight: 700; color: #fff; }}
  .header .sku {{ color: var(--accent-cyan); font-family: monospace; font-size: 14px; margin-top: 4px; }}
  .header .headline {{ color: var(--text-muted); font-style: italic; font-size: 14px; margin-top: 6px; }}
  .price-badge {{
    background: rgba(6, 182, 212, 0.1);
    border: 1px solid var(--accent-cyan);
    color: var(--accent-cyan);
    padding: 12px 20px;
    border-radius: 8px;
    text-align: right;
  }}
  .price-badge .amount {{ font-size: 24px; font-weight: 800; }}
  .verdict-banner {{
    background: {score_color(verdict.priority_score)}22;
    border-left: 6px solid {score_color(verdict.priority_score)};
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 24px;
  }}
  .verdict-banner h2 {{ font-size: 20px; color: {score_color(verdict.priority_score)}; margin-bottom: 8px; }}
  .grid-3 {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 20px;
    margin-bottom: 24px;
  }}
  .card {{
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px;
  }}
  .card h3 {{
    font-size: 16px;
    color: var(--accent-cyan);
    margin-bottom: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }}
  .score-bar-bg {{
    background: #0a0e17;
    height: 8px;
    border-radius: 4px;
    overflow: hidden;
    margin: 8px 0 16px 0;
  }}
  .score-bar-fill {{ height: 100%; border-radius: 4px; }}
  .metric-row {{
    display: flex;
    justify-content: space-between;
    font-size: 13px;
    padding: 6px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }}
  .metric-row:last-child {{ border-bottom: none; }}
  .metric-label {{ color: var(--text-muted); }}
  .metric-val {{ font-weight: 600; text-align: right; }}
  .dealbreaker-card {{
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 8px;
    padding: 14px;
    margin-bottom: 12px;
  }}
  .dealbreaker-title {{
    color: var(--accent-red);
    font-weight: 700;
    font-size: 14px;
    margin-bottom: 4px;
  }}
  .dealbreaker-desc {{ font-size: 13px; color: #cbd5e1; line-height: 1.4; }}
  .remediation {{ color: var(--accent-amber); font-size: 12px; margin-top: 6px; }}
  .tag {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
  }}
  .tag-fatal {{ background: var(--accent-red); color: #fff; }}
  .tag-warn {{ background: var(--accent-amber); color: #000; }}
  .tag-pass {{ background: var(--accent-green); color: #fff; }}
  .footer {{
    text-align: center;
    color: var(--text-muted);
    font-size: 12px;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid var(--border);
  }}
</style>
</head>
<body>
<div class="container">

  <!-- Header -->
  <div class="header">
    <div>
      <h1>{laptop.metadata.brand} {laptop.metadata.model_name}</h1>
      <div class="sku">SKU: {laptop.metadata.exact_sku} | Architecture: {laptop.cpu.architecture}</div>
      <div class="headline">"{laptop.metadata.marketing_headline}"</div>
    </div>
    <div class="price-badge">
      <div class="amount">Rs {laptop.metadata.street_price_inr:,.0f}</div>
      <div style="font-size: 12px;">$ {laptop.metadata.msrp_usd:,.0f} MSRP</div>
    </div>
  </div>

  <!-- Final Tailored Verdict Banner -->
  <div class="verdict-banner">
    <h2>FINAL VERDICT: {verdict.verdict} (Optimized for: {verdict.user_primary_priority})</h2>
    <p><strong>Primary Finding:</strong> {verdict.primary_reason}</p>
    <p style="margin-top: 6px;"><strong>Buying Advice:</strong> {verdict.tailored_buying_advice}</p>
    <p style="margin-top: 4px; color: var(--text-muted);"><strong>Alternative Route:</strong> {verdict.alternative_suggestion}</p>
  </div>

  <!-- Domain Scores Grid -->
  <div class="grid-3">
    <!-- Gaming -->
    <div class="card">
      <h3>
        <span>Modern Gaming</span>
        <span style="color: {score_color(workload.gaming.overall_gaming_score)}">{workload.gaming.overall_gaming_score:.1f} / 100</span>
      </h3>
      <div class="score-bar-bg">
        <div class="score-bar-fill" style="width: {workload.gaming.overall_gaming_score}%; background: {score_color(workload.gaming.overall_gaming_score)}"></div>
      </div>
      <div class="metric-row"><span class="metric-label">Target Tier</span><span class="metric-val">{workload.gaming.gaming_tier}</span></div>
      <div class="metric-row"><span class="metric-label">GPU Silicon</span><span class="metric-val">{laptop.gpu.exact_model}</span></div>
      <div class="metric-row"><span class="metric-label">Configured TGP</span><span class="metric-val">{laptop.gpu.oem_base_tgp_w.value or '?'}W ({laptop.gpu.silicon_max_possible_tgp_w}W max)</span></div>
      <div class="metric-row"><span class="metric-label">Dedicated VRAM</span><span class="metric-val">{laptop.gpu.vram_gb} GB</span></div>
      <div class="metric-row"><span class="metric-label">Display & MUX</span><span class="metric-val">{laptop.display.refresh_rate_hz}Hz | MUX: {laptop.gpu.has_mux_switch.value}</span></div>
    </div>

    <!-- AI / ML -->
    <div class="card">
      <h3>
        <span>AI & Local LLMs</span>
        <span style="color: {score_color(workload.ai_ml.overall_aiml_score)}">{workload.ai_ml.overall_aiml_score:.1f} / 100</span>
      </h3>
      <div class="score-bar-bg">
        <div class="score-bar-fill" style="width: {workload.ai_ml.overall_aiml_score}%; background: {score_color(workload.ai_ml.overall_aiml_score)}"></div>
      </div>
      <div class="metric-row"><span class="metric-label">Model Ceiling</span><span class="metric-val">{workload.ai_ml.largest_local_llm_parameter_fit}</span></div>
      <div class="metric-row"><span class="metric-label">QLoRA Fine-Tuning</span><span class="metric-val">{'Viable' if workload.ai_ml.lora_fine_tuning_viable else 'OOM Blocker'}</span></div>
      <div class="metric-row"><span class="metric-label">SDXL Image Gen</span><span class="metric-val">{'Viable' if workload.ai_ml.stable_diffusion_sdxl_viable else 'OOM Blocker'}</span></div>
      <div class="metric-row"><span class="metric-label">CUDA Cores & Tensor</span><span class="metric-val">{laptop.gpu.cuda_cores_or_shaders} Cores / {laptop.gpu.tensor_cores} Tensors</span></div>
    </div>

    <!-- Software Development -->
    <div class="card">
      <h3>
        <span>Software Development</span>
        <span style="color: {score_color(workload.software_dev.overall_dev_score)}">{workload.software_dev.overall_dev_score:.1f} / 100</span>
      </h3>
      <div class="score-bar-bg">
        <div class="score-bar-fill" style="width: {workload.software_dev.overall_dev_score}%; background: {score_color(workload.software_dev.overall_dev_score)}"></div>
      </div>
      <div class="metric-row"><span class="metric-label">Build Compilation</span><span class="metric-val">{workload.software_dev.code_compilation_speed_rating}</span></div>
      <div class="metric-row"><span class="metric-label">RAM Topology</span><span class="metric-val">{laptop.memory.total_capacity_gb}GB ({laptop.memory.channel_configuration})</span></div>
      <div class="metric-row"><span class="metric-label">Container Headroom</span><span class="metric-val">{workload.software_dev.vm_and_docker_tier}</span></div>
      <div class="metric-row"><span class="metric-label">Code Aspect Ratio</span><span class="metric-val">{laptop.display.aspect_ratio} Canvas</span></div>
    </div>

    <!-- Engineering / CAD -->
    <div class="card">
      <h3>
        <span>Engineering & CAD</span>
        <span style="color: {score_color(workload.engineering_cad.overall_engineering_score)}">{workload.engineering_cad.overall_engineering_score:.1f} / 100</span>
      </h3>
      <div class="score-bar-bg">
        <div class="score-bar-fill" style="width: {workload.engineering_cad.overall_engineering_score}%; background: {score_color(workload.engineering_cad.overall_engineering_score)}"></div>
      </div>
      <div class="metric-row"><span class="metric-label">SolidWorks Viewport</span><span class="metric-val">{workload.engineering_cad.solidworks_cad_rating}</span></div>
      <div class="metric-row"><span class="metric-label">FEA / CFD Solvers</span><span class="metric-val">{workload.engineering_cad.fea_cfd_simulation_rating}</span></div>
      <div class="metric-row"><span class="metric-label">AVX-512 Matrix</span><span class="metric-val">{'Active (+15%)' if laptop.cpu.avx512 else 'AVX2 Only'}</span></div>
      <div class="metric-row"><span class="metric-label">Cooling Dissipation</span><span class="metric-val">{laptop.cooling.rated_thermal_dissipation_watts.value or '?'}W Envelope</span></div>
    </div>

    <!-- Content Creation -->
    <div class="card">
      <h3>
        <span>Content Creation</span>
        <span style="color: {score_color(workload.content_creation.overall_creator_score)}">{workload.content_creation.overall_creator_score:.1f} / 100</span>
      </h3>
      <div class="score-bar-bg">
        <div class="score-bar-fill" style="width: {workload.content_creation.overall_creator_score}%; background: {score_color(workload.content_creation.overall_creator_score)}"></div>
      </div>
      <div class="metric-row"><span class="metric-label">Panel Color Status</span><span class="metric-val">{workload.content_creation.color_accuracy_grade}</span></div>
      <div class="metric-row"><span class="metric-label">Gamut Coverage</span><span class="metric-val">{laptop.display.color_gamut_srgb_pct.value or '?'}% sRGB / {laptop.display.color_gamut_dci_p3_pct.value or '?'}% P3</span></div>
      <div class="metric-row"><span class="metric-label">4K Video Timeline</span><span class="metric-val">{workload.content_creation.video_editing_4k_timeline}</span></div>
      <div class="metric-row"><span class="metric-label">Hardware Encoders</span><span class="metric-val">{', '.join(workload.content_creation.hardware_encoders_available) if workload.content_creation.hardware_encoders_available else 'None'}</span></div>
    </div>

    <!-- Upgradeability & Ownership -->
    <div class="card">
      <h3>
        <span>Upgrade & Ownership</span>
        <span style="color: {score_color(upgrade.long_term_ownership_score)}">{upgrade.long_term_ownership_score:.1f} / 100</span>
      </h3>
      <div class="score-bar-bg">
        <div class="score-bar-fill" style="width: {upgrade.long_term_ownership_score}%; background: {score_color(upgrade.long_term_ownership_score)}"></div>
      </div>
      <div class="metric-row"><span class="metric-label">Projected Lifespan</span><span class="metric-val">~{upgrade.projected_functional_lifespan_years} Years ({upgrade.longevity_rating})</span></div>
      <div class="metric-row"><span class="metric-label">RAM Modularity</span><span class="metric-val">{upgrade.ram_modular_state}</span></div>
      <div class="metric-row"><span class="metric-label">M.2 Storage Slots</span><span class="metric-val">{laptop.storage.m2_slots_total} Slots ({upgrade.storage_expansion_slots_free} Free)</span></div>
      <div class="metric-row"><span class="metric-label">Chassis Hinge Build</span><span class="metric-val">{laptop.chassis.chassis_materials}</span></div>
    </div>
  </div>

  <!-- Dealbreakers & Anti-Marketing -->
  <div class="grid-3">
    <!-- Dealbreakers Card -->
    <div class="card" style="grid-column: span 2;">
      <h3 style="color: var(--accent-red)">
        <span>Detected Hardware Deal-Breakers & Configuration Traps</span>
        <span class="tag tag-fatal">{dealbreakers.fatal_dealbreakers_count} Fatal</span>
      </h3>
      {"".join(f'''
      <div class="dealbreaker-card">
        <div class="dealbreaker-title">[{d.severity}] {d.title}</div>
        <div class="dealbreaker-desc">{d.description}</div>
        <div class="remediation">Recommendation: {d.remediation_or_alternative}</div>
      </div>''' for d in dealbreakers.dealbreakers) if dealbreakers.dealbreakers else '<p style="color: var(--accent-green)">Zero fatal deal-breakers or configuration traps detected. Clean engineering verified.</p>'}
    </div>

    <!-- Anti-Marketing Audit -->
    <div class="card">
      <h3 style="color: var(--accent-amber)">
        <span>Anti-Marketing Audit</span>
        <span>{marketing.marketing_honesty_score:.1f}/100</span>
      </h3>
      <p style="font-size: 13px; margin-bottom: 12px; color: var(--text-muted);">{marketing.executive_summary}</p>
      {"".join(f'''
      <div style="font-size: 12px; border-bottom: 1px solid var(--border); padding: 8px 0;">
        <div style="font-weight: 700; color: #fff;">Claim: "{c.claim_phrase}"</div>
        <div style="color: {'var(--accent-green)' if c.audit_verdict == 'SUPPORTED' else ('var(--accent-red)' if c.audit_verdict == 'MISLEADING_MARKETING_TRAP' else 'var(--accent-amber)')}; font-weight: 700; margin: 2px 0;">[{c.audit_verdict}]</div>
        <div style="color: var(--text-muted);">{c.engineering_explanation}</div>
      </div>''' for c in marketing.claims)}
    </div>
  </div>

  <!-- Footer -->
  <div class="footer">
    SysPulse Laptop Buyer Audit Engine v1.1.0 &bull; Developed by Ajinkya Furange &bull; Grounded in Physical Hardware Reality
  </div>

</div>
</body>
</html>"""

        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(html)
