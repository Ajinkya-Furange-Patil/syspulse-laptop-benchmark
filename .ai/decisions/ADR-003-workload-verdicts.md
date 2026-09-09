# ADR-003: Workload-Centric Verdict Synthesis (No Universal Winner)

## Status
Accepted

## Context
Laptop buyers frequently ask: *"Is this laptop good or bad?"* In real-world computer systems, no machine is universally good or bad. A thick, heavy mobile workstation with a 300W power brick is exceptional for FEA simulation and video editing, but terrible for a student walking across a college campus all day.

## Decision
SysPulse synthesizes final buying verdicts conditioned strictly on the user's primary priority:
- `EXCELLENT BUY`
- `GOOD BUY`
- `CONDITIONAL BUY`
- `WAIT / COMPARE`
- `NOT RECOMMENDED`
- `HARD NO`

The verdict logic weights the user's target domain and checks if fatal deal-breakers exist specifically for that domain.

## Consequences
- Demonstrates genuine engineering nuance: identical hardware yields different verdicts depending on user priority.
- Eliminates superficial "best laptop of the year" rankings.
