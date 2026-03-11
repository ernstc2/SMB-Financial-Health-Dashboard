# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

## Milestone: v1.1 — Dynamic Data Upload

**Shipped:** 2026-03-11
**Phases:** 3 | **Plans:** 5 | **Sessions:** ~4

### What Was Built
- CSV/Excel upload infrastructure with column contract, file reader, and downloadable template
- TDD validation suite (10 tests) catching missing columns, bad types, and impossible values
- Session-state-backed multi-company upload with auto-select and unified dropdown
- Side-by-side company comparison view with dual radar chart, KPI winner table, and revenue overlay
- All 5 existing dashboard sections work on uploaded data without modification to kpi_engine/charts

### What Worked
- **Derived columns in read_uploaded_file()** — computing gross_profit, net_income, month_label, month_index at the upload boundary meant zero changes to the existing KPI engine, charts, or insights modules
- **Human-verify checkpoints** — caught 6 real bugs across phases 7 and 8 (NaN passthrough, pre-validator crash, error placement, yaxis conflict, auto-select timing, date alignment) that static verification missed
- **Clean phase dependency chain** (06→07→08) — each phase had a clear contract for the next, no rework needed
- **TDD for validation** — writing tests first for validate_uploaded_df() caught the NaN-passthrough edge case that would have been hard to find in manual testing

### What Was Inefficient
- **STATE.md staleness** — state file fell behind actual progress (showed 20% when milestone was near complete); accumulated context grew large with per-phase decisions that duplicated PROJECT.md
- **ROADMAP.md checkbox drift** — Phase 8 plan checkboxes never got updated to [x] even though summaries existed; minor but could confuse resume flows

### Patterns Established
- **Upload pipeline pattern:** raw user columns → derived columns → standard ordered column list (ensures downstream code never sees raw uploads)
- **Validate-before-calculate gate:** validation function returns error list; empty list = proceed; non-empty = block and display
- **Session state accumulation store:** `uploaded_companies[name] = raw_df` persists across Streamlit reruns; KPIs calculated fresh at render time
- **Deferred widget auto-select:** use a `_pending` flag consumed before the widget call rather than setting widget key after render (avoids Streamlit timing errors)
- **Month-index alignment:** normalise x-axis to integer months when comparing companies with different date ranges; actual dates in Plotly customdata

### Key Lessons
1. **Guard derived column computation against missing source columns** — if validation runs after file reading, the reader must not assume all columns exist
2. **NaN requires explicit checks separate from dtype** — `is_numeric_dtype()` returns True for columns containing NaN (pandas converts "N/A" strings to NaN during read)
3. **Streamlit widget key timing matters** — cannot set `st.session_state[widget_key]` after the widget has already rendered in the current run; use a flag consumed on the next rerun instead
4. **Human-verify checkpoints are high-ROI** — they caught 6/6 bugs that made it through automated checks, all in UI-interaction edge cases

### Cost Observations
- Model mix: ~70% sonnet (execution, verification, integration checks), ~30% opus (planning, audit orchestration)
- Sessions: ~4 across 5 days
- Notable: Plans 06-01 and 06-02 executed in ~11 min total; validation phase (07) took ~20 min due to TDD cycle + human-verify fixes; comparison view (08-02) required a bug-fix round but still completed in ~15 min

---

## Cross-Milestone Trends

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v1.0 | — | 5 | Pre-GSD; no structured workflow |
| v1.1 | ~4 | 3 | GSD workflow adopted; human-verify checkpoints proved valuable |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|-------------------|
| v1.0 | 0 | — | 5 (all source modules) |
| v1.1 | 10 | Validation fully covered | 2 (src/template.py, tests/test_validation.py) |

### Top Lessons (Verified Across Milestones)

1. Computing derived columns at the data boundary keeps downstream modules untouched — proven in both v1.0 (data_generator) and v1.1 (read_uploaded_file)
2. Human verification catches UI interaction bugs that automated checks miss — 6 bugs caught in v1.1, all in Streamlit widget state transitions
