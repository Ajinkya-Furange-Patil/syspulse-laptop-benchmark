# Task Completion Checklist (Definition of Done)

A task is considered complete **ONLY** when every item on this checklist is satisfied:

---

## 1. Code & Functionality
- [ ] Requested feature or fix is implemented cleanly.
- [ ] Existing behavior is preserved across all unaffected modules.
- [ ] No hardcoded model numbers or magic numbers were introduced into general logic.
- [ ] Unknown hardware values remain marked as `UNKNOWN` rather than `0` or guesses.

---

## 2. Testing & Verification
- [ ] Native C++ code compiles with 0 errors and 0 warnings (`build.bat`).
- [ ] All relevant phase test scripts pass.
- [ ] Master test suite [`test_all_phases.py`](file:///test_all_phases.py) executes with 0 failures.
- [ ] Generated reports (JSON and HTML) are non-empty and well-formed.

---

## 3. Distribution & Version Control
- [ ] The standalone distribution bundle [`SysPulse_Portable/`](file:///SysPulse_Portable) contains only `SysPulse.exe`, `vcomp140.dll`, and `results/`.
- [ ] [`SysPulse_Portable.zip`](file:///SysPulse_Portable.zip) is synchronized and clean.
- [ ] No temporary files or test outputs left unstaged.
- [ ] Git commit uses a descriptive Conventional Commits message.
