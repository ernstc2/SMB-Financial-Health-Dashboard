# Requirements: SMB Financial Health Dashboard

**Defined:** 2026-03-10
**Core Value:** A hiring manager can open this tool, upload or explore sample financial data, and immediately understand an SMB's financial health — no setup, no friction.

## v1.1 Requirements

Requirements for milestone v1.1 — Dynamic Data Upload. Each maps to roadmap phases.

### Data Input

- [x] **INPUT-01**: User can upload CSV/Excel files via the sidebar
- [x] **INPUT-02**: User can download a pre-formatted template file showing the required data shape
- [x] **INPUT-03**: Sample companies (NovaSaaS, CloudForge) load by default when no files are uploaded

### Validation

- [x] **VALID-01**: System validates that required columns are present (date, revenue, COGS, opex, headcount, cash)
- [x] **VALID-02**: System validates data types (numeric values, valid dates, no impossible values)
- [x] **VALID-03**: System displays specific, actionable error messages telling users exactly what to fix

### Analysis

- [x] **ANLYS-01**: Uploaded companies appear in the sidebar dropdown for individual analysis
- [x] **ANLYS-02**: All existing dashboard sections (Overview, Trends, Scorecard, Findings, Cash Flow) work on uploaded data
- [x] **ANLYS-03**: User can compare two companies side-by-side in a new comparison view

## Future Requirements

Deferred to future milestones. Tracked but not in current roadmap.

### External Data

- **EXT-01**: User can look up public company financials by ticker symbol
- **EXT-02**: System auto-detects flexible/non-standard data formats

## Out of Scope

| Feature | Reason |
|---------|--------|
| Public company API lookup | Doesn't fit SMB consulting narrative; adds API dependency |
| Flexible/auto-detected formats | Strict template is more reliable and professional |
| User accounts / saved sessions | Unnecessary for portfolio demo |
| Database backend | File-based is sufficient for this use case |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| INPUT-01 | Phase 6 | Complete |
| INPUT-02 | Phase 6 | Complete (06-01) |
| INPUT-03 | Phase 6 | Complete |
| VALID-01 | Phase 7 | Complete |
| VALID-02 | Phase 7 | Complete |
| VALID-03 | Phase 7 | Complete |
| ANLYS-01 | Phase 8 | Complete |
| ANLYS-02 | Phase 8 | Complete |
| ANLYS-03 | Phase 8 | Complete |

**Coverage:**
- v1.1 requirements: 9 total
- Mapped to phases: 9
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-10*
*Last updated: 2026-03-11 — INPUT-02 completed in 06-01*
