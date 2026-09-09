# ADR-001: Multi-Domain Workload Scoring & Deal-Breakers over Single Universal Score

## Status
Accepted

## Context
Commercial benchmark tools and laptop review sites frequently assign a single aggregate score (e.g. "8.5 / 10" or "Overall: 78%"). This blurs critical engineering compromises: a machine with an excellent CPU but a castrated 45W GPU or single-channel RAM will receive a high aggregate score while failing miserably in actual sustained gaming or simulation.

## Decision
SysPulse rejects the single universal score. Instead, it computes:
1. Baseline physical capability across 6 foundational categories (CPU, GPU, VRAM, RAM, Storage, Cooling).
2. Hard, non-negotiable Deal-Breakers that cap or invalidate specific use-cases.
3. 6 independent workload domain scores (Gaming, AI/ML, Software Development, Engineering/CAD, Content Creation, Portability).

## Consequences
- A laptop can receive 95/100 for Software Development while receiving 15/100 for Local AI.
- Users receive clear, unambiguous guidance tailored to their exact workload.
- Deceptive marketing strategies cannot hide behind blended averages.
