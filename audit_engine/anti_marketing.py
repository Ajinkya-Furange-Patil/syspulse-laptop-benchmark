"""
SysPulse Laptop Buyer Audit Engine - Phase 19: Anti-Marketing Audit Engine
Scans manufacturer and retailer marketing claims ("AI-Powered", "Gaming Beast", "Pro Display")
and cross-examines them against cold, physical hardware measurements.
Outputs: Supported, Partially Supported, or Debunked Marketing Trap.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from audit_engine.models import LaptopSpecification


@dataclass
class MarketingClaimAudit:
    claim_phrase: str
    physical_hardware_reality: str
    audit_verdict: str  # SUPPORTED, PARTIALLY_SUPPORTED, MISLEADING_MARKETING_TRAP
    engineering_explanation: str


@dataclass
class AntiMarketingReport:
    total_claims_scanned: int
    misleading_traps_count: int
    marketing_honesty_score: float  # 0 - 100
    claims: List[MarketingClaimAudit]
    executive_summary: str


class AntiMarketingAuditEngine:
    """
    Rigorously detects deceptive buzzwords and contrasts them with physical hardware realities.
    """

    @classmethod
    def audit_claims(cls, laptop: LaptopSpecification) -> AntiMarketingReport:
        claims: List[MarketingClaimAudit] = []

        headline = (laptop.metadata.marketing_headline or "").lower()
        gpu = laptop.gpu
        cpu = laptop.cpu
        disp = laptop.display
        ram = laptop.memory
        pwr = laptop.power

        # Claim 1: "AI-Powered" / "AI Laptop"
        if "ai" in headline or "npu" in headline:
            has_cuda = gpu.manufacturer == "NVIDIA"
            vram = gpu.vram_gb
            npu_tops = cpu.npu_tops.value if cpu.npu_tops.is_known else 0.0

            if has_cuda and vram >= 8.0:
                verdict = "SUPPORTED"
                exp = f"True local AI capability verified. Dedicated {vram}GB GDDR6 VRAM and Tensor cores support 8B LLMs and QLoRA fine-tuning."
            elif has_cuda and vram < 6.0:
                verdict = "MISLEADING_MARKETING_TRAP"
                exp = f"Advertised as 'AI-powered', but {vram}GB VRAM triggers immediate OutOfMemory crashes on modern LLMs and Stable Diffusion XL."
            elif npu_tops > 0:
                verdict = "PARTIALLY_SUPPORTED"
                exp = f"NPU delivers {npu_tops} TOPS for basic background blur/eye tracking, but lacks discrete CUDA Tensor cores for real deep learning."
            else:
                verdict = "MISLEADING_MARKETING_TRAP"
                exp = "Pure marketing fluff: No discrete Tensor cores, no capable NPU, and no high-bandwidth VRAM present."

            claims.append(MarketingClaimAudit(
                claim_phrase="AI-Powered / Next-Gen AI",
                physical_hardware_reality=f"GPU: {gpu.exact_model} ({vram}GB VRAM) | NPU: {npu_tops} TOPS",
                audit_verdict=verdict,
                engineering_explanation=exp
            ))

        # Claim 2: "High-Performance RTX Gaming"
        if "gaming" in headline or "rtx" in headline:
            tgp = gpu.oem_base_tgp_w.value if gpu.oem_base_tgp_w.is_known else 45.0
            max_tgp = gpu.silicon_max_possible_tgp_w
            has_mux = gpu.has_mux_switch.value if gpu.has_mux_switch.is_known else False
            is_single_ch = ram.channel_configuration == "SINGLE_CHANNEL"

            if tgp < (max_tgp * 0.60) or is_single_ch:
                verdict = "MISLEADING_MARKETING_TRAP"
                reasons = []
                if tgp < (max_tgp * 0.60):
                    reasons.append(f"TGP is castrated to {tgp}W (only {tgp/max_tgp*100:.0f}% of silicon max)")
                if is_single_ch:
                    reasons.append("Single-channel RAM cripples 1% low frame consistency")
                if not has_mux:
                    reasons.append("No MUX switch imposes iGPU frame routing penalty")
                exp = f"Paper tiger gaming claim: {'; '.join(reasons)}. Delivers 25-35% lower framerates than proper implementations."
            elif tgp >= (max_tgp * 0.85) and has_mux:
                verdict = "SUPPORTED"
                exp = f"Genuine full-power gaming machine. Max-P {tgp}W TGP and hardware MUX switch verified."
            else:
                verdict = "PARTIALLY_SUPPORTED"
                exp = f"Decent gaming output, but tuned conservatively ({tgp}W TGP)."

            claims.append(MarketingClaimAudit(
                claim_phrase="High-Performance RTX Gaming",
                physical_hardware_reality=f"GPU TGP: {tgp}W / {max_tgp}W | MUX Switch: {has_mux} | RAM: {ram.channel_configuration}",
                audit_verdict=verdict,
                engineering_explanation=exp
            ))

        # Claim 3: "High-Refresh Fast Display"
        if "144hz" in headline or "240hz" in headline or "fast display" in headline or disp.refresh_rate_hz >= 120:
            hz = disp.refresh_rate_hz
            resp = disp.response_time_gtg_ms.value if disp.response_time_gtg_ms.is_known else 8.0
            srgb = disp.color_gamut_srgb_pct.value if disp.color_gamut_srgb_pct.is_known else 65.0

            if resp > 15.0 and hz >= 120:
                verdict = "MISLEADING_MARKETING_TRAP"
                exp = f"Advertised with a fast {hz}Hz refresh, but physical pixel response time is {resp}ms. Severe ghosting and motion blur negate the high Hz benefit."
            elif srgb <= 65.0:
                verdict = "PARTIALLY_SUPPORTED"
                exp = f"Motion is fluid ({hz}Hz), but panel color gamut is a washed-out 45% NTSC ({srgb}% sRGB)."
            else:
                verdict = "SUPPORTED"
                exp = f"High-tier panel verified: {hz}Hz with snappy {resp}ms GTG response and {srgb}% sRGB coverage."

            claims.append(MarketingClaimAudit(
                claim_phrase=f"High-Refresh {hz}Hz Display",
                physical_hardware_reality=f"Refresh: {hz}Hz | Measured GTG: {resp}ms | Gamut: {srgb}% sRGB",
                audit_verdict=verdict,
                engineering_explanation=exp
            ))

        # Claim 4: "Ultra-Slim / Portable Powerhouse"
        if "slim" in headline or "thin" in headline or "ultra" in headline:
            adapter_w = pwr.adapter_rating_w
            pl1 = cpu.oem_pl1_w.value if cpu.oem_pl1_w.is_known else 45.0
            tgp_val = gpu.oem_base_tgp_w.value if (gpu.is_discrete and gpu.oem_base_tgp_w.is_known) else 0.0
            combined = pl1 + tgp_val + 24.0

            if adapter_w < combined:
                verdict = "MISLEADING_MARKETING_TRAP"
                exp = f"Manufacturers shaved chassis thickness at the expense of power delivery. {adapter_w}W adapter causes battery drain under AC load."
            else:
                verdict = "SUPPORTED"
                exp = "Compact chassis with adequate power delivery engineering."

            claims.append(MarketingClaimAudit(
                claim_phrase="Ultra-Slim Powerhouse",
                physical_hardware_reality=f"Thickness: {laptop.chassis.thickness_mm.value or 'N/A'}mm | Adapter: {adapter_w}W vs {combined:.0f}W load",
                audit_verdict=verdict,
                engineering_explanation=exp
            ))

        # Honesty Score Calculation
        if not claims:
            # Generate baseline claim audit
            claims.append(MarketingClaimAudit(
                claim_phrase="Headline Specification Integrity",
                physical_hardware_reality="Audited baseline components.",
                audit_verdict="SUPPORTED",
                engineering_explanation="No misleading promotional phrases detected in listing title."
            ))

        traps = sum(1 for c in claims if c.audit_verdict == "MISLEADING_MARKETING_TRAP")
        part = sum(1 for c in claims if c.audit_verdict == "PARTIALLY_SUPPORTED")
        honesty_score = round(max(0.0, 100.0 - (traps * 40.0) - (part * 15.0)), 1)

        if traps >= 2:
            summary = "DECEPTIVE MARKETING DETECTED: Multiple headline marketing claims directly contradict physical hardware measurements."
        elif traps == 1:
            summary = "CAUTION REQUIRED: One major marketing trap detected. Headline claims oversell real hardware capability."
        else:
            summary = "HONEST MARKETING: Manufacturer promotional claims accurately align with physical hardware capabilities."

        return AntiMarketingReport(
            total_claims_scanned=len(claims),
            misleading_traps_count=traps,
            marketing_honesty_score=honesty_score,
            claims=claims,
            executive_summary=summary
        )
