# ADR-002: Unknown Values Must Remain Explicitly Unknown

## Status
Accepted

## Context
Many programming paradigms convert `None`, missing keys, or uninitialized metrics into `0`, `false`, or empty strings. In hardware auditing, `0` and `UNKNOWN` have completely different physical meanings:
- `0 GB VRAM` = The machine has no dedicated VRAM (integrated graphics only).
- `UNKNOWN VRAM` = The specification sheet or telemetry query did not provide the VRAM size.

Treating `UNKNOWN` as `0` triggers false fatal deal-breakers and ruins scoring.

## Decision
All hardware metrics must be modeled using `AuditField[T]`, which explicitly tracks:
- `status`: `CONFIRMED`, `ESTIMATED`, or `UNKNOWN`.
- `confidence`: Floating-point scalar from `0.0` to `1.0`.
- Missing values must remain `UNKNOWN`, decay the subsystem confidence score, and apply conservative historical baselines with transparent user disclosure.

## Consequences
- No false zero-value deal-breakers.
- Retailers that hide cost-cutting metrics are highlighted with lower confidence scores rather than artificial zeros.
