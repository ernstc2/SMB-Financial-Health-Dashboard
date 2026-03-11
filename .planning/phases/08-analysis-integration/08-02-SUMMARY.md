---
phase: 08-analysis-integration
plan: 02
subsystem: ui
tags: [streamlit, plotly, session-state, comparison-view]

# Dependency graph
requires:
  - phase: 08-analysis-integration/08-01
    provides: st.session_state.uploaded_companies dict; unified data pipeline accepting both sample and uploaded companies

provides:
  - Compare mode checkbox in sidebar enabling dual-company selection
  - Comparison rendering path: KPI table, dual radar, revenue overlay, side-by-side metric cards
  - Single-company mode untouched — clean if/else branch separation
  - Both sample and uploaded companies can be compared in any combination

affects:
  - Any future plans that touch the comparison view or sidebar layout

# Tech tracking
tech-stack:
  added: []
  patterns:
    - if/else branch at the top-level render block to cleanly separate comparison vs single-company mode
    - Comparison data pipeline mirrors single-company pipeline exactly (session_state check then sample fallback)
    - _pending_select flag pattern for deferred selectbox auto-select before widget instantiation
    - Month-index x-axis alignment for companies with different date ranges (actual dates passed via customdata)

key-files:
  created: []
  modified:
    - app.py

key-decisions:
  - "Clean if/else branch separation — comparison mode is a complete alternative rendering path, not merged into single-company mode"
  - "Comparison pipeline uses identical logic to single-company pipeline (no special-casing for uploaded vs sample)"
  - "yaxis conflicts in CHART_LAYOUT resolved via update_yaxes() calls rather than passing yaxis= to update_layout() when CHART_LAYOUT already has it"
  - "_pending_select flag applied before selectbox widget renders to avoid post-render session state write timing error"
  - "Normalised month index (Month 1, 2, ...) on shared x-axis when companies have different date ranges; actual dates surfaced in hover customdata to preserve readability"
  - "Info banner shown when date ranges differ to explain the alignment choice to the user"
  - "Second selectbox filtered to exclude the currently selected primary company"

patterns-established:
  - "Deferred widget auto-select: use a _pending flag consumed before the widget call rather than setting key after render"
  - "Overlaid radar charts: add second Scatterpolar trace with different color fill; AMBER dashed line for benchmark"
  - "Date-range alignment: when two datasets may not share timestamps, normalise to integer index and keep raw labels in customdata"

requirements-completed: [ANLYS-03]

# Metrics
duration: ~15min
completed: 2026-03-11
---

# Phase 08 Plan 02: Comparison View Summary

**Side-by-side company comparison view with dual radar chart, KPI winner table, revenue overlay, and metric cards — supporting any combination of sample and uploaded companies**

## Performance

- **Duration:** ~15 min (including human-verify checkpoint and bug-fix round)
- **Started:** 2026-03-11T02:20:32Z
- **Completed:** 2026-03-11T02:27:28Z
- **Tasks:** 2 of 2 (checkpoint approved with bug fixes)
- **Files modified:** 1

## Accomplishments
- "Compare two companies" checkbox added below company dropdown; triggers a filtered second selectbox
- Comparison data pipeline loads full df/kpis/scorecard/insights for both companies using the same session_state-aware logic as single-company mode
- Comparison layout: company header badges with RAG status, 6-row KPI table with winner column, dual-overlay radar chart, revenue trend overlay, side-by-side metric cards in two columns
- Single-company mode preserved verbatim inside the `else:` branch — zero behavioural change when compare mode is off
- Three bugs identified at human-verify checkpoint fixed in follow-up commit: yaxis conflict, upload auto-select timing, and date range alignment

## Task Commits

Each task was committed atomically:

1. **Task 1: Build comparison view with dual-company selection** - `3f2bdd9` (feat)
2. **Bug fixes from human-verify checkpoint** - `ae915a8` (fix)

**Plan metadata:** *(created after this summary)*

## Files Created/Modified
- `app.py` - Comparison checkbox, second selectbox, comparison data pipeline, full comparison rendering path (4 sections), single-company mode indented into else branch

## Decisions Made
- Clean if/else branch separation: comparison mode is a complete alternative rendering path. Merging the two paths into a single conditional layout would create fragile code that breaks single-company mode on changes to comparison layout.
- Comparison pipeline uses identical session_state → sample fallback logic as single-company pipeline. No special casing needed.
- yaxis conflicts: CHART_LAYOUT dict already contains a `yaxis` key. Passing another `yaxis=` in `update_layout()` raises TypeError. Fix is to use `update_yaxes()` separately after `update_layout(**CHART_LAYOUT)`.
- Upload auto-select: Streamlit disallows setting `st.session_state[widget_key]` after the widget has already rendered in the current run. Fix is a `_pending_select` flag consumed *before* the selectbox call on the next rerun.
- Date range alignment: companies may cover different calendar months. Aligning on a shared month-index axis avoids misleading overlaps; actual dates are passed in Plotly customdata so hover still shows real months.

## Deviations from Plan

### Auto-fixed Issues (identified at human-verify, committed as ae915a8)

**1. [Rule 1 - Bug] yaxis key conflict in update_layout() call**
- **Found during:** Task 2 (human-verify)
- **Issue:** `CHART_LAYOUT` already defines `yaxis`; passing `yaxis=dict(...)` in the same `update_layout(**CHART_LAYOUT, yaxis=...)` call raises `TypeError: update_layout() got multiple values for keyword argument 'yaxis'`
- **Fix:** Replaced `update_layout(yaxis=...)` with a separate `update_yaxes(...)` call after the base layout is applied
- **Files modified:** app.py
- **Verification:** Dashboard loads without TypeError on chart render
- **Committed in:** ae915a8

**2. [Rule 1 - Bug] Upload auto-select timing error in compare mode**
- **Found during:** Task 2 (human-verify)
- **Issue:** Setting `st.session_state.company_select` after the selectbox renders causes a Streamlit StreamlitAPIException (cannot set widget key after render)
- **Fix:** Replaced direct key-set with a `_pending_select` flag that is read and applied *before* the selectbox widget call on the next rerun
- **Files modified:** app.py
- **Verification:** Uploading a file while in compare mode correctly auto-selects the uploaded company
- **Committed in:** ae915a8

**3. [Rule 1 - Bug] Misaligned x-axis when companies have different date ranges**
- **Found during:** Task 2 (human-verify)
- **Issue:** Companies starting at different months produced overlapping or offset x-axis labels on the revenue overlay chart, making the visual misleading
- **Fix:** Normalised x-axis to integer month index ("Month 1", "Month 2", ...); passed actual date labels as Plotly `customdata` so hover still shows real month names. Added an info banner when date ranges differ explaining the alignment.
- **Files modified:** app.py
- **Verification:** Revenue overlay chart renders cleanly for any two companies regardless of date range alignment
- **Committed in:** ae915a8

---

**Total deviations:** 3 auto-fixed (all Rule 1 — bugs, identified at human-verify checkpoint)
**Impact on plan:** All fixes required for correctness. No scope creep; all changes are contained within the comparison rendering path.

## Issues Encountered
Three bugs surfaced during the human-verify checkpoint that required a follow-up fix commit. All were correctness bugs (not missing features) and were resolved in a single commit (`ae915a8`) without requiring an architectural decision.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- ANLYS-03 requirement satisfied and verified by human checkpoint
- Comparison view supports sample companies and uploaded companies in any combination
- Phase 08 plans complete; no further analysis-integration work planned for v1.1

---
*Phase: 08-analysis-integration*
*Completed: 2026-03-11*
