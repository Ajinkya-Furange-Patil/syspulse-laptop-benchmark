# Buyer Audit Philosophy

The SysPulse Buyer Audit Engine is not a standard laptop recommendation algorithm. It is a technical verification system designed to protect buyers from predatory marketing and superficial spec sheets.

---

## 1. The Reality of Modern Laptop Retailing
Modern laptop manufacturers frequently:
- Pair high-tier silicon dies (e.g. Core i7 / RTX 4060) with castrated power limits (e.g. 45W Max-Q vBIOS instead of 140W Max-P), yielding 30% lower performance than properly cooled models.
- Solder single-channel RAM to motherboards with zero SODIMM expansion slots, crippling CPU multi-tasking and minimum 1% frame rate stability.
- Market high-refresh displays (144Hz) that have abysmal pixel response times (18ms+), resulting in severe motion blur and ghosting that negates the high refresh rate.
- Ship high-draw components with cost-cut, undersized power supplies (e.g. 135W adapter on a 175W combined load), causing the laptop to actively discharge its battery while plugged into the wall.

---

## 2. The Four Pillars of Audit Analysis
1. **Physical Silicon & Power Balance:** Does the OEM vBIOS and cooling system allow the silicon die to operate at its full potential?
2. **Hardware Modularity & Serviceability:** Can the user upgrade RAM, add storage, clean the fans, and replace the battery without damaging the chassis?
3. **Workload Suitability:** Does the machine physically satisfy the constraints of the user's intended tasks (e.g. VRAM capacity for AI, single-core boost for CAD, color gamut for creators)?
4. **Transparent Explainability:** Every score deduction and warning must have an underlying physical reason, not a black-box opinion.
