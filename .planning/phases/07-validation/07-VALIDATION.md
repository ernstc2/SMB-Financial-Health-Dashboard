---
phase: 7
slug: validation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-10
---

# Phase 7 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | none — Wave 0 installs |
| **Quick run command** | `python -m pytest tests/test_validation.py -x -q` |
| **Full suite command** | `python -m pytest tests/ -q` |
| **Estimated runtime** | ~2 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest tests/test_validation.py -x -q`
- **After every plan wave:** Run `python -m pytest tests/ -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 07-01-01 | 01 | 0 | VALID-01, VALID-02, VALID-03 | unit | `pytest tests/test_validation.py -x` | ❌ W0 | ⬜ pending |
| 07-01-02 | 01 | 1 | VALID-01 | unit | `pytest tests/test_validation.py::test_missing_columns -x` | ❌ W0 | ⬜ pending |
| 07-01-03 | 01 | 1 | VALID-02 | unit | `pytest tests/test_validation.py::test_non_numeric_revenue -x` | ❌ W0 | ⬜ pending |
| 07-01-04 | 01 | 1 | VALID-02 | unit | `pytest tests/test_validation.py::test_zero_headcount -x` | ❌ W0 | ⬜ pending |
| 07-01-05 | 01 | 1 | VALID-03 | unit | `pytest tests/test_validation.py::test_valid_file_passes -x` | ❌ W0 | ⬜ pending |
| 07-01-06 | 01 | 1 | VALID-03 | unit | `pytest tests/test_validation.py::test_error_messages_actionable -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_validation.py` — stubs for VALID-01, VALID-02, VALID-03
- [ ] `tests/__init__.py` — empty init so pytest discovers the package
- [ ] `pip install pytest` — not currently in requirements.txt; add as dev dependency

*Wave 0 creates test infrastructure before implementation begins.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Error messages render correctly in sidebar | VALID-03 | Streamlit UI rendering requires visual check | Upload a file missing "revenue" column; verify error appears in sidebar with column name |
| Valid file shows no error UI | VALID-03 | Absence of UI elements hard to assert in unit tests | Upload a valid template CSV; verify no error/warning messages appear |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
