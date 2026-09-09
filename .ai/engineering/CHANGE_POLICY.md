# Code Change & Modification Policy

To prevent architectural regression, instability, and accidental scope creep, all changes by AI coding agents must follow this strict policy.

---

## 1. General Rule
> **Prefer the smallest, most localized correct change over a wide-ranging redesign.**

---

## 2. Permitted Without Friction
The following actions are standard maintenance and encouraged:
- Bug fixes and logic corrections.
- Adding missing unit, integration, or regression test cases.
- Performance optimizations supported by repeatable benchmarks.
- Adding fields to schemas when backed by new validation rules.
- Correcting typos, outdated documentation, and dead links.
- Hardening error handling around unreliable OS sensor queries.

---

## 3. Requires Documented Justification
The following actions require explicit explanation in the commit message or task log:
- Modifying scoring category weights or threshold boundaries.
- Adding or altering public CLI parameters.
- Changing schema field names or JSON output structure.
- Altering the benchmark loop duration or workload intensity.
- Introducing a new file into the top-level repository root.

---

## 4. Strictly Forbidden (Unless Explicitly Requested)
The following actions are **prohibited**:
- Wholesale rewriting of working modules.
- Migrating away from C++ or standard Python to alternative frameworks.
- Replacing the standalone HTML report generator with a dynamic web server.
- Deleting existing test suites or disabling failing tests instead of fixing the root cause.
- Removing any of the 6 core workload domains.
- Adding dependencies that require an active internet connection.
