# SMB Financial Health Dashboard

## What This Is

A portfolio-grade consulting analytics tool that lets users upload SMB financial data (CSV/Excel) and instantly receive KPI scoring, RAG-rated benchmarks, automated insights, and interactive visualizations — with side-by-side company comparison. Built with Python, Pandas, Streamlit, and Plotly. Designed to demonstrate the kind of data-driven deliverable a tech consultant would hand to a client.

## Core Value

A hiring manager can open this tool, upload (or explore sample) financial data, and immediately understand an SMB's financial health — no setup, no friction.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ 5-section dashboard (Overview, Trends, Scorecard, Findings, Cash Flow) — v1.0
- ✓ 6 KPI calculations with RAG benchmarking (GM%, Rev Growth, OpEx Ratio, Rev/Employee, Burn Rate, Runway) — v1.0
- ✓ Rule-based insight generation sorted by severity — v1.0
- ✓ 2 synthetic company profiles (NovaSaaS, CloudForge) with 24-month data — v1.0
- ✓ Polished dark charcoal theme with custom typography — v1.0
- ✓ Interactive Plotly charts (waterfall, dual-axis, radar) — v1.0
- ✓ CSV/Excel file upload for user-supplied company data — v1.1
- ✓ Downloadable data template matching required schema — v1.1
- ✓ Strict upload validation with clear, actionable error messages — v1.1
- ✓ Multi-company upload with session persistence and unified dropdown — v1.1
- ✓ Sample data mode (NovaSaaS, CloudForge) as default demo — v1.1
- ✓ Side-by-side company comparison view (KPI table, radar, revenue overlay) — v1.1

### Active

<!-- Current scope. Building toward these. -->

(None — next milestone not yet planned)

### Out of Scope

- Public company API lookup (e.g., Yahoo Finance, SEC EDGAR) — doesn't fit SMB narrative, adds API dependency
- Flexible/auto-detected data formats — strict template is more reliable and professional
- User accounts or saved sessions — unnecessary for portfolio demo
- Database backend — file-based is sufficient for this use case

## Context

- **Portfolio project** targeting entry-level tech consulting roles. Hiring managers are the primary audience.
- Everything is demo-able with zero setup — sample data loads by default, upload is optional.
- Current data shape: monthly rows with columns for revenue, COGS, operating expenses, headcount, cash balance.
- **v1.0** shipped 5-section dashboard with hardcoded sample companies.
- **v1.1** added CSV/Excel upload, validation, multi-company session state, and side-by-side comparison.
- Codebase: ~2,025 LOC Python (app.py 1,007 + src/ 864 + tests/ 154). Single `streamlit run app.py` deployment.

## Constraints

- **Tech stack**: Python, Streamlit, Pandas, Plotly — no new frameworks
- **Data format**: Monthly financial data (revenue, COGS, opex, headcount, cash)
- **Audience**: Non-technical hiring managers — must be intuitive, polished, zero-friction
- **Deployment**: Must work as a single `streamlit run app.py` command

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| CSV/Excel upload over API lookup | Fits SMB consulting narrative; no API dependencies | ✓ Good — clean UX, no external deps |
| Strict template over flexible parsing | More reliable, professional UX, simpler to build | ✓ Good — validation catches all format issues |
| Keep sample companies as demo mode | Hiring managers can explore without needing a file | ✓ Good — zero-friction default |
| Multi-company comparison | Preserves comparative analysis angle from v1.0 | ✓ Good — natural extension of the tool |
| Session state dict for uploads | Multiple uploads accumulate; raw DataFrame stored pre-KPI | ✓ Good — handles re-uploads cleanly |
| Validate-before-calculate gate | Blocks invalid data from reaching KPI engine | ✓ Good — 10 tests verify all edge cases |
| Derived columns in read_uploaded_file | Existing pipeline stays unchanged; zero modifications to kpi_engine/charts | ✓ Good — minimal blast radius |
| Error display in st.container after upload widget | Errors visible near the upload, not buried at sidebar bottom | ✓ Good — bug fix during human-verify |
| Clean if/else for comparison vs single-company | Complete separation avoids fragile merged layout code | ✓ Good — maintainable |
| Month-index x-axis alignment | Companies with different date ranges render correctly on shared axis | ✓ Good — actual dates in hover customdata |

---
*Last updated: 2026-03-11 after v1.1 milestone*
