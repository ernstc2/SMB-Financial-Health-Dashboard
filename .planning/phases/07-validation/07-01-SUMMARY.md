---
phase: 07-validation
plan: 01
subsystem: testing
tags: [pytest, pandas, validation, upload, streamlit]

# Dependency graph
requires:
  - phase: 06-file-input
    provides: read_uploaded_file() and upload branch wiring in app.py
provides:
  - validate_uploaded_df() function in src/template.py
  - Unit test suite tests/test_validation.py (10 tests)
  - Validation gate in app.py upload branch (before calculate_kpis)
affects: [08-comparison, any future phases touching file upload]

# Tech tracking
tech-stack:
  added: [pytest (dev dependency)]
  patterns: [TDD red-green cycle, accumulate-all-errors pattern, validate-then-block gate]

key-files:
  created:
    - tests/__init__.py
    - tests/test_validation.py
  modified:
    - src/template.py
    - app.py

key-decisions:
  - "validate_uploaded_df returns list[str] (empty = valid) so app controls display logic"
  - "Column presence check returns early — no type/rule checks run on missing columns"
  - "Business rule checks only run when no type errors — prevents KeyError on non-numeric columns"
  - "Row numbers reported as index+2 for spreadsheet display (header row + 0-index offset)"
  - "Validation errors display via st.sidebar.error() consistent with Phase 6 parse errors"
  - "Invalid files fall back to sample data so dashboard remains usable"

patterns-established:
  - "Validate-before-calculate: validate_uploaded_df() called before calculate_kpis() in upload branch"
  - "Accumulate all errors pattern: return full list so users see every problem at once"
  - "Row number display: index + 2 for spreadsheet-friendly row references"

requirements-completed: [VALID-01, VALID-02, VALID-03]

# Metrics
duration: 10min
completed: 2026-03-11
---

# Phase 7 Plan 01: Upload Validation Summary

**validate_uploaded_df() with 10-test TDD suite: column presence, numeric type checks, business rule enforcement, and sidebar error display wired into dashboard upload branch**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-03-11T01:25:56Z
- **Completed:** 2026-03-11T01:35:00Z
- **Tasks:** 2 complete (Task 3 pending human verification at checkpoint)
- **Files modified:** 4

## Accomplishments
- Implemented validate_uploaded_df() in src/template.py following validate-then-block pattern from research
- Created tests/test_validation.py with 10 unit tests covering all VALID-01/02/03 requirements; all pass
- Wired validation gate into app.py upload branch between read_uploaded_file() and calculate_kpis()
- Errors display in sidebar (consistent with Phase 6), invalid files fall back to sample data

## Task Commits

Each task was committed atomically:

1. **Task 1: TDD — validate_uploaded_df function with test suite** - `9b981c9` (feat)
2. **Task 2: Wire validation into app.py upload branch** - `d3e4890` (feat)

_Note: Task 3 (checkpoint:human-verify) pending human visual verification._

## Files Created/Modified
- `tests/__init__.py` - Empty init for pytest discovery
- `tests/test_validation.py` - 10 unit tests covering all VALID-0x requirements
- `src/template.py` - Added validate_uploaded_df() after get_template_csv_bytes()
- `app.py` - Import validate_uploaded_df; wired validate-then-block pattern in upload branch

## Decisions Made
- validate_uploaded_df returns list[str] (empty = valid) — app controls when/how to display errors, function stays pure and testable
- Column presence check (VALID-01) returns early — avoids KeyError on missing columns in type checks
- Business rules only run when type checks clean — guards against is_numeric_dtype false negatives
- Row numbers as index+2 — header offset so spreadsheet row numbers match what users see in Excel/Sheets

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Validation pipeline complete and tested; Task 3 human checkpoint pending
- After human approval: phase 07 plan 01 fully complete
- Phase 08 (comparison) can build on the validated upload flow

---
*Phase: 07-validation*
*Completed: 2026-03-11*
