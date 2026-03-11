---
phase: 06-file-input
plan: 01
subsystem: ui
tags: [pandas, openpyxl, csv, excel, file-upload, template]

# Dependency graph
requires: []
provides:
  - REQUIRED_COLUMNS list defining the upload data contract
  - generate_template_df() returning a 3-row example DataFrame
  - read_uploaded_file() parsing CSV/Excel into a pipeline-compatible DataFrame
  - get_template_csv_bytes() for st.download_button
  - templates/smb_financial_template.csv downloadable template file
affects:
  - 06-02 (sidebar upload wiring uses all exports from this module)
  - 06-file-input (all remaining plans depend on read_uploaded_file)

# Tech tracking
tech-stack:
  added: [openpyxl>=3.1.0]
  patterns:
    - Derive computed columns (gross_profit, net_income, month_label, month_index)
      from uploaded raw columns so downstream pipeline stays unchanged
    - Normalise uploaded column names (strip + lowercase) before processing
    - Return extra user columns after the ordered standard set (non-destructive)

key-files:
  created:
    - src/template.py
    - templates/smb_financial_template.csv
  modified:
    - requirements.txt

key-decisions:
  - "raise ValueError with clear message on parse failure — column validation deferred to Phase 7 (validator plan)"
  - "compute derived columns inside read_uploaded_file so existing kpi_engine/charts need zero changes"
  - "normalise column names (strip + lowercase) defensively to handle common spreadsheet export quirks"

patterns-established:
  - "Upload pipeline pattern: raw user columns -> derived columns -> standard ordered column list"
  - "Template bytes via get_template_csv_bytes() rather than disk file read to avoid path issues in Streamlit Cloud"

requirements-completed: [INPUT-02]

# Metrics
duration: 1min
completed: 2026-03-11
---

# Phase 6 Plan 01: Template and File Reading Utilities Summary

**CSV/Excel upload infrastructure via src/template.py — REQUIRED_COLUMNS contract, 3-row downloadable template, and read_uploaded_file() producing a DataFrame that matches generate_company_data() output exactly**

## Performance

- **Duration:** ~1 min
- **Started:** 2026-03-11T00:53:39Z
- **Completed:** 2026-03-11T00:54:44Z
- **Tasks:** 1
- **Files modified:** 3

## Accomplishments
- Created `src/template.py` with all four exports required by Plan 02 sidebar wiring
- Created `templates/smb_financial_template.csv` with correct header and 3 realistic SMB rows
- Added openpyxl to requirements.txt enabling .xlsx reading via pd.read_excel
- `read_uploaded_file()` computes gross_profit, net_income, month_label, month_index so the existing KPI engine and charting code consume uploaded data without modification

## Task Commits

Each task was committed atomically:

1. **Task 1: Create src/template.py with template generation and file reading** - `49ee99f` (feat)

**Plan metadata:** (docs commit to follow)

## Files Created/Modified
- `src/template.py` - REQUIRED_COLUMNS, generate_template_df(), read_uploaded_file(), get_template_csv_bytes()
- `templates/smb_financial_template.csv` - Downloadable template with header + 3 example rows
- `requirements.txt` - Added openpyxl>=3.1.0

## Decisions Made
- Raise ValueError with a clear message on parse failure — column presence validation is deferred to Phase 7 (validator plan) to keep concerns separate
- Compute all derived columns inside read_uploaded_file() so existing kpi_engine.py, benchmarks.py, insights.py, and app.py require zero changes
- Normalise column names (strip + lowercase) defensively to handle common spreadsheet export quirks where column headers may have extra whitespace

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- All exports needed by Plan 02 (sidebar upload wiring) are implemented and verified
- read_uploaded_file() produces a DataFrame whose column set and dtypes are compatible with calculate_kpis() and all chart functions
- No blockers for Plan 02

## Self-Check: PASSED

- FOUND: src/template.py
- FOUND: templates/smb_financial_template.csv
- FOUND commit: 49ee99f
- All plan verification checks: ALL CHECKS PASSED

---
*Phase: 06-file-input*
*Completed: 2026-03-11*
