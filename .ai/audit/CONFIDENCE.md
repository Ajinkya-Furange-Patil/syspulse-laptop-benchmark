# Confidence & Provenance Tracking

Manufacturers and retailers frequently omit critical performance parameters (e.g. vBIOS TGP, screen color gamut, thermal dissipation envelope). SysPulse explicitly measures and reports input data confidence.

---

## 1. Hierarchy of Source Authority

When contradictory values are reported for the same metric, resolve conflicts using this hierarchy:
1. `BENCHMARK_MEASURED` (Priority: 100) — Direct physical lab measurement.
2. `OEM_SPEC` (Priority: 80) — Official technical whitepaper from the OEM engineering team.
3. `COMMUNITY_DATABASE` (Priority: 60) — Verified teardowns (Notebookcheck, etc.).
4. `USER_MANUAL_INPUT` (Priority: 40) — User-entered values from retail listing.
5. `UNKNOWN` (Priority: 0) — Parameter not provided.

---

## 2. Confidence Tiers
- **HIGH ($\ge 85\%$):** Key parameters confirmed by direct measurement or OEM documentation.
- **MEDIUM ($65\% - 84\%$):** Several tuning parameters estimated from historical silicon baselines.
- **LOW ($< 65\%$):** Critical tuning limits missing. The audit engine must use conservative floors and explicitly alert the user to data deficiency.

---

## 3. The Unknown Value Rule
> **UNKNOWN $\ne$ ZERO.**
>
> If a laptop specification sheet omits the display color gamut, do NOT treat it as 0% sRGB. Mark the field as `UNKNOWN`, decay the display subsystem confidence, and apply a conservative historical floor (e.g. 60% sRGB for budget panels) while flagging the missing data.
