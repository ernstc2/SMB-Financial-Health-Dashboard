# Roadmap: SMB Financial Health Dashboard

## Milestones

- ✅ **v1.0 Foundation Dashboard** - Phases 1-5 (shipped pre-GSD)
- 🚧 **v1.1 Dynamic Data Upload** - Phases 6-8 (in progress)

## Phases

<details>
<summary>✅ v1.0 Foundation Dashboard (Phases 1-5) - SHIPPED pre-GSD</summary>

Phases 1-5 were built before GSD was adopted. What shipped:
- 5-section Streamlit dashboard with dark charcoal theme
- 2 synthetic SaaS company profiles (NovaSaaS, CloudForge) with 24-month data
- 6 KPI calculations with RAG benchmarking
- Rule-based insight generation
- Interactive Plotly charts (waterfall, dual-axis, radar)
- Custom typography and polished UI

</details>

### 🚧 v1.1 Dynamic Data Upload (In Progress)

**Milestone Goal:** Transform the dashboard from hardcoded demo data to a tool that analyzes any SMB's financials via CSV/Excel upload, while keeping sample companies for demo mode.

#### Phase 6: File Input

**Goal**: Users can supply their own financial data or explore sample companies with zero friction
**Depends on**: Phase 5 (v1.0 complete)
**Requirements**: INPUT-01, INPUT-02, INPUT-03
**Success Criteria** (what must be TRUE):
  1. User can upload a CSV or Excel file via the sidebar without leaving the dashboard
  2. User can download a pre-formatted template file that shows exactly what columns and format are required
  3. Dashboard loads NovaSaaS and CloudForge sample data by default when no file is uploaded
**Plans**: 2 plans

Plans:
- [x] 06-01-PLAN.md — Template file infrastructure and CSV/Excel reading utilities
- [x] 06-02-PLAN.md — Sidebar upload widget, download button, and data source switching

#### Phase 7: Validation

**Goal**: Uploaded files are reliably checked and users receive clear, fixable feedback on any problem
**Depends on**: Phase 6
**Requirements**: VALID-01, VALID-02, VALID-03
**Success Criteria** (what must be TRUE):
  1. User sees a specific error identifying which required columns are missing when the file lacks them
  2. User sees a specific error identifying which cells contain invalid data types or impossible values (e.g. negative headcount)
  3. Valid files pass through silently with no error shown
  4. Error messages tell the user exactly what to fix, not just that something is wrong
**Plans**: 1 plan

Plans:
- [x] 07-01-PLAN.md — TDD validation: column presence, data types, business rules, and app.py wiring

#### Phase 8: Analysis Integration

**Goal**: Uploaded company data flows through the full dashboard and users can compare any two companies side-by-side
**Depends on**: Phase 7
**Requirements**: ANLYS-01, ANLYS-02, ANLYS-03
**Success Criteria** (what must be TRUE):
  1. Uploaded companies appear by name in the sidebar company dropdown alongside sample companies
  2. Selecting an uploaded company shows a fully populated dashboard — all five sections render correctly with that company's data
  3. User can select any two companies and view their KPIs, charts, and scorecard side-by-side in a comparison view
**Plans**: 2 plans

Plans:
- [ ] 08-01-PLAN.md — Session state for uploaded companies, unified dropdown, full dashboard rendering
- [ ] 08-02-PLAN.md — Side-by-side comparison view with dual-company selection

## Progress

**Execution Order:** 6 → 7 → 8

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1-5. Foundation | v1.0 | — | Complete | pre-GSD |
| 6. File Input | v1.1 | 2/2 | Complete | 2026-03-11 |
| 7. Validation | v1.1 | 1/1 | Complete | 2026-03-11 |
| 8. Analysis Integration | 2/2 | Complete   | 2026-03-11 | - |
