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
  patterns: [TDD red-green cycle, accumulate-all-errors pattern, validate-then-block gate, NaN guard after is_numeric_dtype]

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
  - "Business rule checks only run when no type errors — prevents misleading row-number errors on non-numeric data"
  - "Row numbers reported as index+2 for spreadsheet display (header row + 0-index offset)"
  - "NaN check required separately from is_numeric_dtype — pandas converts 'N/A' strings to NaN which passes dtype check"
  - "Derived columns computed conditionally in read_uploaded_file() so missing columns don't crash before validator runs"
  - "Errors render in st.container() placed immediately after upload widget, not st.sidebar.error() at bottom"
  - "Invalid files fall back to sample data so dashboard remains usable"

patterns-established:
  - "Validate-before-calculate: validate_uploaded_df() called before calculate_kpis() in upload branch"
  - "Accumulate all errors pattern: return full list so users see every problem at once"
  - "Row number display: index + 2 for spreadsheet-friendly row references"
  - "Guard derived column computation with column presence checks to avoid crashing before validator"

requirements-completed: [VALID-01, VALID-02, VALID-03]

# Metrics
duration: ~20min
completed: 2026-03-11
---

# Phase 7 Plan 01: Upload Validation Summary

**validate_uploaded_df() with 10-test TDD suite — column presence, NaN, numeric type, and business rule checks wired into dashboard upload branch with actionable error display confirmed by human verification**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-03-11T01:25:56Z
- **Completed:** 2026-03-11T01:50:00Z
- **Tasks:** 3 complete
- **Files modified:** 4

## Accomplishments
- Implemented validate_uploaded_df() in src/template.py following validate-then-block pattern from research
- Created tests/test_validation.py with 10 unit tests covering all VALID-01/02/03 requirements; all pass
- Wired validation gate into app.py upload branch between read_uploaded_file() and calculate_kpis()
- Human verification confirmed all 7 UX scenarios pass: missing columns, non-numeric data, NaN values, business rule violations, valid template passthrough, error placement, and dashboard fallback
- Three correctness bugs found during human-verify and auto-fixed: NaN passthrough, pre-validator crash on missing columns, error widget placement

## Task Commits

Each task was committed atomically:

1. **Task 1: TDD — validate_uploaded_df function with test suite** - `9b981c9` (feat)
2. **Task 2: Wire validation into app.py upload branch** - `d3e4890` (feat)
3. **Task 3: Visual verification fixes** - `431167a` (fix)

## Files Created/Modified
- `tests/__init__.py` - Empty init for pytest discovery
- `tests/test_validation.py` - 10 unit tests covering all VALID-0x requirements
- `src/template.py` - Added validate_uploaded_df(); guarded derived column computation in read_uploaded_file()
- `app.py` - Import validate_uploaded_df; wired validate-then-block pattern; errors in st.container() after upload widget

## Decisions Made
- validate_uploaded_df returns list[str] (empty = valid) — app controls when/how to display errors, function stays pure and testable
- Column presence check (VALID-01) returns early — avoids KeyError on missing columns in type checks
- Business rules only run when type checks clean — guards against is_numeric_dtype false negatives
- Row numbers as index+2 — header offset so spreadsheet row numbers match what users see in Excel/Sheets
- NaN check added as separate tier — is_numeric_dtype passes for NaN-containing columns, requiring explicit isna() guard

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Guarded derived column computation in read_uploaded_file()**
- **Found during:** Task 3 (visual verification)
- **Issue:** read_uploaded_file() computed gross_profit and net_income unconditionally, causing a KeyError crash when source columns like cogs were absent — the validator never ran
- **Fix:** Wrapped derived column computation in `if all(c in df.columns for c in [...])` guard
- **Files modified:** src/template.py
- **Verification:** Missing-columns scenario no longer crashes; validator reports actionable error
- **Committed in:** 431167a

**2. [Rule 1 - Bug] Added NaN check to validate_uploaded_df()**
- **Found during:** Task 3 (visual verification — "N/A" in revenue column)
- **Issue:** pandas.read_csv converts "N/A" strings to NaN, which passes is_numeric_dtype(); validator reported no error for cells containing "N/A"
- **Fix:** Added elif df[col].isna().any() branch after dtype check to catch NaN values and report row numbers
- **Files modified:** src/template.py
- **Verification:** "N/A" in revenue now shows error naming column and row number
- **Committed in:** 431167a

**3. [Rule 1 - Bug] Moved error display from st.sidebar.error() to st.container() after upload widget**
- **Found during:** Task 3 (visual verification — error placement)
- **Issue:** st.sidebar.error() appends to the bottom of the sidebar; errors appeared far below the upload widget and were easy to miss
- **Fix:** Created upload_errors container immediately after upload widget; errors rendered inside that container
- **Files modified:** app.py
- **Verification:** Errors appear directly below upload widget in all test scenarios
- **Committed in:** 431167a

---

**Total deviations:** 3 auto-fixed (all Rule 1 — bugs discovered during human verification)
**Impact on plan:** All fixes necessary for correct UX and correctness. NaN and crash fixes are correctness requirements. Error placement is the intended UX even if plan specified a different Streamlit API call. No scope creep.

## Issues Encountered

None beyond the three auto-fixed bugs above, all caught during the human-verify checkpoint.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Validation pipeline complete and tested; all three tasks done
- Phase 08 (comparison/data pipeline refactor) can build on validated upload flow
- Blocker: Phase 8 refactor scope (how much of app.py/kpi_engine.py/benchmarks.py/insights.py needs changes) remains unknown until Phase 8 planning

---
*Phase: 07-validation*
*Completed: 2026-03-11*
