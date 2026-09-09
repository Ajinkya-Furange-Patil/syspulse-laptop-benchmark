# AI Task Specification Template

Use this format when formulating an engineering task for an AI coding agent working on SysPulse:

---

## 1. Task Objective
- **Goal:** [Clear, concise 1-2 sentence statement of what needs to be accomplished]
- **Subsystem:** [`Native C++ Engine` | `Analytical Audit Engine` | `Schema/Validator` | `Reporting` | `Packaging`]

---

## 2. Reconnaissance & Affected Files
- **Files to Inspect:**
  - `path/to/file1`
  - `path/to/file2`
- **Existing Behavior:** [How the code currently behaves]
- **Target Behavior:** [Exact behavior required after modification]

---

## 3. Constraints & Invariants
- **Non-Negotiables:** [Specific rules from `.ai/constitution/NON_NEGOTIABLES.md` that apply]
- **Output Schema Impact:** [Does this modify JSON output? If yes, provide backward compatibility plan]
- **Dependencies:** [Zero new dependencies allowed, or specify justified ADR]

---

## 4. Verification Plan
- **Compilation Command:** [e.g. `cmd.exe /c "echo. | build.bat"`]
- **Test Command:** [e.g. `python test_all_phases.py` or specific phase test]
- **Acceptance Criteria:** [Specific conditions that prove the task is complete]
