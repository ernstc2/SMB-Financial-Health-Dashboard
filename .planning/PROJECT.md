# SMB Financial Health Dashboard

## What This Is

A portfolio-grade consulting analytics tool that lets users upload SMB financial data (CSV/Excel) and instantly receive KPI scoring, RAG-rated benchmarks, automated insights, and interactive visualizations. Built with Python, Pandas, Streamlit, and Plotly. Designed to demonstrate the kind of data-driven deliverable a tech consultant would hand to a client.

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

### Active

<!-- Current scope. Building toward these. -->

- [ ] CSV/Excel file upload for user-supplied company data
- [ ] Downloadable data template matching required schema
- [ ] Strict upload validation with clear error messages
- [ ] Multi-company upload and side-by-side comparison
- [ ] Sample data mode (existing companies) as default demo
- [ ] All existing analysis works on uploaded data

### Out of Scope

- Public company API lookup (e.g., Yahoo Finance, SEC EDGAR) — doesn't fit SMB narrative, adds API dependency
- Flexible/auto-detected data formats — strict template is more reliable and professional
- User accounts or saved sessions — unnecessary for portfolio demo
- Database backend — file-based is sufficient for this use case

## Context

- **Portfolio project** targeting entry-level tech consulting roles. Hiring managers are the primary audience.
- Everything should be demo-able with zero setup — sample data loads by default, upload is optional.
- Current data shape: monthly rows with columns for revenue, COGS, operating expenses, headcount, cash balance.
- All KPI calculations and chart logic already work — they just need to accept dynamic data instead of hardcoded profiles.

## Constraints

- **Tech stack**: Python, Streamlit, Pandas, Plotly — no new frameworks
- **Data format**: Monthly financial data (revenue, COGS, opex, headcount, cash)
- **Audience**: Non-technical hiring managers — must be intuitive, polished, zero-friction
- **Deployment**: Must work as a single `streamlit run app.py` command

## Current Milestone: v1.1 Dynamic Data Upload

**Goal:** Transform the dashboard from hardcoded demo data to a tool that analyzes any SMB's financials via CSV/Excel upload, while keeping sample companies for demo mode.

**Target features:**
- CSV/Excel upload with multi-company support
- Downloadable template + strict validation with clear errors
- Sample data preserved as default demo mode
- Side-by-side comparison of uploaded companies

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| CSV/Excel upload over API lookup | Fits SMB consulting narrative; no API dependencies | — Pending |
| Strict template over flexible parsing | More reliable, professional UX, simpler to build | — Pending |
| Keep sample companies as demo mode | Hiring managers can explore without needing a file | — Pending |
| Multi-company comparison | Preserves comparative analysis angle from v1.0 | — Pending |

---
*Last updated: 2026-03-10 after milestone v1.1 kickoff*
